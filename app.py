import streamlit as st
import pandas as pd
from datetime import datetime
import math
import io
import os
import html as html_lib
import urllib.parse

# 1. Page Configuration
st.set_page_config(page_title="Sales Manager Live Monitoring Dashboard", layout="wide", initial_sidebar_state="expanded")

# ================= CUSTOM CSS FOR ULTRA-PREMIUM LOOK =================
st.markdown("""
    <style>
    .main, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #050b14 0%, #0a192f 50%, #050b14 100%);
        background-size: 200% 200%;
        animation: gradientBG 15s ease infinite;
        color: #e6f1ff;
    }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #050b14; }
    ::-webkit-scrollbar-thumb { background: rgba(72, 202, 228, 0.5); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #f72585; }

    [data-testid="stSidebar"] {
        background: rgba(10, 25, 47, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(72, 202, 228, 0.15);
    }

    .premium-title {
        font-size: 2.8rem;
        font-weight: 900;
        text-align: left;
        background: linear-gradient(to right, #ffffff 0%, #48cae4 20%, #f72585 50%, #48cae4 80%, #ffffff 100%);
        background-size: 200% auto;
        color: #fff;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textShine 4s linear infinite;
        margin-bottom: 10px;
        margin-top: 0px;
        padding-bottom: 5px;
    }
    @keyframes textShine { to { background-position: 200% center; } }
    
    .news-ticker-container {
        width: 100%;
        background: linear-gradient(90deg, #f72585, #7209b7);
        color: white;
        overflow: hidden;
        white-space: nowrap;
        box-sizing: border-box;
        border-radius: 8px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(247, 37, 133, 0.4);
        position: relative;
        display: flex;
        align-items: center;
        height: 45px;
    }
    .ticker-label {
        background: #050b14; color: #64ffda; font-weight: 900; padding: 0 15px; height: 100%;
        display: flex; align-items: center; position: absolute; left: 0; z-index: 10;
        border-radius: 8px 0 0 8px; border-right: 2px solid #64ffda; text-transform: uppercase;
    }
    .ticker-text-wrapper {
        padding-left: 160px; display: inline-block; white-space: nowrap; animation: marquee 45s linear infinite; 
    }
    .ticker-item { display: inline-block; padding: 0 40px; font-size: 15.5px; font-weight: 600; }
    @keyframes marquee { 0% { transform: translateX(100vw); } 100% { transform: translateX(-100%); } }

    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(28, 37, 65, 0.6) !important;
        border: 1px solid rgba(72, 202, 228, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #f72585, #7209b7) !important;
        border: none !important; color: white !important; border-radius: 8px !important; font-weight: 700 !important;
    }

    .custom-table-container {
        overflow-x: auto; max-height: 480px; border: 1px solid rgba(72, 202, 228, 0.2);
        border-radius: 12px; background-color: rgba(10, 25, 47, 0.7); box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px; backdrop-filter: blur(5px);
    }
    .custom-table { width: 100%; border-collapse: collapse; font-size: 13.5px; white-space: nowrap; }
    .custom-table th { 
        background: rgba(17, 34, 64, 0.95); color: #48cae4; padding: 14px 16px; text-align: left; 
        position: sticky; top: 0; font-weight: 800; z-index: 1; border-bottom: 2px solid #f72585;
    }
    .custom-table td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #8892b0; }
    .custom-table tr:hover td { background-color: rgba(72, 202, 228, 0.08); color: #48cae4; }
    </style>
""", unsafe_allow_html=True)

# ================= CONSTANTS & DIRECTORIES =================
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DATA_DIR = "saved_data"
os.makedirs(DATA_DIR, exist_ok=True)
CALLOUT_PATH = os.path.join(DATA_DIR, "callout.pkl")
MIS_PATH = os.path.join(DATA_DIR, "mis.pkl")

# ================= STAFF USERS DATABASE =================
STAFF_CREDENTIALS = {
    "dhananjay": {"password": "123", "staff_name": "DHANANJAY"},
    "staff2": {"password": "456", "staff_name": "STAFF NAME 2"}
}


# ================= DATA HELPERS =================
def is_blank(v):
    if v is None: return True
    try:
        if pd.isna(v): return True
    except: pass
    return str(v).strip().lower() in ("", "nan", "nat", "none")

def is_zero_late(v):
    if is_blank(v): return True
    s = str(v).strip().lower()
    if s in ("0", "0.0", "00:00", "0:00", "00:00:00", "0:00:00", "0 days 00:00:00"): return True
    try: return pd.to_timedelta(s) <= pd.Timedelta(0)
    except: pass
    try: return float(s) <= 0
    except: return False

def get_delay_minutes(v):
    if is_blank(v): return 0.0
    s = str(v).strip().lower()
    if s in ("0", "0.0", "00:00", "0:00"): return 0.0
    try: return pd.to_timedelta(s).total_seconds() / 60.0
    except: pass
    try: return float(s) * 60.0
    except: return 0.0

def clean_party(v, keep_other=True):
    if is_blank(v): return "Other"
    v_str = str(v).upper().strip()
    if "DHL" in v_str: return "DHL"
    elif "BUSYBEE" in v_str: return "Busybees"
    elif "TRACKON" in v_str: return "Trackon"
    return str(v).strip() if keep_other else "Other"

def vendor_column(df):
    return next((c for c in df.columns if any(k in c.lower() for k in ('vendor', 'party', 'client', 'customer'))), None)

def render_html_table(df_to_show, max_rows=2000):
    clean_df = df_to_show.fillna("").astype(str)
    note = ""
    if len(clean_df) > max_rows:
        note = f'<div style="color:#f72585; font-size:12px; margin-bottom:6px; font-weight:600;">⚡ Showing first {max_rows} rows. Download Excel for full data.</div>'
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
        for name, frame in sheets.items(): frame.to_excel(writer, index=False, sheet_name=name)
    return buffer_excel.getvalue()


# ================= NEWS TICKER =================
def render_news_ticker(df):
    if df.empty:
        ticker_text = "🟢 SYSTEM READY... WAITING FOR DATA UPLOAD..."
    else:
        late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in df.columns), None)
        total = len(df)
        delayed = len(df[~df[late_col].apply(is_zero_late)]) if late_col else 0
        on_time_pct = round(((total - delayed) / total) * 100, 1) if total > 0 else 0
        ticker_text = f"🚀 LIVE PERFORMANCE: Total Trips: {total} | ✅ On-Time: {on_time_pct}% | ⚠️ Delayed: {delayed} | ⚡ KEEP MONITORING DASHBOARD"

    full_text = f"<span class='ticker-item'>{ticker_text}</span>" * 4
    st.markdown(f"""<div class="news-ticker-container"><div class="ticker-label">BREAKING 🔴</div><div class="ticker-text-wrapper">{full_text}</div></div>""", unsafe_allow_html=True)


# ================= IN-TRANSIT TABLE WITH CLIENT FILTER =================
def show_in_transit_table(df, unique_key="", locked_staff=None):
    st.markdown("<br><h2 style='color:#f72585;'>🚚 In-Transit Vehicles (Live Tracking)</h2>", unsafe_allow_html=True)
    final_rep_col = next((c for c in ['Final Touching Reporting Date & Time', 'Reporting Date & Time', 'Reporting Date', 'Desp. Date & Time'] if c in df.columns), None)
    
    if not final_rep_col:
        st.warning("Reporting Date column not found.")
        return
        
    in_transit_df = df[df[final_rep_col].apply(is_blank)].copy()
    staff_col = next((c for c in in_transit_df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
    client_col_name = vendor_column(in_transit_df) or 'VendorName'
    
    if locked_staff and staff_col:
        in_transit_df = in_transit_df[in_transit_df[staff_col].astype(str).str.strip().str.upper() == locked_staff.upper()]

    if in_transit_df.empty:
        st.success("🎉 Koi In-Transit vehicle nahi bacha.")
        return

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        client_list = ["ALL"] + sorted([str(x).strip() for x in in_transit_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in in_transit_df.columns else ["ALL"]
        selected_client = st.selectbox("🏢 Filter by Client:", client_list, key=f"it_client_{unique_key}")
        
    if selected_client != "ALL" and client_col_name in in_transit_df.columns:
        in_transit_df = in_transit_df[in_transit_df[client_col_name].astype(str).str.strip() == selected_client]

    st.metric("Total In-Transit Vehicles", len(in_transit_df))
    final_it_df = in_transit_df.copy()
    final_it_df.insert(0, 'S.No', range(1, 1 + len(final_it_df)))
    st.markdown(render_html_table(final_it_df), unsafe_allow_html=True)
    
    excel_bytes = to_excel_bytes({'In_Transit_Vehicles': final_it_df})
    st.download_button(label="📥 Download In-Transit Excel", data=excel_bytes, file_name="In_Transit_Vehicles.xlsx", mime=EXCEL_MIME, type="primary", key=f"dl_it_{unique_key}")


# ================= CLIENT SUMMARY VIEW =================
def show_client_summary_view(df, unique_key="", locked_staff=None):
    st.markdown("<br><h2 style='color:#f72585;'>🏢 Client-wise Performance Summary</h2>", unsafe_allow_html=True)
    
    client_col_name = vendor_column(df) or 'VendorName'
    late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in df.columns), None)
    staff_col = next((c for c in df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
    
    view_df = df.copy()
    if locked_staff and staff_col:
        view_df = view_df[view_df[staff_col].astype(str).str.strip().str.upper() == locked_staff.upper()]
        st.info(f"🔒 Restricted View: Showing client summary for **{locked_staff}** only.")
        
    if client_col_name and client_col_name in view_df.columns and late_col:
        view_df['Is_OnTime'] = view_df[late_col].apply(is_zero_late)
        view_df['Is_Delay'] = ~view_df[late_col].apply(is_zero_late)
        
        client_summary = view_df.groupby(client_col_name).agg(
            Total=('Is_OnTime', 'count'),
            OnTime=('Is_OnTime', 'sum'),
            Delay=('Is_Delay', 'sum')
        ).reset_index()
        
        client_summary['On-Time %'] = client_summary.apply(
            lambda r: f"{round((r['OnTime'] / r['Total']) * 100, 1)}%" if r['Total'] > 0 else "0.0%", axis=1
        )
        client_summary = client_summary.rename(columns={
            client_col_name: 'Client Name',
            'Total': 'Total Trips',
            'OnTime': 'On-Time Trips',
            'Delay': 'Delay Trips'
        }).sort_values(by='Total Trips', ascending=False)
        
        client_summary.insert(0, 'S.No', range(1, 1 + len(client_summary)))
        st.markdown(render_html_table(client_summary), unsafe_allow_html=True)
        
        excel_client = to_excel_bytes({'Client_Performance': client_summary})
        st.download_button(label="📥 Download Client Performance Excel", data=excel_client, file_name="Client_Performance_Summary.xlsx", mime=EXCEL_MIME, type="primary", key=f"dl_client_summary_{unique_key}")
    else:
        st.info("Client performance data ke liye required columns nahi mile.")


# ================= MAIN MIS TABLE & PERFORMANCE REPORTS =================
def show_reported_vehicle_table(df, unique_key="", locked_staff=None):
    final_rep_col = next((c for c in ['Final Touching Reporting Date & Time', 'Reporting Date & Time', 'Reporting Date', 'Desp. Date & Time'] if c in df.columns), None)
    if not final_rep_col: final_rep_col = next((c for c in df.columns if 'report' in c.lower() or 'desp' in c.lower() or 'date' in c.lower()), None)

    reported_df = df[~df[final_rep_col].apply(is_blank)].copy() if final_rep_col else df.copy()

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
    def get_relative_week(row_date):
        if pd.isna(row_date): return None
        diff = (current_dt - row_date).days
        if diff < 0: return "Current / Future"
        elif diff <= 7: return "Last 1 Week"
        elif diff <= 14: return "Last 2 Weeks"
        elif diff <= 21: return "Last 3 Weeks"
        elif diff <= 28: return "Last 4 Weeks"
        return None

    reported_df['_Rel_Week'] = reported_df['_Rep_Date_Obj'].apply(get_relative_week)

    valid_dates = reported_df[reported_df['_Rep_Date_Obj'].notna()].drop_duplicates(subset=['_Rep_Date_Str']).sort_values('_Rep_Date_Obj', ascending=False)
    date_options = ["ALL"] + valid_dates['_Rep_Date_Str'].tolist()
    valid_months = reported_df[reported_df['_Rep_Date_Obj'].notna()].drop_duplicates(subset=['_Month_Str']).sort_values('_Rep_Date_Obj', ascending=False)
    month_options = ["ALL"] + valid_months['_Month_Str'].tolist()

    staff_col = next((c for c in reported_df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
    client_col_name = vendor_column(reported_df) or 'VendorName'

    if locked_staff and staff_col:
        reported_df = reported_df[reported_df[staff_col].astype(str).str.strip().str.upper() == locked_staff.upper()]
        st.info(f"🔒 Restricted View: Showing records for **{locked_staff}** only.")

    if reported_df.empty:
        st.warning("Aapke naam ka koi data available nahi hai.")
        return

    if not locked_staff:
        st.markdown("<h3 style='color:#48cae4; font-size:18px;'>🔍 Live Data Filters</h3>", unsafe_allow_html=True)
        f_col1, f_col2, f_col3, f_col4, f_col5, f_col6, f_col7 = st.columns(7)
        with f_col1: selected_date = st.selectbox("📅 Date:", date_options, index=0, key=f"d_{unique_key}")
        with f_col2: selected_month = st.selectbox("🗓️ Month:", month_options, index=0, key=f"m_{unique_key}")
        with f_col3: delay_filter = st.selectbox("🚨 Status:", ["ALL Reported Vehicles", "Only Delay", "Only On-Time"], index=0, key=f"s_{unique_key}")
        with f_col4: 
            staff_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"]
            selected_staff = st.selectbox("👨‍💼 Staff:", staff_list, index=0, key=f"st_{unique_key}")
        with f_col5: 
            client_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in reported_df.columns else ["ALL"]
            selected_client = st.selectbox("🏢 Client:", client_list, index=0, key=f"c_{unique_key}")
        with f_col6: selected_delay_hours = st.selectbox("⏱️ Delay Hrs:", ["ALL", "Delay < 10 mins", "Delay < 30 mins"], index=0, key=f"dh_{unique_key}")
        with f_col7: selected_remarks = st.selectbox("📝 Remarks:", ["ALL", "With Remarks", "Without Remarks (Empty)"], index=0, key=f"r_{unique_key}")

        strict_week_options = ["Last 1 Week", "Last 2 Weeks", "Last 3 Weeks", "Last 4 Weeks"]
        available_weeks = [w for w in strict_week_options if w in reported_df['_Rel_Week'].unique()]
        selected_weeks = []
        if available_weeks:
            st.markdown("<div style='font-size: 13px; color: #8892b0; margin-bottom: 5px; margin-top:10px;'>Filter by Week:</div>", unsafe_allow_html=True)
            chk_cols = st.columns(len(strict_week_options))
            for i, wk in enumerate(strict_week_options):
                with chk_cols[i]:
                    if st.checkbox(wk, key=f"w_{unique_key}_{wk}"): selected_weeks.append(wk)

    # Yeh filtered data sirf upar wale main table ke liye use hoga
    filtered_report_df = reported_df.copy()
    late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in filtered_report_df.columns), None)
    remark_col = next((c for c in ['Tracking Remark', 'Remark', 'Remarks'] if c in filtered_report_df.columns), None)

    if not locked_staff:
        if selected_date != "ALL": filtered_report_df = filtered_report_df[filtered_report_df['_Rep_Date_Str'] == selected_date]
        if selected_month != "ALL": filtered_report_df = filtered_report_df[filtered_report_df['_Month_Str'] == selected_month]
        if selected_weeks: filtered_report_df = filtered_report_df[filtered_report_df['_Rel_Week'].isin(selected_weeks)]
        
        if late_col:
            if delay_filter == "Only Delay": filtered_report_df = filtered_report_df[~filtered_report_df[late_col].apply(is_zero_late)]
            elif delay_filter == "Only On-Time": filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(is_zero_late)]

            if selected_delay_hours != "ALL":
                def check_delay(val):
                    mins = get_delay_minutes(val)
                    if mins <= 0: return False
                    if "10" in selected_delay_hours: return mins < 10
                    if "30" in selected_delay_hours: return mins < 30
                    return False
                filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(check_delay)]

        if selected_remarks != "ALL" and remark_col:
            valid_indices = []
            for idx, row in filtered_report_df.iterrows():
                is_empty = is_blank(row.get(remark_col, None))
                is_delayed = not is_zero_late(row.get(late_col, 0)) if late_col else True
                if selected_remarks == "With Remarks" and not is_empty: valid_indices.append(idx)
                elif selected_remarks == "Without Remarks (Empty)" and is_empty: valid_indices.append(idx)
            filtered_report_df = filtered_report_df.loc[valid_indices]

        if selected_staff != "ALL" and staff_col: filtered_report_df = filtered_report_df[filtered_report_df[staff_col].astype(str).str.strip() == selected_staff]
        if selected_client != "ALL" and client_col_name in filtered_report_df.columns: filtered_report_df = filtered_report_df[filtered_report_df[client_col_name].astype(str).str.strip() == selected_client]

    if filtered_report_df.empty:
        st.info("No data found for the selected filters.")
        return

    desired_cols = [
        'Lorry No.', 'Veh.Type', 'From', 'Destination', 'Party', 'Desp. Date & Time',
        'Hrs. Given', '1st Touching', '1st Touching Reporting Date & Time', 
        '1st Touching Delivery Date & Time', '1st Touching Hrs.', '2nd Touching', 
        '2nd Touching Reporting Date & Time', '2nd Touching Delivery Date & Time', 
        '2nd Touching Hrs.', 'Final Touching Reporting Date & Time', 
        'Total Touching Hrs.', 'Hrs. Taken with touching', 'Hrs. Taken without touching (Dly.)', 
        'Late Hrs', 'Tracking Remark', 'Group Name', 'Controlling Staff Name', 'Foreman Name'
    ]

    actual_display_cols = []
    for col in desired_cols:
        matched_c = next((c for c in filtered_report_df.columns if c.lower().strip() == col.lower().strip()), None)
        if matched_c: actual_display_cols.append(matched_c)
        else:
            if col == 'Tracking Remark': 
                rem_alt = next((c for c in filtered_report_df.columns if 'remark' in c.lower()), None)
                if rem_alt: actual_display_cols.append(rem_alt)
            elif col == 'Party':
                party_alt = vendor_column(filtered_report_df)
                if party_alt: actual_display_cols.append(party_alt)

    if not actual_display_cols: actual_display_cols = [c for c in filtered_report_df.columns if not c.startswith('_')]

    final_report_df = filtered_report_df[actual_display_cols].copy()
    final_report_df.insert(0, 'S.No', range(1, 1 + len(final_report_df)))

    # 1. LIVE DATA TABLE
    st.markdown(render_html_table(final_report_df), unsafe_allow_html=True)
    
    # DOWNLOAD & SEND MAIL BUTTONS
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        excel_bytes = to_excel_bytes({'Reported_Vehicles': final_report_df})
        st.download_button(label="📥 Download Filtered Excel", data=excel_bytes, file_name="Reported_Vehicles.xlsx", mime=EXCEL_MIME, type="primary", key=f"dl_{unique_key}")
        
    with col_b2:
        with st.expander("📧 Send Data via Email"):
            recipient_email = st.text_input("Recipient Email:", placeholder="manager@example.com", key=f"recipient_{unique_key}")
            if st.button("📤 Generate Mail Link", key=f"btn_send_{unique_key}"):
                if recipient_email:
                    subject = urllib.parse.quote("Sales Manager Dashboard - Filtered Report")
                    body = f"Hello,%0D%0A%0D%0APlease find the filtered MIS report containing {len(final_report_df)} records.%0D%0A%0D%0ARegards,%0D%0ASales Dashboard"
                    mailto_url = f"mailto:{recipient_email}?subject={subject}&body={body}"
                    st.success("✅ Mail link ready!")
                    st.markdown(f'<a href="{mailto_url}" target="_blank" style="background:#64ffda;color:#050b14;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:bold;">✉️ Click to Open Mail App</a>', unsafe_allow_html=True)
                else:
                    st.error("⚠️ Enter valid email.")

    late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in reported_df.columns), None)

    # 2. CLIENT-WISE PERFORMANCE REPORT (UNFILTERED /
