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
    /* 1. Global Animated Background */
    .main, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #050b14 0%, #0a192f 50%, #050b14 100%);
        background-size: 200% 200%;
        animation: gradientBG 15s ease infinite;
        color: #e6f1ff;
    }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

    /* 2. Custom Sleek Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #050b14; }
    ::-webkit-scrollbar-thumb { background: rgba(72, 202, 228, 0.5); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #f72585; }

    /* 3. Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 25, 47, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(72, 202, 228, 0.15);
    }

    /* 4. Premium Animated Title */
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
        margin-bottom: 25px;
        margin-top: 5px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    @keyframes textShine { to { background-position: 200% center; } }
    
    /* 5. Streamlit Widget Enhancements */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(28, 37, 65, 0.6) !important;
        border: 1px solid rgba(72, 202, 228, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
        transition: all 0.3s ease;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border: 1px solid #f72585 !important;
        box-shadow: 0 0 10px rgba(247, 37, 133, 0.2);
    }
    
    /* 6. Glowing Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #f72585, #7209b7) !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(247, 37, 133, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(247, 37, 133, 0.6) !important;
    }

    /* 7. Built-in Smart Insights Panel */
    .smart-panel {
        background: rgba(17, 34, 64, 0.7);
        backdrop-filter: blur(10px);
        border-left: 4px solid #48cae4;
        border-radius: 12px;
        padding: 25px 30px;
        margin: 15px 0 30px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        animation: slideDown 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    .smart-title {
        color: #48cae4; font-size: 20px; font-weight: 900; margin-bottom: 20px;
        letter-spacing: 1.5px; text-transform: uppercase; display: flex; align-items: center; gap: 10px;
    }
    .smart-bullet {
        color: #e6f1ff; font-size: 15px; margin-bottom: 14px; line-height: 1.7;
        display: flex; align-items: flex-start; gap: 12px;
        background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; border: 1px solid rgba(72,202,228,0.15);
    }
    .smart-bullet strong { color: #f72585; }

    /* 8. Modern Tables */
    .custom-table-container {
        overflow-x: auto; max-height: 480px;
        border: 1px solid rgba(72, 202, 228, 0.2);
        border-radius: 12px;
        background-color: rgba(10, 25, 47, 0.7);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        animation: fadeUp 1s ease-out both;
        backdrop-filter: blur(5px);
    }
    .custom-table { width: 100%; border-collapse: collapse; font-size: 13.5px; white-space: nowrap; }
    .custom-table th { 
        background: rgba(17, 34, 64, 0.95); color: #48cae4; 
        padding: 14px 16px; text-align: left; position: sticky; top: 0; 
        font-weight: 800; z-index: 1; border-bottom: 2px solid #f72585;
    }
    .custom-table td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #8892b0; transition: all 0.2s ease;}
    .custom-table tr:hover td { background-color: rgba(72, 202, 228, 0.08); color: #48cae4; transform: scale(1.002); }
    
    @keyframes slideDown { 0% { transform: translateY(-20px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
    @keyframes fadeUp { 0% { transform: translateY(20px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# ================= CONSTANTS & DIRECTORIES =================
ONTIME = 'On-Time Trip Closed'
DELAY = 'Delay Trip Closed'
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DATA_DIR = "saved_data"
os.makedirs(DATA_DIR, exist_ok=True)
CALLOUT_PATH = os.path.join(DATA_DIR, "callout.pkl")
MIS_PATH = os.path.join(DATA_DIR, "mis.pkl")


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
        note = f'<div style="color:#f72585; font-size:12px; margin-bottom:6px; font-weight:600;">⚡ Showing first {max_rows} rows for performance. Download Excel for full data.</div>'
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

# ================= BUILT-IN SMART INSIGHTS ENGINE =================
def render_smart_insights(df, late_col, client_col):
    if df.empty or not late_col: return
    
    total_vehicles = len(df)
    delayed_vehicles = df[~df[late_col].apply(is_zero_late)]
    delay_count = len(delayed_vehicles)
    delay_percentage = round((delay_count / total_vehicles) * 100, 1) if total_vehicles > 0 else 0
    
    # Analyze Routes
    from_col = next((c for c in df.columns if c.lower().strip() in ['from', 'source', 'origin']), None)
    dest_col = next((c for c in df.columns if c.lower().strip() in ['destination', 'to']), None)
    
    top_route_str = "No specific route data available."
    if from_col and dest_col and delay_count > 0:
        delayed_routes = delayed_vehicles[from_col].astype(str) + " ➔ " + delayed_vehicles[dest_col].astype(str)
        if not delayed_routes.empty:
            top_route = delayed_routes.value_counts().index[0]
            top_route_count = delayed_routes.value_counts().iloc[0]
            top_route_str = f"Route <strong>{top_route}</strong> is facing maximum bottlenecks with <strong>{top_route_count}</strong> delayed vehicles."

    # Analyze Clients
    top_client_str = "No specific client data available."
    if client_col and delay_count > 0:
        if not delayed_vehicles[client_col].empty:
            top_client = delayed_vehicles[client_col].value_counts().index[0]
            top_client_count = delayed_vehicles[client_col].value_counts().iloc[0]
            top_client_str = f"Client <strong>{top_client}</strong> is heavily impacted, experiencing <strong>{top_client_count}</strong> delays."

    # Generate HTML Output - NO LEADING SPACES to prevent code block parsing
    html_out = f"""<div class="smart-panel">
<div class="smart-title">📊 Smart Auto-Insights Engine</div>
<div style="color:#8892b0; font-size:13.5px; margin-bottom:15px;">Live analysis generated directly from current filters without external APIs.</div>
<div class="smart-bullet">
<span style="font-size:18px;">🚦</span>
<span><strong>Performance Overview:</strong> Out of {total_vehicles} total tracked trips, <strong>{delay_count}</strong> are currently running late. This represents a delay rate of <strong>{delay_percentage}%</strong>.</span>
</div>
<div class="smart-bullet">
<span style="font-size:18px;">🛣️</span>
<span><strong>Route Alert:</strong> {top_route_str}</span>
</div>
<div class="smart-bullet">
<span style="font-size:18px;">🏢</span>
<span><strong>Vendor Impact:</strong> {top_client_str}</span>
</div>
</div>"""
    
    st.markdown(html_out, unsafe_allow_html=True)


# ================= REPORTED VEHICLE TABLE & REPORTS =================
def show_reported_vehicle_table(df, unique_key="", staff_filter=None):
    final_rep_col = next((c for c in ['Final Touching Reporting Date & Time', 'Reporting Date & Time', 'Reporting Date', 'Desp. Date & Time'] if c in df.columns), None)
    if not final_rep_col: final_rep_col = next((c for c in df.columns if 'report' in c.lower() or 'desp' in c.lower() or 'date' in c.lower()), None)

    temp_df = df.copy()
    if final_rep_col: reported_df = temp_df[~temp_df[final_rep_col].apply(is_blank)].copy()
    else: reported_df = temp_df.copy()

    if reported_df.empty:
        st.warning("Selected data khali hai.")
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

    if staff_filter:
        selected_staff = staff_filter
        st.info(f"🔒 Logged in as Staff View: **{selected_staff}**")
        selected_client_report, selected_delay_hours, selected_remarks_filter = "ALL", "ALL", "ALL"
        selected_month, selected_date, delay_filter, selected_weeks = "ALL", "ALL", "ALL Reported Vehicles", []
    else:
        st.markdown("<h3 style='color:#48cae4; font-size:18px;'>🔍 Live Data Filters</h3>", unsafe_allow_html=True)
        f_col1, f_col2, f_col3, f_col4, f_col5, f_col6, f_col7 = st.columns(7)
        with f_col1: selected_date = st.selectbox("📅 Date:", date_options, index=0, key=f"d_{unique_key}")
        with f_col2: selected_month = st.selectbox("🗓️ Month:", month_options, index=0, key=f"m_{unique_key}")
        with f_col3: delay_filter = st.selectbox("🚨 Status:", ["ALL Reported Vehicles", "Only Delay", "Only On-Time"], index=0, key=f"s_{unique_key}")
        with f_col4: selected_staff = st.selectbox("👨‍💼 Staff:", ["ALL"] + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"], index=0, key=f"st_{unique_key}")
        with f_col5: selected_client_report = st.selectbox("🏢 Client:", ["ALL"] + sorted([str(x).strip() for x in reported_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in reported_df.columns else ["ALL"], index=0, key=f"c_{unique_key}")
        with f_col6: selected_delay_hours = st.selectbox("⏱️ Delay Hrs:", ["ALL", "Delay < 10 mins", "Delay < 30 mins", "Delay <= 1 hour"], index=0, key=f"dh_{unique_key}")
        with f_col7: selected_remarks_filter = st.selectbox("📝 Remarks:", ["ALL", "With Remarks", "Without Remarks (Empty)", "Delay + Without Remarks"], index=0, key=f"r_{unique_key}")

        strict_week_options = ["Last 1 Week", "Last 2 Weeks", "Last 3 Weeks", "Last 4 Weeks"]
        available_weeks = [w for w in strict_week_options if w in reported_df['_Rel_Week'].unique()]
        selected_weeks = []
        if available_weeks:
            st.markdown("<div style='font-size: 13px; color: #8892b0; margin-bottom: 5px; margin-top:10px;'>Filter by Week:</div>", unsafe_allow_html=True)
            chk_cols = st.columns(len(strict_week_options))
            for i, wk in enumerate(strict_week_options):
                with chk_cols[i]:
                    if st.checkbox(wk, key=f"w_{unique_key}_{wk}"): selected_weeks.append(wk)

    filtered_report_df = reported_df.copy()
    late_col = next((c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in filtered_report_df.columns), None)
    remark_col = next((c for c in ['Tracking Remark', 'Remark', 'Remarks'] if c in filtered_report_df.columns), None)

    if not staff_filter:
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
                    if "1" in selected_delay_hours: return mins <= 60
                    return False
                filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(check_delay)]

        if selected_remarks_filter != "ALL" and remark_col:
            valid_indices = []
            for idx, row in filtered_report_df.iterrows():
                is_empty = is_blank(row.get(remark_col, None))
                is_delayed = not is_zero_late(row.get(late_col, 0)) if late_col else True
                if selected_remarks_filter == "With Remarks" and not is_empty: valid_indices.append(idx)
                elif selected_remarks_filter == "Without Remarks (Empty)" and is_empty: valid_indices.append(idx)
                elif selected_remarks_filter == "Delay + Without Remarks" and is_delayed and is_empty: valid_indices.append(idx)
            filtered_report_df = filtered_report_df.loc[valid_indices]

        if selected_staff != "ALL" and staff_col: filtered_report_df = filtered_report_df[filtered_report_df[staff_col].astype(str).str.strip() == selected_staff]
        if selected_client_report != "ALL" and client_col_name in filtered_report_df.columns: filtered_report_df = filtered_report_df[filtered_report_df[client_col_name].astype(str).str.strip() == selected_client_report]
    else:
        if staff_col: filtered_report_df = filtered_report_df[filtered_report_df[staff_col].astype(str).str.strip() == staff_filter]

    if filtered_report_df.empty:
        st.info("No data found for the selected filters.")
        return

    # ================= CALL SMART BUILT-IN INSIGHTS =================
    render_smart_insights(filtered_report_df, late_col, client_col_name)

    # EXACT USER SPECIFIED COLUMNS FILTERING
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

    st.markdown(render_html_table(final_report_df), unsafe_allow_html=True)

    excel_bytes_reported = to_excel_bytes({'Reported_Vehicles': final_report_df})
    st.download_button(label=f"📥 Download Filtered Excel", data=excel_bytes_reported, file_name="Reported_Vehicles.xlsx", mime=EXCEL_MIME, type="primary", key=f"dl_{unique_key}")

    if staff_filter: return

    # ================= VEHICLE-WISE PERFORMANCE SECTION =================
    st.markdown("<br><h3 style='color:#48cae4; font-size:22px; margin-bottom:15px;'>🚛 Vehicle-wise Trip Closed Performance</h3>", unsafe_allow_html=True)

    lorry_col = next((c for c in reported_df.columns if c.lower().strip() in ['lorry no.', 'lorry no', 'vehicle no', 'vehicle', 'truck']), None)
    if not lorry_col: lorry_col = next((c for c in reported_df.columns if any(k in c.lower() for k in ['lorry', 'vehicle', 'truck'])) , None)
    from_col = next((c for c in reported_df.columns if c.lower().strip() in ['from', 'source', 'origin']), None)
    dest_col = next((c for c in reported_df.columns if c.lower().strip() in ['destination', 'to']), None)
    group_col = next((c for c in reported_df.columns if str(c).strip().lower() == 'group name'), None)
    if not group_col: group_col = next((c for c in reported_df.columns if 'group' in str(c).lower()), None)

    if lorry_col and late_col:
        temp_veh_df = reported_df.copy()
        if from_col and dest_col: temp_veh_df['Route'] = temp_veh_df[from_col].astype(str).str.strip() + " ➔ " + temp_veh_df[dest_col].astype(str).str.strip()
        else: temp_veh_df['Route'] = "N/A"

        v_f1, v_f2, v_f3, v_f4 = st.columns(4)
        veh_staff_list = ["ALL"] + sorted([str(x).strip() for x in temp_veh_df[staff_col].dropna().unique() if str(x).strip() != ""]) if staff_col else ["ALL"]
        veh_client_list = ["ALL"] + sorted([str(x).strip() for x in temp_veh_df[client_col_name].dropna().unique() if str(x).strip() != ""]) if client_col_name in temp_veh_df.columns else ["ALL"]
        veh_group_list = ["ALL"] + sorted([str(x).strip() for x in temp_veh_df[group_col].dropna().unique() if str(x).strip() != ""]) if group_col else ["ALL"]
        
        with v_f1: sel_veh_staff = st.selectbox("👨‍💼 Controlling Staff:", veh_staff_list, key=f"vs_{unique_key}")
        with v_f2: sel_veh_client = st.selectbox("🏢 Client:", veh_client_list, key=f"vc_{unique_key}")
        with v_f3: sel_veh_group = st.selectbox("🏷️ Group Name:", veh_group_list, key=f"vg_{unique_key}")
        with v_f4: sel_veh_status = st.selectbox("⚖️ Delay/On-time:", ["ALL", "Only On-Time", "Only Delay"], key=f"vst_{unique_key}")

        veh_df = temp_veh_df.copy()
        if sel_veh_staff != "ALL" and staff_col: veh_df = veh_df[veh_df[staff_col].astype(str).str.strip() == sel_veh_staff]
        if sel_veh_client != "ALL" and client_col_name in veh_df.columns: veh_df = veh_df[veh_df[client_col_name].astype(str).str.strip() == sel_veh_client]
        if sel_veh_group != "ALL" and group_col: veh_df = veh_df[veh_df[group_col].astype(str).str.strip() == sel_veh_group]

        veh_df['Is_OnTime'] = veh_df[late_col].apply(is_zero_late)
        veh_df['Is_Delay'] = ~veh_df[late_col].apply(is_zero_late)

        if sel_veh_status == "Only On-Time": veh_df = veh_df[veh_df['Is_OnTime']]
        elif sel_veh_status == "Only Delay": veh_df = veh_df[veh_df['Is_Delay']]

        veh_groups = veh_df.groupby([lorry_col, 'Route']).agg(Total=('Is_OnTime', 'count'), OnTime=('Is_OnTime', 'sum'), Delay=('Is_Delay', 'sum')).reset_index()
        veh_summary_df = veh_groups.copy()
        veh_summary_df['On-Time %'] = veh_summary_df.apply(lambda r: f"{round((r['OnTime'] / r['Total']) * 100, 1)}%" if r['Total'] > 0 else "0.0%", axis=1)
        veh_summary_df = veh_summary_df.rename(columns={lorry_col: 'Vehicle No.', 'Route': 'Route (From ➔ Destination)', 'Total': 'Total Trips', 'OnTime': 'On-Time Trips', 'Delay': 'Delay Trips'})
        veh_summary_df = veh_summary_df.sort_values(by='Total Trips', ascending=False)
        veh_summary_df.insert(0, 'S.No', range(1, 1 + len(veh_summary_df)))

        if not veh_summary_df.empty:
            st.markdown(render_html_table(veh_summary_df), unsafe_allow_html=True)
        else:
            st.info("No records found for Vehicle Performance.")


# ================= FILE PROCESSING =================
def process_uploaded_files(uploaded_files):
    callout_dfs, mis_dfs = [], []
    for uploaded_file in uploaded_files:
        try:
            filename_lower = uploaded_file.name.lower()
            temp_df = None
            if filename_lower.endswith('.csv'):
                for enc in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        uploaded_file.seek(0)
                        temp_df = pd.read_csv(uploaded_file, low_memory=False, encoding=enc)
                        break
                    except: continue
            else:
                temp_df = pd.read_excel(uploaded_file)

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
    # 🌟 ULTRA PREMIUM ANIMATED HEADING 🌟
    st.markdown("<h1 class='premium-title'>🚀 Sales Manager Live Monitoring Dashboard</h1>", unsafe_allow_html=True)

    if 'stored_mis_df' not in st.session_state: st.session_state.stored_mis_df = pd.read_pickle(MIS_PATH) if os.path.exists(MIS_PATH) else pd.DataFrame()
    if 'stored_callout_df' not in st.session_state: st.session_state.stored_callout_df = pd.read_pickle(CALLOUT_PATH) if os.path.exists(CALLOUT_PATH) else pd.DataFrame()

    st.sidebar.markdown("<h2 style='color:#64ffda; font-size:18px; margin-top:10px;'>📁 Data Management</h2>", unsafe_allow_html=True)
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

    st.sidebar.markdown("---")
    st.sidebar.markdown("<h2 style='color:#64ffda; font-size:18px;'>📊 Application Views</h2>", unsafe_allow_html=True)
    
    app_mode = st.sidebar.selectbox("Navigate To:", ["Main MIS Dashboard", "Callout Summary", "Staff Login Portal"])

    callout_df = st.session_state.stored_callout_df
    mis_df = st.session_state.stored_mis_df

    if mis_df.empty and callout_df.empty:
        st.info("👋 Welcome! Please upload your MIS or Callout files in the sidebar and click 'Process & Save Data' to start.")
        return

    if app_mode == "Main MIS Dashboard":
        if not mis_df.empty:
            show_reported_vehicle_table(mis_df, unique_key="main")
        else:
            st.warning("Koi MIS data available nahi hai.")

    elif app_mode == "Callout Summary":
        st.markdown("<h2 style='color:#f72585;'>⚠️ Callout / Breakdown Summary</h2>", unsafe_allow_html=True)
        if not callout_df.empty:
            st.metric("TOTAL CALLOUT COUNT", len(callout_df))
            st.markdown(render_html_table(callout_df), unsafe_allow_html=True)
        else:
            st.info("Koi Callout data available nahi hai.")

    elif app_mode == "Staff Login Portal":
        st.markdown("<h2 style='color:#48cae4;'>🔒 Staff Login Portal</h2>", unsafe_allow_html=True)
        staff_col = next((c for c in mis_df.columns if 'controlling' in c.lower() or 'staff' in c.lower()), None)
        if staff_col and not mis_df.empty:
            staff_names = sorted([str(x).strip() for x in mis_df[staff_col].dropna().unique() if str(x).strip() != ""])
            selected_staff = st.selectbox("Select Staff Member", staff_names)
            if selected_staff:
                show_reported_vehicle_table(mis_df, unique_key="staff", staff_filter=selected_staff)

if __name__ == '__main__':
    main()
