# LabTrack

# 🔬 LabTrack - Sistem Inventaris & Peminjaman Laboratorium

Aplikasi desktop modern untuk manajemen inventaris dan peminjaman barang laboratorium kampus.

## ✅ Fitur Lengkap

| Fitur | Status |
|-------|--------|
| Login Multi-Role (Admin, Laboran, Viewer) | ✅ |
| Dashboard interaktif + grafik Matplotlib | ✅ |
| CRUD Inventaris Barang + foto | ✅ |
| CRUD Kategori Barang | ✅ |
| CRUD Data Peminjam | ✅ |
| Sistem Peminjaman + validasi stok | ✅ |
| Sistem Pengembalian + deteksi terlambat | ✅ |
| Activity Log otomatis | ✅ |
| Export CSV & PDF | ✅ |
| Prediksi ML (Linear Regression) | ✅ |
| Dark / Light Mode | ✅ |
| Validasi input lengkap | ✅ |

## 🚀 Cara Menjalankan

```bash
# 1. Install dependencies
pip install PySide6 matplotlib pandas fpdf2 scikit-learn Pillow

# 2. Jalankan aplikasi
cd LabTrack
python main.py
```

## 🔑 Akun Default

| Username | Password    | Role    | Akses |
|----------|-------------|---------|-------|
| admin    | admin123    | Admin   | Full (CRUD + Log) |
| laboran  | laboran123  | Laboran | CRUD (tanpa log) |
| viewer   | viewer123   | Viewer  | Read-only |

## 📁 Struktur Project

```
LabTrack/
├── main.py          # Entry point
├── database.py      # Koneksi & schema SQLite
├── models.py        # Model data per entitas
├── controllers.py   # Business logic & validasi
├── utils.py         # Validasi, export CSV/PDF, prediksi ML
├── styles.py        # QSS stylesheet dark & light theme
├── windows/
│   ├── login_window.py   # Halaman login
│   ├── main_window.py    # Window utama + sidebar
│   ├── base_page.py      # Base class semua halaman
│   ├── dashboard_page.py # Dashboard + charts
│   ├── inventory_page.py # Manajemen barang
│   ├── category_page.py  # Manajemen kategori
│   ├── borrower_page.py  # Manajemen peminjam
│   ├── loan_page.py      # Sistem peminjaman
│   ├── return_page.py    # Sistem pengembalian
│   ├── report_page.py    # Export laporan
│   ├── activity_page.py  # Activity log
│   └── predict_page.py   # Prediksi ML
├── exports/         # Output file CSV
└── reports/         # Output file PDF
```

## 🗄️ Skema Database (SQLite)

- **users** — data akun pengguna
- **categories** — kategori barang
- **items** — inventaris barang
- **borrowers** — data peminjam
- **loans** — transaksi peminjaman
- **loan_details** — detail barang per transaksi
- **activity_logs** — log semua aktivitas

## 🧠 Teknologi

- **PySide6** — GUI framework
- **SQLite** — database relasional
- **Matplotlib** — grafik & visualisasi
- **Scikit-Learn** — prediksi Linear Regression
- **FPDF2** — export PDF
- **Pandas** — export CSV
