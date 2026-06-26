import os, re, csv
from datetime import datetime, date

# ── Validasi ─────────────────────────────────────────────────────

def validate_nim(nim: str) -> tuple[bool, str]:
    if not nim.strip():
        return False, "NIM tidak boleh kosong"
    if not nim.isdigit():
        return False, "NIM hanya boleh berisi angka"
    if len(nim) < 5 or len(nim) > 15:
        return False, "NIM harus 5-15 digit"
    return True, ""

def validate_stock(stock_str: str) -> tuple[bool, str]:
    try:
        val = int(stock_str)
        if val < 0:
            return False, "Stok tidak boleh negatif"
        return True, ""
    except ValueError:
        return False, "Stok harus berupa angka bulat"

def validate_quantity(qty_str: str, available_stock: int) -> tuple[bool, str]:
    try:
        qty = int(qty_str)
        if qty <= 0:
            return False, "Quantity harus lebih dari 0"
        if qty > available_stock:
            return False, f"Quantity ({qty}) melebihi stok tersedia ({available_stock})"
        return True, ""
    except ValueError:
        return False, "Quantity harus berupa angka"

def validate_dates(loan_date: str, due_date: str) -> tuple[bool, str]:
    try:
        ld = datetime.strptime(loan_date, "%Y-%m-%d").date()
        dd = datetime.strptime(due_date, "%Y-%m-%d").date()
        if dd < ld:
            return False, "Deadline tidak boleh sebelum tanggal pinjam"
        return True, ""
    except ValueError:
        return False, "Format tanggal tidak valid (YYYY-MM-DD)"

def validate_required(fields: dict) -> tuple[bool, str]:
    """fields = {'Nama Field': 'nilai', ...}"""
    for label, val in fields.items():
        if not str(val).strip():
            return False, f"Field '{label}' tidak boleh kosong"
    return True, ""

def validate_email(email: str) -> tuple[bool, str]:
    if not email:
        return True, ""
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    if not re.match(pattern, email):
        return False, "Format email tidak valid"
    return True, ""


# ── Export CSV ───────────────────────────────────────────────────

def export_csv(data: list, filename: str, headers: list = None) -> str:
    """Export data ke file CSV. Kembalikan path file."""
    os.makedirs("exports", exist_ok=True)
    path = os.path.join("exports", filename)
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        if not data:
            f.write("Tidak ada data\n")
            return path
        writer = csv.DictWriter(f, fieldnames=headers or list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    return path


# ── Export PDF ───────────────────────────────────────────────────

def export_pdf(title: str, data: list, filename: str, headers: list = None, col_widths: list = None) -> str:
    from fpdf import FPDF
    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Dicetak: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(4)

    if not data:
        pdf.cell(0, 10, "Tidak ada data", ln=True)
        pdf.output(path)
        return path

    keys = headers or list(data[0].keys())
    widths = col_widths or [max(15, int(180/len(keys)))] * len(keys)

    # Header tabel
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for i, h in enumerate(keys):
        pdf.cell(widths[i], 8, str(h).upper(), border=1, fill=True, align="C")
    pdf.ln()

    # Baris data
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    for idx, row in enumerate(data):
        fill = idx % 2 == 0
        pdf.set_fill_color(240, 248, 255) if fill else pdf.set_fill_color(255,255,255)
        for i, k in enumerate(keys):
            val = str(row.get(k, ""))[:30]
            pdf.cell(widths[i], 7, val, border=1, fill=fill)
        pdf.ln()

    pdf.output(path)
    return path


# ── Prediksi ML ──────────────────────────────────────────────────

def predict_next_month_demand():
    """
    Prediksi jumlah peminjaman bulan depan menggunakan Linear Regression.
    Kembalikan dict {item_name: predicted_count}
    """
    try:
        import numpy as np
        from sklearn.linear_model import LinearRegression
        import database.database as db

        rows = db.fetchall("""
            SELECT i.name as item_name,
                   strftime('%Y-%m', l.loan_date) as month,
                   SUM(ld.quantity) as total
            FROM loan_details ld
            JOIN loans l ON ld.loan_id = l.id
            JOIN items i ON ld.item_id = i.id
            GROUP BY i.id, month
            ORDER BY i.id, month
        """)

        if not rows:
            return {}

        from collections import defaultdict
        item_history = defaultdict(dict)
        months_set = set()
        for r in rows:
            item_history[r['item_name']][r['month']] = r['total']
            months_set.add(r['month'])

        months = sorted(months_set)
        month_idx = {m: i for i, m in enumerate(months)}

        predictions = {}
        next_x = len(months)

        for item_name, monthly in item_history.items():
            X = np.array([[month_idx[m]] for m in monthly])
            y = np.array([monthly[m] for m in monthly])
            if len(X) < 2:
                predictions[item_name] = int(y[0])
                continue
            model = LinearRegression()
            model.fit(X, y)
            pred = model.predict([[next_x]])[0]
            predictions[item_name] = max(0, round(pred))

        return dict(sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:10])

    except Exception as e:
        print(f"[Prediksi] Error: {e}")
        return {}


# ── Format helpers ────────────────────────────────────────────────

def format_date(date_str: str, fmt_in="%Y-%m-%d", fmt_out="%d %b %Y") -> str:
    if not date_str:
        return "-"
    try:
        return datetime.strptime(date_str, fmt_in).strftime(fmt_out)
    except:
        return date_str

def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")

def is_overdue(due_date_str: str) -> bool:
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return date.today() > due
    except:
        return False
