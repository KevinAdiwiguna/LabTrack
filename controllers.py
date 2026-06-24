from models import User, Category, Item, Borrower, Loan, LoanRequest, ActivityLog
import database as db
import utils


# ── Auth Controller ───────────────────────────────────────────────

class AuthController:
    current_user: User = None

    @classmethod
    def login(cls, username, password):
        user = User.authenticate(username, password)
        if user:
            cls.current_user = user
            db.log_activity(user.id, user.username, "LOGIN",
                            f"Login berhasil sebagai {user.role}")
            return True, user
        return False, None

    @classmethod
    def logout(cls):
        if cls.current_user:
            db.log_activity(cls.current_user.id, cls.current_user.username, "LOGOUT", "Logout")
            cls.current_user = None

    @classmethod
    def register(cls, username, password, full_name):
        ok, result = User.register(username, password, full_name)
        if ok:
            db.log_activity(result, username, "REGISTRASI",
                            f"Akun baru terdaftar: {full_name} (viewer)")
        return ok, result

    @classmethod
    def has_permission(cls, min_role):
        roles = ['viewer', 'laboran', 'admin']
        if not cls.current_user:
            return False
        return roles.index(cls.current_user.role) >= roles.index(min_role)

    @classmethod
    def can_edit(cls):
        return cls.has_permission('laboran')

    @classmethod
    def is_admin(cls):
        return cls.has_permission('admin')

    @classmethod
    def is_viewer(cls):
        return cls.current_user and cls.current_user.role == 'viewer'


# ── User Management Controller (Admin only) ──────────────────────

class UserController:
    @staticmethod
    def get_all():
        return User.get_all()

    @staticmethod
    def create(username, password, full_name, role):
        ok, msg = utils.validate_required({'Username': username, 'Nama': full_name, 'Password': password})
        if not ok:
            return False, msg
        if len(password) < 6:
            return False, "Password minimal 6 karakter"
        if User.username_exists(username):
            return False, "Username sudah digunakan"
        uid = User.create(username, password, full_name, role)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "TAMBAH_USER",
                        f"Tambah user: {username} (role: {role})")
        return True, uid

    @staticmethod
    def update(uid, username, full_name, role, is_active):
        ok, msg = utils.validate_required({'Username': username, 'Nama': full_name})
        if not ok:
            return False, msg
        if User.username_exists(username, exclude_id=uid):
            return False, "Username sudah digunakan oleh akun lain"
        User.update(uid, username, full_name, role, is_active)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "EDIT_USER",
                        f"Edit user ID {uid}: {username} role→{role}")
        return True, None

    @staticmethod
    def reset_password(uid, new_password):
        if len(new_password) < 6:
            return False, "Password minimal 6 karakter"
        User.change_password(uid, new_password)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "RESET_PASSWORD",
                        f"Reset password user ID {uid}")
        return True, None

    @staticmethod
    def delete(uid, username):
        if uid == AuthController.current_user.id:
            return False, "Tidak bisa menghapus akun sendiri"
        User.delete(uid)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "HAPUS_USER", f"Hapus user: {username}")
        return True, None

    @staticmethod
    def change_role(uid, new_role):
        if uid == AuthController.current_user.id:
            return False, "Tidak bisa mengubah role akun sendiri"
        row = User.get_by_id(uid)
        if not row:
            return False, "User tidak ditemukan"
        User.update(uid, row['username'], row['full_name'], new_role, row['is_active'])
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "UBAH_ROLE",
                        f"Ubah role {row['username']}: {row['role']} → {new_role}")
        return True, None


# ── Item Controller ───────────────────────────────────────────────

class ItemController:
    @staticmethod
    def get_all(search="", category_id=None):
        return Item.get_all(search, category_id)

    @staticmethod
    def create(data):
        code = Item.generate_code()
        ok, msg = utils.validate_required({'Nama': data.get('name'), 'Stok': data.get('stock')})
        if not ok:
            return False, msg
        ok2, msg2 = utils.validate_stock(str(data.get('stock', 0)))
        if not ok2:
            return False, msg2
        iid = Item.create(
            code, data['name'], data.get('category_id'),
            int(data['stock']), data.get('condition', 'Baik'),
            data.get('location', ''), data.get('description', ''),
            data.get('photo_path', '')
        )
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "TAMBAH_BARANG",
                        f"Tambah barang: {data['name']} ({code})")
        return True, iid

    @staticmethod
    def update(iid, data):
        ok, msg = utils.validate_required({'Nama': data.get('name')})
        if not ok:
            return False, msg
        ok2, msg2 = utils.validate_stock(str(data.get('stock', 0)))
        if not ok2:
            return False, msg2
        Item.update(
            iid, data['name'], data.get('category_id'),
            int(data['stock']), data.get('condition', 'Baik'),
            data.get('location', ''), data.get('description', ''),
            data.get('photo_path', '')
        )
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "EDIT_BARANG",
                        f"Edit barang ID {iid}: {data['name']}")
        return True, None

    @staticmethod
    def delete(iid, name):
        Item.delete(iid)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "HAPUS_BARANG",
                        f"Hapus barang: {name} (ID {iid})")
        return True, None


# ── Category Controller ───────────────────────────────────────────

class CategoryController:
    @staticmethod
    def get_all():
        return Category.get_all()

    @staticmethod
    def create(name, description):
        ok, msg = utils.validate_required({'Nama Kategori': name})
        if not ok:
            return False, msg
        Category.create(name, description)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "TAMBAH_KATEGORI", f"Tambah kategori: {name}")
        return True, None

    @staticmethod
    def update(cid, name, description):
        ok, msg = utils.validate_required({'Nama Kategori': name})
        if not ok:
            return False, msg
        Category.update(cid, name, description)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "EDIT_KATEGORI", f"Edit kategori ID {cid}: {name}")
        return True, None

    @staticmethod
    def delete(cid, name):
        Category.delete(cid)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "HAPUS_KATEGORI", f"Hapus kategori: {name}")
        return True, None


# ── Borrower Controller ───────────────────────────────────────────

class BorrowerController:
    @staticmethod
    def get_all(search=""):
        return Borrower.get_all(search)

    @staticmethod
    def create(data, user_id=None):
        ok, msg = utils.validate_required({'NIM': data.get('nim'), 'Nama': data.get('name')})
        if not ok:
            return False, msg
        ok2, msg2 = utils.validate_nim(data.get('nim', ''))
        if not ok2:
            return False, msg2
        ok3, msg3 = utils.validate_email(data.get('email', ''))
        if not ok3:
            return False, msg3
        Borrower.create(data['nim'], data['name'],
                        data.get('department', ''), data.get('phone', ''),
                        data.get('email', ''), user_id)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "TAMBAH_PEMINJAM",
                        f"Tambah peminjam: {data['name']} ({data['nim']})")
        return True, None

    @staticmethod
    def update(bid, data):
        ok, msg = utils.validate_required({'NIM': data.get('nim'), 'Nama': data.get('name')})
        if not ok:
            return False, msg
        ok2, msg2 = utils.validate_nim(data.get('nim', ''))
        if not ok2:
            return False, msg2
        Borrower.update(bid, data['nim'], data['name'],
                        data.get('department', ''), data.get('phone', ''),
                        data.get('email', ''))
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "EDIT_PEMINJAM",
                        f"Edit peminjam ID {bid}: {data['name']}")
        return True, None

    @staticmethod
    def delete(bid, name):
        Borrower.delete(bid)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "HAPUS_PEMINJAM", f"Hapus peminjam: {name}")
        return True, None


# ── Loan Controller ───────────────────────────────────────────────

class LoanController:
    @staticmethod
    def get_all(status=None, search="", borrower_id=None):
        return Loan.get_all(status, search, borrower_id)

    @staticmethod
    def create(borrower_id, loan_date, due_date, notes, details):
        ok, msg = utils.validate_dates(loan_date, due_date)
        if not ok:
            return False, msg
        if not details:
            return False, "Pilih minimal satu barang"
        for item_id, qty, cond in details:
            item = Item.get_by_id(item_id)
            if not item:
                return False, f"Barang ID {item_id} tidak ditemukan"
            ok2, msg2 = utils.validate_quantity(str(qty), item['stock'])
            if not ok2:
                return False, f"{item['name']}: {msg2}"
        code = Loan.generate_code()
        u = AuthController.current_user
        loan_id = Loan.create(code, borrower_id, loan_date, due_date, notes, u.id, details)
        db.log_activity(u.id, u.username, "PEMINJAMAN",
                        f"Peminjaman {code} oleh borrower ID {borrower_id}")
        return True, loan_id

    @staticmethod
    def return_loan(loan_id, return_date, detail_conditions):
        status = Loan.return_loan(loan_id, return_date, detail_conditions)
        u = AuthController.current_user
        keterangan = "terlambat" if status == "terlambat" else "tepat waktu"
        db.log_activity(u.id, u.username, "PENGEMBALIAN",
                        f"Pengembalian loan ID {loan_id} ({keterangan})")
        return True, status


# ── Loan Request Controller (untuk Viewer) ───────────────────────

class LoanRequestController:
    @staticmethod
    def get_all(status=None, user_id=None):
        return LoanRequest.get_all(status, user_id)

    @staticmethod
    def submit_loan_request(user_id, due_date, notes, item_details):
        """Viewer mengajukan permintaan peminjaman"""
        if not item_details:
            return False, "Pilih minimal satu barang"
        ok, msg = utils.validate_dates(utils.today_str(), due_date)
        if not ok:
            return False, msg
        # Cek stok
        for item_id, qty in item_details:
            item = Item.get_by_id(item_id)
            if not item:
                return False, "Barang tidak ditemukan"
            ok2, msg2 = utils.validate_quantity(str(qty), item['stock'])
            if not ok2:
                return False, f"{item['name']}: {msg2}"
        rid, code = LoanRequest.create_loan_request(user_id, due_date, notes, item_details)
        db.log_activity(user_id, AuthController.current_user.username,
                        "AJUKAN_PINJAM", f"Pengajuan peminjaman {code}")
        return True, code

    @staticmethod
    def submit_return_request(user_id, loan_id, notes):
        """Viewer mengajukan permintaan pengembalian"""
        loan = Loan.get_by_id(loan_id)
        if not loan:
            return False, "Data peminjaman tidak ditemukan"
        if loan['status'] != 'dipinjam':
            return False, "Peminjaman ini sudah dikembalikan"
        rid, code = LoanRequest.create_return_request(user_id, loan_id, notes)
        db.log_activity(user_id, AuthController.current_user.username,
                        "AJUKAN_KEMBALI", f"Pengajuan pengembalian {code} untuk loan {loan['loan_code']}")
        return True, code

    @staticmethod
    def approve(rid, review_note=""):
        u = AuthController.current_user
        ok, msg = LoanRequest.approve(rid, u.id, review_note)
        if ok:
            db.log_activity(u.id, u.username, "SETUJUI_REQUEST",
                            f"Setujui request ID {rid}: {review_note}")
        return ok, msg

    @staticmethod
    def reject(rid, review_note=""):
        if not review_note.strip():
            return False, "Alasan penolakan harus diisi"
        u = AuthController.current_user
        ok, msg = LoanRequest.reject(rid, u.id, review_note)
        if ok:
            db.log_activity(u.id, u.username, "TOLAK_REQUEST",
                            f"Tolak request ID {rid}: {review_note}")
        return ok, msg

    @staticmethod
    def get_pending_count():
        return LoanRequest.get_pending_count()


# ── Report Controller ─────────────────────────────────────────────

class ReportController:
    @staticmethod
    def export_loans_csv(date_from=None, date_to=None):
        loans = Loan.get_all()
        filename = f"laporan_peminjaman_{utils.today_str()}.csv"
        headers = ['loan_code', 'borrower_name', 'nim', 'items_list',
                   'loan_date', 'due_date', 'return_date', 'status']
        filtered = []
        for l in loans:
            if date_from and l['loan_date'] < date_from:
                continue
            if date_to and l['loan_date'] > date_to:
                continue
            filtered.append({k: l.get(k, '') for k in headers})
        path = utils.export_csv(filtered, filename, headers)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "EXPORT_CSV", f"Export CSV: {filename}")
        return path

    @staticmethod
    def export_loans_pdf(date_from=None, date_to=None):
        loans = Loan.get_all()
        filtered = []
        for l in loans:
            if date_from and l['loan_date'] < date_from:
                continue
            if date_to and l['loan_date'] > date_to:
                continue
            filtered.append({
                'Kode': l.get('loan_code', ''),
                'Peminjam': l.get('borrower_name', ''),
                'NIM': l.get('nim', ''),
                'Barang': (l.get('items_list') or '')[:25],
                'Tgl Pinjam': l.get('loan_date', ''),
                'Deadline': l.get('due_date', ''),
                'Status': l.get('status', ''),
            })
        filename = f"laporan_peminjaman_{utils.today_str()}.pdf"
        path = utils.export_pdf(
            "Laporan Peminjaman - LabTrack", filtered, filename,
            headers=['Kode', 'Peminjam', 'NIM', 'Barang', 'Tgl Pinjam', 'Deadline', 'Status'],
            col_widths=[28, 35, 22, 45, 22, 22, 22]
        )
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "EXPORT_PDF", f"Export PDF: {filename}")
        return path

    @staticmethod
    def export_inventory_csv():
        items = Item.get_all()
        headers = ['item_code', 'name', 'category_name', 'stock', 'condition', 'location', 'description']
        data = [{k: i.get(k, '') for k in headers} for i in items]
        filename = f"inventaris_{utils.today_str()}.csv"
        path = utils.export_csv(data, filename, headers)
        u = AuthController.current_user
        db.log_activity(u.id, u.username, "EXPORT_CSV", f"Export inventaris CSV: {filename}")
        return path
