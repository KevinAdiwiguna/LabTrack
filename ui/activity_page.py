"""
activity_page.py - Halaman activity log (admin only)
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QFrame, QDateEdit
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont

from ui.base_page import BasePage
from models.models import ActivityLog
import database.database as db


ACTIVITY_ICONS = {
    "LOGIN":           ("🔐", "#38bdf8"),
    "LOGOUT":          ("🚪", "#94a3b8"),
    "TAMBAH_BARANG":   ("➕", "#22c55e"),
    "EDIT_BARANG":     ("✏️", "#f59e0b"),
    "HAPUS_BARANG":    ("🗑️", "#ef4444"),
    "TAMBAH_KATEGORI": ("➕", "#22c55e"),
    "EDIT_KATEGORI":   ("✏️", "#f59e0b"),
    "HAPUS_KATEGORI":  ("🗑️", "#ef4444"),
    "TAMBAH_PEMINJAM": ("👤", "#22c55e"),
    "EDIT_PEMINJAM":   ("👤", "#f59e0b"),
    "HAPUS_PEMINJAM":  ("👤", "#ef4444"),
    "PEMINJAMAN":      ("📤", "#f59e0b"),
    "PENGEMBALIAN":    ("📥", "#22c55e"),
    "EXPORT_CSV":      ("📄", "#a78bfa"),
    "EXPORT_PDF":      ("📃", "#a78bfa"),
}


class ActivityPage(BasePage):
    def __init__(self):
        super().__init__("📝  Activity Log", "Rekaman semua aktivitas pengguna dalam sistem")
        self._setup_content()

    def _setup_content(self):
        # Filter bar
        fr = QHBoxLayout()
        fr.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari aksi / username / deskripsi...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(lambda: self._timer.start(300))

        lbl_from = QLabel("Dari:")
        lbl_from.setStyleSheet("color: #94a3b8;")
        self.date_from = QDateEdit(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setMinimumHeight(38)
        self.date_from.dateChanged.connect(self._load_data)

        lbl_to = QLabel("s/d:")
        lbl_to.setStyleSheet("color: #94a3b8;")
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setMinimumHeight(38)
        self.date_to.dateChanged.connect(self._load_data)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btn_icon")
        btn_refresh.clicked.connect(self._load_data)
        btn_refresh.setMinimumHeight(38)

        fr.addWidget(self.search_input, 2)
        fr.addWidget(lbl_from)
        fr.addWidget(self.date_from)
        fr.addWidget(lbl_to)
        fr.addWidget(self.date_to)
        fr.addWidget(btn_refresh)
        self.main_layout.addLayout(fr)

        # Table
        self.table = self.make_table(
            ["Waktu", "Username", "Aksi", "Deskripsi"],
            stretch_col=3
        )
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 110)
        self.table.setColumnWidth(2, 150)
        self.main_layout.addWidget(self.table)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("label_muted")
        self.main_layout.addWidget(self.lbl_count)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._load_data)

    def refresh(self):
        self._load_data()

    def _load_data(self):
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to   = self.date_to.date().toString("yyyy-MM-dd")
        logs   = ActivityLog.get_all(d_from, d_to)

        # Filter search
        search = self.search_input.text().strip().lower()
        if search:
            logs = [l for l in logs if
                    search in (l.get('action','') or '').lower() or
                    search in (l.get('username','') or '').lower() or
                    search in (l.get('description','') or '').lower()]

        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            icon, color = ACTIVITY_ICONS.get(log['action'], ("📌", "#94a3b8"))

            ts_item = self.table_item(log['timestamp'][:19], Qt.AlignCenter)
            ts_item.setForeground(QColor("#94a3b8"))
            self.table.setItem(row, 0, ts_item)

            user_item = self.colored_item(log.get('username') or "-", "#38bdf8")
            self.table.setItem(row, 1, user_item)

            action_item = self.colored_item(f"{icon}  {log['action']}", color)
            action_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.table.setItem(row, 2, action_item)

            self.table.setItem(row, 3, self.table_item(log.get('description') or "-"))

        self.lbl_count.setText(f"Menampilkan {len(logs)} aktivitas")
