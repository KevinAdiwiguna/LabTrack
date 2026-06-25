"""
report_page.py - Halaman laporan & export data
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QDateEdit, QGroupBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
import os, subprocess, sys

from windows.base_page import BasePage
from controllers import AuthController, ReportController


class ReportPage(BasePage):
    def __init__(self):
        super().__init__("📊  Laporan & Export", "Export data ke CSV atau PDF dengan filter tanggal")
        self._setup_content()

    def _setup_content(self):
        # ── Filter Tanggal ────────────────────────────────────────
        date_group = QGroupBox("Filter Rentang Tanggal")
        date_layout = QHBoxLayout(date_group)
        date_layout.setSpacing(12)

        lbl_from = QLabel("Dari:")
        lbl_from.setStyleSheet("color: #94a3b8;")
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setMinimumHeight(38)
        self.date_from.setMinimumWidth(150)

        lbl_to = QLabel("Sampai:")
        lbl_to.setStyleSheet("color: #94a3b8;")
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setMinimumHeight(38)
        self.date_to.setMinimumWidth(150)

        btn_reset = QPushButton("↺  Reset Filter")
        btn_reset.setObjectName("btn_secondary")
        btn_reset.clicked.connect(self._reset_filter)

        date_layout.addWidget(lbl_from)
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(lbl_to)
        date_layout.addWidget(self.date_to)
        date_layout.addWidget(btn_reset)
        date_layout.addStretch()
        self.main_layout.addWidget(date_group)

        # ── Export Cards ──────────────────────────────────────────
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        # Export Peminjaman CSV
        card1 = self._make_export_card(
            "📄  Export Peminjaman CSV",
            "Export data transaksi peminjaman ke format CSV.\nKompatibel dengan Excel dan Google Sheets.",
            "Export CSV",
            "btn_primary",
            self._export_loans_csv
        )

        # Export Peminjaman PDF
        card2 = self._make_export_card(
            "📃  Export Peminjaman PDF",
            "Export laporan peminjaman ke format PDF.\nSiap cetak dengan format profesional.",
            "Export PDF",
            "btn_danger",
            self._export_loans_pdf
        )

        # Export Inventaris CSV
        card3 = self._make_export_card(
            "📦  Export Inventaris CSV",
            "Export seluruh data barang inventaris\nke format CSV dengan semua detail.",
            "Export Inventaris",
            "btn_success",
            self._export_inventory_csv
        )

        cards_layout.addWidget(card1)
        cards_layout.addWidget(card2)
        cards_layout.addWidget(card3)
        self.main_layout.addLayout(cards_layout)

        # ── Status Label ──────────────────────────────────────────
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #22c55e; font-size: 13px; padding: 8px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.lbl_status)

        # ── Folder shortcut ───────────────────────────────────────
        folder_row = QHBoxLayout()
        btn_open_exports = QPushButton("📂  Buka Folder Exports")
        btn_open_exports.setObjectName("btn_secondary")
        btn_open_exports.clicked.connect(lambda: self._open_folder("exports"))

        btn_open_reports = QPushButton("📂  Buka Folder Reports")
        btn_open_reports.setObjectName("btn_secondary")
        btn_open_reports.clicked.connect(lambda: self._open_folder("reports"))

        folder_row.addStretch()
        folder_row.addWidget(btn_open_exports)
        folder_row.addWidget(btn_open_reports)
        folder_row.addStretch()
        self.main_layout.addLayout(folder_row)

        self.main_layout.addStretch()

    def _make_export_card(self, title, description, btn_text, btn_style, callback):
        card = QFrame()
        card.setObjectName("stat_card")
        card.setMinimumHeight(180)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #e2e8f0;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(description)
        lbl_desc.setStyleSheet("color: #64748b; font-size: 12px;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        layout.addStretch()

        btn = QPushButton(f"⬇  {btn_text}")
        btn.setObjectName(btn_style)
        btn.setMinimumHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        layout.addWidget(btn)

        return card

    def _get_date_range(self):
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to   = self.date_to.date().toString("yyyy-MM-dd")
        return d_from, d_to

    def _reset_filter(self):
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())

    def _export_loans_csv(self):
        try:
            d_from, d_to = self._get_date_range()
            path = ReportController.export_loans_csv(d_from, d_to)
            self.lbl_status.setText(f"✅  Berhasil export: {os.path.abspath(path)}")
            self.show_message("Export Berhasil", f"File disimpan di:\n{os.path.abspath(path)}")
        except Exception as e:
            self.show_message("Export Gagal", str(e), QMessageBox.Critical)

    def _export_loans_pdf(self):
        try:
            d_from, d_to = self._get_date_range()
            path = ReportController.export_loans_pdf(d_from, d_to)
            self.lbl_status.setText(f"✅  Berhasil export PDF: {os.path.abspath(path)}")
            self.show_message("Export Berhasil", f"File PDF disimpan di:\n{os.path.abspath(path)}")
        except Exception as e:
            self.show_message("Export Gagal", str(e), QMessageBox.Critical)

    def _export_inventory_csv(self):
        try:
            path = ReportController.export_inventory_csv()
            self.lbl_status.setText(f"✅  Inventaris berhasil diexport: {os.path.abspath(path)}")
            self.show_message("Export Berhasil", f"File disimpan di:\n{os.path.abspath(path)}")
        except Exception as e:
            self.show_message("Export Gagal", str(e), QMessageBox.Critical)

    def _open_folder(self, folder):
        path = os.path.abspath(folder)
        os.makedirs(path, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def refresh(self):
        pass
