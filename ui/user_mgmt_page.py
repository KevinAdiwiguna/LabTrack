

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDialog, QFormLayout, QMessageBox,
    QCheckBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

from ui.base_page import BasePage
from controllers import AuthController, UserController


class UserDialog(QDialog):
    """Dialog untuk tambah / edit user"""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Edit Pengguna" if user else "Tambah Pengguna")
        self.setMinimumWidth(420)
        self._setup_ui()
        if user:
            self._populate(user)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        icon = "✏️" if self.user else "➕"
        title = QLabel(f"{icon}  {'Edit' if self.user else 'Tambah'} Pengguna")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_fullname = QLineEdit(); self.inp_fullname.setMinimumHeight(38)
        self.inp_username = QLineEdit(); self.inp_username.setMinimumHeight(38)

        self.inp_password = QLineEdit()
        self.inp_password.setEchoMode(QLineEdit.Password)
        self.inp_password.setMinimumHeight(38)
        if self.user:
            self.inp_password.setPlaceholderText("Kosongkan jika tidak ingin mengubah password")
        else:
            self.inp_password.setPlaceholderText("Minimal 6 karakter")

        self.combo_role = QComboBox()
        self.combo_role.setMinimumHeight(38)
        self.combo_role.addItems(["viewer", "laboran", "admin"])

        self.chk_active = QCheckBox("Akun Aktif")
        self.chk_active.setChecked(True)
        self.chk_active.setStyleSheet("color: #e2e8f0;")

        form.addRow("Nama Lengkap *", self.inp_fullname)
        form.addRow("Username *",     self.inp_username)
        form.addRow("Password",       self.inp_password)
        form.addRow("Role *",         self.combo_role)
        form.addRow("Status",         self.chk_active)
        layout.addLayout(form)

        # Info role
        info = QFrame()
        info.setStyleSheet("QFrame { background: #162032; border-radius: 6px; padding: 6px; }")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(8, 6, 8, 6)
        info_lbl = QLabel(
            "👁️ <b>Viewer</b> — Lihat katalog, ajukan permintaan pinjam/kembali\n"
            "🔧 <b>Laboran</b> — CRUD inventaris, peminjam, konfirmasi request\n"
            "👑 <b>Admin</b> — Semua akses + kelola pengguna + activity log"
        )
        info_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        info_lbl.setWordWrap(True)
        info_layout.addWidget(info_lbl)
        layout.addWidget(info)

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

    def _populate(self, user):
        self.inp_fullname.setText(user['full_name'])
        self.inp_username.setText(user['username'])
        idx = self.combo_role.findText(user['role'])
        if idx >= 0:
            self.combo_role.setCurrentIndex(idx)
        self.chk_active.setChecked(bool(user['is_active']))

    def get_data(self):
        return {
            'full_name': self.inp_fullname.text().strip(),
            'username':  self.inp_username.text().strip(),
            'password':  self.inp_password.text(),
            'role':      self.combo_role.currentText(),
            'is_active': 1 if self.chk_active.isChecked() else 0,
        }


class ResetPasswordDialog(QDialog):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.setWindowTitle(f"Reset Password — {username}")
        self.setMinimumWidth(360)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel(f"🔑  Reset Password\n@{username}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        lbl = QLabel("Password Baru (minimal 6 karakter):")
        lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl)

        self.inp_pwd = QLineEdit()
        self.inp_pwd.setEchoMode(QLineEdit.Password)
        self.inp_pwd.setPlaceholderText("Password baru...")
        self.inp_pwd.setMinimumHeight(40)
        layout.addWidget(self.inp_pwd)

        lbl2 = QLabel("Konfirmasi Password Baru:")
        lbl2.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl2)

        self.inp_pwd2 = QLineEdit()
        self.inp_pwd2.setEchoMode(QLineEdit.Password)
        self.inp_pwd2.setPlaceholderText("Ulangi password baru...")
        self.inp_pwd2.setMinimumHeight(40)
        layout.addWidget(self.inp_pwd2)

        self.lbl_err = QLabel("")
        self.lbl_err.setStyleSheet("color: #f87171; font-size: 12px;")
        self.lbl_err.hide()
        layout.addWidget(self.lbl_err)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal"); btn_cancel.setObjectName("btn_secondary"); btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("🔑  Reset"); btn_ok.setObjectName("btn_primary"); btn_ok.clicked.connect(self._check)
        btn_row.addWidget(btn_cancel); btn_row.addStretch(); btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _check(self):
        p1 = self.inp_pwd.text()
        p2 = self.inp_pwd2.text()
        if p1 != p2:
            self.lbl_err.setText("Password tidak cocok"); self.lbl_err.show(); return
        if len(p1) < 6:
            self.lbl_err.setText("Password minimal 6 karakter"); self.lbl_err.show(); return
        self.accept()

    def get_password(self):
        return self.inp_pwd.text()


class UserMgmtPage(BasePage):
    def __init__(self):
        super().__init__("🔑  Kelola Pengguna", "Manajemen akun dan hak akses pengguna sistem")
        self._setup_content()

    def _setup_content(self):
        # Tombol tambah
        btn_add = QPushButton("➕  Tambah Pengguna")
        btn_add.setObjectName("btn_primary")
        btn_add.setMinimumHeight(36)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._add_user)
        self.header_buttons.addWidget(btn_add)

        # Filter
        fr = QHBoxLayout(); fr.setSpacing(8)
        self.filter_role = QComboBox()
        self.filter_role.setMinimumHeight(38)
        self.filter_role.setMinimumWidth(150)
        self.filter_role.addItems(["Semua Role", "admin", "laboran", "viewer"])
        self.filter_role.currentIndexChanged.connect(self._load_data)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Cari nama / username...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self._load_data)

        fr.addWidget(QLabel("Role:"))
        fr.addWidget(self.filter_role)
        fr.addWidget(self.search_input, 1)
        self.main_layout.addLayout(fr)

        # Stats bar
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(8)
        self.lbl_total  = self._make_stat_chip("Total", 0, "#38bdf8")
        self.lbl_admin  = self._make_stat_chip("Admin", 0, "#a78bfa")
        self.lbl_lab    = self._make_stat_chip("Laboran", 0, "#22c55e")
        self.lbl_viewer = self._make_stat_chip("Viewer", 0, "#f59e0b")
        for w in (self.lbl_total, self.lbl_admin, self.lbl_lab, self.lbl_viewer):
            self.stats_row.addWidget(w)
        self.stats_row.addStretch()
        self.main_layout.addLayout(self.stats_row)

        # Tabel
        self.table = self.make_table(
            ["ID", "Nama Lengkap", "Username", "Role", "Status", "Dibuat", "Aksi"],
            stretch_col=1
        )
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 220)
        self.main_layout.addWidget(self.table)

    def _make_stat_chip(self, label, val, color):
        chip = QLabel(f"{label}: {val}")
        chip.setStyleSheet(f"""
            QLabel {{
                background: #1e293b;
                border: 1px solid {color};
                border-radius: 12px;
                color: {color};
                font-size: 12px;
                font-weight: bold;
                padding: 4px 12px;
            }}
        """)
        return chip

    def refresh(self):
        self._load_data()

    def _load_data(self):
        users = UserController.get_all()

        # Filter role
        role_filter = self.filter_role.currentText()
        if role_filter != "Semua Role":
            users = [u for u in users if u['role'] == role_filter]

        # Filter search
        search = self.search_input.text().strip().lower()
        if search:
            users = [u for u in users if
                     search in u['full_name'].lower() or
                     search in u['username'].lower()]

        # Update stat chips
        all_users = UserController.get_all()
        self.lbl_total.setText(f"Total: {len(all_users)}")
        self.lbl_admin.setText(f"Admin: {sum(1 for u in all_users if u['role']=='admin')}")
        self.lbl_lab.setText(f"Laboran: {sum(1 for u in all_users if u['role']=='laboran')}")
        self.lbl_viewer.setText(f"Viewer: {sum(1 for u in all_users if u['role']=='viewer')}")

        self.table.setRowCount(len(users))
        role_colors = {'admin': '#a78bfa', 'laboran': '#22c55e', 'viewer': '#f59e0b'}
        role_icons  = {'admin': '👑', 'laboran': '🔧', 'viewer': '👁️'}
        current_uid = AuthController.current_user.id

        for row, user in enumerate(users):
            is_self = user['id'] == current_uid

            self.table.setItem(row, 0, self.colored_item(user['id'], "#94a3b8"))
            name_item = self.table_item(user['full_name'] + (" (Anda)" if is_self else ""))
            if is_self:
                name_item.setForeground(QColor("#38bdf8"))
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, self.table_item(user['username']))
            color = role_colors.get(user['role'], '#e2e8f0')
            icon  = role_icons.get(user['role'], '')
            self.table.setItem(row, 3, self.colored_item(
                f"{icon} {user['role'].upper()}", color
            ))
            active_item = self.colored_item(
                "✅ Aktif" if user['is_active'] else "🔴 Nonaktif",
                "#22c55e" if user['is_active'] else "#ef4444"
            )
            self.table.setItem(row, 4, active_item)
            self.table.setItem(row, 5, self.table_item(
                (user.get('created_at') or "")[:16], Qt.AlignCenter
            ))

            # Aksi
            bw = QWidget()
            bl = QHBoxLayout(bw)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(4)

            btn_edit = QPushButton("✏️ Edit")
            btn_edit.setObjectName("btn_icon")
            btn_edit.clicked.connect(lambda _, u=user: self._edit_user(u))

            btn_role = QPushButton("🔄 Role")
            btn_role.setObjectName("btn_icon")
            btn_role.setToolTip("Ubah role")
            btn_role.clicked.connect(lambda _, u=user: self._change_role(u))

            btn_pwd = QPushButton("🔑")
            btn_pwd.setObjectName("btn_icon")
            btn_pwd.setToolTip("Reset password")
            btn_pwd.clicked.connect(lambda _, u=user: self._reset_pwd(u))

            bl.addWidget(btn_edit)
            bl.addWidget(btn_role)
            bl.addWidget(btn_pwd)

            if not is_self:
                btn_del = QPushButton("🗑️")
                btn_del.setObjectName("btn_icon")
                btn_del.setToolTip("Hapus akun")
                btn_del.clicked.connect(lambda _, u=user: self._delete_user(u))
                bl.addWidget(btn_del)

            self.table.setCellWidget(row, 6, bw)

    def _add_user(self):
        dlg = UserDialog(self)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            ok, msg = UserController.create(
                data['username'], data['password'], data['full_name'], data['role']
            )
            if ok:
                self.show_message("Berhasil", "✅  Pengguna berhasil ditambahkan!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _edit_user(self, user):
        dlg = UserDialog(self, user)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            ok, msg = UserController.update(
                user['id'], data['username'], data['full_name'],
                data['role'], data['is_active']
            )
            if ok:
                # Jika ada password baru
                if data['password']:
                    UserController.reset_password(user['id'], data['password'])
                self.show_message("Berhasil", "✅  Data pengguna berhasil diupdate!")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _change_role(self, user):
        """Dialog cepat untuk ubah role"""
        if user['id'] == AuthController.current_user.id:
            self.show_message("Tidak Diizinkan", "Tidak bisa mengubah role akun sendiri",
                              QMessageBox.Warning)
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Ubah Role — {user['username']}")
        dlg.setMinimumWidth(320)
        dlg.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel(f"🔄  Ubah Role\n@{user['username']}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        lbl = QLabel(f"Role saat ini: <b>{user['role'].upper()}</b>")
        lbl.setStyleSheet("color: #94a3b8; font-size: 13px;")
        layout.addWidget(lbl)

        combo = QComboBox()
        combo.setMinimumHeight(40)
        combo.addItems(["viewer", "laboran", "admin"])
        idx = combo.findText(user['role'])
        if idx >= 0:
            combo.setCurrentIndex(idx)
        layout.addWidget(combo)

        btn_row = QHBoxLayout()
        btn_c = QPushButton("Batal"); btn_c.setObjectName("btn_secondary"); btn_c.clicked.connect(dlg.reject)
        btn_ok = QPushButton("✅  Simpan"); btn_ok.setObjectName("btn_primary"); btn_ok.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_c); btn_row.addStretch(); btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        if dlg.exec() == QDialog.Accepted:
            new_role = combo.currentText()
            ok, msg = UserController.change_role(user['id'], new_role)
            if ok:
                self.show_message("Berhasil",
                                  f"Role @{user['username']} berubah menjadi {new_role.upper()}")
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _reset_pwd(self, user):
        dlg = ResetPasswordDialog(self, user['username'])
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec() == QDialog.Accepted:
            ok, msg = UserController.reset_password(user['id'], dlg.get_password())
            if ok:
                self.show_message("Berhasil", f"Password @{user['username']} berhasil direset!")
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)

    def _delete_user(self, user):
        if self.confirm("Hapus Pengguna",
                        f"Hapus akun '@{user['username']}'?\nTindakan ini tidak dapat dibatalkan."):
            ok, msg = UserController.delete(user['id'], user['username'])
            if ok:
                self._load_data()
            else:
                self.show_message("Gagal", msg, QMessageBox.Warning)
