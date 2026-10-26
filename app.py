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
REQUIRED_COLUMNS = [
    'Lorry No.', 'Veh.Type', 'From', 'Destination', 'KM', 'Party', 'Desp. Date & Time',
    'Hrs. Given', '1st Touching', '1st Touching Reporting Date & Time', '1st Touching Delivery Date & Time', '1st Touching Hrs.',
    '2nd Touching', '2nd Touching Reporting Date & Time', '2nd Touching Delivery Date & Time', '2nd Touching Hrs', '2nd Touching Hrs.',
    'Final Touching Reporting Date & Time', 'Final Touching Delivery Date & Time',
    'Total Touching Hrs.', 'Hrs. Taken with touching', 'Hrs. Taken without touching (Dly.)',
    'Late Hrs', 'Tracking Remark', 'Group Name', 'Controlling Staff Name', 'Foreman Name'
]
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


def find_col(df, exact=None, contains=None):
    if exact:
        for c in df.columns:
            if c.lower().strip() in exact:
                return c
    if contains:
        for c in df.columns:
            if any(k in c.lower() for k in contains):
                return c
    return None


def get_lorry_col(df):
    if 'Lorry No.' in df.columns:
        return 'Lorry No.'
    return find_col(df, exact=('lorry no.', 'lorry no', 'vehicle no.', 'vehicle no'), contains=('lorry no', 'vehicle no'))


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
        (c for c in ['Final Touching Reporting Date & Time', 'Reporting Date & Time', 'Reporting Date'] if c in df.columns),
        None
    )
    if not final_rep_col:
        final_rep_col = next((c for c in df.columns if 'final touching' in c.lower() and 'report' in c.lower()), None)

    if not final_rep_col:
        st.warning("Data mein 'Final Touching Reporting Date & Time' column nahi mila.")
        return

    temp_df = df.copy()
    reported_df = temp_df[~temp_df[final_rep_col].apply(is_blank)].copy()

    if reported_df.empty:
        st.warning("Selected data mein kisi bhi gaadi ke aage 'Final Touching Reporting Date & Time' mention nahi hai.")
        return

    parsed_rep_dt = pd.to_datetime(reported_df[final_rep_col], errors='coerce', dayfirst=True)
    reported_df['_Rep_Date_Obj'] = parsed_rep_dt.dt.date
    reported_df['_Rep_Date_Str'] = parsed_rep_dt.dt.strftime('%d-%m-%Y')

    current_dt = datetime.now().date()
    def get_relative_week_label(row_date):
        if pd.isna(row_date):
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
            w_num = (diff_days // 7) + 1
            return f"Last {w_num} Weeks"

    reported_df['_Rel_Week'] = reported_df['_Rep_Date_Obj'].apply(get_relative_week_label)

    valid_dates = (
        reported_df[reported_df['_Rep_Date_Obj'].notna()]
        .drop_duplicates(subset=['_Rep_Date_Str'])
        .sort_values('_Rep_Date_Obj', ascending=False)
    )
    date_options = ["ALL"] + valid_dates['_Rep_Date_Str'].tolist()

    staff_col = next((c for c in reported_df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
    client_col_name = vendor_column(reported_df) or 'VendorName'

    if staff_filter:
        selected_staff = staff_filter
        st.info(f"🔒 Logged in as Staff View: **{selected_staff}**")
        selected_client_report = "ALL"
        selected_delay_hours = "ALL"
    else:
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
        with f_col1:
            selected_date = st.selectbox(
                "📅 Filter by Reporting Date:",
                date_options,
                index=0,
                key=f"reported_date_filter_{unique_key}"
            )
        with f_col2:
            delay_filter = st.selectbox(
                "🚨 Filter by Delay Status:",
                ["ALL Reported Vehicles", "Only Delay Vehicles", "Only On-Time Vehicles"],
                index=0,
                key=f"reported_delay_filter_{unique_key}"
            )
        with f_col3:
            if staff_col:
                staff_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""])
            else:
                staff_list = ["ALL"]
            selected_staff = st.selectbox(
                "👨‍💼 Filter by Controlling Staff:",
                staff_list,
                index=0,
                key=f"reported_staff_filter_{unique_key}"
            )
        with f_col4:
            if client_col_name in reported_df.columns:
                client_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[client_col_name].dropna().unique() if str(x).strip() != ""])
            else:
                client_list = ["ALL"]
            selected_client_report = st.selectbox(
                "🏢 Filter by Client:",
                client_list,
                index=0,
                key=f"reported_client_filter_{unique_key}"
            )
        with f_col5:
            selected_delay_hours = st.selectbox(
                "⏱️ Filter by Delay Hours:",
                ["ALL", "Delay < 10 mins", "Delay < 20 mins", "Delay < 30 mins", "Delay < 40 mins", "Delay <= 1 hour"],
                index=0,
                key=f"reported_delay_hours_filter_{unique_key}"
            )

        st.markdown("📅 **Filter by Week (Multiple Selection):**")
        standard_weeks = ["Last 1 Week", "Last 2 Weeks", "Last 3 Weeks", "Last 4 Weeks"]
        available_weeks = [w for w in standard_weeks if w in reported_df['_Rel_Week'].unique()]
        other_weeks = sorted([w for w in reported_df['_Rel_Week'].unique() if w not in standard_weeks and w is not None])
        all_week_options = available_weeks + other_weeks

        if all_week_options:
            chk_cols = st.columns(min(len(all_week_options), 6))
            selected_weeks = []
            for i, wk in enumerate(all_week_options):
                with chk_cols[i % len(chk_cols)]:
                    if st.checkbox(wk, value=False, key=f"chk_rel_week_{unique_key}_{wk}"):
                        selected_weeks.append(wk)
        else:
            selected_weeks = []

    filtered_report_df = reported_df.copy()
    late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in filtered_report_df.columns), None)

    if not staff_filter:
        if selected_date != "ALL":
            filtered_report_df = filtered_report_df[filtered_report_df['_Rep_Date_Str'] == selected_date].copy()
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
                    if selected_delay_hours == "Delay < 10 mins":
                        return mins < 10
                    elif selected_delay_hours == "Delay < 20 mins":
                        return mins < 20
                    elif selected_delay_hours == "Delay < 30 mins":
                        return mins < 30
                    elif selected_delay_hours == "Delay < 40 mins":
                        return mins < 40
                    elif selected_delay_hours == "Delay <= 1 hour":
                        return mins <= 60
                    return False
                filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(check_delay_range)].copy()

        if selected_staff != "ALL" and staff_col:
            filtered_report_df = filtered_report_df[filtered_report_df[staff_col].astype(str).str.strip() == selected_staff].copy()
        if selected_client_report != "ALL" and client_col_name in filtered_report_df.columns:
            filtered_report_df = filtered_report_df[filtered_report_df[client_col_name].astype(str).str.strip() == selected_client_report].copy()
    else:
        if staff_col:
            filtered_report_df = filtered_report_df[filtered_report_df[staff_col].astype(str).str.strip() == staff_filter].copy()

    if filtered_report_df.empty:
        st.info(f"Selected filter ke liye koi Reported Vehicle data nahi mila.")
        return

    requested_cols = [
        'Lorry No.', 'Veh.Type', 'From', 'Destination', 'Party', 'Desp. Date & Time',
        'Hrs. Given', '1st Touching', '1st Touching Reporting Date & Time', 
        '1st Touching Delivery Date & Time', '1st Touching Hrs.', '2nd Touching', 
        '2nd Touching Reporting Date & Time', '2nd Touching Delivery Date & Time', 
        '2nd Touching Hrs', '2nd Touching Hrs.', 'Final Touching Reporting Date & Time', 
        'Total Touching Hrs.', 'Hrs. Taken with touching', 'Hrs. Taken without touching (Dly.)', 
        'Late Hrs', 'Tracking Remark', 'Controlling Staff Name', 'Foreman Name', 'Remarks'
    ]

    actual_cols = []
    rename_dict = {}
    remark_src_col = next((c for c in ['Tracking Remark', 'Remark', 'Remarks'] if c in filtered_report_df.columns), None)

    for req_col in requested_cols:
        if req_col == 'Remarks':
            if remark_src_col and remark_src_col not in actual_cols:
                actual_cols.append(remark_src_col)
                rename_dict[remark_src_col] = 'Remarks'
        elif req_col in filtered_report_df.columns and req_col not in actual_cols:
            actual_cols.append(req_col)
        elif req_col == 'Party' and 'Party' not in filtered_report_df.columns:
            vendor_c = vendor_column(filtered_report_df) or 'VendorName'
            if vendor_c in filtered_report_df.columns and vendor_c not in actual_cols:
                actual_cols.append(vendor_c)
                rename_dict[vendor_c] = 'Party'

    if not actual_cols:
        actual_cols = [c for c in filtered_report_df.columns if not c.startswith('_') and c not in ['Parsed_Date', 'VendorName', 'Status_Category', 'MonthKey']]

    final_report_df = filtered_report_df[actual_cols].copy()
    final_report_df.rename(columns=rename_dict, inplace=True)
    final_report_df.insert(0, 'S.No', range(1, 1 + len(final_report_df)))

    st.markdown(render_html_table(final_report_df), unsafe_allow_html=True)

    file_date_str = "All_Dates" if (staff_filter or selected_date == "ALL") else selected_date.replace('-', '_')
    status_tag = "All" if staff_filter else ("Delay_Only" if delay_filter == "Only Delay Vehicles" else ("OnTime_Only" if delay_filter == "Only On-Time Vehicles" else "All"))
    staff_tag = f"_Staff_{selected_staff.replace(' ', '_')}" if (not staff_filter and selected_staff != "ALL") else (f"_Staff_{staff_filter.replace(' ', '_')}" if staff_filter else "")
    client_tag = f"_Client_{selected_client_report.replace(' ', '_')}" if (not staff_filter and selected_client_report != "ALL") else ""
    
    excel_bytes_reported = to_excel_bytes({'Reported_Vehicles': final_report_df})
    filename_reported = f"Reported_Vehicles_{file_date_str}_{status_tag}{staff_tag}{client_tag}.xlsx"

    st.download_button(
        label=f"📥 Download Reported Vehicles Excel",
        data=excel_bytes_reported,
        file_name=filename_reported,
        mime=EXCEL_MIME,
        type="primary",
        key=f"download_reported_{unique_key}"
    )

    if staff_filter:
        return

    # ================= 1. OVERALL TRIP CLOSED DATA (CLIENT-WISE SPEEDOMETER) =================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📊 Overall Trip Closed Data (Client-wise)")
    
    if client_col_name in reported_df.columns and late_col:
        temp_stat_df = reported_df.copy()
        temp_stat_df['Is_OnTime'] = temp_stat_df[late_col].apply(is_zero_late)
        temp_stat_df['Is_Delay'] = ~temp_stat_df[late_col].apply(is_zero_late)
        
        client_groups = temp_stat_df.groupby(client_col_name).agg(
            Total=('Is_OnTime', 'count'),
            OnTime=('Is_OnTime', 'sum'),
            Delay=('Is_Delay', 'sum')
        ).reset_index()
        
        cols = st.columns(min(len(client_groups), 4) if not client_groups.empty else 1)
        for idx, row in client_groups.iterrows():
            c_name = row[client_col_name]
            tot = int(row['Total'])
            ot = int(row['OnTime'])
            dl = int(row['Delay'])
            rate = round((ot / tot) * 100, 1) if tot > 0 else 0.0
            
            with cols[idx % len(cols)]:
                st.markdown(render_speedometer_html(c_name, rate, ot, dl, tot), unsafe_allow_html=True)
    else:
        st.info("Client-wise summary ke liye required columns nahi mile.")

    # ================= 2. ROUTE-WISE PERFORMANCE REPORT SECTION =================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📍 Route-wise Performance Report")

    route_client_options = ["ALL"] + sorted([str(x).strip() for x in reported_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in reported_df.columns else ["ALL"]
    route_staff_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"]

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        route_client_selected = st.selectbox(
            "🏢 Filter Route-wise by Client:",
            route_client_options,
            index=0,
            key=f"route_client_filter_{unique_key}"
        )
    with r_col2:
        route_staff_selected = st.selectbox(
            "👨‍💼 Filter Route-wise by Controlling Staff:",
            route_staff_list,
            index=0,
            key=f"route_staff_filter_{unique_key}"
        )

    route_base_df = reported_df.copy()
    if route_client_selected != "ALL" and client_col_name in route_base_df.columns:
        route_base_df = route_base_df[route_base_df[client_col_name].astype(str).str.strip() == route_client_selected].copy()
    if route_staff_selected != "ALL" and staff_col:
        route_base_df = route_base_df[route_base_df[staff_col].astype(str).str.strip() == route_staff_selected].copy()

    from_c = find_col(route_base_df, exact=('from',))
    dest_c = find_col(route_base_df, exact=('destination', 'to'))
    client_c = 'Party' if 'Party' in final_report_df.columns else client_col_name

    if from_c and dest_c:
        route_base_df['Route'] = route_base_df[from_c].astype(str).str.upper().str.strip() + " ➔ " + route_base_df[dest_c].astype(str).str.upper().str.strip()
    else:
        route_base_df['Route'] = "N/A"

    if 'Status_Category' not in route_base_df.columns and late_col:
        route_base_df['Status_Category'] = route_base_df[late_col].apply(lambda v: DELAY if not is_zero_late(v) else ONTIME)

    route_summary = []
    if not route_base_df.empty:
        group_keys = ['Route']
        if client_c and client_c in route_base_df.columns:
            group_keys.append(client_c)

        grouped = route_base_df.groupby(group_keys)
        for name, g_df in grouped:
            if isinstance(name, tuple):
                route, client = name
            else:
                route, client = name, "ALL"

            total = len(g_df)
            ontime = int((g_df['Status_Category'] == ONTIME).sum()) if 'Status_Category' in g_df.columns else total
            delay = int((g_df['Status_Category'] == DELAY).sum()) if 'Status_Category' in g_df.columns else 0
            perf_pct = f"{round((ontime / total) * 100, 1)}%" if total > 0 else "0%"

            route_summary.append({
                "Route": route,
                "Client": client,
                "Total Trips": total,
                "On-Time Trips": ontime,
                "Delay Trips": delay,
                "Performance (%)": perf_pct
            })

    if route_summary:
        route_df = pd.DataFrame(route_summary).sort_values(by="Total Trips", ascending=False)
        route_df.insert(0, 'S.No', range(1, 1 + len(route_df)))
        st.markdown(render_html_table(route_df), unsafe_allow_html=True)

        route_client_tag = f"_Client_{route_client_selected.replace(' ', '_')}" if route_client_selected != "ALL" else ""
        route_staff_tag = f"_Staff_{route_staff_selected.replace(' ', '_')}" if route_staff_selected != "ALL" else ""
        excel_bytes_route = to_excel_bytes({'Route_Performance': route_df})
        filename_route = f"Route_Performance{route_client_tag}{route_staff_tag}.xlsx"

        st.download_button(
            label="📥 Download Route-wise Performance Excel",
            data=excel_bytes_route,
            file_name=filename_route,
            mime=EXCEL_MIME,
            type="secondary",
            key=f"download_route_perf_{unique_key}"
        )
    else:
        st.info("Route-wise performance ke liye koi data available nahi hai.")

    # ================= 3. VEHICLE-WISE PERFORMANCE REPORT SECTION =================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 🚛 Vehicle-wise Performance Report")

    veh_staff_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"]
    veh_client_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in reported_df.columns else ["ALL"]

    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        selected_veh_client = st.selectbox(
            "🏢 Filter Vehicle-wise by Client:",
            veh_client_list,
            index=0,
            key=f"veh_client_filter_{unique_key}"
        )
    with v_col2:
        selected_veh_staff = st.selectbox(
            "👨‍💼 Filter Vehicle-wise by Controlling Staff:",
            veh_staff_list,
            index=0,
            key=f"veh_staff_filter_{unique_key}"
        )
    with v_col3:
        freq_filter_option = st.selectbox(
            "🚨 Filter by Delay Frequency:",
            ["ALL", "Delay > 1 time", "Delay > 2 times", "Delay > 3 times", "Delay > 4 times", "Delay > 5 times"],
            index=0,
            key=f"veh_freq_filter_{unique_key}"
        )
    with v_col4:
        status_filter_option = st.selectbox(
            "🚦 Filter by Status:",
            ["ALL", "Only On-Time Vehicles", "Only Delay Vehicles"],
            index=0,
            key=f"veh_status_filter_{unique_key}"
        )

    base_veh_df = reported_df.copy()
    if selected_veh_staff != "ALL" and staff_col:
        base_veh_df = base_veh_df[base_veh_df[staff_col].astype(str).str.strip() == selected_veh_staff].copy()
    if selected_veh_client != "ALL" and client_col_name in base_veh_df.columns:
        base_veh_df = base_veh_df[base_veh_df[client_col_name].astype(str).str.upper().str.contains(selected_veh_client.upper(), na=False)].copy()

    if not base_veh_df.empty and late_col:
        lorry_c = get_lorry_col(base_veh_df) or 'Lorry No.'
        if lorry_c in base_veh_df.columns:
            base_veh_df[lorry_c] = base_veh_df[lorry_c].astype(str).str.strip()
            mask = (base_veh_df[lorry_c] != "") & (base_veh_df[lorry_c].str.upper() != "NAN") & ~base_veh_df[lorry_c].str.upper().str.contains('TBC|TBA|DUMMY', na=False)
            base_veh_df = base_veh_df[mask].copy()

        if from_c and dest_c:
            base_veh_df['Route'] = base_veh_df[from_c].astype(str).str.upper().str.strip() + " ➔ " + base_veh_df[dest_c].astype(str).str.upper().str.strip()
        else:
            base_veh_df['Route'] = "N/A"

        base_veh_df['Is_Delay'] = ~base_veh_df[late_col].apply(is_zero_late)
        base_veh_df['Is_OnTime'] = base_veh_df[late_col].apply(is_zero_late)

        agg_df = base_veh_df.groupby(lorry_c).agg(
            Total_Trips=(lorry_c, 'count'),
            Delay_Trips=('Is_Delay', 'sum'),
            OnTime_Trips=('Is_OnTime', 'sum')
        ).reset_index()

        if status_filter_option == "Only Delay Vehicles":
            agg_df = agg_df[agg_df['Delay_Trips'] > 0]
        elif status_filter_option == "Only On-Time Vehicles":
            agg_df = agg_df[(agg_df['Delay_Trips'] == 0) & (agg_df['OnTime_Trips'] > 0)]

        if freq_filter_option == "Delay > 1 time":
            agg_df = agg_df[agg_df['Delay_Trips'] > 1]
        elif freq_filter_option == "Delay > 2 times":
            agg_df = agg_df[agg_df['Delay_Trips'] > 2]
        elif freq_filter_option == "Delay > 3 times":
            agg_df = agg_df[agg_df['Delay_Trips'] > 3]
        elif freq_filter_option == "Delay > 4 times":
            agg_df = agg_df[agg_df['Delay_Trips'] > 4]
        elif freq_filter_option == "Delay > 5 times":
            agg_df = agg_df[agg_df['Delay_Trips'] > 5]

        if agg_df.empty:
            st.info(f"Selected filter ke liye koi vehicle data nahi mila.")
            return

        merged_veh_df = base_veh_df.drop_duplicates(subset=[lorry_c], keep='last').merge(agg_df, on=lorry_c, how='inner')

        veh_type_c = next((c for c in merged_veh_df.columns if 'veh' in c.lower() and 'type' in c.lower()), None)
        staff_name_c = staff_col if staff_col else None

        veh_table_data = []
        for _, r_row in merged_veh_df.iterrows():
            d_item = {}
            d_item['Lorry No.'] = r_row.get(lorry_c, '')
            if veh_type_c:
                d_item['Veh.Type'] = r_row.get(veh_type_c, '')
            d_item['Route'] = r_row.get('Route', 'N/A')
            d_item['Client'] = r_row.get(client_col_name, 'N/A')
            d_item['On-Time Trips'] = int(r_row.get('OnTime_Trips', 0))
            d_item['Delay Trips'] = int(r_row.get('Delay_Trips', 0))
            d_item['Total Trips'] = int(r_row.get('Total_Trips', 0))
            perf_pct_veh = f"{round((d_item['On-Time Trips'] / d_item['Total Trips']) * 100, 1)}%" if d_item['Total Trips'] > 0 else "0%"
            d_item['Performance (%)'] = perf_pct_veh
            if staff_name_c:
                d_item['Controlling Staff'] = r_row.get(staff_name_c, '')
            if remark_src_col:
                d_item['Remarks'] = r_row.get(remark_src_col, '')
            veh_table_data.append(d_item)

        veh_report_df = pd.DataFrame(veh_table_data).sort_values(by='Delay Trips', ascending=False)
        veh_report_df.insert(0, 'S.No', range(1, 1 + len(veh_report_df)))

        st.markdown(render_html_table(veh_report_df), unsafe_allow_html=True)

        staff_tag = f"_Staff_{selected_veh_staff.replace(' ', '_')}" if selected_veh_staff != "ALL" else ""
        client_tag = f"_Client_{selected_veh_client.replace(' ', '_')}" if selected_veh_client != "ALL" else ""
        freq_tag = f"_{freq_filter_option.replace(' ', '_')}"
        status_tag = f"_{status_filter_option.replace(' ', '_')}"
        excel_bytes_veh = to_excel_bytes({'Vehicle_Performance_Report': veh_report_df})
        filename_veh = f"Vehicle_Performance_Report{staff_tag}{client_tag}{freq_tag}{status_tag}.xlsx"

        st.download_button(
            label="📥 Download Vehicle-wise Report Excel",
            data=excel_bytes_veh,
            file_name=filename_veh,
            mime=EXCEL_MIME,
            type="secondary",
            key=f"download_veh_perf_{unique_key}"
        )
    else:
        st.info("Vehicle-wise performance ke liye koi data available nahi hai.")


# ================= FILE PROCESSING =================
def process_uploaded_files(uploaded_files):
    callout_dfs = []
    mis_dfs = []

    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.lower().endswith('.csv'):
                temp_df = pd.read_csv(uploaded_file, low_memory=False)
            else:
                temp_df = pd.read_excel(uploaded_file)

            temp_df.columns = temp_df.columns.astype(str).str.strip()
            fname = uploaded_file.name.lower()
            
            has_category = any(kw in c.lower() for c in temp_df.columns for kw in ['category', 'cat', 'callout', 'reason', 'breakdown', 'issue'])
            is_callout = ('callout' in fname) or has_category or ('breakdown' in fname)

            if is_callout:
                cat_col = next((c for c in temp_df.columns if any(kw in c.lower() for kw in ['category', 'cat', 'reason', 'issue'])), None)
                if cat_col:
                    allowed_keywords = ['breakdown', 'break down', 'accident', 'tyre', 'tire', 'puncture', 'puncher', 'blast']
                    def check_cat(val):
                        if is_blank(val):
                            return False
                        s = str(val).lower().strip()
                        return any(kw in s for kw in allowed_keywords)
                    temp_df = temp_df[temp_df[cat_col].apply(check_cat)].copy()

                vendor_c = vendor_column(temp_df)
                if vendor_c:
                    temp_df['VendorName'] = temp_df[vendor_c].apply(lambda x: clean_party(x, keep_other=True))

                date_col = next((c for c in temp_df.columns if 'date' in c.lower() or 'desp' in c.lower() or 'time' in c.lower()), None)
                if date_col:
                    temp_df['Parsed_Date'] = pd.to_datetime(temp_df[date_col], errors='coerce', dayfirst=True)

                callout_dfs.append(temp_df)
            else:
                desp_col = next((c for c in temp_df.columns if 'desp' in c.lower() or 'date' in c.lower() or 'time' in c.lower()), None)
                if desp_col:
                    temp_df['Parsed_Date'] = pd.to_datetime(temp_df[desp_col], errors='coerce', dayfirst=True)

                vendor_c = vendor_column(temp_df)
                if vendor_c:
                    temp_df['VendorName'] = temp_df[vendor_c].apply(lambda x: clean_party(x, keep_other=True))
                else:
                    temp_df['VendorName'] = "Other"

                late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in temp_df.columns), None)
                if late_col:
                    temp_df['Status_Category'] = temp_df[late_col].apply(lambda v: DELAY if not is_zero_late(v) else ONTIME)
                else:
                    temp_df['Status_Category'] = ONTIME

                mis_dfs.append(temp_df)

        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")

    combined_callout = pd.concat(callout_dfs, ignore_index=True) if callout_dfs else pd.DataFrame()
    combined_mis = pd.concat(mis_dfs, ignore_index=True) if mis_dfs else pd.DataFrame()
    return combined_callout, combined_mis


# ================= MAIN APP =================
def main():
    st.title("🚀 Sales Manager Live Monitoring Dashboard")
    st.markdown("Upload your MIS or Callout files to view real-time trip performance and statistics.")

    # Initialize Session State & Load Persistent Disk Data if available
    if 'stored_callout_df' not in st.session_state:
        if os.path.exists(CALLOUT_PATH):
            st.session_state.stored_callout_df = pd.read_pickle(CALLOUT_PATH)
        else:
            st.session_state.stored_callout_df = pd.DataFrame()

    if 'stored_mis_df' not in st.session_state:
        if os.path.exists(MIS_PATH):
            st.session_state.stored_mis_df = pd.read_pickle(MIS_PATH)
        else:
            st.session_state.stored_mis_df = pd.DataFrame()

    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = not st.session_state.stored_mis_df.empty or not st.session_state.stored_callout_df.empty

    # Sidebar Controls
    st.sidebar.header("📁 Data Management")
    uploaded_files = st.sidebar.file_uploader("Upload MIS / Callout Excel or CSV", type=["xlsx", "csv"], accept_multiple_files=True)

    if uploaded_files:
        if st.sidebar.button("💾 Process & Save Data", type="primary"):
            c_df, m_df = process_uploaded_files(uploaded_files)
            st.session_state.stored_callout_df = c_df
            st.session_state.stored_mis_df = m_df
            st.session_state.data_loaded = True
            
            # Save permanently to disk
            c_df.to_pickle(CALLOUT_PATH)
            m_df.to_pickle(MIS_PATH)
            
            st.sidebar.success("Data successfully loaded and saved permanently!")

    if st.sidebar.button("🗑️ Remove Data", type="secondary"):
        st.session_state.stored_callout_df = pd.DataFrame()
        st.session_state.stored_mis_df = pd.DataFrame()
        st.session_state.data_loaded = False
        
        # Remove from disk
        if os.path.exists(CALLOUT_PATH):
            os.remove(CALLOUT_PATH)
        if os.path.exists(MIS_PATH):
            os.remove(MIS_PATH)
            
        st.sidebar.warning("Data has been removed.")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Dashboard Navigation")
    app_mode = st.sidebar.selectbox("Choose View", ["Main MIS Dashboard", "Callout Summary", "Staff Login Portal"])

    # Access stored data from session state
    callout_df = st.session_state.stored_callout_df
    mis_df = st.session_state.stored_mis_df

    if not st.session_state.data_loaded and mis_df.empty and callout_df.empty:
        st.info("Kripya sidebar mein files upload karke 'Process & Save Data' button par click karein.")
        return

    if app_mode == "Main MIS Dashboard":
        st.header("📈 Main MIS Performance Dashboard")
        if not mis_df.empty:
            show_reported_vehicle_table(mis_df, unique_key="main_dashboard")
        else:
            st.warning("Koi MIS data available nahi hai ya remove kiya ja chuka hai.")

    elif app_mode == "Callout Summary":
        st.header("⚠️ Callout / Breakdown Summary")
        if not callout_df.empty:
            st.metric("TOTAL CALLOUT COUNT (ALL)", len(callout_df))
            st.markdown(render_html_table(callout_df), unsafe_allow_html=True)
        else:
            st.info("Koi Callout data available nahi hai.")

    elif app_mode == "Staff Login Portal":
        st.header("🔒 Staff Login Portal")
        staff_col = next((c for c in mis_df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
        if staff_col and not mis_df.empty:
            staff_names = sorted([str(x).strip() for x in mis_df[staff_col].dropna().unique() if str(x).strip() != ""])
            selected_staff = st.selectbox("Select Staff Member", staff_names)
            if selected_staff:
                show_reported_vehicle_table(mis_df, unique_key="staff_portal", staff_filter=selected_staff)
        else:
            st.warning("Controlling Staff column nahi mila ya MIS data khali hai.")

if __name__ == '__main__':
    main()
