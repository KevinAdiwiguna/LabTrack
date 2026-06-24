"""
styles.py - Stylesheet QSS untuk LabTrack (Dark & Light Theme)
"""

DARK_THEME = """
/* ─── Global ─────────────────────────────────────── */
QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QMainWindow { background-color: #0f172a; }

/* ─── Sidebar ────────────────────────────────────── */
#sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
    min-width: 220px;
    max-width: 220px;
}
#sidebar_logo {
    color: #38bdf8;
    font-size: 20px;
    font-weight: bold;
    padding: 20px 16px 10px 16px;
}
#sidebar_subtitle {
    color: #64748b;
    font-size: 11px;
    padding: 0 16px 16px 16px;
}
QPushButton#nav_btn {
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #94a3b8;
    text-align: left;
    padding: 10px 16px;
    font-size: 13px;
    margin: 1px 8px;
}
QPushButton#nav_btn:hover {
    background-color: #334155;
    color: #e2e8f0;
}
QPushButton#nav_btn[active=true] {
    background-color: #0369a1;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#nav_btn[active=true]:hover {
    background-color: #0284c7;
}
#user_badge {
    background: #334155;
    border-radius: 8px;
    padding: 10px;
    margin: 8px;
}

/* ─── Content Area ───────────────────────────────── */
#content_area { background: #0f172a; }
#page_title {
    font-size: 22px;
    font-weight: bold;
    color: #f1f5f9;
    padding: 4px 0;
}
#page_subtitle { color: #64748b; font-size: 12px; }

/* ─── Cards ──────────────────────────────────────── */
QFrame#stat_card {
    background: #1e293b;
    border-radius: 12px;
    border: 1px solid #334155;
    padding: 16px;
}
QFrame#stat_card:hover { border: 1px solid #0ea5e9; }
#card_value {
    font-size: 32px;
    font-weight: bold;
    color: #38bdf8;
}
#card_label {
    color: #94a3b8;
    font-size: 12px;
}
#card_icon { font-size: 28px; }

/* ─── Buttons ────────────────────────────────────── */
QPushButton#btn_primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #0369a1, stop:1 #0891b2);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton#btn_primary:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #0284c7, stop:1 #06b6d4);
}
QPushButton#btn_primary:pressed { background: #075985; }

QPushButton#btn_danger {
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton#btn_danger:hover { background: #ef4444; }

QPushButton#btn_success {
    background: #16a34a;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton#btn_success:hover { background: #22c55e; }

QPushButton#btn_secondary {
    background: #334155;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 8px 18px;
}
QPushButton#btn_secondary:hover { background: #475569; }

QPushButton#btn_icon {
    background: #334155;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 5px 10px;
    color: #94a3b8;
    min-width: 32px;
}
QPushButton#btn_icon:hover { background: #475569; color: #e2e8f0; }

/* ─── Input Fields ───────────────────────────────── */
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e2e8f0;
    selection-background-color: #0369a1;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDateEdit:focus {
    border: 1px solid #0ea5e9;
    background: #1e3a5f;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background: #1e293b;
    border: 1px solid #334155;
    selection-background-color: #0369a1;
    color: #e2e8f0;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: #334155;
    border: none;
    width: 20px;
}
QDateEdit::drop-down { border: none; }
QCalendarWidget { background: #1e293b; color: #e2e8f0; }

/* ─── Table ──────────────────────────────────────── */
QTableWidget {
    background: #1e293b;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 8px;
    selection-background-color: #0c4a6e;
    alternate-background-color: #162032;
}
QTableWidget::item { padding: 6px 8px; border: none; }
QTableWidget::item:selected { background: #0c4a6e; color: #e2e8f0; }
QHeaderView::section {
    background: #0f172a;
    color: #94a3b8;
    border: none;
    border-bottom: 1px solid #334155;
    padding: 8px;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}

/* ─── Tabs ───────────────────────────────────────── */
QTabWidget::pane { border: 1px solid #334155; border-radius: 8px; }
QTabBar::tab {
    background: #1e293b;
    color: #94a3b8;
    border: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
}
QTabBar::tab:selected { background: #0369a1; color: white; }
QTabBar::tab:hover { background: #334155; }

/* ─── ScrollBar ──────────────────────────────────── */
QScrollBar:vertical {
    background: #1e293b;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #475569;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #64748b; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ─── Dialog ─────────────────────────────────────── */
QDialog {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}
QDialog QLabel { color: #e2e8f0; }

/* ─── GroupBox ───────────────────────────────────── */
QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    color: #94a3b8;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #38bdf8;
}

/* ─── Label ──────────────────────────────────────── */
QLabel { color: #e2e8f0; }
QLabel#label_muted { color: #64748b; font-size: 12px; }
QLabel#badge_danger {
    background: #dc2626;
    color: white;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: bold;
}
QLabel#badge_success {
    background: #16a34a;
    color: white;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
}
QLabel#badge_warning {
    background: #d97706;
    color: white;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
}

/* ─── Separator / divider ────────────────────────── */
QFrame#divider {
    background: #334155;
    max-height: 1px;
}

/* ─── MessageBox ─────────────────────────────────── */
QMessageBox { background: #1e293b; }
QMessageBox QLabel { color: #e2e8f0; }
QMessageBox QPushButton {
    background: #0369a1;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 70px;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QMainWindow { background-color: #f1f5f9; }
#sidebar {
    background-color: #1e3a5f;
    border-right: 1px solid #1e40af;
    min-width: 220px;
    max-width: 220px;
}
#sidebar_logo { color: #38bdf8; font-size: 20px; font-weight: bold; padding: 20px 16px 10px 16px; }
#sidebar_subtitle { color: #93c5fd; font-size: 11px; padding: 0 16px 16px 16px; }
QPushButton#nav_btn {
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #bfdbfe;
    text-align: left;
    padding: 10px 16px;
    font-size: 13px;
    margin: 1px 8px;
}
QPushButton#nav_btn:hover { background-color: #1e40af; color: #ffffff; }
QPushButton#nav_btn[active=true] { background-color: #0ea5e9; color: #ffffff; font-weight: bold; }
#user_badge { background: #1e40af; border-radius: 8px; padding: 10px; margin: 8px; }
#content_area { background: #f1f5f9; }
#page_title { font-size: 22px; font-weight: bold; color: #1e293b; }
#page_subtitle { color: #94a3b8; font-size: 12px; }
QFrame#stat_card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 16px;
}
QFrame#stat_card:hover { border: 1px solid #0ea5e9; }
#card_value { font-size: 32px; font-weight: bold; color: #0369a1; }
#card_label { color: #64748b; font-size: 12px; }
QPushButton#btn_primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0369a1,stop:1 #0891b2);
    color: white; border: none; border-radius: 8px; padding: 8px 18px; font-weight: bold;
}
QPushButton#btn_primary:hover { background: #0284c7; }
QPushButton#btn_danger { background: #dc2626; color: white; border: none; border-radius: 8px; padding: 8px 18px; font-weight: bold; }
QPushButton#btn_success { background: #16a34a; color: white; border: none; border-radius: 8px; padding: 8px 18px; font-weight: bold; }
QPushButton#btn_secondary { background: #e2e8f0; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 18px; }
QPushButton#btn_icon { background: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 6px; padding: 5px 10px; color: #64748b; min-width: 32px; }
QPushButton#btn_icon:hover { background: #cbd5e1; }
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {
    background: white; border: 1px solid #cbd5e1; border-radius: 8px;
    padding: 8px 12px; color: #1e293b; selection-background-color: #0369a1;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus { border: 1px solid #0ea5e9; }
QComboBox QAbstractItemView { background: white; border: 1px solid #cbd5e1; selection-background-color: #0369a1; color: #1e293b; }
QTableWidget { background: white; gridline-color: #e2e8f0; border: 1px solid #e2e8f0; border-radius: 8px; alternate-background-color: #f8fafc; }
QTableWidget::item { padding: 6px 8px; }
QTableWidget::item:selected { background: #dbeafe; color: #1e293b; }
QHeaderView::section { background: #f1f5f9; color: #64748b; border: none; border-bottom: 1px solid #e2e8f0; padding: 8px; font-weight: bold; font-size: 12px; }
QScrollBar:vertical { background: #f1f5f9; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 20px; }
QGroupBox { border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 12px; padding-top: 8px; color: #64748b; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #0369a1; }
QLabel { color: #1e293b; }
QDialog { background: white; }
QMessageBox { background: white; }
QMessageBox QPushButton { background: #0369a1; color: white; border: none; border-radius: 6px; padding: 6px 16px; min-width: 70px; }
QFrame#divider { background: #e2e8f0; max-height: 1px; }
"""
