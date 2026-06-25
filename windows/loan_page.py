"""
loan_page.py - Halaman sistem peminjaman barang
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDialog, QFormLayout, QMessageBox,
    QSpinBox, QDateEdit, QTextEdit, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont

from windows.base_page import BasePage
from controllers import AuthController, LoanController, BorrowerController, ItemController
import utils


class LoanItemRow(QFrame):
    """Baris pemilihan barang dalam form peminjaman"""
    def __init__(self, items_list, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background: #162032; border-radius: 6px; padding: 4px; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.combo_item = QComboBox()
        self.combo_item.setMinimumHeight(36)
        self.combo_item.setMinimumWidth(240)
        for item in items_list:
            self.combo_item.addItem(f"{item['name']} (Stok: {item['stock']})", item['id'])

        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 999)
        self.spin_qty.setValue(1)
        self.spin_qty.setMinimumHeight(36)
        self.spin_qty.setMinimumWidth(80)

        self.combo_cond = QComboBox()
        self.combo_cond.addItems(["Baik", "Rusak Ringan"])
        self.combo_cond.setMinimumHeight(36)

        btn_remove = QPushButton("✕")
        btn_remove.setObjectName("btn_icon")
        btn_remove.setFixedWidth(36)
        btn_remove.clicked.connect(lambda: self.setParent(None))

        layout.addWidget(QLabel("Barang:"))
        layout.addWidget(self.combo_item, 2)
        layout.addWidget(QLabel("Qty:"))
        layout.addWidget(self.spin_qty)
        layout.addWidget(QLabel("Kondisi:"))
        layout.addWidget(self.combo_cond)
        layout.addWidget(btn_remove)

    def get_data(self):
        return (
            self.combo_item.currentData(),
            self.spin_qty.value(),
            self.combo_cond.currentText()
        )


class LoanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Peminjaman")
        self.setMinimumWidth(620)
        self.setMinimumHeight(580)
        self.item_rows = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("📋  Form Peminjaman Barang")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        # Peminjam
        self.combo_borrower = QComboBox()
        self.combo_borrower.setMinimumHeight(38)
        borrowers = BorrowerController.get_all()
        for b in borrowers:
            self.combo_borrower.addItem(f"{b['name']} ({b['nim']})", b['id'])

        # Tanggal
        today = QDate.currentDate()
        self.date_loan = QDateEdit(today)
        self.date_loan.setMinimumHeight(38)
        self.date_loan.setCalendarPopup(True)
        self.date_loan.setDisplayFormat("dd/MM/yyyy")

        self.date_due = QDateEdit(today.addDays(7))
        self.date_due.setMinimumHeight(38)
        self.date_due.setCalendarPopup(True)
        self.date_due.setDisplayFormat("dd/MM/yyyy")

        self.inp_notes = QTextEdit()
        self.inp_notes.setPlaceholderText("Catatan tambahan...")
        self.inp_notes.setMaximumHeight(70)

        form.addRow("Peminjam *",      self.combo_borrower)
        form.addRow("Tanggal Pinjam *", self.date_loan)
        form.addRow("Deadline Kembali *", self.date_due)
        form.addRow("Catatan",         self.inp_notes)
        layout.addLayout(form)

        # Daftar barang
        items_header = QHBoxLayout()
        items_label = QLabel("Barang yang Dipinjam *")
        items_label.setStyleSheet("color: #94a3b8; font-weight: bold;")
        items_header.addWidget(items_label)
        items_header.addStretch()

        btn_add_item = QPushButton("➕  Tambah Barang")
        btn_add_item.setObjectName("btn_secondary")
        btn_add_item.clicked.connect(self._add_item_row)
        items_header.addWidget(btn_add_item)
        layout.addLayout(items_header)

        # Scroll area untuk baris barang
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #334155; border-radius: 8px; }")
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(4, 4, 4, 4)
        self.items_layout.setSpacing(4)
        self.items_layout.addStretch()
        scroll.setWidget(self.items_container)
        layout.addWidget(scroll)

        # Load items
        self.all_items = ItemController.get_all()
        self._add_item_row()  # Default satu baris

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal"); btn_cancel.setObjectName("btn_secondary"); btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("✅  Proses Peminjaman"); btn_save.setObjectName("btn_primary"); btn_save.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel); btn_row.addStretch(); btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _add_item_row(self):
        row = LoanItemRow(self.all_items, self.items_container)
        self.items_layout.insertWidget(self.items_layout.count() - 1, row)
        self.item_rows.append(row)

    def get_data(self):
        details = []
        for i in range(self.items_layout.count() - 1):
            widget = self.items_layout.itemAt(i).widget()
            if isinstance(widget, LoanItemRow) and widget.parent():
                details.append(widget.get_data())
        return {
            'borrower_id': self.combo_borrower.currentData(),
            'loan_date':   self.date_loan.date().toString("yyyy-MM-dd"),
            'due_date':    self.date_due.date().toString("yyyy-MM-dd"),
            'notes':       self.inp_notes.toPlainText().strip(),
            'details':     details,
        }


class LoanPage(BasePage):
    def __init__(self):
        super().__init__("📋  Peminjaman", "Manajemen transaksi peminjaman alat laboratorium")
        self._setup_content()

    def _setup_content(self):
        if AuthController.can_edit():
            btn_add = QPushButton("➕  Buat Peminjaman")
            btn_add.setObjectName("btn_primary")
            btn_add.setMinimumHeight(36)
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.clicked.connect(self._add_loan)
            self.header_buttons.addWidget(btn_add)

        # Filter bar
        fr = QHBoxLayout(); fr.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari kode / nama / NIM...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(lambda: self._timer.start(300))

        self.filter_status = QComboBox()
        self.filter_status.setMinimumHeight(38)
        self.filter_status.setMinimumWidth(150)
        self.filter_status.addItems(["Semua Status", "dipinjam", "dikembalikan", "terlambat"])
        self.filter_status.currentIndexChanged.connect(self._load_data)

        fr.addWidget(self.search_input, 2)
        fr.addWidget(self.filter_status, 1)
        self.main_layout.addLayout(fr)

        self.table = self.make_table(
            ["Kode Pinjam", "Peminjam", "NIM", "Barang", "Tgl Pinjam", "Deadline", "Status"],
            stretch_col=3
        )
        self.table.setColumnWidth(0, 140)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 110)
        self.main_layout.addWidget(self.table)

        self._timer = QTimer(); self._timer.setSingleShot(True); self._timer.timeout.connect(self._load_data)

    def refresh(self):
        self._load_data()

    def _load_data(self):
        status = self.filter_status.currentText()
        if status == "Semua Status":
            status = None
        loans = LoanController.get_all(status, self.search_input.text().strip())
        self.table.setRowCount(len(loans))
        for row, loan in enumerate(loans):
            self.table.setItem(row, 0, self.colored_item(loan['loan_code'], "#38bdf8"))
            self.table.setItem(row, 1, self.table_item(loan['borrower_name']))
            self.table.setItem(row, 2, self.table_item(loan['nim'], Qt.AlignCenter))
            self.table.setItem(row, 3, self.table_item(loan.get('items_list') or "-"))
            self.table.setItem(row, 4, self.table_item(utils.format_date(loan['loan_date']), Qt.AlignCenter))
            # Highlight deadline
            due_color = "#ef4444" if utils.is_overdue(loan['due_date']) and loan['status']=='dipinjam' else "#e2e8f0"
            due_item = self.table_item(utils.format_date(loan['due_date']), Qt.AlignCenter)
            from PySide6.QtGui import QColor
            due_item.setForeground(QColor(due_color))
            self.table.setItem(row, 5, due_item)

            status_colors = {"dipinjam": "#f59e0b", "dikembalikan": "#22c55e", "terlambat": "#ef4444"}
            self.table.setItem(row, 6, self.colored_item(
                loan['status'].upper(), status_colors.get(loan['status'], "#e2e8f0")
            ))

    def _add_loan(self):
        dlg = LoanDialog(self); dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            ok, msg = LoanController.create(
                data['borrower_id'], data['loan_date'], data['due_date'],
                data['notes'], data['details']
            )
            if ok:
                self.show_message("Berhasil", f"Peminjaman berhasil dicatat!")
                self._load_data()
            else:
                self.show_message("Gagal", str(msg), QMessageBox.Warning)
