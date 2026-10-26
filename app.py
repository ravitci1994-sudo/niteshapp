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
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, index=False, sheet_name=name)
    return buffer_excel.getvalue()


# ================= REPORTED VEHICLE TABLE & REPORTS =================
def show_reported_vehicle_table(df, unique_key="", staff_filter=None):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📄 Reported Vehicle")

    final_rep_col = next(
        (c for c in ['Final Touching Reporting Date & Time', 'Reporting Date & Time', 'Reporting Date', 'Desp. Date & Time'] if c in df.columns),
        None
    )
    if not final_rep_col:
        final_rep_col = next((c for c in df.columns if 'report' in c.lower() or 'desp' in c.lower() or 'date' in c.lower()), None)

    temp_df = df.copy()
    if final_rep_col:
        reported_df = temp_df[~temp_df[final_rep_col].apply(is_blank)].copy()
    else:
        reported_df = temp_df.copy()

    if reported_df.empty:
        st.warning("Selected data khali hai ya koi valid records nahi mile.")
        return

    if final_rep_col:
        parsed_rep_dt = pd.to_datetime(reported_df[final_rep_col], errors='coerce', dayfirst=True)
        reported_df['_Rep_Date_Obj'] = parsed_rep_dt.dt.date
        reported_df['_Rep_Date_Str'] = parsed_rep_dt.dt.strftime('%d-%m-%Y')
        reported_df['_Month_Str'] = parsed_rep_dt.dt.strftime('%B %Y')
    else:
        reported_df['_Rep_Date_Obj'] = None
        reported_df['_Rep_Date_Str'] = "ALL"
        reported_df['_Month_Str'] = "ALL"

    current_dt = datetime.now().date()
    def get_relative_week_label(row_date):
        if pd.isna(row_date) or row_date is None:
            return None
        diff_days = (current_dt - row_date).days
        if diff_days < 0:
            return "Current / Future"
        elif diff_days <= 7:
            return "Last 1 Week"
        elif diff_days <= 14:
            return "Last 2 Weeks"
        elif diff_days <= 21:
            return "Last 3 Weeks"
        elif diff_days <= 28:
            return "Last 4 Weeks"
        else:
            return None

    reported_df['_Rel_Week'] = reported_df['_Rep_Date_Obj'].apply(get_relative_week_label)

    valid_dates = (
        reported_df[reported_df['_Rep_Date_Obj'].notna()]
        .drop_duplicates(subset=['_Rep_Date_Str'])
        .sort_values('_Rep_Date_Obj', ascending=False)
    )
    date_options = ["ALL"] + valid_dates['_Rep_Date_Str'].tolist()

    valid_months = (
        reported_df[reported_df['_Rep_Date_Obj'].notna()]
        .drop_duplicates(subset=['_Month_Str'])
        .sort_values('_Rep_Date_Obj', ascending=False)
    )
    month_options = ["ALL"] + valid_months['_Month_Str'].tolist()

    staff_col = next((c for c in reported_df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
    client_col_name = vendor_column(reported_df) or 'VendorName'

    if staff_filter:
        selected_staff = staff_filter
        st.info(f"🔒 Logged in as Staff View: **{selected_staff}**")
        selected_client_report = "ALL"
        selected_delay_hours = "ALL"
        selected_remarks_filter = "ALL"
        selected_month = "ALL"
        selected_date = "ALL"
        delay_filter = "ALL Reported Vehicles"
        selected_weeks = []
    else:
        f_col1, f_col2, f_col3, f_col4, f_col5, f_col6, f_col7 = st.columns(7)
        with f_col1:
            selected_date = st.selectbox(
                "📅 Filter by Reporting Date:",
                date_options,
                index=0,
                key=f"reported_date_filter_{unique_key}"
            )
        with f_col2:
            selected_month = st.selectbox(
                "🗓️ Filter by Month:",
                month_options,
                index=0,
                key=f"reported_month_filter_{unique_key}"
            )
        with f_col3:
            delay_filter = st.selectbox(
                "🚨 Filter by Delay Status:",
                ["ALL Reported Vehicles", "Only Delay Vehicles", "Only On-Time Vehicles"],
                index=0,
                key=f"reported_delay_filter_{unique_key}"
            )
        with f_col4:
            staff_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"]
            selected_staff = st.selectbox(
                "👨‍💼 Filter by Controlling Staff:",
                staff_list,
                index=0,
                key=f"reported_staff_filter_{unique_key}"
            )
        with f_col5:
            client_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in reported_df.columns else ["ALL"]
            selected_client_report = st.selectbox(
                "🏢 Filter by Client:",
                client_list,
                index=0,
                key=f"reported_client_filter_{unique_key}"
            )
        with f_col6:
            selected_delay_hours = st.selectbox(
                "⏱️ Filter by Delay Hours:",
                ["ALL", "Delay < 10 mins", "Delay < 20 mins", "Delay < 30 mins", "Delay < 40 mins", "Delay <= 1 hour"],
                index=0,
                key=f"reported_delay_hours_filter_{unique_key}"
            )
        with f_col7:
            selected_remarks_filter = st.selectbox(
                "📝 Filter by Remarks:",
                [
                    "ALL", 
                    "With Remarks", 
                    "Without Remarks (Empty)", 
                    "Delay + Without Remarks (Empty)", 
                    "Delay + With Remarks"
                ],
                index=0,
                key=f"reported_remarks_filter_{unique_key}"
            )

        strict_week_options = ["Last 1 Week", "Last 2 Weeks", "Last 3 Weeks", "Last 4 Weeks"]
        available_weeks = [w for w in strict_week_options if w in reported_df['_Rel_Week'].unique()]

        if available_weeks:
            st.markdown("📅 **Filter by Week (Multiple Selection):**")
            chk_cols = st.columns(len(strict_week_options))
            selected_weeks = []
            for i, wk in enumerate(strict_week_options):
                with chk_cols[i]:
                    if st.checkbox(wk, value=False, key=f"chk_rel_week_{unique_key}_{wk}"):
                        selected_weeks.append(wk)
        else:
            selected_weeks = []

    filtered_report_df = reported_df.copy()
    late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in filtered_report_df.columns), None)
    remark_col = next((c for c in ['Tracking Remark', 'Remark', 'Remarks'] if c in filtered_report_df.columns), None)

    if not staff_filter:
        if selected_date != "ALL":
            filtered_report_df = filtered_report_df[filtered_report_df['_Rep_Date_Str'] == selected_date].copy()
        if selected_month != "ALL":
            filtered_report_df = filtered_report_df[filtered_report_df['_Month_Str'] == selected_month].copy()
        if selected_weeks:
            filtered_report_df = filtered_report_df[filtered_report_df['_Rel_Week'].isin(selected_weeks)].copy()
        
        if late_col:
            if delay_filter == "Only Delay Vehicles":
                filtered_report_df = filtered_report_df[~filtered_report_df[late_col].apply(is_zero_late)].copy()
            elif delay_filter == "Only On-Time Vehicles":
                filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(is_zero_late)].copy()

            if selected_delay_hours != "ALL":
                def check_delay_range(val):
                    mins = get_delay_minutes(val)
                    if mins <= 0:
                        return False
                    if selected_delay_hours == "Delay < 10 mins": return mins < 10
                    elif selected_delay_hours == "Delay < 20 mins": return mins < 20
                    elif selected_delay_hours == "Delay < 30 mins": return mins < 30
                    elif selected_delay_hours == "Delay < 40 mins": return mins < 40
                    elif selected_delay_hours == "Delay <= 1 hour": return mins <= 60
                    return False
                filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(check_delay_range)].copy()

        if selected_remarks_filter != "ALL":
            if remark_col:
                valid_indices = []
                for idx, row in filtered_report_df.iterrows():
                    r_val = row.get(remark_col, None)
                    is_empty = is_blank(r_val)
                    is_delayed = not is_zero_late(row.get(late_col, 0)) if late_col else True

                    if selected_remarks_filter == "With Remarks" and not is_empty:
                        valid_indices.append(idx)
                    elif selected_remarks_filter == "Without Remarks (Empty)" and is_empty:
                        valid_indices.append(idx)
                    elif selected_remarks_filter == "Delay + Without Remarks (Empty)" and is_delayed and is_empty:
                        valid_indices.append(idx)
                    elif selected_remarks_filter == "Delay + With Remarks" and is_delayed and not is_
