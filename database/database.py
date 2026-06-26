"""
database.py - Modul manajemen database SQLite untuk LabTrack
Versi 2.0 - Tambah tabel loan_requests untuk fitur pengajuan viewer
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "labtrack.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    # ── Users ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','laboran','viewer')),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Categories ───────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Items ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            condition TEXT NOT NULL DEFAULT 'Baik'
                CHECK(condition IN ('Baik','Rusak Ringan','Rusak Berat')),
            location TEXT,
            description TEXT,
            photo_path TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Borrowers ────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS borrowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            department TEXT,
            phone TEXT,
            email TEXT,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Loans ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_code TEXT NOT NULL UNIQUE,
            borrower_id INTEGER NOT NULL REFERENCES borrowers(id),
            loan_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL DEFAULT 'dipinjam'
                CHECK(status IN ('dipinjam','dikembalikan','terlambat')),
            notes TEXT,
            created_by INTEGER REFERENCES users(id),
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Loan Details ─────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loan_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
            item_id INTEGER NOT NULL REFERENCES items(id),
            quantity INTEGER NOT NULL DEFAULT 1,
            condition_borrowed TEXT DEFAULT 'Baik',
            condition_returned TEXT
        )
    """)

    # ── Loan Requests (Pengajuan oleh Viewer) ────────────────────
    # Viewer mengajukan permintaan, lalu admin/laboran konfirmasi
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loan_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_code TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL REFERENCES users(id),
            request_type TEXT NOT NULL CHECK(request_type IN ('pinjam','kembali')),
            loan_id INTEGER REFERENCES loans(id),
            due_date TEXT,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'menunggu'
                CHECK(status IN ('menunggu','disetujui','ditolak')),
            reviewed_by INTEGER REFERENCES users(id),
            review_note TEXT,
            reviewed_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Loan Request Details (item yang diminta viewer) ──────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loan_request_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL REFERENCES loan_requests(id) ON DELETE CASCADE,
            item_id INTEGER NOT NULL REFERENCES items(id),
            quantity INTEGER NOT NULL DEFAULT 1
        )
    """)

    # ── Activity Logs ────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            username TEXT,
            action TEXT NOT NULL,
            description TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # Migrasi: tambah kolom user_id ke borrowers jika belum ada
    try:
        cur.execute("ALTER TABLE borrowers ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL")
    except Exception:
        pass  # Kolom sudah ada

    _seed_initial_data(cur)
    conn.commit()
    conn.close()


def _seed_initial_data(cur):
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        users = [
            ("admin",   hash_password("admin123"),   "Administrator", "admin"),
            ("laboran", hash_password("laboran123"), "Staff Laboran", "laboran"),
            ("viewer",  hash_password("viewer123"),  "Viewer Umum",   "viewer"),
        ]
        cur.executemany(
            "INSERT INTO users (username,password,full_name,role) VALUES (?,?,?,?)", users
        )

    cur.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] == 0:
        cats = [
            ("Elektronik",  "Peralatan elektronik dan komputer"),
            ("Optik",       "Peralatan optik dan lensa"),
            ("Mekanik",     "Peralatan mekanik dan perkakas"),
            ("Kimia",       "Peralatan laboratorium kimia"),
            ("Biologi",     "Peralatan laboratorium biologi"),
            ("Pengukuran",  "Alat ukur dan instrumen"),
        ]
        cur.executemany("INSERT INTO categories (name,description) VALUES (?,?)", cats)

    cur.execute("SELECT COUNT(*) FROM items")
    if cur.fetchone()[0] == 0:
        items = [
            ("ITM-001","Oscilloscope Digital",  1, 5, "Baik",        "Rak A1", "Pengukur sinyal listrik"),
            ("ITM-002","Multimeter Digital",    1, 8, "Baik",        "Rak A2", "Pengukur tegangan arus"),
            ("ITM-003","Mikroskop Binokuler",   2, 3, "Baik",        "Rak B1", "Pembesaran hingga 1000x"),
            ("ITM-004","Beaker Glass 500ml",    4,20, "Baik",        "Rak C1", "Gelas beker borosilikat"),
            ("ITM-005","Pipette Controller",    4,10, "Baik",        "Rak C2", "Pipet otomatis elektrik"),
            ("ITM-006","Jangka Sorong",         6,12, "Baik",        "Rak D1", "Presisi 0.01mm"),
            ("ITM-007","Laptop Acer Aspire",    1, 4, "Baik",        "Rak A3", "Core i5 RAM 8GB"),
            ("ITM-008","Catu Daya DC 30V",      1, 6, "Rusak Ringan","Rak A4", "Output 0-30V 5A"),
        ]
        cur.executemany(
            "INSERT INTO items (item_code,name,category_id,stock,condition,location,description) VALUES (?,?,?,?,?,?,?)",
            items
        )

    cur.execute("SELECT COUNT(*) FROM borrowers")
    if cur.fetchone()[0] == 0:
        borrowers = [
            ("2021001","Budi Santoso",  "Teknik Elektro","081234567890","budi@email.com",  None),
            ("2021002","Siti Rahayu",   "Fisika",        "081234567891","siti@email.com",  None),
            ("2021003","Ahmad Fauzi",   "Kimia",         "081234567892","ahmad@email.com", None),
            ("2021004","Dewi Lestari",  "Biologi",       "081234567893","dewi@email.com",  None),
            ("2021005","Rizky Pratama", "Teknik Mesin",  "081234567894","rizky@email.com", None),
        ]
        cur.executemany(
            "INSERT INTO borrowers (nim,name,department,phone,email,user_id) VALUES (?,?,?,?,?,?)",
            borrowers
        )


# ── Helper umum ──────────────────────────────────────────────────

def fetchall(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetchone(query, params=()):
    conn = get_connection()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None


def execute(query, params=()):
    conn = get_connection()
    cur = conn.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def log_activity(user_id, username, action, description=""):
    execute(
        "INSERT INTO activity_logs (user_id,username,action,description) VALUES (?,?,?,?)",
        (user_id, username, action, description)
    )
