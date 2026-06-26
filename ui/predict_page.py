"""
predict_page.py - Halaman prediksi kebutuhan barang menggunakan ML
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.base_page import BasePage
import utils.utils as utils


class PredictWorker(QThread):
    """Background thread untuk menjalankan prediksi ML agar UI tidak freeze"""
    finished = Signal(dict)
    error    = Signal(str)

    def run(self):
        try:
            result = utils.predict_next_month_demand()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class PredictPage(BasePage):
    def __init__(self):
        super().__init__(
            "🤖  Prediksi Kebutuhan Barang",
            "Linear Regression untuk memprediksi peminjaman bulan depan"
        )
        self._setup_content()
        self.worker = None

    def _setup_content(self):
        # Header action
        btn_predict = QPushButton("▶  Jalankan Prediksi")
        btn_predict.setObjectName("btn_primary")
        btn_predict.setMinimumHeight(38)
        btn_predict.setCursor(Qt.PointingHandCursor)
        btn_predict.clicked.connect(self._run_prediction)
        self.header_buttons.addWidget(btn_predict)

        # Info card
        info = QFrame()
        info.setObjectName("stat_card")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(16, 12, 16, 12)

        info_title = QLabel("ℹ️  Cara Kerja Prediksi")
        info_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 13px; background: transparent;")
        info_layout.addWidget(info_title)

        info_desc = QLabel(
            "Sistem menggunakan algoritma <b>Linear Regression (Scikit-Learn)</b> untuk menganalisis "
            "histori peminjaman setiap barang per bulan, kemudian memprediksi jumlah peminjaman "
            "yang kemungkinan terjadi pada bulan berikutnya. "
            "Prediksi lebih akurat jika data histori lebih banyak."
        )
        info_desc.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
        info_desc.setWordWrap(True)
        info_layout.addWidget(info_desc)
        self.main_layout.addWidget(info)

        # Status
        self.lbl_status = QLabel("Klik 'Jalankan Prediksi' untuk melihat hasil analisis ML.")
        self.lbl_status.setStyleSheet("color: #64748b; font-size: 12px; padding: 4px 0;")
        self.main_layout.addWidget(self.lbl_status)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.hide()
        self.progress.setMaximumHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar { border: none; border-radius: 3px; background: #1e293b; }
            QProgressBar::chunk { background: #38bdf8; border-radius: 3px; }
        """)
        self.main_layout.addWidget(self.progress)

        # Chart
        self.chart_frame = QFrame()
        self.chart_frame.setObjectName("stat_card")
        self.chart_frame.setMinimumHeight(300)
        chart_layout = QVBoxLayout(self.chart_frame)
        chart_layout.setContentsMargins(12, 12, 12, 12)

        self.fig = Figure(figsize=(8, 3.5), dpi=90, facecolor="#1e293b")
        self.ax  = self.fig.add_subplot(111, facecolor="#162032")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background: transparent;")
        chart_layout.addWidget(self.canvas)
        self.main_layout.addWidget(self.chart_frame)

        # Result cards area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(220)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.result_container = QWidget()
        self.result_container.setStyleSheet("background: transparent;")
        self.result_layout = QHBoxLayout(self.result_container)
        self.result_layout.setSpacing(10)
        self.result_layout.setAlignment(Qt.AlignLeft)
        scroll.setWidget(self.result_container)
        self.main_layout.addWidget(scroll)

    def refresh(self):
        pass  # Tidak auto-refresh karena komputasi berat

    def _run_prediction(self):
        self.lbl_status.setText("⏳  Menjalankan analisis Machine Learning...")
        self.progress.show()

        # Clear previous results
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.ax.clear()
        self.canvas.draw()

        # Jalankan di thread terpisah
        self.worker = PredictWorker()
        self.worker.finished.connect(self._on_predict_done)
        self.worker.error.connect(self._on_predict_error)
        self.worker.start()

    def _on_predict_done(self, predictions: dict):
        self.progress.hide()

        if not predictions:
            self.lbl_status.setText("⚠️  Data histori peminjaman belum cukup untuk prediksi yang akurat.")
            return

        self.lbl_status.setText(
            f"✅  Prediksi selesai! Ditemukan {len(predictions)} barang dengan proyeksi peminjaman bulan depan."
        )

        # Update chart
        self._draw_chart(predictions)

        # Result cards
        colors = ["#38bdf8","#0ea5e9","#22c55e","#f59e0b","#a78bfa","#f472b6","#34d399","#fb923c"]
        for idx, (name, count) in enumerate(predictions.items()):
            card = QFrame()
            card.setObjectName("stat_card")
            card.setFixedWidth(170)
            card.setFixedHeight(110)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 12, 12, 12)
            cl.setSpacing(4)

            color = colors[idx % len(colors)]
            val_lbl = QLabel(str(count))
            val_lbl.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
            cl.addWidget(val_lbl)

            name_lbl = QLabel(name[:20])
            name_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
            name_lbl.setWordWrap(True)
            cl.addWidget(name_lbl)

            unit_lbl = QLabel("prediksi pinjaman")
            unit_lbl.setStyleSheet("color: #475569; font-size: 10px;")
            cl.addWidget(unit_lbl)

            self.result_layout.addWidget(card)

    def _on_predict_error(self, error: str):
        self.progress.hide()
        self.lbl_status.setText(f"❌  Error: {error}")

    def _draw_chart(self, predictions: dict):
        self.ax.clear()
        self.ax.set_facecolor("#162032")
        self.fig.set_facecolor("#1e293b")

        names  = [n[:18] for n in predictions.keys()]
        values = list(predictions.values())

        colors = ["#38bdf8","#0ea5e9","#22c55e","#f59e0b","#a78bfa",
                  "#f472b6","#34d399","#fb923c","#60a5fa","#4ade80"]

        bars = self.ax.barh(names, values, color=colors[:len(names)], height=0.55, alpha=0.9)
        self.ax.set_xlabel("Prediksi Jumlah Peminjaman", color="#64748b", fontsize=9)
        self.ax.tick_params(colors="#94a3b8", labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color("#334155")
        self.ax.grid(True, axis='x', color="#334155", linestyle="--", alpha=0.5)

        # Label nilai
        for bar, val in zip(bars, values):
            self.ax.text(
                bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"  {val}", va='center', color="#e2e8f0", fontsize=9, fontweight='bold'
            )

        self.ax.set_title("Prediksi Kebutuhan Peminjaman Bulan Depan",
                          color="#94a3b8", fontsize=11, pad=10)
        self.ax.invert_yaxis()
        self.fig.tight_layout(pad=0.8)
        self.canvas.draw()
