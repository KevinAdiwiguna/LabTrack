
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models import Item, Loan, ActivityLog
import database as db
from controllers import AuthController
from datetime import datetime


DARK_COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "text": "#e2e8f0",
    "muted": "#64748b",
    "accent": "#38bdf8",
    "green": "#22c55e",
    "red": "#ef4444",
    "yellow": "#f59e0b",
    "grid": "#334155",
}


class StatCard(QFrame):
    def __init__(self, icon, value, label, color="#38bdf8"):
        super().__init__()
        self.setObjectName("stat_card")
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Icon
        ic = QLabel(icon)
        ic.setObjectName("card_icon")
        ic.setFont(QFont("Segoe UI Emoji", 28))
        ic.setFixedWidth(50)
        layout.addWidget(ic)

        # Text
        text_col = QVBoxLayout()
        val_lbl = QLabel(str(value))
        val_lbl.setObjectName("card_value")
        val_lbl.setFont(QFont("Segoe UI", 28, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {color};")
        text_col.addWidget(val_lbl)

        lbl = QLabel(label)
        lbl.setObjectName("card_label")
        text_col.addWidget(lbl)

        layout.addLayout(text_col)
        layout.addStretch()

        self.val_lbl = val_lbl

    def set_value(self, v):
        self.val_lbl.setText(str(v))


class ChartWidget(QFrame):
    """Wrapper untuk matplotlib chart"""
    def __init__(self, title=""):
        super().__init__()
        self.setObjectName("stat_card")
        self.setMinimumHeight(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        if title:
            t = QLabel(title)
            t.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold;")
            layout.addWidget(t)

        self.fig = Figure(figsize=(5, 3.2), dpi=90, facecolor="#1e293b")
        self.ax = self.fig.add_subplot(111, facecolor="#1e293b")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background: transparent;")
        layout.addWidget(self.canvas)

    def get_ax(self):
        self.ax.clear()
        self.ax.set_facecolor("#162032")
        self.ax.tick_params(colors=DARK_COLORS["muted"], labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(DARK_COLORS["grid"])
        self.ax.grid(True, color=DARK_COLORS["grid"], linestyle="--", alpha=0.5)
        return self.ax

    def refresh(self):
        self.canvas.draw()


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("content_area")
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # ── Header ──────────────────────────────────────────────
        now = datetime.now()
        hdr = QHBoxLayout()
        left = QVBoxLayout()
        t = QLabel("🏠  Dashboard")
        t.setObjectName("page_title")
        left.addWidget(t)
        s = QLabel(f"Selamat datang! · {now.strftime('%A, %d %B %Y  %H:%M')}")
        s.setObjectName("page_subtitle")
        left.addWidget(s)
        hdr.addLayout(left)
        hdr.addStretch()
        layout.addLayout(hdr)

        div = QFrame(); div.setObjectName("divider"); div.setFixedHeight(1)
        layout.addWidget(div)

        # ── Stat Cards ───────────────────────────────────────────
        card_row = QHBoxLayout()
        card_row.setSpacing(12)

        self.card_total    = StatCard("📦", 0, "Total Barang",       "#38bdf8")
        self.card_borrowed = StatCard("📤", 0, "Sedang Dipinjam",    "#f59e0b")
        self.card_avail    = StatCard("✅", 0, "Tersedia",           "#22c55e")
        self.card_trans    = StatCard("📋", 0, "Total Transaksi",    "#a78bfa")

        for card in (self.card_total, self.card_borrowed, self.card_avail, self.card_trans):
            card_row.addWidget(card)
        layout.addLayout(card_row)

        # ── Charts Row ───────────────────────────────────────────
        charts_row = QHBoxLayout()
        charts_row.setSpacing(12)

        self.chart_monthly = ChartWidget("📈  Peminjaman Per Bulan")
        self.chart_top     = ChartWidget("🏆  Barang Paling Sering Dipinjam")
        charts_row.addWidget(self.chart_monthly, 3)
        charts_row.addWidget(self.chart_top, 2)
        layout.addLayout(charts_row)

        # ── Recent Activity (admin only) ─────────────────────────
        self.activity_container = None
        role = AuthController.current_user.role if AuthController.current_user else ''
        if role == 'admin':
            act_frame = QFrame()
            act_frame.setObjectName("stat_card")
            act_layout = QVBoxLayout(act_frame)
            act_layout.setContentsMargins(16, 12, 16, 12)

            act_title = QLabel("⚡  Aktivitas Terbaru")
            act_title.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold;")
            act_layout.addWidget(act_title)

            self.activity_container = QVBoxLayout()
            self.activity_container.setSpacing(4)
            act_layout.addLayout(self.activity_container)
            layout.addWidget(act_frame)

        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def refresh(self):
        self._update_stats()
        self._update_monthly_chart()
        self._update_top_items_chart()
        self._update_activity()

    def _update_stats(self):
        total   = db.fetchone("SELECT COUNT(*) as c FROM items")['c']
        on_loan = db.fetchone("""
            SELECT COALESCE(SUM(ld.quantity),0) as c FROM loan_details ld
            JOIN loans l ON ld.loan_id=l.id WHERE l.status='dipinjam'
        """)['c']
        trans   = db.fetchone("SELECT COUNT(*) as c FROM loans")['c']

        self.card_total.set_value(total)
        self.card_borrowed.set_value(on_loan)
        self.card_avail.set_value(total - (1 if on_loan > 0 else 0))
        self.card_trans.set_value(trans)

    def _update_monthly_chart(self):
        rows = db.fetchall("""
            SELECT strftime('%b %Y', loan_date) as month,
                   strftime('%Y-%m', loan_date) as sort_key,
                   COUNT(*) as total
            FROM loans GROUP BY sort_key ORDER BY sort_key DESC LIMIT 8
        """)
        rows = list(reversed(rows))

        ax = self.chart_monthly.get_ax()
        if not rows:
            ax.text(0.5, 0.5, "Belum ada data", ha='center', color=DARK_COLORS["muted"],
                    transform=ax.transAxes, fontsize=11)
        else:
            months = [r['month'] for r in rows]
            totals = [r['total'] for r in rows]
            x_pos  = list(range(len(months)))
            bars = ax.bar(x_pos, totals, color=DARK_COLORS["accent"], alpha=0.85, width=0.6)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(months, rotation=30, ha='right', fontsize=7)
            ax.set_ylabel("Jumlah", color=DARK_COLORS["muted"], fontsize=8)
            for bar, val in zip(bars, totals):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        str(val), ha='center', va='bottom',
                        color=DARK_COLORS["text"], fontsize=8, fontweight='bold')
        self.chart_monthly.fig.tight_layout(pad=0.5)
        self.chart_monthly.refresh()

    def _update_top_items_chart(self):
        rows = db.fetchall("""
            SELECT i.name, SUM(ld.quantity) as total
            FROM loan_details ld
            JOIN items i ON ld.item_id=i.id
            JOIN loans l ON ld.loan_id=l.id
            GROUP BY i.id ORDER BY total DESC LIMIT 6
        """)

        ax = self.chart_top.get_ax()
        if not rows:
            ax.text(0.5, 0.5, "Belum ada data", ha='center', color=DARK_COLORS["muted"],
                    transform=ax.transAxes, fontsize=11)
        else:
            names = [r['name'][:15] for r in rows]
            totals = [r['total'] for r in rows]
            colors = ["#38bdf8","#0ea5e9","#0284c7","#0369a1","#1d4ed8","#2563eb"][:len(rows)]
            wedges, texts, autotexts = ax.pie(
                totals, labels=None, autopct='%1.0f%%',
                colors=colors, startangle=90,
                pctdistance=0.75,
                wedgeprops=dict(width=0.55)
            )
            for at in autotexts:
                at.set_color(DARK_COLORS["text"])
                at.set_fontsize(8)
            ax.legend(names, loc='lower center', bbox_to_anchor=(0.5, -0.15),
                      ncol=2, fontsize=7, frameon=False,
                      labelcolor=DARK_COLORS["muted"])
        self.chart_top.fig.tight_layout(pad=0.3)
        self.chart_top.refresh()

    def _update_activity(self):
        if self.activity_container is None:
            return
        # Clear existing
        while self.activity_container.count():
            item = self.activity_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        logs = ActivityLog.get_recent(8)
        icons = {
            "LOGIN": "🔐", "LOGOUT": "🚪",
            "TAMBAH_BARANG": "➕", "EDIT_BARANG": "✏️", "HAPUS_BARANG": "🗑️",
            "PEMINJAMAN": "📤", "PENGEMBALIAN": "📥",
            "EXPORT_CSV": "📄", "EXPORT_PDF": "📃",
        }

        for log in logs:
            row = QFrame()
            row.setStyleSheet("""
                QFrame { background: #162032; border-radius: 6px; padding: 6px; }
                QFrame:hover { background: #1a2a42; }
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 4, 8, 4)

            icon = icons.get(log['action'], "📌")
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 13))
            icon_lbl.setFixedWidth(24)
            row_layout.addWidget(icon_lbl)

            desc = QLabel(f"<b>{log['username']}</b> · {log['description'] or log['action']}")
            desc.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            row_layout.addWidget(desc, 1)

            ts = QLabel(log['timestamp'][:16])
            ts.setStyleSheet("color: #475569; font-size: 11px;")
            row_layout.addWidget(ts)

            self.activity_container.addWidget(row)

        if not logs:
            empty = QLabel("Belum ada aktivitas")
            empty.setStyleSheet("color: #475569; font-size: 12px; padding: 8px;")
            self.activity_container.addWidget(empty)
