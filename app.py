import streamlit as st
import pandas as pd
from datetime import datetime
import math
import io
import os
import html as html_lib

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


# ================= IN-TRANSIT TABLE =================
def show_in_transit_table(df, unique_key="", locked_staff=None):
    st.markdown("<br><h2 style='color:#f72585;'>🚚 In-Transit Vehicles (Live Tracking)</h2>", unsafe_allow_html=True)
    final_rep_col = next((c for c in ['Final Touching Reporting Date & Time', 'Reporting Date & Time', 'Reporting Date', 'Desp. Date & Time'] if c in df.columns), None)
    
    if not final_rep_col:
        st.warning("Reporting Date column not found.")
        return
        
    in_transit_df = df[df[final_rep_col].apply(is_blank)].copy()
    staff_col = next((c for c in in_transit_df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
    
    if locked_staff and staff_col:
        in_transit_df = in_transit_df[in_transit_df[staff_col].astype(str).str.strip().str.upper() == locked_staff.upper()]

    if in_transit_df.empty:
        st.success("🎉 Koi In-Transit vehicle nahi bacha.")
        return

    st.metric("Total In-Transit Vehicles", len(in_transit_df))
    final_it_df = in_transit_df.copy()
    final_it_df.insert(0, 'S.No', range(1, 1 + len(final_it_df)))
    st.markdown(render_html_table(final_it_df), unsafe_allow_html=True)
    
    excel_bytes = to_excel_bytes({'In_Transit_Vehicles': final_it_df})
    st.download_button(label="📥 Download In-Transit Excel", data=excel_bytes, file_name="In_Transit_Vehicles.xlsx", mime=EXCEL_MIME, type="primary", key=f"dl_it_{unique_key}")


# ================= MAIN MIS TABLE & PERFORMANCE REPORTS =================
def show_reported_vehicle_table(df, unique_key="", locked_staff=None):
    final_rep_col = next((c for c in ['Final Touching Reporting Date & Time', 'Reporting Date & Time', 'Reporting Date', 'Desp. Date & Time'] if c in df.columns), None)
    if not final_rep_col: final_rep_col = next((c for c in df.columns if 'report' in c.lower() or 'desp' in c.lower() or 'date' in c.lower()), None)

    reported_df = df[~df[final_rep_col].apply(is_blank)].copy() if final_rep_col else df.copy()
    
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
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
        with f_col1: delay_filter = st.selectbox("🚨 Status:", ["ALL Reported Vehicles", "Only Delay", "Only On-Time"], key=f"s_{unique_key}")
        with f_col2: 
            staff_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"]
            selected_staff = st.selectbox("👨‍💼 Staff:", staff_list, key=f"st_{unique_key}")
        with f_col3: 
            client_list = ["ALL"] + sorted([str(x).strip() for x in reported_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in reported_df.columns else ["ALL"]
            selected_client = st.selectbox("🏢 Client:", client_list, key=f"c_{unique_key}")
        with f_col4: selected_delay_hours = st.selectbox("⏱️ Delay Hrs:", ["ALL", "Delay < 10 mins", "Delay < 30 mins"], key=f"dh_{unique_key}")
        with f_col5: selected_remarks = st.selectbox("📝 Remarks:", ["ALL", "With Remarks", "Without Remarks (Empty)"], key=f"r_{unique_key}")

        late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in reported_df.columns), None)
        if selected_staff != "ALL" and staff_col: reported_df = reported_df[reported_df[staff_col].astype(str).str.strip() == selected_staff]
        if selected_client != "ALL" and client_col_name in reported_df.columns: reported_df = reported_df[reported_df[client_col_name].astype(str).str.strip() == selected_client]
        if delay_filter == "Only Delay" and late_col: reported_df = reported_df[~reported_df[late_col].apply(is_zero_late)]
        elif delay_filter == "Only On-Time" and late_col: reported_df = reported_df[reported_df[late_col].apply(is_zero_late)]

    final_report_df = reported_df.copy()
    final_report_df.insert(0, 'S.No', range(1, 1 + len(final_report_df)))

    # 1. LIVE DATA TABLE
    st.markdown(render_html_table(final_report_df), unsafe_allow_html=True)
    
    excel_bytes = to_excel_bytes({'Reported_Vehicles': final_report_df})
    st.download_button(label="📥 Download Filtered Excel", data=excel_bytes, file_name="Reported_Vehicles.xlsx", mime=EXCEL_MIME, type="primary", key=f"dl_{unique_key}")

    late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in reported_df.columns), None)

    # 2. CLIENT-WISE PERFORMANCE REPORT (NICHE SHOW HOGA)
    st.markdown("<br><h3 style='color:#f72585; font-size:22px; margin-bottom:15px;'>🏢 Client-wise Performance Report</h3>", unsafe_allow_html=True)
    if client_col_name and client_col_name in reported_df.columns and late_col:
        client_df = reported_df.copy()
        client_df['Is_OnTime'] = client_df[late_col].apply(is_zero_late)
        client_df['Is_Delay'] = ~client_df[late_col].apply(is_zero_late)
        
        client_summary = client_df.groupby(client_col_name).agg(
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
        st.download_button(label="📥 Download Client Performance", data=excel_client, file_name="Client_Performance.xlsx", mime=EXCEL_MIME, type="secondary", key=f"dl_client_{unique_key}")
    else:
        st.info("Client performance data available nahi hai.")

    # 3. VEHICLE-WISE PERFORMANCE REPORT (USKE NICHE SHOW HOGA)
    st.markdown("<br><h3 style='color:#48cae4; font-size:22px; margin-bottom:15px;'>🚛 Vehicle-wise Performance Report</h3>", unsafe_allow_html=True)
    
    lorry_col = next((c for c in reported_df.columns if c.lower().strip() in ['lorry no.', 'lorry no', 'vehicle no', 'vehicle', 'truck']), None)
    if not lorry_col: lorry_col = next((c for c in reported_df.columns if any(k in c.lower() for k in ['lorry', 'vehicle', 'truck'])) , None)
    from_col = next((c for c in reported_df.columns if c.lower().strip() in ['from', 'source', 'origin']), None)
    dest_col = next((c for c in reported_df.columns if c.lower().strip() in ['destination', 'to']), None)

    if lorry_col and late_col:
        temp_veh_df = reported_df.copy()
        if from_col and dest_col: temp_veh_df['Route'] = temp_veh_df[from_col].astype(str).str.strip() + " ➔ " + temp_veh_df[dest_col].astype(str).str.strip()
        else: temp_veh_df['Route'] = "N/A"

        v_f1, v_f2, v_f3, v_f4 = st.columns(4)
        veh_staff_list = ["ALL"] + sorted([str(x).strip() for x in temp_veh_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"]
        veh_client_list = ["ALL"] + sorted([str(x).strip() for x in temp_veh_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in temp_veh_df.columns else ["ALL"]
        freq_options = ["ALL", "> 1 Delay", "> 2 Delays", "> 3 Delays", "> 4 Delays", "> 5 Delays"]
        
        with v_f1: sel_veh_staff = st.selectbox("👨‍💼 Controlling Staff:", veh_staff_list, key=f"vs_{unique_key}")
        with v_f2: sel_veh_client = st.selectbox("🏢 Client:", veh_client_list, key=f"vc_{unique_key}")
        with v_f3: sel_veh_freq = st.selectbox("🔄 Delay Frequency:", freq_options, key=f"vf_{unique_key}")
        with v_f4: sel_veh_status = st.selectbox("⚖️ Delay/On-time:", ["ALL", "Only On-Time", "Only Delay"], key=f"vst_{unique_key}")

        veh_df = temp_veh_df.copy()
        if sel_veh_staff != "ALL" and staff_col: veh_df = veh_df[veh_df[staff_col].astype(str).str.strip() == sel_veh_staff]
        if sel_veh_client != "ALL" and client_col_name in veh_df.columns: veh_df = veh_df[veh_df[client_col_name].astype(str).str.strip() == sel_veh_client]

        veh_df['Is_OnTime'] = veh_df[late_col].apply(is_zero_late)
        veh_df['Is_Delay'] = ~veh_df[late_col].apply(is_zero_late)

        if sel_veh_status == "Only On-Time": veh_df = veh_df[veh_df['Is_OnTime']]
        elif sel_veh_status == "Only Delay": veh_df = veh_df[veh_df['Is_Delay']]

        veh_groups = veh_df.groupby([lorry_col, 'Route']).agg(Total=('Is_OnTime', 'count'), OnTime=('Is_OnTime', 'sum'), Delay=('Is_Delay', 'sum')).reset_index()
        
        if sel_veh_freq != "ALL":
            if sel_veh_freq == "> 1 Delay": veh_groups = veh_groups[veh_groups['Delay'] > 1]
            elif sel_veh_freq == "> 2 Delays": veh_groups = veh_groups[veh_groups['Delay'] > 2]
            elif sel_veh_freq == "> 3 Delays": veh_groups = veh_groups[veh_groups['Delay'] > 3]
            elif sel_veh_freq == "> 4 Delays": veh_groups = veh_groups[veh_groups['Delay'] > 4]
            elif sel_veh_freq == "> 5 Delays": veh_groups = veh_groups[veh_groups['Delay'] > 5]

        veh_summary_df = veh_groups.copy()
        veh_summary_df['On-Time %'] = veh_summary_df.apply(lambda r: f"{round((r['OnTime'] / r['Total']) * 100, 1)}%" if r['Total'] > 0 else "0.0%", axis=1)
        veh_summary_df = veh_summary_df.rename(columns={lorry_col: 'Vehicle No.', 'Route': 'Route (From ➔ Destination)', 'Total': 'Total Trips', 'OnTime': 'On-Time Trips', 'Delay': 'Delay Trips'})
        veh_summary_df = veh_summary_df.sort_values(by='Total Trips', ascending=False)
        veh_summary_df.insert(0, 'S.No', range(1, 1 + len(veh_summary_df)))

        if not veh_summary_df.empty:
            st.markdown(render_html_table(veh_summary_df), unsafe_allow_html=True)
            excel_veh = to_excel_bytes({'Vehicle_Performance': veh_summary_df})
            st.download_button(label="📥 Download Vehicle Performance", data=excel_veh, file_name="Vehicle_Performance.xlsx", mime=EXCEL_MIME, type="primary", key=f"dl_veh_{unique_key}")
        else:
            st.info("Vehicle performance ke liye records nahi mile.")
    else:
        st.info("Vehicle performance ke liye required columns nahi mile.")


# ================= FILE PROCESSING =================
def process_uploaded_files(uploaded_files):
    callout_dfs, mis_dfs = [], []
    for uploaded_file in uploaded_files:
        try:
            filename_lower = uploaded_file.name.lower()
            temp_df = pd.read_csv(uploaded_file, low_memory=False) if filename_lower.endswith('.csv') else pd.read_excel(uploaded_file)
            if temp_df is None or temp_df.empty: continue
            temp_df.columns = temp_df.columns.astype(str).str.strip()
            
            vendor_c = vendor_column(temp_df)
            if ('callout' in filename_lower) or ('breakdown' in filename_lower):
                temp_df['VendorName'] = temp_df[vendor_c].apply(lambda x: clean_party(x, False)) if vendor_c else "Other"
                callout_dfs.append(temp_df)
            else:
                temp_df['VendorName'] = temp_df[vendor_c].apply(lambda x: clean_party(x, True)) if vendor_c else "Other"
                mis_dfs.append(temp_df)
        except Exception as e: st.error(f"Error: {e}")

    return pd.concat(callout_dfs, ignore_index=True) if callout_dfs else pd.DataFrame(), pd.concat(mis_dfs, ignore_index=True) if mis_dfs else pd.DataFrame()


# ================= MAIN APP =================
def main():
    st.markdown("<h1 class='premium-title'>🚀 Sales Manager Live Monitoring Dashboard</h1>", unsafe_allow_html=True)

    if 'stored_mis_df' not in st.session_state: st.session_state.stored_mis_df = pd.read_pickle(MIS_PATH) if os.path.exists(MIS_PATH) else pd.DataFrame()
    if 'stored_callout_df' not in st.session_state: st.session_state.stored_callout_df = pd.read_pickle(CALLOUT_PATH) if os.path.exists(CALLOUT_PATH) else pd.DataFrame()

    render_news_ticker(st.session_state.stored_mis_df)

    st.sidebar.markdown("<h2 style='color:#64ffda; font-size:18px;'>🔐 User Authentication</h2>", unsafe_allow_html=True)
    
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.session_state.staff_name = None

    if st.session_state.logged_in_user is None:
        login_type = st.sidebar.radio("Login As:", ["Admin (Full Access)", "Staff Portal"])
        
        if login_type == "Admin (Full Access)":
            adm_pass = st.sidebar.text_input("Admin Password", type="password")
            if st.sidebar.button("Admin Login"):
                if adm_pass == "admin123":
                    st.session_state.logged_in_user = "Admin"
                    st.session_state.user_role = "admin"
                    st.rerun()
                else:
                    st.sidebar.error("Wrong Password!")
        else:
            username = st.sidebar.text_input("Staff Username (e.g., dhananjay)")
            password = st.sidebar.text_input("Staff Password", type="password")
            if st.sidebar.button("Staff Login"):
                user_info = STAFF_CREDENTIALS.get(username.lower())
                if user_info and user_info["password"] == password:
                    st.session_state.logged_in_user = username
                    st.session_state.user_role = "staff"
                    st.session_state.staff_name = user_info["staff_name"]
                    st.rerun()
                else:
                    st.sidebar.error("Invalid Username or Password!")
        return

    st.sidebar.success(f"Logged in as: **{st.session_state.logged_in_user.upper()}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.session_state.staff_name = None
        st.rerun()

    if st.session_state.user_role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.markdown("<h2 style='color:#64ffda; font-size:18px;'>📁 Data Management (Admin Only)</h2>", unsafe_allow_html=True)
        uploaded_files = st.sidebar.file_uploader("Upload MIS/Callout (Excel/CSV)", type=["xlsx", "csv"], accept_multiple_files=True)

        if uploaded_files and st.sidebar.button("💾 Process & Save Data", type="primary"):
            c_df, m_df = process_uploaded_files(uploaded_files)
            st.session_state.stored_callout_df = c_df
            st.session_state.stored_mis_df = m_df
            c_df.to_pickle(CALLOUT_PATH)
            m_df.to_pickle(MIS_PATH)
            st.sidebar.success("Saved successfully!")
            st.rerun()

        if st.sidebar.button("🗑️ Clear Dashboard Data"):
            st.session_state.stored_callout_df = pd.DataFrame()
            st.session_state.stored_mis_df = pd.DataFrame()
            if os.path.exists(CALLOUT_PATH): os.remove(CALLOUT_PATH)
            if os.path.exists(MIS_PATH): os.remove(MIS_PATH)
            st.rerun()
    else:
        st.sidebar.info("🔒 Staff Account: Upload and Delete features are disabled for security.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("<h2 style='color:#64ffda; font-size:18px;'>📊 Application Views</h2>", unsafe_allow_html=True)
    
    app_mode = st.sidebar.selectbox("Navigate To:", ["Main MIS Dashboard", "In-Transit Vehicles", "Callout Summary"])

    callout_df = st.session_state.stored_callout_df
    mis_df = st.session_state.stored_mis_df

    if mis_df.empty and callout_df.empty:
        st.info("👋 Welcome! Please upload your data files in the sidebar.")
        return

    current_locked_staff = st.session_state.staff_name if st.session_state.user_role == "staff" else None

    if app_mode == "Main MIS Dashboard":
        if not mis_df.empty:
            show_reported_vehicle_table(mis_df, unique_key="main", locked_staff=current_locked_staff)
        else:
            st.warning("Koi MIS data available nahi hai.")
            
    elif app_mode == "In-Transit Vehicles":
        if not mis_df.empty:
            show_in_transit_table(mis_df, unique_key="intransit", locked_staff=current_locked_staff)
        else:
            st.warning("Koi MIS data available nahi hai.")

    elif app_mode == "Callout Summary":
        st.markdown("<h2 style='color:#f72585;'>⚠️ Callout / Breakdown Summary</h2>", unsafe_allow_html=True)
        if not callout_df.empty:
            st.markdown(render_html_table(callout_df), unsafe_allow_html=True)
        else:
            st.info("Koi Callout data available nahi hai.")

if __name__ == '__main__':
    main()
