"""
borrower_page.py - Halaman manajemen data peminjam (Laboran & Admin only)
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDialog, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from windows.base_page import BasePage
from controllers import AuthController, BorrowerController


class BorrowerDialog(QDialog):
    def __init__(self, parent=None, borrower=None):
        super().__init__(parent)
        self.borrower = borrower
        self.setWindowTitle("Edit Peminjam" if borrower else "Tambah Peminjam")
        self.setMinimumWidth(420)
        self._setup_ui()
        if borrower:
            self.inp_nim.setText(borrower['nim'])
            self.inp_name.setText(borrower['name'])
            self.inp_dept.setText(borrower.get('department') or "")
            self.inp_phone.setText(borrower.get('phone') or "")
            self.inp_email.setText(borrower.get('email') or "")

    def _setup_ui(self):
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("👥  Tambah Peminjam" if not self.borrower else "✏️  Edit Peminjam")
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_nim   = QLineEdit(); self.inp_nim.setMinimumHeight(38); self.inp_nim.setPlaceholderText("NIM mahasiswa...")
        self.inp_name  = QLineEdit(); self.inp_name.setMinimumHeight(38); self.inp_name.setPlaceholderText("Nama lengkap...")
        self.inp_dept  = QLineEdit(); self.inp_dept.setMinimumHeight(38); self.inp_dept.setPlaceholderText("Teknik Elektro, Kimia...")
        self.inp_phone = QLineEdit(); self.inp_phone.setMinimumHeight(38); self.inp_phone.setPlaceholderText("08xxxxxxxxxx")
        self.inp_email = QLineEdit(); self.inp_email.setMinimumHeight(38); self.inp_email.setPlaceholderText("email@domain.com")

        form.addRow("NIM *",   self.inp_nim)
        form.addRow("Nama *",  self.inp_name)
        form.addRow("Jurusan", self.inp_dept)
        form.addRow("No HP",   self.inp_phone)
        form.addRow("Email",   self.inp_email)
        layout.addLayout(form)

        from PySide6.QtWidgets import QHBoxLayout
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal"); btn_cancel.setObjectName("btn_secondary"); btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("💾  Simpan"); btn_save.setObjectName("btn_primary"); btn_save.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel); btn_row.addStretch(); btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            'nim':        self.inp_nim.text().strip(),
            'name':       self.inp_name.text().strip(),
            'department': self.inp_dept.text().strip(),
            'phone':      self.inp_phone.text().strip(),
            'email':      self.inp_email.text().strip(),
        }


class BorrowerPage(BasePage):
    def __init__(self):
        super().__init__(
            "👥  Data Peminjam",
            "Kelola data mahasiswa/peminjam alat laboratorium"
        )
        self._setup_content()

    def _setup_content(self):
        if AuthController.can_edit():
            btn_add = QPushButton("➕  Tambah Peminjam")
            btn_add.setObjectName("btn_primary")
            btn_add.setMinimumHeight(36)
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.clicked.connect(self._add_borrower)
            self.header_buttons.addWidget(btn_add)

        from PySide6.QtWidgets import QHBoxLayout
        sr = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari nama / NIM / jurusan...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self._debounce_search)
        sr.addWidget(self.search_input)
        self.main_layout.addLayout(sr)

        self.table = self.make_table(
            ["NIM", "Nama", "Jurusan", "No HP", "Email", "Akun", "Aksi"],
            stretch_col=1
        )
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 110)
        self.table.setColumnWidth(6, 110)
        self.main_layout.addWidget(self.table)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("label_muted")
        self.main_layout.addWidget(self.lbl_count)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._load_data)

    def refresh(self):
        self._load_data()

    def _debounce_search(self):
        self._timer.start(300)

    def _load_data(self):
        borrowers = BorrowerController.get_all(self.search_input.text().strip())
        self.table.setRowCount(len(borrowers))
        for row, b in enumerate(borrowers):
            self.table.setItem(row, 0, self.colored_item(b['nim'], "#38bdf8"))
            self.table.setItem(row, 1, self.table_item(b['name']))
            self.table.setItem(row, 2, self.table_item(b.get('department') or "-", Qt.AlignCenter))
            self.table.setItem(row, 3, self.table_item(b.get('phone') or "-", Qt.AlignCenter))
            self.table.setItem(row, 4, self.table_item(b.get('email') or "-"))

            # Kolom akun terhubung
            if b.get('username'):
                acct_item = self.colored_item(f"@{b['username']}", "#22c55e")
            else:
                acct_item = self.colored_item("Belum ada", "#475569")
            self.table.setItem(row, 5, acct_item)

            if AuthController.can_edit():
                bw = QWidget(); bl = QHBoxLayout(bw); bl.setContentsMargins(4,2,4,2); bl.setSpacing(4)
                btn_e = QPushButton("✏️"); btn_e.setObjectName("btn_icon"); btn_e.clicked.connect(lambda _,x=b: self._edit_borrower(x))
                btn_d = QPushButton("🗑️"); btn_d.setObjectName("btn_icon"); btn_d.clicked.connect(lambda _,x=b: self._delete_borrower(x))
                bl.addWidget(btn_e); bl.addWidget(btn_d)
                self.table.setCellWidget(row, 6, bw)

        self.lbl_count.setText(f"Menampilkan {len(borrowers)} peminjam")

    def _add_borrower(self):
        dlg = BorrowerDialog(self); dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            ok, msg = BorrowerController.create(dlg.get_data())
            if ok:
                self.show_message("Berhasil", "Peminjam berhasil ditambahkan!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _edit_borrower(self, b):
        dlg = BorrowerDialog(self, b); dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            ok, msg = BorrowerController.update(b['id'], dlg.get_data())
            if ok:
                self.show_message("Berhasil", "Data peminjam berhasil diupdate!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _delete_borrower(self, b):
        if self.confirm("Hapus Peminjam", f"Hapus data '{b['name']}'?"):
            BorrowerController.delete(b['id'], b['name'])
            self._load_data()
