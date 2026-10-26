import streamlit as st
import pandas as pd
from datetime import datetime
import math
import io
import os
import html as html_lib

# 1. Page Configuration
st.set_page_config(page_title="Sales Manager Live Monitoring Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Dynamic & Attractive Modern Dark Theme Styling
st.markdown("""
    <style>
    .main, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
    }
    .metric-card {
        background: linear-gradient(145deg, #1c2541, #131b2e);
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #48cae4;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 15px;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 25px rgba(72, 202, 228, 0.25);
        border-color: #90e0ef;
    }
    .metric-title {
        font-size: 15px;
        color: #90e0ef;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-bottom: 2px solid rgba(72, 202, 228, 0.3);
        padding-bottom: 6px;
        margin-bottom: 10px;
    }
    .custom-table-container {
        overflow-x: auto;
        max-height: 450px;
        overflow-y: auto;
        border: 1px solid #48cae4;
        border-radius: 12px;
        background-color: #1c2541;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        margin-bottom: 15px;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        color: #ffffff;
        font-size: 13px;
        font-family: Arial, sans-serif;
        white-space: nowrap;
    }
    .custom-table th {
        background: linear-gradient(90deg, #0b132b, #1c2541);
        color: #48cae4;
        padding: 12px 15px;
        text-align: left;
        position: sticky;
        top: 0;
        border-bottom: 3px solid #48cae4;
        font-weight: 800;
        z-index: 1;
    }
    .custom-table td {
        padding: 10px 15px;
        border-bottom: 1px solid #2b3a55;
        color: #e0e6ed;
    }
    .custom-table tr:hover td {
        background-color: #2b3a55;
        color: #90e0ef;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 900 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# ================= CONSTANTS =================
ONTIME = 'On-Time Trip Closed'
DELAY = 'Delay Trip Closed'
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Persistent storage directory
DATA_DIR = "saved_data"
os.makedirs(DATA_DIR, exist_ok=True)
CALLOUT_PATH = os.path.join(DATA_DIR, "callout.pkl")
MIS_PATH = os.path.join(DATA_DIR, "mis.pkl")


# ================= HELPERS =================
def is_blank(v):
    if v is None:
        return True
    try:
        if pd.isna(v):
            return True
    except (TypeError, ValueError):
        pass
    return str(v).strip().lower() in ("", "nan", "nat", "none")


def is_zero_late(v):
    if is_blank(v):
        return True
    s = str(v).strip().lower()
    if s in ("0", "0.0", "00:00", "0:00", "00:00:00", "0:00:00", "0 days 00:00:00"):
        return True
    try:
        return pd.to_timedelta(s) <= pd.Timedelta(0)
    except Exception:
        pass
    try:
        return float(s) <= 0
    except Exception:
        return False


def get_delay_minutes(v):
    if is_blank(v):
        return 0.0
    s = str(v).strip().lower()
    if s in ("0", "0.0", "00:00", "0:00", "00:00:00", "0:00:00", "0 days 00:00:00"):
        return 0.0
    try:
        td = pd.to_timedelta(s)
        return td.total_seconds() / 60.0
    except Exception:
        pass
    try:
        val = float(s)
        return val * 60.0
    except Exception:
        return 0.0


def clean_party(v, keep_other=True):
    if is_blank(v):
        return "Other"
    v_str = str(v).upper().strip()
    if "DHL" in v_str:
        return "DHL"
    elif "BUSYBEE" in v_str:
        return "Busybees"
    elif "TRACKON" in v_str:
        return "Trackon"
    return str(v).strip() if keep_other else "Other"


def vendor_column(df):
    return next((c for c in df.columns if any(k in c.lower() for k in ('vendor', 'party', 'client', 'customer'))), None)


def render_speedometer_html(client_name, rate, ontime, delay, total):
    clamped_rate = max(0.0, min(100.0, float(rate)))
    if clamped_rate >= 80:
        val_color = "#2ec4b6"
    elif clamped_rate >= 50:
        val_color = "#ffb703"
    else:
        val_color = "#e63946"

    cx, cy = 120, 110
    ticks_svg = ""
    for p in range(0, 101, 10):
        rad = math.radians(180 - (p * 1.8))
        r_inner = 62 if p % 20 == 0 else 65
        r_outer = 70
        x1 = cx + r_inner * math.cos(rad)
        y1 = cy - r_inner * math.sin(rad)
        x2 = cx + r_outer * math.cos(rad)
        y2 = cy - r_outer * math.sin(rad)
        stroke_w = "2" if p % 20 == 0 else "1"
        ticks_svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#90e0ef" stroke-width="{stroke_w}"/>'

    labels_svg = ""
    for p in [0, 25, 50, 75, 100]:
        rad = math.radians(180 - (p * 1.8))
        r_lbl = 98
        lx = cx + r_lbl * math.cos(rad)
        ly = cy - r_lbl * math.sin(rad) + 4
        labels_svg += f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#90e0ef" font-size="10" font-weight="bold" text-anchor="middle" font-family="Arial">{p}%</text>'

    n_rad = math.radians(180 - (clamped_rate * 1.8))
    tip_x = cx + 65 * math.cos(n_rad)
    tip_y = cy - 65 * math.sin(n_rad)

    perp_rad = n_rad + (math.pi / 2)
    b1_x = cx + 4.5 * math.cos(perp_rad)
    b1_y = cy - 4.5 * math.sin(perp_rad)
    b2_x = cx - 4.5 * math.cos(perp_rad)
    b2_y = cy + 4.5 * math.sin(perp_rad)
    tail_x = cx - 12 * math.cos(n_rad)
    tail_y = cy + 12 * math.sin(n_rad)

    needle_points = f"{b1_x:.1f},{b1_y:.1f} {tip_x:.1f},{tip_y:.1f} {b2_x:.1f},{b2_y:.1f} {tail_x:.1f},{tail_y:.1f}"
    safe_name = html_lib.escape(str(client_name))

    html_lines = [
        '<div class="metric-card" style="text-align: center; padding: 18px 15px;">',
        f'<div class="metric-title" style="margin-bottom: 8px;">🔥 {safe_name} PERFORMANCE</div>',
        '<svg viewBox="0 0 240 130" width="100%" style="max-width: 260px; margin: 0 auto; display: block;">',
        '<path d="M 40 110 A 80 80 0 0 1 200 110" fill="none" stroke="#0b132b" stroke-width="18" stroke-linecap="round"/>',
        '<path d="M 40 110 A 80 80 0 0 1 120 30" fill="none" stroke="#e63946" stroke-width="14" stroke-linecap="butt"/>',
        '<path d="M 120 30 A 80 80 0 0 1 184.72 62.98" fill="none" stroke="#ffb703" stroke-width="14" stroke-linecap="butt"/>',
        '<path d="M 184.72 62.98 A 80 80 0 0 1 200 110" fill="none" stroke="#2ec4b6" stroke-width="14" stroke-linecap="butt"/>',
        ticks_svg,
        labels_svg,
        f'<polygon points="{needle_points}" fill="#ffffff"/>',
        f'<circle cx="{cx}" cy="{cy}" r="8" fill="#ffffff"/>',
        f'<circle cx="{cx}" cy="{cy}" r="4" fill="#1c2541"/>',
        '</svg>',
        f'<div style="font-size: 34px; font-weight: 900; color: {val_color}; margin-top: 4px; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{rate}%</div>',
        '<div style="font-size: 13px; color: #90e0ef; margin-top: 6px; font-weight: 700;">',
        f'<span style="color:#2ec4b6;">On-Time: <b>{ontime}</b></span> &nbsp;|&nbsp; ',
        f'<span style="color:#e63946;">Delay: <b>{delay}</b></span> &nbsp;|&nbsp; ',
        f'<span style="color:#ffffff;">Total: <b>{total}</b></span>',
        '</div>',
        '</div>'
    ]
    return "".join(html_lines)


def render_html_table(df_to_show, max_rows=2000):
    clean_df = df_to_show.fillna("").astype(str)
    note = ""
    if len(clean_df) > max_rows:
        note = f'<div style="color:#ffb703; font-size:12px; margin-bottom:6px;">Showing first {max_rows} of {len(clean_df)} rows. Full data Excel download me milega.</div>'
        clean_df = clean_df.head(max_rows)
    headers = "".join([f"<th>{html_lib.escape(str(col))}</th>" for col in clean_df.columns])
    rows_html = []
    for _, row in clean_df.iterrows():
        cells = "".join([f"<td>{html_lib.escape('' if val.lower() in ('nan', 'nat') else val)}</td>" for val in row])
        rows_html.append(f"<tr>{cells}</tr>")
    body = "".join(rows_html)
    return f'{note}<div class="custom-table-container"><table class="custom-table"><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table></div>'


def to_excel_bytes(sheets):
    buffer_excel = io.
