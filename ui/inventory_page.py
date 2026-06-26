"""
inventory_page.py - Halaman manajemen inventaris barang
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QDialog, QFormLayout,
    QSpinBox, QTextEdit, QFileDialog, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

from ui.base_page import BasePage
from controllers import AuthController, ItemController, CategoryController


class ItemDialog(QDialog):
    """Dialog untuk tambah/edit barang"""

    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item
        self.photo_path = item['photo_path'] if item else ""
        self.setWindowTitle("Edit Barang" if item else "Tambah Barang")
        self.setMinimumWidth(480)
        self.setMinimumHeight(560)
        self._setup_ui()
        if item:
            self._populate(item)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("✏️ Edit Barang" if self.item else "➕ Tambah Barang Baru")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nama barang...")
        self.inp_name.setMinimumHeight(38)

        self.inp_category = QComboBox()
        self.inp_category.setMinimumHeight(38)
        cats = CategoryController.get_all()
        self.inp_category.addItem("-- Pilih Kategori --", None)
        for c in cats:
            self.inp_category.addItem(c['name'], c['id'])

        self.inp_stock = QSpinBox()
        self.inp_stock.setRange(0, 99999)
        self.inp_stock.setMinimumHeight(38)

        self.inp_condition = QComboBox()
        self.inp_condition.setMinimumHeight(38)
        self.inp_condition.addItems(["Baik", "Rusak Ringan", "Rusak Berat"])

        self.inp_location = QLineEdit()
        self.inp_location.setPlaceholderText("Rak A1, Lemari B2...")
        self.inp_location.setMinimumHeight(38)

        self.inp_description = QTextEdit()
        self.inp_description.setPlaceholderText("Deskripsi barang...")
        self.inp_description.setMaximumHeight(80)

        # Foto
        photo_row = QHBoxLayout()
        self.lbl_photo = QLabel("Belum ada foto")
        self.lbl_photo.setStyleSheet("color: #64748b; font-size: 11px;")
        btn_photo = QPushButton("📷 Pilih Foto")
        btn_photo.setObjectName("btn_secondary")
        btn_photo.clicked.connect(self._pick_photo)
        photo_row.addWidget(self.lbl_photo)
        photo_row.addStretch()
        photo_row.addWidget(btn_photo)

        form.addRow("Nama Barang *", self.inp_name)
        form.addRow("Kategori", self.inp_category)
        form.addRow("Stok *", self.inp_stock)
        form.addRow("Kondisi", self.inp_condition)
        form.addRow("Lokasi", self.inp_location)
        form.addRow("Deskripsi", self.inp_description)
        form.addRow("Foto", photo_row)
        layout.addLayout(form)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("💾  Simpan")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

    def _populate(self, item):
        self.inp_name.setText(item['name'])
        idx = self.inp_category.findData(item['category_id'])
        if idx >= 0:
            self.inp_category.setCurrentIndex(idx)
        self.inp_stock.setValue(item['stock'])
        cond_idx = self.inp_condition.findText(item['condition'])
        if cond_idx >= 0:
            self.inp_condition.setCurrentIndex(cond_idx)
        self.inp_location.setText(item['location'] or "")
        self.inp_description.setPlainText(item['description'] or "")
        if item.get('photo_path'):
            self.lbl_photo.setText(item['photo_path'].split("/")[-1])

    def _pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Foto", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.photo_path = path
            self.lbl_photo.setText(path.split("/")[-1])

    def _save(self):
        self.accept()

    def get_data(self) -> dict:
        return {
            'name':        self.inp_name.text().strip(),
            'category_id': self.inp_category.currentData(),
            'stock':       self.inp_stock.value(),
            'condition':   self.inp_condition.currentText(),
            'location':    self.inp_location.text().strip(),
            'description': self.inp_description.toPlainText().strip(),
            'photo_path':  self.photo_path,
        }


class InventoryPage(BasePage):
    def __init__(self):
        super().__init__("📦  Inventaris Barang", "Kelola semua barang laboratorium")
        self._setup_content()

    def _setup_content(self):
        # Tombol header
        if AuthController.can_edit():
            btn_add = QPushButton("➕  Tambah Barang")
            btn_add.setObjectName("btn_primary")
            btn_add.setMinimumHeight(36)
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.clicked.connect(self._add_item)
            self.header_buttons.addWidget(btn_add)

        # Filter bar
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari nama / kode / lokasi...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self._on_search_changed)

        self.filter_category = QComboBox()
        self.filter_category.setMinimumHeight(38)
        self.filter_category.setMinimumWidth(160)
        self.filter_category.addItem("Semua Kategori", None)
        self.filter_category.currentIndexChanged.connect(self._load_data)

        filter_row.addWidget(self.search_input, 2)
        filter_row.addWidget(self.filter_category, 1)
        self.main_layout.addLayout(filter_row)

        # Table
        self.table = self.make_table(
            ["Kode", "Nama Barang", "Kategori", "Stok", "Kondisi", "Lokasi", "Aksi"],
            stretch_col=1
        )
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(3, 65)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 130)
        self.main_layout.addWidget(self.table)

        # Count label
        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("label_muted")
        self.main_layout.addWidget(self.lbl_count)

        # Timer untuk debounce search
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load_data)

    def refresh(self):
        # Refresh kategori filter
        self.filter_category.clear()
        self.filter_category.addItem("Semua Kategori", None)
        for cat in CategoryController.get_all():
            self.filter_category.addItem(cat['name'], cat['id'])
        self._load_data()

    def _on_search_changed(self):
        self._search_timer.start(300)

    def _load_data(self):
        search = self.search_input.text().strip()
        cat_id = self.filter_category.currentData()
        items  = ItemController.get_all(search, cat_id)

        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, self.table_item(item['item_code'], Qt.AlignCenter))
            self.table.setItem(row, 1, self.table_item(item['name']))
            self.table.setItem(row, 2, self.table_item(item.get('category_name') or "-", Qt.AlignCenter))
            self.table.setItem(row, 3, self.colored_item(
                item['stock'],
                "#22c55e" if item['stock'] > 3 else "#f59e0b" if item['stock'] > 0 else "#ef4444"
            ))
            cond_color = {"Baik": "#22c55e", "Rusak Ringan": "#f59e0b", "Rusak Berat": "#ef4444"}
            self.table.setItem(row, 4, self.colored_item(item['condition'], cond_color.get(item['condition'], "#e2e8f0")))
            self.table.setItem(row, 5, self.table_item(item['location'] or "-", Qt.AlignCenter))

            # Tombol aksi
            if AuthController.can_edit():
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(4, 2, 4, 2)
                btn_layout.setSpacing(4)

                btn_edit = QPushButton("✏️")
                btn_edit.setObjectName("btn_icon")
                btn_edit.setToolTip("Edit")
                btn_edit.clicked.connect(lambda _, i=item: self._edit_item(i))

                btn_del = QPushButton("🗑️")
                btn_del.setObjectName("btn_icon")
                btn_del.setToolTip("Hapus")
                btn_del.clicked.connect(lambda _, i=item: self._delete_item(i))

                btn_layout.addWidget(btn_edit)
                btn_layout.addWidget(btn_del)
                self.table.setCellWidget(row, 6, btn_widget)

        self.lbl_count.setText(f"Menampilkan {len(items)} barang")

    def _add_item(self):
        dlg = ItemDialog(self)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            ok, msg = ItemController.create(data)
            if ok:
                self.show_message("Berhasil", "Barang berhasil ditambahkan!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _edit_item(self, item):
        dlg = ItemDialog(self, item)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            ok, msg = ItemController.update(item['id'], data)
            if ok:
                self.show_message("Berhasil", "Barang berhasil diupdate!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _delete_item(self, item):
        if self.confirm("Hapus Barang", f"Hapus '{item['name']}'? Tindakan ini tidak dapat dibatalkan."):
            ItemController.delete(item['id'], item['name'])
            self._load_data()
