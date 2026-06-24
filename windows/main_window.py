

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

import styles
from controllers import AuthController, LoanRequestController


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.dark_mode = True
        self.nav_buttons = {}
        self.pages = {}
        self._badge_timer = QTimer()
        self._badge_timer.timeout.connect(self._update_badge)

        self.setWindowTitle(f"LabTrack — {user.full_name}  [{user.role.upper()}]")
        self.setMinimumSize(1200, 720)
        self.setStyleSheet(styles.DARK_THEME)
        self._setup_ui()
        self._navigate("dashboard")

        # Polling badge notifikasi setiap 15 detik (untuk admin/laboran)
        if AuthController.can_edit():
            self._badge_timer.start(15000)
            self._update_badge()

    # ── Setup UI ──────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Logo
        logo = QLabel("🔬  LabTrack")
        logo.setObjectName("sidebar_logo")
        logo.setFont(QFont("Segoe UI", 17, QFont.Bold))
        sb_layout.addWidget(logo)

        sub = QLabel("Lab Inventory System")
        sub.setObjectName("sidebar_subtitle")
        sb_layout.addWidget(sub)

        div1 = QFrame(); div1.setObjectName("divider"); div1.setFixedHeight(1)
        sb_layout.addWidget(div1)
        sb_layout.addSpacing(6)

        # Nav items sesuai role
        for key, label in self._get_nav_items():
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(42)
            btn.setProperty("active", False)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            sb_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        sb_layout.addStretch()

        div2 = QFrame(); div2.setObjectName("divider"); div2.setFixedHeight(1)
        sb_layout.addWidget(div2)

        # Theme toggle
        self.btn_theme = QPushButton("☀️  Light Mode")
        self.btn_theme.setObjectName("nav_btn")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setMinimumHeight(40)
        self.btn_theme.clicked.connect(self._toggle_theme)
        sb_layout.addWidget(self.btn_theme)

        # User badge
        badge = QFrame()
        badge.setObjectName("user_badge")
        bl = QVBoxLayout(badge)
        bl.setContentsMargins(8, 8, 8, 8)
        bl.setSpacing(3)

        name_lbl = QLabel(self.user.full_name)
        name_lbl.setStyleSheet("color: #e2e8f0; font-weight: bold; font-size: 12px; background: transparent;")
        role_lbl = QLabel(f"@{self.user.username}  ·  {self.user.role.upper()}")
        role_lbl.setStyleSheet("color: #38bdf8; font-size: 11px; background: transparent;")
        bl.addWidget(name_lbl)
        bl.addWidget(role_lbl)

        btn_logout = QPushButton("🚪  Logout")
        btn_logout.setObjectName("btn_danger")
        btn_logout.setMinimumHeight(32)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.clicked.connect(self._do_logout)
        bl.addWidget(btn_logout)
        sb_layout.addWidget(badge)

        root.addWidget(sidebar)

        # Content Area
        content = QWidget()
        content.setObjectName("content_area")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        self.stack = QStackedWidget()
        cl.addWidget(self.stack)
        root.addWidget(content, 1)

    def _get_nav_items(self):
        role = self.user.role

        if role == 'viewer':
            return [
                ("dashboard",      "🏠  Dashboard"),
                ("catalog",        "🔎  Katalog Barang"),
                ("my_request",     "📬  Pengajuan Saya"),
                ("my_loans",       "📋  Riwayat Pinjam Saya"),
                ("my_profile",     "👤  Profil Saya"),
            ]
        elif role == 'laboran':
            return [
                ("dashboard",      "🏠  Dashboard"),
                ("inventory",      "📦  Inventaris"),
                ("categories",     "🏷️  Kategori"),
                ("borrowers",      "👥  Data Peminjam"),
                ("loans",          "📋  Peminjaman"),
                ("returns",        "🔄  Pengembalian"),
                ("approvals",      "✅  Konfirmasi Request"),
                ("reports",        "📊  Laporan & Export"),
                ("predict",        "🤖  Prediksi AI"),
            ]
        else:  # admin
            return [
                ("dashboard",      "🏠  Dashboard"),
                ("inventory",      "📦  Inventaris"),
                ("categories",     "🏷️  Kategori"),
                ("borrowers",      "👥  Data Peminjam"),
                ("loans",          "📋  Peminjaman"),
                ("returns",        "🔄  Pengembalian"),
                ("approvals",      "✅  Konfirmasi Request"),
                ("reports",        "📊  Laporan & Export"),
                ("users",          "🔑  Kelola Pengguna"),
                ("activity",       "📝  Activity Log"),
                ("predict",        "🤖  Prediksi AI"),
            ]

    # ── Navigasi ──────────────────────────────────────────────────

    def _get_page(self, key):
        if key not in self.pages:
            page = self._create_page(key)
            self.pages[key] = page
            self.stack.addWidget(page)
        return self.pages[key]

    def _create_page(self, key):
        from windows.dashboard_page  import DashboardPage
        from windows.inventory_page  import InventoryPage
        from windows.category_page   import CategoryPage
        from windows.borrower_page   import BorrowerPage
        from windows.loan_page       import LoanPage
        from windows.return_page     import ReturnPage
        from windows.report_page     import ReportPage
        from windows.activity_page   import ActivityPage
        from windows.predict_page    import PredictPage
        from windows.approvals_page  import ApprovalsPage
        from windows.user_mgmt_page  import UserMgmtPage
        from windows.viewer_pages    import CatalogPage, MyRequestPage, MyLoansPage, MyProfilePage

        mapping = {
            "dashboard":   DashboardPage,
            "inventory":   InventoryPage,
            "categories":  CategoryPage,
            "borrowers":   BorrowerPage,
            "loans":       LoanPage,
            "returns":     ReturnPage,
            "reports":     ReportPage,
            "activity":    ActivityPage,
            "predict":     PredictPage,
            "approvals":   ApprovalsPage,
            "users":       UserMgmtPage,
            "catalog":     CatalogPage,
            "my_request":  MyRequestPage,
            "my_loans":    MyLoansPage,
            "my_profile":  MyProfilePage,
        }
        cls = mapping.get(key)
        return cls() if cls else QWidget()

    def _navigate(self, key):
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        page = self._get_page(key)
        self.stack.setCurrentWidget(page)
        if hasattr(page, 'refresh'):
            page.refresh()

    def _update_badge(self):
        """Update label tombol Konfirmasi Request dengan jumlah pending"""
        if "approvals" not in self.nav_buttons:
            return
        count = LoanRequestController.get_pending_count()
        btn = self.nav_buttons["approvals"]
        if count > 0:
            btn.setText(f"✅  Konfirmasi Request  🔴{count}")
        else:
            btn.setText("✅  Konfirmasi Request")

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(styles.DARK_THEME)
            self.btn_theme.setText("☀️  Light Mode")
        else:
            self.setStyleSheet(styles.LIGHT_THEME)
            self.btn_theme.setText("🌙  Dark Mode")

    def _do_logout(self):
        reply = QMessageBox.question(
            self, "Konfirmasi Logout", "Apakah Anda yakin ingin logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._badge_timer.stop()
            AuthController.logout()
            from windows.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
