from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect,
    QStackedWidget, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from controllers import AuthController
import assets.styles as styles


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LabTrack - Login")
        self.setMinimumSize(960, 620)
        self.setStyleSheet(styles.DARK_THEME)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0c1445, stop:0.5 #0e2858, stop:1 #0c3b6e);
            }
        """)
        left_panel.setMinimumWidth(420)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setSpacing(12)

        icon_frame = QFrame()
        icon_frame.setFixedSize(90, 90)
        icon_frame.setStyleSheet("""
            QFrame {
                background: rgba(56,189,248,0.15);
                border: 2px solid #38bdf8;
                border-radius: 20px;
            }
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_label = QLabel("🔬")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI Emoji", 36))
        icon_layout.addWidget(icon_label)
        left_layout.addWidget(icon_frame, alignment=Qt.AlignHCenter)

        app_name = QLabel("LabTrack")
        app_name.setStyleSheet("color: #38bdf8; font-size: 42px; font-weight: bold; background: transparent;")
        app_name.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(app_name)

        tagline = QLabel("Sistem Inventaris & Peminjaman\nLaboratorium Kampus")
        tagline.setStyleSheet("color: #93c5fd; font-size: 15px; background: transparent;")
        tagline.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(tagline)

        left_layout.addSpacing(24)

        features = [
            ("🔐", "Login Multi-Role: Admin, Laboran, Viewer"),
            ("📦", "Manajemen Inventaris Lengkap"),
            ("📋", "Sistem Peminjaman & Pengembalian"),
            ("✅", "Pengajuan & Konfirmasi oleh Laboran"),
            ("📊", "Laporan, Grafik & Prediksi AI"),
        ]
        for icon, text in features:
            row = QHBoxLayout()
            row.setAlignment(Qt.AlignLeft)
            row.setContentsMargins(40, 0, 40, 0)
            ic = QLabel(icon)
            ic.setFont(QFont("Segoe UI Emoji", 13))
            ic.setFixedWidth(28)
            tx = QLabel(text)
            tx.setStyleSheet("color: #bfdbfe; font-size: 12px;")
            row.addWidget(ic)
            row.addWidget(tx)
            left_layout.addLayout(row)

        left_layout.addSpacing(20)
        version = QLabel("v2.0.0 · Tugas Pemrograman Visual")
        version.setStyleSheet("color: #475569; font-size: 11px; background: transparent;")
        version.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(version)

        main_layout.addWidget(left_panel)

        # ── Panel Kanan (Form) ────────────────────────────────────
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background: #0f172a; }")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(60, 40, 60, 40)

        # Stack: halaman login & registrasi
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_login_card())
        self.stack.addWidget(self._build_register_card())
        self.stack.setCurrentIndex(0)

        right_layout.addWidget(self.stack, alignment=Qt.AlignCenter)
        main_layout.addWidget(right_panel, 1)

    # ── Form Login ────────────────────────────────────────────────

    def _build_login_card(self):
        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet("""
            #loginCard {
                background: #1e293b;
                border-radius: 16px;
                border: 1px solid #334155;
            }
        """)
        card.setMinimumWidth(360)
        card.setMaximumWidth(420)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        title = QLabel("Selamat Datang 👋")
        title.setStyleSheet("color: #f1f5f9; font-size: 22px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title)

        sub = QLabel("Masuk ke sistem LabTrack")
        sub.setStyleSheet("color: #64748b; font-size: 13px; background: transparent;")
        header_layout.addWidget(sub)

        layout.addLayout(header_layout)
        layout.addSpacing(16)

        input_style = """
            QLineEdit {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #38bdf8;
            }
        """

        # Username
        user_layout = QVBoxLayout()
        user_layout.setSpacing(6)
        lbl_u = QLabel("Username")
        lbl_u.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: transparent;")
        user_layout.addWidget(lbl_u)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Masukkan username...")
        self.inp_username.setStyleSheet(input_style)
        self.inp_username.setFixedHeight(40)
        self.inp_username.setText("admin")
        user_layout.addWidget(self.inp_username)
        layout.addLayout(user_layout)

        # Password
        pass_layout = QVBoxLayout()
        pass_layout.setSpacing(6)
        lbl_p = QLabel("Password")
        lbl_p.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: transparent;")
        pass_layout.addWidget(lbl_p)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)

        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Masukkan password...")
        self.inp_password.setEchoMode(QLineEdit.Password)
        self.inp_password.setStyleSheet(input_style)
        self.inp_password.setFixedHeight(40)
        self.inp_password.setText("admin123")
        self.inp_password.returnPressed.connect(self._do_login)
        pwd_row.addWidget(self.inp_password)

        self.chk_show = QCheckBox()
        self.chk_show.setToolTip("Tampilkan password")
        self.chk_show.setStyleSheet("""
            QCheckBox { color: #64748b; }
            QCheckBox::indicator { width: 16px; height: 16px; }
        """)
        self.chk_show.toggled.connect(
            lambda v: self.inp_password.setEchoMode(
                QLineEdit.Normal if v else QLineEdit.Password
            )
        )
        pwd_row.addWidget(self.chk_show)
        pass_layout.addLayout(pwd_row)
        layout.addLayout(pass_layout)

        layout.addSpacing(16)

        # Error & Tombol Login
        self.lbl_login_error = QLabel("")
        self.lbl_login_error.setStyleSheet("color: #f87171; font-size: 12px;")
        self.lbl_login_error.setAlignment(Qt.AlignCenter)
        self.lbl_login_error.hide()
        layout.addWidget(self.lbl_login_error)

        self.btn_login = QPushButton("  🔓  Masuk")
        self.btn_login.setObjectName("btn_primary")
        self.btn_login.setMinimumHeight(46)
        self.btn_login.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._do_login)
        layout.addWidget(self.btn_login)

        # Divider
        div_row = QHBoxLayout()
        l1 = QFrame()
        l1.setStyleSheet("background-color: #334155; border: none;")
        l1.setFixedHeight(1)
        l2 = QFrame()
        l2.setStyleSheet("background-color: #334155; border: none;")
        l2.setFixedHeight(1)
        div_lbl = QLabel("atau")
        div_lbl.setStyleSheet("color: #475569; font-size: 11px; padding: 0 8px; background: transparent;")
        div_lbl.setAlignment(Qt.AlignCenter)
        div_row.addWidget(l1)
        div_row.addWidget(div_lbl)
        div_row.addWidget(l2)
        layout.addLayout(div_row)

        btn_reg = QPushButton("📝  Daftar Akun Baru")
        btn_reg.setObjectName("btn_secondary")
        btn_reg.setMinimumHeight(40)
        btn_reg.setCursor(Qt.PointingHandCursor)
        btn_reg.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(btn_reg)

        hint = QLabel("Demo: admin/admin123 · laboran/laboran123 · viewer/viewer123")
        hint.setStyleSheet("color: #334155; font-size: 10px; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        layout.addWidget(hint)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setAlignment(Qt.AlignCenter)
        wrapper_layout.addWidget(card)

        return wrapper

    # ── Form Registrasi ───────────────────────────────────────────

    def _build_register_card(self):
        card = QFrame()
        card.setObjectName("registerCard")
        card.setStyleSheet("""
            #registerCard {
                background: #1e293b;
                border-radius: 16px;
                border: 1px solid #334155;
            }
        """)
        card.setMinimumWidth(360)
        card.setMaximumWidth(420)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(10)

        title = QLabel("Buat Akun Baru 📝")
        title.setStyleSheet("color: #f1f5f9; font-size: 21px; font-weight: bold; background: transparent;")
        layout.addWidget(title)

        sub = QLabel("Akun baru akan terdaftar sebagai Viewer")
        sub.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        layout.addWidget(sub)

        # Role badge info
        info = QFrame()
        info.setStyleSheet("""
            QFrame { background: rgba(56,189,248,0.08);
                     border: 1px solid #0369a1; border-radius: 8px; padding: 6px; }
        """)
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(10, 6, 10, 6)
        info_layout.setSpacing(2)
        info_lbl = QLabel(
            "ℹ️  Setelah daftar, Anda dapat:\n"
            "• Melihat katalog barang laboratorium\n"
            "• Mengajukan peminjaman barang\n"
            "• Mengajukan pengembalian barang\n"
            "• Admin/Laboran akan mengkonfirmasi pengajuan Anda"
        )
        info_lbl.setStyleSheet("color: #93c5fd; font-size: 11px;")
        info_lbl.setWordWrap(True)
        info_layout.addWidget(info_lbl)
        layout.addWidget(info)

        layout.addSpacing(8)

        input_style = """
            QLineEdit {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #38bdf8;
            }
        """

        lbl_fn = QLabel("Nama Lengkap *")
        lbl_fn.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: transparent;")
        layout.addWidget(lbl_fn)
        self.reg_fullname = QLineEdit()
        self.reg_fullname.setPlaceholderText("Nama lengkap Anda...")
        self.reg_fullname.setStyleSheet(input_style)
        self.reg_fullname.setFixedHeight(40)
        layout.addWidget(self.reg_fullname)

        lbl_u = QLabel("Username *")
        lbl_u.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: transparent;")
        layout.addWidget(lbl_u)
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Minimal 4 karakter...")
        self.reg_username.setStyleSheet(input_style)
        self.reg_username.setFixedHeight(40)
        layout.addWidget(self.reg_username)

        lbl_p = QLabel("Password *")
        lbl_p.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: transparent;")
        layout.addWidget(lbl_p)
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Minimal 6 karakter...")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setStyleSheet(input_style)
        self.reg_password.setFixedHeight(40)
        layout.addWidget(self.reg_password)

        lbl_p2 = QLabel("Konfirmasi Password *")
        lbl_p2.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: transparent;")
        layout.addWidget(lbl_p2)
        self.reg_password2 = QLineEdit()
        self.reg_password2.setPlaceholderText("Ulangi password...")
        self.reg_password2.setEchoMode(QLineEdit.Password)
        self.reg_password2.setStyleSheet(input_style)
        self.reg_password2.setFixedHeight(40)
        self.reg_password2.returnPressed.connect(self._do_register)
        layout.addWidget(self.reg_password2)

        layout.addSpacing(8)

        self.lbl_reg_error = QLabel("")
        self.lbl_reg_error.setStyleSheet("color: #f87171; font-size: 12px;")
        self.lbl_reg_error.setAlignment(Qt.AlignCenter)
        self.lbl_reg_error.setWordWrap(True)
        self.lbl_reg_error.hide()
        layout.addWidget(self.lbl_reg_error)

        self.btn_register = QPushButton("✅  Daftar Sekarang")
        self.btn_register.setObjectName("btn_success")
        self.btn_register.setMinimumHeight(44)
        self.btn_register.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.clicked.connect(self._do_register)
        layout.addWidget(self.btn_register)

        btn_back = QPushButton("← Kembali ke Login")
        btn_back.setObjectName("btn_secondary")
        btn_back.setMinimumHeight(38)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(btn_back)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setAlignment(Qt.AlignCenter)
        wrapper_layout.addWidget(card)

        return wrapper

    # ── Aksi Login ────────────────────────────────────────────────

    def _do_login(self):
        username = self.inp_username.text().strip()
        password = self.inp_password.text()
        if not username or not password:
            self._show_login_error("Username dan password tidak boleh kosong")
            return
        self.btn_login.setText("⏳  Memproses...")
        self.btn_login.setEnabled(False)
        QTimer.singleShot(350, lambda: self._process_login(username, password))

    def _process_login(self, username, password):
        ok, user = AuthController.login(username, password)
        if ok:
            self._open_main(user)
        else:
            self._show_login_error("Username atau password salah")
            self.btn_login.setText("  🔓  Masuk")
            self.btn_login.setEnabled(True)

    def _show_login_error(self, msg):
        self.lbl_login_error.setText(f"⚠  {msg}")
        self.lbl_login_error.show()

    # ── Aksi Registrasi ───────────────────────────────────────────

    def _do_register(self):
        full_name = self.reg_fullname.text().strip()
        username  = self.reg_username.text().strip()
        password  = self.reg_password.text()
        password2 = self.reg_password2.text()

        if not full_name or not username or not password:
            self._show_reg_error("Semua field wajib diisi")
            return
        if password != password2:
            self._show_reg_error("Konfirmasi password tidak cocok")
            return

        self.btn_register.setText("⏳  Mendaftarkan...")
        self.btn_register.setEnabled(False)

        ok, result = AuthController.register(username, password, full_name)
        if ok:
            # Kosongkan form
            self.reg_fullname.clear()
            self.reg_username.clear()
            self.reg_password.clear()
            self.reg_password2.clear()
            self.lbl_reg_error.hide()
            self.btn_register.setText("✅  Daftar Sekarang")
            self.btn_register.setEnabled(True)

            QMessageBox.information(
                self, "Registrasi Berhasil",
                f"🎉  Akun <b>{username}</b> berhasil dibuat!\n\n"
                "Silakan login dengan akun Anda.\n"
                "Anda bisa langsung mengajukan peminjaman setelah login."
            )
            # Isi username di form login dan kembali
            self.inp_username.setText(username)
            self.inp_password.clear()
            self.stack.setCurrentIndex(0)
        else:
            self._show_reg_error(str(result))
            self.btn_register.setText("✅  Daftar Sekarang")
            self.btn_register.setEnabled(True)

    def _show_reg_error(self, msg):
        self.lbl_reg_error.setText(f"⚠  {msg}")
        self.lbl_reg_error.show()

    def _open_main(self, user):
        from ui.main_window import MainWindow
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()
