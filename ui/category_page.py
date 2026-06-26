"""
category_page.py - Halaman manajemen kategori barang
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QDialog, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt

from ui.base_page import BasePage
from controllers import AuthController, CategoryController


class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("Edit Kategori" if category else "Tambah Kategori")
        self.setMinimumWidth(380)
        self._setup_ui()
        if category:
            self.inp_name.setText(category['name'])
            self.inp_desc.setPlainText(category['description'] or "")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("🏷️  Tambah Kategori" if not self.category else "✏️  Edit Kategori")
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nama kategori...")
        self.inp_name.setMinimumHeight(38)

        self.inp_desc = QTextEdit()
        self.inp_desc.setPlaceholderText("Deskripsi kategori...")
        self.inp_desc.setMaximumHeight(80)

        form.addRow("Nama *", self.inp_name)
        form.addRow("Deskripsi", self.inp_desc)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("💾  Simpan")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def get_data(self):
        return self.inp_name.text().strip(), self.inp_desc.toPlainText().strip()


class CategoryPage(BasePage):
    def __init__(self):
        super().__init__("🏷️  Kategori Barang", "Kelola kategori inventaris laboratorium")
        self._setup_content()

    def _setup_content(self):
        if AuthController.can_edit():
            btn_add = QPushButton("➕  Tambah Kategori")
            btn_add.setObjectName("btn_primary")
            btn_add.setMinimumHeight(36)
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.clicked.connect(self._add_cat)
            self.header_buttons.addWidget(btn_add)

        self.table = self.make_table(["ID", "Nama Kategori", "Deskripsi", "Aksi"], stretch_col=1)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(3, 130)
        self.main_layout.addWidget(self.table)

    def refresh(self):
        self._load_data()

    def _load_data(self):
        cats = CategoryController.get_all()
        self.table.setRowCount(len(cats))
        for row, cat in enumerate(cats):
            self.table.setItem(row, 0, self.colored_item(cat['id'], "#94a3b8"))
            self.table.setItem(row, 1, self.table_item(cat['name']))
            self.table.setItem(row, 2, self.table_item(cat.get('description') or "-"))

            if AuthController.can_edit():
                btn_w = QWidget()
                bl = QHBoxLayout(btn_w)
                bl.setContentsMargins(4, 2, 4, 2)
                bl.setSpacing(4)

                btn_edit = QPushButton("✏️")
                btn_edit.setObjectName("btn_icon")
                btn_edit.clicked.connect(lambda _, c=cat: self._edit_cat(c))

                btn_del = QPushButton("🗑️")
                btn_del.setObjectName("btn_icon")
                btn_del.clicked.connect(lambda _, c=cat: self._delete_cat(c))

                bl.addWidget(btn_edit)
                bl.addWidget(btn_del)
                self.table.setCellWidget(row, 3, btn_w)

    def _add_cat(self):
        dlg = CategoryDialog(self)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            name, desc = dlg.get_data()
            ok, msg = CategoryController.create(name, desc)
            if ok:
                self.show_message("Berhasil", "Kategori berhasil ditambahkan!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _edit_cat(self, cat):
        dlg = CategoryDialog(self, cat)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            name, desc = dlg.get_data()
            ok, msg = CategoryController.update(cat['id'], name, desc)
            if ok:
                self.show_message("Berhasil", "Kategori berhasil diupdate!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _delete_cat(self, cat):
        if self.confirm("Hapus Kategori", f"Hapus kategori '{cat['name']}'?"):
            CategoryController.delete(cat['id'], cat['name'])
            self._load_data()
