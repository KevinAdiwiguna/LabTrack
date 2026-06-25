"""
return_page.py - Halaman pengembalian barang
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDialog, QFormLayout, QMessageBox,
    QDateEdit, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor

from windows.base_page import BasePage
from controllers import AuthController, LoanController
from models import Loan
import utils


class ReturnDialog(QDialog):
    def __init__(self, parent, loan):
        super().__init__(parent)
        self.loan = loan
        self.detail_combos = {}
        self.setWindowTitle(f"Pengembalian - {loan['loan_code']}")
        self.setMinimumWidth(500)
        self._setup_ui()

    def _setup_ui(self):
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel(f"🔄  Pengembalian Barang")
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        # Info peminjaman
        info = QFrame()
        info.setStyleSheet("QFrame { background: #162032; border-radius: 8px; padding: 8px; }")
        info_layout = QVBoxLayout(info)
        info_layout.setSpacing(4)

        fields = [
            ("Kode Pinjam:",   self.loan['loan_code']),
            ("Peminjam:",      self.loan['borrower_name']),
            ("NIM:",           self.loan['nim']),
            ("Deadline:",      utils.format_date(self.loan['due_date'])),
        ]
        for label, val in fields:
            row = QHBoxLayout()
            l = QLabel(label); l.setStyleSheet("color: #64748b; font-size: 12px;"); l.setFixedWidth(100)
            v = QLabel(val);   v.setStyleSheet("color: #e2e8f0; font-size: 12px; font-weight: bold;")
            row.addWidget(l); row.addWidget(v); row.addStretch()
            info_layout.addLayout(row)

        # Terlambat
        if utils.is_overdue(self.loan['due_date']):
            warn = QLabel("⚠️  PERHATIAN: Peminjaman ini SUDAH MELEWATI batas waktu!")
            warn.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 12px; padding: 4px 0;")
            info_layout.addWidget(warn)
        layout.addWidget(info)

        # Tanggal pengembalian
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)
        self.date_return = QDateEdit(QDate.currentDate())
        self.date_return.setCalendarPopup(True)
        self.date_return.setDisplayFormat("dd/MM/yyyy")
        self.date_return.setMinimumHeight(38)
        form.addRow("Tanggal Kembali *", self.date_return)
        layout.addLayout(form)

        # Kondisi per barang
        details = Loan.get_details(self.loan['id'])
        if details:
            lbl = QLabel("Kondisi Barang yang Dikembalikan:")
            lbl.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 12px;")
            layout.addWidget(lbl)

            for d in details:
                row = QFrame()
                row.setStyleSheet("QFrame { background: #1e293b; border-radius: 6px; padding: 6px; }")
                rl = QHBoxLayout(row)
                rl.setContentsMargins(8, 4, 8, 4)

                item_lbl = QLabel(f"• {d['item_name']} (x{d['quantity']})")
                item_lbl.setStyleSheet("color: #e2e8f0; font-size: 12px;")
                rl.addWidget(item_lbl, 1)

                combo = QComboBox()
                combo.addItems(["Baik", "Rusak Ringan", "Rusak Berat"])
                combo.setMinimumHeight(34)
                combo.setMinimumWidth(140)
                rl.addWidget(combo)
                self.detail_combos[d['id']] = combo
                layout.addWidget(row)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal"); btn_cancel.setObjectName("btn_secondary"); btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("✅  Konfirmasi Pengembalian"); btn_save.setObjectName("btn_success"); btn_save.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel); btn_row.addStretch(); btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def get_data(self):
        return (
            self.date_return.date().toString("yyyy-MM-dd"),
            {did: combo.currentText() for did, combo in self.detail_combos.items()}
        )


class ReturnPage(BasePage):
    def __init__(self):
        super().__init__("🔄  Pengembalian Barang", "Proses pengembalian barang yang sedang dipinjam")
        self._setup_content()

    def _setup_content(self):
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari kode / nama peminjam / NIM...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(lambda: self._timer.start(300))
        self.main_layout.addWidget(self.search_input)

        self.table = self.make_table(
            ["Kode Pinjam", "Peminjam", "NIM", "Barang", "Tgl Pinjam", "Deadline", "Aksi"],
            stretch_col=3
        )
        self.table.setColumnWidth(0, 140)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)
        self.main_layout.addWidget(self.table)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("label_muted")
        self.main_layout.addWidget(self.lbl_count)

        self._timer = QTimer(); self._timer.setSingleShot(True); self._timer.timeout.connect(self._load_data)

    def refresh(self):
        self._load_data()

    def _load_data(self):
        loans = LoanController.get_all("dipinjam", self.search_input.text().strip())
        self.table.setRowCount(len(loans))
        for row, loan in enumerate(loans):
            overdue = utils.is_overdue(loan['due_date'])
            self.table.setItem(row, 0, self.colored_item(loan['loan_code'], "#38bdf8"))
            self.table.setItem(row, 1, self.table_item(loan['borrower_name']))
            self.table.setItem(row, 2, self.table_item(loan['nim'], Qt.AlignCenter))
            self.table.setItem(row, 3, self.table_item(loan.get('items_list') or "-"))
            self.table.setItem(row, 4, self.table_item(utils.format_date(loan['loan_date']), Qt.AlignCenter))

            due_item = self.table_item(utils.format_date(loan['due_date']), Qt.AlignCenter)
            due_item.setForeground(QColor("#ef4444" if overdue else "#e2e8f0"))
            if overdue:
                due_item.setText(utils.format_date(loan['due_date']) + " ⚠️")
            self.table.setItem(row, 5, due_item)

            if AuthController.can_edit():
                bw = QWidget(); bl = QHBoxLayout(bw); bl.setContentsMargins(4,2,4,2)
                btn_ret = QPushButton("↩️  Kembalikan")
                btn_ret.setObjectName("btn_success")
                btn_ret.clicked.connect(lambda _, l=loan: self._return_loan(l))
                bl.addWidget(btn_ret)
                self.table.setCellWidget(row, 6, bw)

        self.lbl_count.setText(f"{len(loans)} peminjaman aktif")

    def _return_loan(self, loan):
        dlg = ReturnDialog(self, loan); dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            return_date, conditions = dlg.get_data()
            ok, status = LoanController.return_loan(loan['id'], return_date, conditions)
            if ok:
                msg = "Pengembalian berhasil dicatat!"
                if status == "terlambat":
                    msg += "\n⚠️ Status: TERLAMBAT"
                self.show_message("Berhasil", msg)
                self._load_data()
