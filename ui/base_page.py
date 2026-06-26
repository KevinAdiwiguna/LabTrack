"""
base_page.py - Widget dasar untuk semua halaman
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QSizePolicy, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor


class BasePage(QWidget):
    """Widget dasar dengan header dan layout standar"""

    def __init__(self, title: str, subtitle: str = ""):
        super().__init__()
        self.setObjectName("content_area")

        # Layout utama
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_col = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setObjectName("page_title")
        title_col.addWidget(lbl_title)
        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setObjectName("page_subtitle")
            title_col.addWidget(lbl_sub)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        # Placeholder untuk tombol header (diisi subclass)
        self.header_buttons = QHBoxLayout()
        self.header_buttons.setSpacing(8)
        header_layout.addLayout(self.header_buttons)

        self.main_layout.addWidget(header)

        # Divider
        div = QFrame()
        div.setObjectName("divider")
        div.setFixedHeight(1)
        self.main_layout.addWidget(div)

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.exec()

    def confirm(self, title, message) -> bool:
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def make_table(self, headers: list, stretch_col: int = 1) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(stretch_col, QHeaderView.Stretch)
        table.setShowGrid(False)
        table.verticalHeader().setDefaultSectionSize(40)
        return table

    def table_item(self, text: str, align=Qt.AlignVCenter | Qt.AlignLeft) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text) if text is not None else "")
        item.setTextAlignment(align)
        return item

    def colored_item(self, text: str, color: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor(color))
        item.setTextAlignment(Qt.AlignCenter)
        return item
