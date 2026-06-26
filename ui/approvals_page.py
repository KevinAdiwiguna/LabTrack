"""
approvals_page.py - Halaman konfirmasi pengajuan peminjaman/pengembalian dari viewer
Hanya bisa diakses oleh admin dan laboran
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QDialog, QTextEdit, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from ui.base_page import BasePage
from controllers import AuthController, LoanRequestController
from models.models import LoanRequest
import utils.utils as utils


class ReviewDialog(QDialog):
    """Dialog untuk menyetujui atau menolak pengajuan"""

    def __init__(self, parent, request, action):
        super().__init__(parent)
        self.request = request
        self.action  = action  # 'approve' atau 'reject'
        title = "✅  Setujui Pengajuan" if action == 'approve' else "❌  Tolak Pengajuan"
        self.setWindowTitle(title)
        self.setMinimumWidth(480)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Judul
        title_color = "#22c55e" if self.action == 'approve' else "#ef4444"
        icon = "✅" if self.action == 'approve' else "❌"
        title = QLabel(f"{icon}  {'Setujui' if self.action == 'approve' else 'Tolak'} Pengajuan")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {title_color};")
        layout.addWidget(title)

        # Info pengajuan
        info = QFrame()
        info.setStyleSheet("QFrame { background: #162032; border-radius: 8px; padding: 4px; }")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.setSpacing(4)

        req_type_label = "Peminjaman" if self.request['request_type'] == 'pinjam' else "Pengembalian"
        fields = [
            ("Kode Request:",   self.request['request_code']),
            ("Pengaju:",        self.request['requester_name']),
            ("Jenis:",          req_type_label),
            ("Barang:",         (self.request.get('items_list') or '-')[:60]),
            ("Diajukan:",       self.request['created_at'][:16]),
        ]
        if self.request.get('due_date'):
            fields.append(("Deadline:", self.request['due_date']))

        for lbl, val in fields:
            row = QHBoxLayout()
            l = QLabel(lbl); l.setStyleSheet("color: #64748b; font-size: 12px;"); l.setFixedWidth(110)
            v = QLabel(val); v.setStyleSheet("color: #e2e8f0; font-size: 12px; font-weight: bold;")
            v.setWordWrap(True)
            row.addWidget(l); row.addWidget(v, 1)
            info_layout.addLayout(row)
        layout.addWidget(info)

        # Catatan
        lbl_note = QLabel(
            "Catatan (wajib diisi jika menolak):" if self.action == 'reject'
            else "Catatan tambahan (opsional):"
        )
        lbl_note.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_note)

        self.inp_note = QTextEdit()
        self.inp_note.setPlaceholderText(
            "Masukkan alasan penolakan..." if self.action == 'reject'
            else "Catatan untuk pengaju (opsional)..."
        )
        self.inp_note.setMaximumHeight(80)
        layout.addWidget(self.inp_note)

        # Tombol
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        if self.action == 'approve':
            btn_ok = QPushButton("✅  Ya, Setujui")
            btn_ok.setObjectName("btn_success")
        else:
            btn_ok = QPushButton("❌  Ya, Tolak")
            btn_ok.setObjectName("btn_danger")

        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_note(self):
        return self.inp_note.toPlainText().strip()


class ApprovalsPage(BasePage):
    def __init__(self):
        super().__init__(
            "✅  Konfirmasi Request",
            "Setujui atau tolak pengajuan peminjaman/pengembalian dari pengunjung"
        )
        self._setup_content()

    def _setup_content(self):
        # Filter bar
        fr = QHBoxLayout()
        fr.setSpacing(8)

        self.filter_type = QComboBox()
        self.filter_type.setMinimumHeight(38)
        self.filter_type.setMinimumWidth(150)
        self.filter_type.addItems(["Semua Jenis", "pinjam", "kembali"])
        self.filter_type.currentIndexChanged.connect(self._load_data)

        self.filter_status = QComboBox()
        self.filter_status.setMinimumHeight(38)
        self.filter_status.setMinimumWidth(150)
        self.filter_status.addItems(["Menunggu", "Semua Status", "disetujui", "ditolak"])
        self.filter_status.currentIndexChanged.connect(self._load_data)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari nama pengaju / kode request...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(lambda: self._timer.start(300))

        fr.addWidget(QLabel("Jenis:"))
        fr.addWidget(self.filter_type)
        fr.addWidget(QLabel("Status:"))
        fr.addWidget(self.filter_status)
        fr.addWidget(self.search_input, 1)
        self.main_layout.addLayout(fr)

        # Tabel
        self.table = self.make_table(
            ["Kode", "Pengaju", "Jenis", "Barang", "Deadline", "Diajukan", "Status", "Aksi"],
            stretch_col=3
        )
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(4, 95)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 180)
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
        status_map = {
            "Menunggu": "menunggu",
            "Semua Status": None,
            "disetujui": "disetujui",
            "ditolak": "ditolak",
        }
        status = status_map.get(self.filter_status.currentText())
        requests = LoanRequestController.get_all(status=status)

        # Filter jenis
        jenis = self.filter_type.currentText()
        if jenis != "Semua Jenis":
            requests = [r for r in requests if r['request_type'] == jenis]

        # Filter search
        search = self.search_input.text().strip().lower()
        if search:
            requests = [r for r in requests if
                        search in (r.get('requester_name') or '').lower() or
                        search in (r.get('request_code') or '').lower()]

        self.table.setRowCount(len(requests))
        for row, req in enumerate(requests):
            type_label = "📤 Pinjam" if req['request_type'] == 'pinjam' else "📥 Kembali"
            type_color = "#f59e0b" if req['request_type'] == 'pinjam' else "#38bdf8"

            status_colors = {
                "menunggu":  "#f59e0b",
                "disetujui": "#22c55e",
                "ditolak":   "#ef4444",
            }
            status_icons = {
                "menunggu":  "⏳ Menunggu",
                "disetujui": "✅ Disetujui",
                "ditolak":   "❌ Ditolak",
            }

            self.table.setItem(row, 0, self.colored_item(req['request_code'], "#38bdf8"))
            self.table.setItem(row, 1, self.table_item(req.get('requester_name') or "-"))
            self.table.setItem(row, 2, self.colored_item(type_label, type_color))
            self.table.setItem(row, 3, self.table_item(
                (req.get('items_list') or req.get('loan_code') or "-")[:40]
            ))
            self.table.setItem(row, 4, self.table_item(
                utils.format_date(req.get('due_date') or ""), Qt.AlignCenter
            ))
            self.table.setItem(row, 5, self.table_item(
                (req['created_at'] or "")[:16], Qt.AlignCenter
            ))
            self.table.setItem(row, 6, self.colored_item(
                status_icons.get(req['status'], req['status']),
                status_colors.get(req['status'], "#e2e8f0")
            ))

            # Tombol aksi
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            btn_l.setSpacing(4)

            if req['status'] == 'menunggu':
                btn_approve = QPushButton("✅ Setujui")
                btn_approve.setObjectName("btn_success")
                btn_approve.clicked.connect(lambda _, r=req: self._approve(r))

                btn_reject = QPushButton("❌ Tolak")
                btn_reject.setObjectName("btn_danger")
                btn_reject.clicked.connect(lambda _, r=req: self._reject(r))

                btn_l.addWidget(btn_approve)
                btn_l.addWidget(btn_reject)
            else:
                # Tampilkan reviewer
                reviewer = req.get('reviewer_name') or "-"
                info_lbl = QLabel(f"👤 {reviewer}")
                info_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
                btn_l.addWidget(info_lbl)

            self.table.setCellWidget(row, 7, btn_w)

        self.lbl_count.setText(f"Menampilkan {len(requests)} pengajuan")

    def _approve(self, req):
        dlg = ReviewDialog(self, req, 'approve')
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            note = dlg.get_note()
            ok, msg = LoanRequestController.approve(req['id'], note)
            if ok:
                self.show_message("Berhasil", "✅  Pengajuan berhasil disetujui dan diproses!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _reject(self, req):
        dlg = ReviewDialog(self, req, 'reject')
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            note = dlg.get_note()
            ok, msg = LoanRequestController.reject(req['id'], note)
            if ok:
                self.show_message("Info", "❌  Pengajuan telah ditolak.")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)
