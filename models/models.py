"""
models.py - Model/DTO untuk entitas LabTrack v2.0
"""

from dataclasses import dataclass
from datetime import datetime
import database.database as db


# ── User ─────────────────────────────────────────────────────────

@dataclass
class User:
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool = True

    @staticmethod
    def authenticate(username, password):
        hashed = db.hash_password(password)
        row = db.fetchone(
            "SELECT * FROM users WHERE username=? AND password=? AND is_active=1",
            (username, hashed)
        )
        if row:
            return User(row['id'], row['username'], row['full_name'], row['role'], bool(row['is_active']))
        return None

    @staticmethod
    def get_all():
        return db.fetchall("SELECT * FROM users ORDER BY role, username")

    @staticmethod
    def get_by_id(uid):
        return db.fetchone("SELECT * FROM users WHERE id=?", (uid,))

    @staticmethod
    def username_exists(username, exclude_id=None):
        if exclude_id:
            r = db.fetchone("SELECT id FROM users WHERE username=? AND id!=?", (username, exclude_id))
        else:
            r = db.fetchone("SELECT id FROM users WHERE username=?", (username,))
        return r is not None

    @staticmethod
    def create(username, password, full_name, role):
        hashed = db.hash_password(password)
        return db.execute(
            "INSERT INTO users (username,password,full_name,role) VALUES (?,?,?,?)",
            (username, hashed, full_name, role)
        )

    @staticmethod
    def update(uid, username, full_name, role, is_active=1):
        db.execute(
            "UPDATE users SET username=?,full_name=?,role=?,is_active=? WHERE id=?",
            (username, full_name, role, is_active, uid)
        )

    @staticmethod
    def change_password(uid, new_password):
        hashed = db.hash_password(new_password)
        db.execute("UPDATE users SET password=? WHERE id=?", (hashed, uid))

    @staticmethod
    def delete(uid):
        db.execute("DELETE FROM users WHERE id=?", (uid,))

    @staticmethod
    def register(username, password, full_name):
        """Registrasi akun baru dengan role viewer secara default"""
        if User.username_exists(username):
            return False, "Username sudah digunakan"
        if len(username) < 4:
            return False, "Username minimal 4 karakter"
        if len(password) < 6:
            return False, "Password minimal 6 karakter"
        uid = User.create(username, password, full_name, 'viewer')
        return True, uid


# ── Category ─────────────────────────────────────────────────────

class Category:
    @staticmethod
    def get_all():
        return db.fetchall("SELECT * FROM categories ORDER BY name")

    @staticmethod
    def create(name, description=""):
        return db.execute(
            "INSERT INTO categories (name,description) VALUES (?,?)", (name, description)
        )

    @staticmethod
    def update(cid, name, description):
        db.execute("UPDATE categories SET name=?,description=? WHERE id=?", (name, description, cid))

    @staticmethod
    def delete(cid):
        db.execute("DELETE FROM categories WHERE id=?", (cid,))


# ── Item ─────────────────────────────────────────────────────────

class Item:
    @staticmethod
    def get_all(search="", category_id=None):
        q = """
            SELECT i.*, c.name AS category_name
            FROM items i
            LEFT JOIN categories c ON i.category_id = c.id
            WHERE 1=1
        """
        params = []
        if search:
            q += " AND (i.name LIKE ? OR i.item_code LIKE ? OR i.location LIKE ?)"
            params += [f"%{search}%"] * 3
        if category_id:
            q += " AND i.category_id = ?"
            params.append(category_id)
        q += " ORDER BY i.name"
        return db.fetchall(q, tuple(params))

    @staticmethod
    def get_by_id(item_id):
        return db.fetchone(
            "SELECT i.*,c.name AS category_name FROM items i LEFT JOIN categories c ON i.category_id=c.id WHERE i.id=?",
            (item_id,)
        )

    @staticmethod
    def generate_code():
        row = db.fetchone("SELECT item_code FROM items ORDER BY id DESC LIMIT 1")
        if row:
            try:
                num = int(row['item_code'].split('-')[1]) + 1
            except Exception:
                num = 1
        else:
            num = 1
        return f"ITM-{num:03d}"

    @staticmethod
    def create(item_code, name, category_id, stock, condition, location, description, photo_path=""):
        return db.execute(
            """INSERT INTO items (item_code,name,category_id,stock,condition,location,description,photo_path)
               VALUES (?,?,?,?,?,?,?,?)""",
            (item_code, name, category_id, stock, condition, location, description, photo_path)
        )

    @staticmethod
    def update(iid, name, category_id, stock, condition, location, description, photo_path=""):
        db.execute(
            """UPDATE items SET name=?,category_id=?,stock=?,condition=?,location=?,
               description=?,photo_path=?,updated_at=datetime('now','localtime') WHERE id=?""",
            (name, category_id, stock, condition, location, description, photo_path, iid)
        )

    @staticmethod
    def delete(iid):
        db.execute("DELETE FROM items WHERE id=?", (iid,))

    @staticmethod
    def update_stock(item_id, delta):
        db.execute("UPDATE items SET stock = stock + ? WHERE id=?", (delta, item_id))


# ── Borrower ─────────────────────────────────────────────────────

class Borrower:
    @staticmethod
    def get_all(search=""):
        q = """
            SELECT b.*, u.username, u.role
            FROM borrowers b
            LEFT JOIN users u ON b.user_id = u.id
            WHERE 1=1
        """
        params = []
        if search:
            q += " AND (b.name LIKE ? OR b.nim LIKE ? OR b.department LIKE ?)"
            params += [f"%{search}%"] * 3
        q += " ORDER BY b.name"
        return db.fetchall(q, tuple(params))

    @staticmethod
    def get_by_id(bid):
        return db.fetchone("""
            SELECT b.*, u.username FROM borrowers b
            LEFT JOIN users u ON b.user_id = u.id
            WHERE b.id=?
        """, (bid,))

    @staticmethod
    def get_by_user_id(user_id):
        return db.fetchone("SELECT * FROM borrowers WHERE user_id=?", (user_id,))

    @staticmethod
    def create(nim, name, department, phone, email, user_id=None):
        return db.execute(
            "INSERT INTO borrowers (nim,name,department,phone,email,user_id) VALUES (?,?,?,?,?,?)",
            (nim, name, department, phone, email, user_id)
        )

    @staticmethod
    def update(bid, nim, name, department, phone, email):
        db.execute(
            "UPDATE borrowers SET nim=?,name=?,department=?,phone=?,email=? WHERE id=?",
            (nim, name, department, phone, email, bid)
        )

    @staticmethod
    def delete(bid):
        db.execute("DELETE FROM borrowers WHERE id=?", (bid,))


# ── Loan ─────────────────────────────────────────────────────────

class Loan:
    @staticmethod
    def generate_code():
        today = datetime.now().strftime("%Y%m%d")
        row = db.fetchone(
            "SELECT COUNT(*) as c FROM loans WHERE loan_code LIKE ?", (f"LN-{today}%",)
        )
        num = (row['c'] if row else 0) + 1
        return f"LN-{today}-{num:03d}"

    @staticmethod
    def get_all(status=None, search="", borrower_id=None):
        q = """
            SELECT l.*, b.name as borrower_name, b.nim,
                   GROUP_CONCAT(i.name, ', ') as items_list
            FROM loans l
            JOIN borrowers b ON l.borrower_id = b.id
            LEFT JOIN loan_details ld ON ld.loan_id = l.id
            LEFT JOIN items i ON ld.item_id = i.id
            WHERE 1=1
        """
        params = []
        if status:
            q += " AND l.status = ?"
            params.append(status)
        if search:
            q += " AND (b.name LIKE ? OR b.nim LIKE ? OR l.loan_code LIKE ?)"
            params += [f"%{search}%"] * 3
        if borrower_id:
            q += " AND l.borrower_id = ?"
            params.append(borrower_id)
        q += " GROUP BY l.id ORDER BY l.created_at DESC"
        return db.fetchall(q, tuple(params))

    @staticmethod
    def get_by_id(loan_id):
        return db.fetchone("""
            SELECT l.*, b.name as borrower_name, b.nim, b.department, b.phone
            FROM loans l JOIN borrowers b ON l.borrower_id = b.id
            WHERE l.id=?
        """, (loan_id,))

    @staticmethod
    def get_details(loan_id):
        return db.fetchall("""
            SELECT ld.*, i.name as item_name, i.item_code
            FROM loan_details ld
            JOIN items i ON ld.item_id = i.id
            WHERE ld.loan_id = ?
        """, (loan_id,))

    @staticmethod
    def create(loan_code, borrower_id, loan_date, due_date, notes, created_by, details):
        loan_id = db.execute(
            """INSERT INTO loans (loan_code,borrower_id,loan_date,due_date,notes,created_by)
               VALUES (?,?,?,?,?,?)""",
            (loan_code, borrower_id, loan_date, due_date, notes, created_by)
        )
        for item_id, qty, cond in details:
            db.execute(
                "INSERT INTO loan_details (loan_id,item_id,quantity,condition_borrowed) VALUES (?,?,?,?)",
                (loan_id, item_id, qty, cond)
            )
            Item.update_stock(item_id, -qty)
        return loan_id

    @staticmethod
    def return_loan(loan_id, return_date, detail_conditions):
        loan = Loan.get_by_id(loan_id)
        due = datetime.strptime(loan['due_date'], "%Y-%m-%d").date()
        ret = datetime.strptime(return_date, "%Y-%m-%d").date()
        status = "terlambat" if ret > due else "dikembalikan"
        db.execute(
            "UPDATE loans SET status=?,return_date=? WHERE id=?",
            (status, return_date, loan_id)
        )
        details = Loan.get_details(loan_id)
        for d in details:
            cond = detail_conditions.get(d['id'], 'Baik')
            db.execute(
                "UPDATE loan_details SET condition_returned=? WHERE id=?",
                (cond, d['id'])
            )
            Item.update_stock(d['item_id'], d['quantity'])
        return status

    @staticmethod
    def get_monthly_stats():
        return db.fetchall("""
            SELECT strftime('%Y-%m', loan_date) as month, COUNT(*) as total
            FROM loans GROUP BY month ORDER BY month DESC LIMIT 12
        """)

    @staticmethod
    def get_top_items():
        return db.fetchall("""
            SELECT i.name, SUM(ld.quantity) as total
            FROM loan_details ld
            JOIN items i ON ld.item_id = i.id
            GROUP BY i.id ORDER BY total DESC LIMIT 8
        """)

    @staticmethod
    def get_active_count():
        row = db.fetchone("SELECT COUNT(*) as c FROM loans WHERE status='dipinjam'")
        return row['c'] if row else 0

    @staticmethod
    def get_total_count():
        row = db.fetchone("SELECT COUNT(*) as c FROM loans")
        return row['c'] if row else 0


# ── LoanRequest (Pengajuan Viewer) ───────────────────────────────

class LoanRequest:
    @staticmethod
    def generate_code(req_type):
        prefix = "REQ-P" if req_type == 'pinjam' else "REQ-K"
        today = datetime.now().strftime("%Y%m%d")
        row = db.fetchone(
            "SELECT COUNT(*) as c FROM loan_requests WHERE request_code LIKE ?",
            (f"{prefix}-{today}%",)
        )
        num = (row['c'] if row else 0) + 1
        return f"{prefix}-{today}-{num:03d}"

    @staticmethod
    def get_all(status=None, user_id=None):
        q = """
            SELECT r.*, u.full_name as requester_name, u.username as requester_username,
                   rv.full_name as reviewer_name,
                   GROUP_CONCAT(i.name || ' (x' || rd.quantity || ')', ', ') as items_list,
                   l.loan_code
            FROM loan_requests r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN users rv ON r.reviewed_by = rv.id
            LEFT JOIN loan_request_details rd ON rd.request_id = r.id
            LEFT JOIN items i ON rd.item_id = i.id
            LEFT JOIN loans l ON r.loan_id = l.id
            WHERE 1=1
        """
        params = []
        if status:
            q += " AND r.status = ?"
            params.append(status)
        if user_id:
            q += " AND r.user_id = ?"
            params.append(user_id)
        q += " GROUP BY r.id ORDER BY r.created_at DESC"
        return db.fetchall(q, tuple(params))

    @staticmethod
    def get_by_id(rid):
        return db.fetchone("""
            SELECT r.*, u.full_name as requester_name, u.username as requester_username,
                   rv.full_name as reviewer_name
            FROM loan_requests r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN users rv ON r.reviewed_by = rv.id
            WHERE r.id=?
        """, (rid,))

    @staticmethod
    def get_details(rid):
        return db.fetchall("""
            SELECT rd.*, i.name as item_name, i.item_code, i.stock
            FROM loan_request_details rd
            JOIN items i ON rd.item_id = i.id
            WHERE rd.request_id = ?
        """, (rid,))

    @staticmethod
    def create_loan_request(user_id, due_date, notes, item_details):
        """item_details = list of (item_id, quantity)"""
        code = LoanRequest.generate_code('pinjam')
        rid = db.execute(
            """INSERT INTO loan_requests (request_code,user_id,request_type,due_date,notes)
               VALUES (?,?,?,?,?)""",
            (code, user_id, 'pinjam', due_date, notes)
        )
        for item_id, qty in item_details:
            db.execute(
                "INSERT INTO loan_request_details (request_id,item_id,quantity) VALUES (?,?,?)",
                (rid, item_id, qty)
            )
        return rid, code

    @staticmethod
    def create_return_request(user_id, loan_id, notes):
        """Viewer mengajukan pengembalian atas loan yang aktif"""
        code = LoanRequest.generate_code('kembali')
        rid = db.execute(
            """INSERT INTO loan_requests (request_code,user_id,request_type,loan_id,notes)
               VALUES (?,?,?,?,?)""",
            (code, user_id, 'kembali', loan_id, notes)
        )
        return rid, code

    @staticmethod
    def approve(rid, reviewer_id, review_note=""):
        """Setujui pengajuan — eksekusi peminjaman/pengembalian aktual"""
        req  = LoanRequest.get_by_id(rid)
        now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.now().strftime("%Y-%m-%d")

        if req['request_type'] == 'pinjam':
            # Cari borrower yang terhubung dengan user ini
            borrower = db.fetchone(
                "SELECT * FROM borrowers WHERE user_id=?", (req['user_id'],)
            )
            if not borrower:
                return False, "Profil peminjam belum lengkap. Hubungi Admin."

            details_raw = LoanRequest.get_details(rid)
            details = [(d['item_id'], d['quantity'], 'Baik') for d in details_raw]

            loan_code = Loan.generate_code()
            due = req['due_date'] or (
                datetime.now().strftime("%Y-%m-%d")
            )
            Loan.create(loan_code, borrower['id'], today, due, req['notes'], reviewer_id, details)

        elif req['request_type'] == 'kembali':
            if req['loan_id']:
                Loan.return_loan(req['loan_id'], today, {})

        db.execute(
            """UPDATE loan_requests SET status='disetujui', reviewed_by=?,
               review_note=?, reviewed_at=? WHERE id=?""",
            (reviewer_id, review_note, now, rid)
        )
        return True, "Pengajuan berhasil disetujui"

    @staticmethod
    def reject(rid, reviewer_id, review_note=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            """UPDATE loan_requests SET status='ditolak', reviewed_by=?,
               review_note=?, reviewed_at=? WHERE id=?""",
            (reviewer_id, review_note, now, rid)
        )
        return True, "Pengajuan ditolak"

    @staticmethod
    def get_pending_count():
        row = db.fetchone(
            "SELECT COUNT(*) as c FROM loan_requests WHERE status='menunggu'"
        )
        return row['c'] if row else 0


# ── ActivityLog ──────────────────────────────────────────────────

class ActivityLog:
    @staticmethod
    def get_recent(limit=20):
        return db.fetchall(
            "SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
        )

    @staticmethod
    def get_all(date_from=None, date_to=None):
        q = "SELECT * FROM activity_logs WHERE 1=1"
        params = []
        if date_from:
            q += " AND timestamp >= ?"
            params.append(date_from)
        if date_to:
            q += " AND timestamp <= ?"
            params.append(date_to + " 23:59:59")
        q += " ORDER BY timestamp DESC"
        return db.fetchall(q, tuple(params))
