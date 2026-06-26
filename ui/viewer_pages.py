"""
viewer_pages.py - Halaman khusus untuk role Viewer
  - CatalogPage   : lihat katalog barang & ajukan peminjaman
  - MyRequestPage : lihat status pengajuan sendiri
  - MyLoansPage   : riwayat peminjaman sendiri
  - MyProfilePage : profil & lengkapi data peminjam
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QDialog, QFormLayout,
    QDateEdit, QTextEdit, QMessageBox, QScrollArea, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont

from ui.base_page import BasePage
from controllers import AuthController, LoanRequestController, CategoryController, BorrowerController
from models.models import Item, Borrower, Loan, LoanRequest
import database.database as db
import utils.utils as utils


# ── Helper: cek apakah viewer sudah punya profil peminjam ────────

def get_my_borrower():
    uid = AuthController.current_user.id
    return Borrower.get_by_user_id(uid)


# ═════════════════════════════════════════════════════════════════
# 1. Katalog Barang
# ═════════════════════════════════════════════════════════════════

class RequestLoanDialog(QDialog):
    """Dialog pengajuan peminjaman oleh viewer"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📬  Ajukan Peminjaman")
        self.setMinimumWidth(580)
        self.setMinimumHeight(520)
        self.item_rows = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("📬  Formulir Pengajuan Peminjaman")
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        info = QLabel(
            "ℹ️  Pengajuan Anda akan menunggu konfirmasi dari Laboran/Admin sebelum diproses."
        )
        info.setStyleSheet(
            "color: #93c5fd; font-size: 12px; background: rgba(56,189,248,0.08);"
            "border: 1px solid #0369a1; border-radius: 6px; padding: 8px;"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.date_due = QDateEdit(QDate.currentDate().addDays(7))
        self.date_due.setCalendarPopup(True)
        self.date_due.setDisplayFormat("dd/MM/yyyy")
        self.date_due.setMinimumHeight(38)

        self.inp_notes = QTextEdit()
        self.inp_notes.setPlaceholderText("Tujuan peminjaman, keperluan, dll...")
        self.inp_notes.setMaximumHeight(60)

        form.addRow("Deadline Pengembalian *", self.date_due)
        form.addRow("Catatan / Tujuan",        self.inp_notes)
        layout.addLayout(form)

        # Daftar barang
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Barang yang Ingin Dipinjam *"))
        hdr.addStretch()
        btn_add = QPushButton("➕  Tambah Barang")
        btn_add.setObjectName("btn_secondary")
        btn_add.clicked.connect(self._add_row)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(180)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #334155; border-radius: 8px; }")
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(4, 4, 4, 4)
        self.items_layout.setSpacing(4)
        self.items_layout.addStretch()
        scroll.setWidget(self.items_container)
        layout.addWidget(scroll)

        self.all_items = Item.get_all()
        self._add_row()

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("📬  Kirim Pengajuan")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _add_row(self):
        row_frame = QFrame()
        row_frame.setStyleSheet(
            "QFrame { background: #162032; border-radius: 6px; }"
        )
        rl = QHBoxLayout(row_frame)
        rl.setContentsMargins(8, 4, 8, 4)
        rl.setSpacing(8)

        combo = QComboBox()
        combo.setMinimumHeight(34)
        for item in self.all_items:
            combo.addItem(f"{item['name']}  (Stok: {item['stock']})", item['id'])

        spin = QSpinBox()
        spin.setRange(1, 999)
        spin.setMinimumHeight(34)
        spin.setMinimumWidth(70)

        btn_rm = QPushButton("✕")
        btn_rm.setObjectName("btn_icon")
        btn_rm.setFixedWidth(32)
        btn_rm.clicked.connect(lambda: row_frame.setParent(None))

        rl.addWidget(QLabel("Barang:"))
        rl.addWidget(combo, 2)
        rl.addWidget(QLabel("Qty:"))
        rl.addWidget(spin)
        rl.addWidget(btn_rm)

        self.items_layout.insertWidget(self.items_layout.count() - 1, row_frame)

    def get_data(self):
        details = []
        for i in range(self.items_layout.count() - 1):
            w = self.items_layout.itemAt(i).widget()
            if w and isinstance(w, QFrame) and w.parent():
                rl = w.layout()
                combo = None
                spin  = None
                for j in range(rl.count()):
                    item = rl.itemAt(j).widget()
                    if isinstance(item, QComboBox):
                        combo = item
                    elif isinstance(item, QSpinBox):
                        spin = item
                if combo and spin:
                    details.append((combo.currentData(), spin.value()))
        return {
            'due_date': self.date_due.date().toString("yyyy-MM-dd"),
            'notes':    self.inp_notes.toPlainText().strip(),
            'details':  details,
        }


class CatalogPage(BasePage):
    def __init__(self):
        super().__init__(
            "🔎  Katalog Barang",
            "Lihat ketersediaan barang laboratorium dan ajukan peminjaman"
        )
        self._setup_content()

    def _setup_content(self):
        # Tombol ajukan
        self.btn_request = QPushButton("📬  Ajukan Peminjaman")
        self.btn_request.setObjectName("btn_primary")
        self.btn_request.setMinimumHeight(36)
        self.btn_request.setCursor(Qt.PointingHandCursor)
        self.btn_request.clicked.connect(self._open_request_dialog)
        self.header_buttons.addWidget(self.btn_request)

        # Info profil
        self.info_banner = QFrame()
        self.info_banner.setStyleSheet("""
            QFrame { background: rgba(245,158,11,0.12);
                     border: 1px solid #d97706; border-radius: 8px; }
        """)
        ib_layout = QHBoxLayout(self.info_banner)
        ib_layout.setContentsMargins(12, 8, 12, 8)
        self.lbl_profile_info = QLabel("")
        self.lbl_profile_info.setStyleSheet("color: #fbbf24; font-size: 12px;")
        self.lbl_profile_info.setWordWrap(True)
        btn_goto = QPushButton("→ Lengkapi Profil")
        btn_goto.setObjectName("btn_secondary")
        btn_goto.clicked.connect(self._goto_profile)
        ib_layout.addWidget(self.lbl_profile_info, 1)
        ib_layout.addWidget(btn_goto)
        self.main_layout.addWidget(self.info_banner)

        # Filter
        fr = QHBoxLayout(); fr.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari nama barang...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(lambda: self._timer.start(300))

        self.filter_cat = QComboBox()
        self.filter_cat.setMinimumHeight(38)
        self.filter_cat.setMinimumWidth(160)
        self.filter_cat.addItem("Semua Kategori", None)
        self.filter_cat.currentIndexChanged.connect(self._load_data)

        fr.addWidget(self.search_input, 2)
        fr.addWidget(self.filter_cat, 1)
        self.main_layout.addLayout(fr)

        # Tabel
        self.table = self.make_table(
            ["Kode", "Nama Barang", "Kategori", "Stok", "Kondisi", "Lokasi"],
            stretch_col=1
        )
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(3, 65)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 120)
        self.main_layout.addWidget(self.table)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._load_data)

    def refresh(self):
        # Update filter kategori
        self.filter_cat.clear()
        self.filter_cat.addItem("Semua Kategori", None)
        for c in CategoryController.get_all():
            self.filter_cat.addItem(c['name'], c['id'])

        # Cek profil
        borrower = get_my_borrower()
        if not borrower:
            self.info_banner.show()
            self.lbl_profile_info.setText(
                "⚠️  Profil peminjam Anda belum dilengkapi. "
                "Lengkapi profil terlebih dahulu agar pengajuan dapat diproses."
            )
        else:
            self.info_banner.hide()

        self._load_data()

    def _load_data(self):
        items = Item.get_all(
            self.search_input.text().strip(),
            self.filter_cat.currentData()
        )
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, self.colored_item(item['item_code'], "#64748b"))
            self.table.setItem(row, 1, self.table_item(item['name']))
            self.table.setItem(row, 2, self.table_item(item.get('category_name') or "-", Qt.AlignCenter))
            stk = item['stock']
            stk_color = "#22c55e" if stk > 3 else "#f59e0b" if stk > 0 else "#ef4444"
            stk_label = str(stk) if stk > 0 else "Habis"
            self.table.setItem(row, 3, self.colored_item(stk_label, stk_color))
            cond_c = {"Baik": "#22c55e", "Rusak Ringan": "#f59e0b", "Rusak Berat": "#ef4444"}
            self.table.setItem(row, 4, self.colored_item(
                item['condition'], cond_c.get(item['condition'], "#e2e8f0")
            ))
            self.table.setItem(row, 5, self.table_item(item['location'] or "-", Qt.AlignCenter))

    def _open_request_dialog(self):
        borrower = get_my_borrower()
        if not borrower:
            self.show_message(
                "Profil Belum Lengkap",
                "Anda harus melengkapi profil peminjam terlebih dahulu.\n"
                "Silakan buka menu 'Profil Saya' dan isi data NIM, nama, jurusan, dll.",
                QMessageBox.Warning
            )
            return

        dlg = RequestLoanDialog(self)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            uid  = AuthController.current_user.id
            ok, result = LoanRequestController.submit_loan_request(
                uid, data['due_date'], data['notes'], data['details']
            )
            if ok:
                self.show_message(
                    "Pengajuan Terkirim",
                    f"✅  Pengajuan berhasil dikirim!\nKode: <b>{result}</b>\n\n"
                    "Tunggu konfirmasi dari Laboran/Admin."
                )
            else:
                self.show_message("Gagal", str(result), QMessageBox.Warning)

    def _goto_profile(self):
        # Trigger navigasi ke profil via sinyal parent
        mw = self.window()
        if hasattr(mw, '_navigate'):
            mw._navigate("my_profile")


# ═════════════════════════════════════════════════════════════════
# 2. Pengajuan Saya
# ═════════════════════════════════════════════════════════════════

class ReturnRequestDialog(QDialog):
    """Viewer mengajukan pengembalian atas pinjaman aktif miliknya"""

    def __init__(self, parent, loan):
        super().__init__(parent)
        self.loan = loan
        self.setWindowTitle("📬  Ajukan Pengembalian")
        self.setMinimumWidth(440)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("📬  Pengajuan Pengembalian Barang")
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        info = QFrame()
        info.setStyleSheet("QFrame { background: #162032; border-radius: 8px; }")
        il = QVBoxLayout(info)
        il.setContentsMargins(12, 8, 12, 8)
        il.setSpacing(4)
        for lbl, val in [
            ("Kode Pinjam:", self.loan['loan_code']),
            ("Barang:", (self.loan.get('items_list') or '-')[:50]),
            ("Deadline:", utils.format_date(self.loan['due_date'])),
        ]:
            r = QHBoxLayout()
            l = QLabel(lbl); l.setStyleSheet("color: #64748b; font-size: 12px;"); l.setFixedWidth(100)
            v = QLabel(val); v.setStyleSheet("color: #e2e8f0; font-size: 12px;"); v.setWordWrap(True)
            r.addWidget(l); r.addWidget(v, 1)
            il.addLayout(r)
        layout.addWidget(info)

        lbl_n = QLabel("Catatan (opsional):")
        lbl_n.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_n)

        self.inp_notes = QTextEdit()
        self.inp_notes.setPlaceholderText("Kondisi barang saat dikembalikan, dll...")
        self.inp_notes.setMaximumHeight(70)
        layout.addWidget(self.inp_notes)

        btn_row = QHBoxLayout()
        btn_c = QPushButton("Batal"); btn_c.setObjectName("btn_secondary"); btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("📬  Kirim Pengajuan"); btn_ok.setObjectName("btn_primary"); btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_c); btn_row.addStretch(); btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_notes(self):
        return self.inp_notes.toPlainText().strip()


class MyRequestPage(BasePage):
    def __init__(self):
        super().__init__(
            "📬  Pengajuan Saya",
            "Status pengajuan peminjaman dan pengembalian yang Anda kirimkan"
        )
        self._setup_content()

    def _setup_content(self):
        # Filter status
        fr = QHBoxLayout(); fr.setSpacing(8)
        self.filter_status = QComboBox()
        self.filter_status.setMinimumHeight(38)
        self.filter_status.addItems(["Semua Status", "menunggu", "disetujui", "ditolak"])
        self.filter_status.currentIndexChanged.connect(self._load_data)
        fr.addWidget(QLabel("Filter:"))
        fr.addWidget(self.filter_status)
        fr.addStretch()
        self.main_layout.addLayout(fr)

        # Tabel
        self.table = self.make_table(
            ["Kode", "Jenis", "Barang", "Deadline", "Diajukan", "Status", "Catatan Reviewer"],
            stretch_col=2
        )
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 130)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 200)
        self.main_layout.addWidget(self.table)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("label_muted")
        self.main_layout.addWidget(self.lbl_count)

        # Tombol ajukan pengembalian di bagian bawah
        divider = QFrame(); divider.setObjectName("divider"); divider.setFixedHeight(1)
        self.main_layout.addWidget(divider)

        lbl_return = QLabel("Ajukan Pengembalian untuk Pinjaman Aktif:")
        lbl_return.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold;")
        self.main_layout.addWidget(lbl_return)

        self.active_loans_layout = QVBoxLayout()
        self.active_loans_layout.setSpacing(6)
        self.main_layout.addLayout(self.active_loans_layout)

    def refresh(self):
        self._load_data()
        self._load_active_loans()

    def _load_data(self):
        uid = AuthController.current_user.id
        status_map = {
            "Semua Status": None,
            "menunggu": "menunggu",
            "disetujui": "disetujui",
            "ditolak": "ditolak",
        }
        status = status_map.get(self.filter_status.currentText())
        requests = LoanRequestController.get_all(status=status, user_id=uid)

        self.table.setRowCount(len(requests))
        for row, req in enumerate(requests):
            type_label = "📤 Pinjam" if req['request_type'] == 'pinjam' else "📥 Kembali"
            type_color  = "#f59e0b" if req['request_type'] == 'pinjam' else "#38bdf8"
            status_colors = {"menunggu": "#f59e0b", "disetujui": "#22c55e", "ditolak": "#ef4444"}
            status_icons  = {"menunggu": "⏳", "disetujui": "✅", "ditolak": "❌"}

            self.table.setItem(row, 0, self.colored_item(req['request_code'], "#38bdf8"))
            self.table.setItem(row, 1, self.colored_item(type_label, type_color))
            self.table.setItem(row, 2, self.table_item(
                (req.get('items_list') or req.get('loan_code') or "-")[:40]
            ))
            self.table.setItem(row, 3, self.table_item(
                utils.format_date(req.get('due_date') or ""), Qt.AlignCenter
            ))
            self.table.setItem(row, 4, self.table_item(
                (req['created_at'] or "")[:16], Qt.AlignCenter
            ))
            sc = status_colors.get(req['status'], "#e2e8f0")
            si = status_icons.get(req['status'], "")
            self.table.setItem(row, 5, self.colored_item(
                f"{si}  {req['status'].upper()}", sc
            ))
            self.table.setItem(row, 6, self.table_item(
                req.get('review_note') or "-"
            ))

        self.lbl_count.setText(f"Total {len(requests)} pengajuan")

    def _load_active_loans(self):
        # Hapus widget lama
        while self.active_loans_layout.count():
            item = self.active_loans_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        uid = AuthController.current_user.id
        borrower = get_my_borrower()
        if not borrower:
            lbl = QLabel("⚠️  Profil belum dilengkapi. Tidak bisa melihat riwayat pinjaman.")
            lbl.setStyleSheet("color: #f59e0b; font-size: 12px; padding: 4px;")
            self.active_loans_layout.addWidget(lbl)
            return

        active_loans = Loan.get_all(status='dipinjam', borrower_id=borrower['id'])
        if not active_loans:
            lbl = QLabel("✅  Tidak ada pinjaman aktif saat ini.")
            lbl.setStyleSheet("color: #22c55e; font-size: 12px; padding: 4px;")
            self.active_loans_layout.addWidget(lbl)
            return

        for loan in active_loans:
            card = QFrame()
            card.setStyleSheet(
                "QFrame { background: #1e293b; border: 1px solid #334155; border-radius: 8px; }"
            )
            cl = QHBoxLayout(card)
            cl.setContentsMargins(12, 8, 12, 8)

            overdue = utils.is_overdue(loan['due_date'])
            color = "#ef4444" if overdue else "#e2e8f0"
            info_text = (
                f"<b>{loan['loan_code']}</b>  ·  "
                f"{loan.get('items_list') or '-'}  ·  "
                f"Deadline: {utils.format_date(loan['due_date'])}"
            )
            if overdue:
                info_text += "  <b style='color:#ef4444'>⚠️ TERLAMBAT</b>"

            lbl = QLabel(info_text)
            lbl.setStyleSheet(f"color: {color}; font-size: 12px;")
            lbl.setWordWrap(True)
            cl.addWidget(lbl, 1)

            # Cek apakah sudah ada request kembali yang pending
            existing = db.fetchone("""
                SELECT id FROM loan_requests
                WHERE loan_id=? AND request_type='kembali' AND status='menunggu'
            """, (loan['id'],))

            if existing:
                btn = QPushButton("⏳ Sedang Diproses")
                btn.setObjectName("btn_secondary")
                btn.setEnabled(False)
            else:
                btn = QPushButton("↩️  Ajukan Kembali")
                btn.setObjectName("btn_primary" if not overdue else "btn_danger")
                btn.clicked.connect(lambda _, l=loan: self._request_return(l))

            cl.addWidget(btn)
            self.active_loans_layout.addWidget(card)

    def _request_return(self, loan):
        dlg = ReturnRequestDialog(self, loan)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            uid = AuthController.current_user.id
            ok, result = LoanRequestController.submit_return_request(
                uid, loan['id'], dlg.get_notes()
            )
            if ok:
                self.show_message(
                    "Pengajuan Terkirim",
                    f"✅  Pengajuan pengembalian berhasil dikirim!\nKode: <b>{result}</b>\n\n"
                    "Tunggu konfirmasi dari Laboran/Admin."
                )
                self.refresh()
            else:
                self.show_message("Gagal", str(result), QMessageBox.Warning)


# ═════════════════════════════════════════════════════════════════
# 3. Riwayat Pinjam Saya
# ═════════════════════════════════════════════════════════════════

class MyLoansPage(BasePage):
    def __init__(self):
        super().__init__(
            "📋  Riwayat Pinjam Saya",
            "Histori peminjaman barang laboratorium yang pernah Anda lakukan"
        )
        self._setup_content()

    def _setup_content(self):
        self.table = self.make_table(
            ["Kode Pinjam", "Barang", "Tgl Pinjam", "Deadline", "Tgl Kembali", "Status"],
            stretch_col=1
        )
        self.table.setColumnWidth(0, 140)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 110)
        self.main_layout.addWidget(self.table)

        self.lbl_empty = QLabel("")
        self.lbl_empty.setStyleSheet("color: #64748b; font-size: 13px;")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.lbl_empty)

    def refresh(self):
        borrower = get_my_borrower()
        if not borrower:
            self.table.setRowCount(0)
            self.lbl_empty.setText(
                "⚠️  Profil belum dilengkapi.\nBuka 'Profil Saya' untuk mengisi data peminjam."
            )
            return

        loans = Loan.get_all(borrower_id=borrower['id'])
        self.lbl_empty.setText("" if loans else "Belum ada riwayat peminjaman.")
        self.table.setRowCount(len(loans))

        status_colors = {"dipinjam": "#f59e0b", "dikembalikan": "#22c55e", "terlambat": "#ef4444"}
        for row, loan in enumerate(loans):
            self.table.setItem(row, 0, self.colored_item(loan['loan_code'], "#38bdf8"))
            self.table.setItem(row, 1, self.table_item(loan.get('items_list') or "-"))
            self.table.setItem(row, 2, self.table_item(
                utils.format_date(loan['loan_date']), Qt.AlignCenter
            ))
            due_color = "#ef4444" if (
                utils.is_overdue(loan['due_date']) and loan['status'] == 'dipinjam'
            ) else "#e2e8f0"
            due_item = self.table_item(utils.format_date(loan['due_date']), Qt.AlignCenter)
            due_item.setForeground(QColor(due_color))
            self.table.setItem(row, 3, due_item)
            self.table.setItem(row, 4, self.table_item(
                utils.format_date(loan.get('return_date') or ""), Qt.AlignCenter
            ))
            sc = status_colors.get(loan['status'], "#e2e8f0")
            self.table.setItem(row, 5, self.colored_item(loan['status'].upper(), sc))


# ═════════════════════════════════════════════════════════════════
# 4. Profil Saya
# ═════════════════════════════════════════════════════════════════

class MyProfilePage(BasePage):
    def __init__(self):
        super().__init__(
            "👤  Profil Saya",
            "Lengkapi data diri agar pengajuan peminjaman dapat diproses"
        )
        self._setup_content()

    def _setup_content(self):
        # Info akun
        self.acct_card = QFrame()
        self.acct_card.setObjectName("stat_card")
        acct_layout = QHBoxLayout(self.acct_card)
        acct_layout.setContentsMargins(16, 12, 16, 12)

        ic = QLabel("👤")
        ic.setFont(QFont("Segoe UI Emoji", 28))
        ic.setFixedWidth(50)
        acct_layout.addWidget(ic)

        info_col = QVBoxLayout()
        u = AuthController.current_user
        self.lbl_acct_name = QLabel(u.full_name)
        self.lbl_acct_name.setStyleSheet("color: #e2e8f0; font-size: 16px; font-weight: bold;")
        self.lbl_acct_role = QLabel(f"@{u.username}  ·  {u.role.upper()}")
        self.lbl_acct_role.setStyleSheet("color: #38bdf8; font-size: 12px;")
        info_col.addWidget(self.lbl_acct_name)
        info_col.addWidget(self.lbl_acct_role)
        acct_layout.addLayout(info_col)
        acct_layout.addStretch()
        self.main_layout.addWidget(self.acct_card)

        # Status profil
        self.status_banner = QFrame()
        self.status_banner.setStyleSheet(
            "QFrame { background: rgba(245,158,11,0.12); "
            "border: 1px solid #d97706; border-radius: 8px; }"
        )
        sb_l = QHBoxLayout(self.status_banner)
        sb_l.setContentsMargins(12, 8, 12, 8)
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #fbbf24; font-size: 12px;")
        sb_l.addWidget(self.lbl_status)
        self.main_layout.addWidget(self.status_banner)

        # Form profil peminjam
        form_card = QFrame()
        form_card.setObjectName("stat_card")
        form_layout_outer = QVBoxLayout(form_card)
        form_layout_outer.setContentsMargins(20, 16, 20, 16)
        form_layout_outer.setSpacing(10)

        title_lbl = QLabel("📋  Data Profil Peminjam")
        title_lbl.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: bold;")
        form_layout_outer.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_nim  = QLineEdit(); self.inp_nim.setMinimumHeight(38); self.inp_nim.setPlaceholderText("NIM mahasiswa (angka saja)...")
        self.inp_name = QLineEdit(); self.inp_name.setMinimumHeight(38); self.inp_name.setPlaceholderText("Nama lengkap sesuai KTM...")
        self.inp_dept = QLineEdit(); self.inp_dept.setMinimumHeight(38); self.inp_dept.setPlaceholderText("Teknik Elektro, Kimia, dsb...")
        self.inp_phone= QLineEdit(); self.inp_phone.setMinimumHeight(38); self.inp_phone.setPlaceholderText("08xxxxxxxxxx")
        self.inp_email= QLineEdit(); self.inp_email.setMinimumHeight(38); self.inp_email.setPlaceholderText("email@domain.com")

        form.addRow("NIM *",      self.inp_nim)
        form.addRow("Nama *",     self.inp_name)
        form.addRow("Jurusan",    self.inp_dept)
        form.addRow("No HP",      self.inp_phone)
        form.addRow("Email",      self.inp_email)
        form_layout_outer.addLayout(form)

        btn_save = QPushButton("💾  Simpan Profil")
        btn_save.setObjectName("btn_primary")
        btn_save.setMinimumHeight(42)
        btn_save.clicked.connect(self._save_profile)
        form_layout_outer.addWidget(btn_save)

        self.main_layout.addWidget(form_card)
        self.main_layout.addStretch()

    def refresh(self):
        borrower = get_my_borrower()
        if borrower:
            self.status_banner.setStyleSheet(
                "QFrame { background: rgba(34,197,94,0.1); "
                "border: 1px solid #16a34a; border-radius: 8px; }"
            )
            self.lbl_status.setStyleSheet("color: #4ade80; font-size: 12px;")
            self.lbl_status.setText("✅  Profil lengkap! Anda dapat mengajukan peminjaman barang.")
            # Isi form
            self.inp_nim.setText(borrower['nim'])
            self.inp_name.setText(borrower['name'])
            self.inp_dept.setText(borrower.get('department') or "")
            self.inp_phone.setText(borrower.get('phone') or "")
            self.inp_email.setText(borrower.get('email') or "")
        else:
            self.status_banner.setStyleSheet(
                "QFrame { background: rgba(245,158,11,0.12); "
                "border: 1px solid #d97706; border-radius: 8px; }"
            )
            self.lbl_status.setStyleSheet("color: #fbbf24; font-size: 12px;")
            self.lbl_status.setText(
                "⚠️  Profil belum dilengkapi. "
                "Isi data di bawah agar pengajuan peminjaman Anda dapat diproses."
            )

    def _save_profile(self):
        uid = AuthController.current_user.id
        data = {
            'nim':        self.inp_nim.text().strip(),
            'name':       self.inp_name.text().strip(),
            'department': self.inp_dept.text().strip(),
            'phone':      self.inp_phone.text().strip(),
            'email':      self.inp_email.text().strip(),
        }

        existing = get_my_borrower()
        if existing:
            ok, msg = BorrowerController.update(existing['id'], data)
        else:
            ok, msg = BorrowerController.create(data, user_id=uid)

        if ok:
            self.show_message("Berhasil", "✅  Profil peminjam berhasil disimpan!")
            self.refresh()
        else:
            self.show_message("Gagal", msg, QMessageBox.Warning)
