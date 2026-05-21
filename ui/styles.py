"""Color constants and stylesheets for the dark-theme TODO app."""

# ── Priority dot colors ──────────────────────────────────
PRIORITY_COLORS = {
    "urgent_important":         "#E74C3C",  # red
    "urgent_not_important":     "#3498DB",  # blue
    "not_urgent_important":     "#F39C12",  # orange
    "not_urgent_not_important": "#27AE60",  # green
}

PRIORITY_LABELS = {
    "urgent_important":         "紧急且重要",
    "urgent_not_important":     "紧急但不重要",
    "not_urgent_important":     "不紧急但重要",
    "not_urgent_not_important": "不紧急且不重要",
}

PERIOD_LABELS = {
    "daily":   "每日",
    "weekly":  "每周",
    "monthly": "每月",
}

# ── Theme colors ─────────────────────────────────────────
BG_DARK      = "#1E1E1E"
BG_CARD      = "#1A1A1A"
BG_TAB_BAR   = "#252525"
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#888888"
ACCENT_BLUE  = "#0078D4"
BTN_GREEN    = "#27AE60"
BTN_RED      = "#E74C3C"
BTN_GRAY     = "#555555"
BORDER_CARD  = "#2A2A2A"

# ── Dimensions ───────────────────────────────────────────
CARD_RADIUS = 12
DOT_SIZE    = 12
BTN_SIZE    = 28
WIN_WIDTH   = 900
WIN_HEIGHT  = 650
WIN_MIN_W   = 700
WIN_MIN_H   = 500

# ── Global stylesheet ────────────────────────────────────
GLOBAL_STYLE = f"""
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 14px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: {BG_DARK};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #444;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QComboBox {{
    background: #2B2B2B;
    border: 1px solid #3A3A3A;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 20px;
}}
QComboBox:hover {{
    border-color: #555;
}}
QComboBox QAbstractItemView {{
    background: #2B2B2B;
    border: 1px solid #3A3A3A;
    selection-background-color: {ACCENT_BLUE};
}}

QTextEdit {{
    background: #2B2B2B;
    border: 1px solid #3A3A3A;
    border-radius: 6px;
    padding: 8px;
}}
QTextEdit:focus {{
    border-color: {ACCENT_BLUE};
}}

QPushButton {{
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
}}
"""
