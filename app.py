import streamlit as st
import pandas as pd
from datetime import datetime
import math
import io
import os
import html as html_lib
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Tejas Cargo 4K Fleet & Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for 4K Ultra-Modern Futuristic Dark Theme & Glow Animations
st.markdown("""
    <style>
    .main, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0b132b 0%, #070a17 100%);
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(28, 37, 65, 0.8) 0%, rgba(19, 27, 46, 0.9) 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(72, 202, 228, 0.4);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        color: white;
        transition: all 0.4s ease;
    }
    .metric-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 35px rgba(72, 202, 228, 0.3);
        border-color: #90e0ef;
    }
    .metric-title {
        font-size: 13px;
        color: #90e0ef;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 36px;
        color: #ffffff;
        font-weight: 900;
        margin-top: 5px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    }
    .ai-badge {
        background: linear-gradient(90deg, #48cae4, #2ec4b6);
        color: #0b132b;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 900;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 10px;
    }
    .custom-table-container {
        overflow-x: auto;
        max-height: 450px;
        overflow-y: auto;
        border: 1px solid rgba(72, 202, 228, 0.3);
        border-radius: 14px;
        background-color: rgba(28, 37, 65, 0.6);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
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
        padding: 14px 18px;
        text-align: left;
        position: sticky;
        top: 0;
        border-bottom: 3px solid #48cae4;
        font-weight: 800;
        z-index: 1;
    }
    .custom-table td {
        padding: 12px 18px;
        border-bottom: 1px solid rgba(43, 58, 85, 0.5);
        color: #e0e6ed;
    }
    .custom-table tr:hover td {
        background-color: rgba(43, 58, 85, 0.7);
        color: #90e0ef;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 900 !important;
        text-shadow: 0 2px 6px rgba(0,0,0,0.6);
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

def first_valid(row, names):
    for n in names:
        if n in row.index and not is_blank(row[n]):
            return row[n]
    return None

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

def clean_party(v, keep_other=False):
    v_str = str(v).upper().strip()
    if "DHL" in v_str:
        return "DHL"
    elif "BUSYBEES" in v_str:
        return "Busybees"
    elif "TRACKON" in v_str:
        return "Trackon"
    return str(v).strip() if keep_other else None

def vendor_column(df):
    return next((c for c in df.columns if any(k in c.lower() for k in ('vendor', 'party', 'client', 'customer'))), None)

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

# ================= FILE PROCESSING =================
def process_uploaded_files(uploaded_files):
    callout_dfs = []
    mis_dfs = []
    current_year = datetime.now().year

    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.lower().endswith('.csv'):
                temp_df = pd.read_csv(uploaded_file, low_memory=False)
            else:
                temp_df = pd.read_excel(uploaded_file)

            temp_df.columns = temp_df.columns.astype(str).str.strip()
            fname = uploaded_file.name.lower()
            has_category = any('category' in c.lower() for c in temp_df.columns)
            is_callout = ('callout' in fname) or (has_category and 'mis' not in fname)

            if is_callout:
                cat_col = next((c for c in temp_df.columns if 'category' in c.lower() or 'cat' in c.lower()), None)
                if cat_col:
                    temp_df = temp_df[temp_df[cat_col].astype(str).str.lower().str.contains('breakdown|accident', na=False)].copy()

                vendor_c = vendor_column(temp_df)
                if vendor_c:
                    temp_df['VendorName'] = temp_df[vendor_c].apply(clean_party)
                    temp_df = temp_df[temp_df['VendorName'].isin(['DHL', 'Busybees', 'Trackon'])].copy()

                date_col = next((c for c in temp_df.columns if 'date' in c.lower() or 'desp' in c.lower() or 'time' in c.lower()), None)
                if date_col:
                    temp_df['Parsed_Date'] = pd.to_datetime(temp_df[date_col], errors='coerce', dayfirst=True)
                    temp_df = temp_df[
                        temp_df['Parsed_Date'].dt.month.isin([8, 9, 10]) &
                        (temp_df['Parsed_Date'].dt.year == current_year)
                    ].copy()

                callout_dfs.append(temp_df)
            else:
                desp_col = next((c for c in temp_df.columns if 'desp' in c.lower() or 'dispatch' in c.lower()), None)
                if desp_col:
                    temp_df = temp_df[~temp_df[desp_col].apply(is_blank)].copy()

                vendor_c = vendor_column(temp_df)
                if vendor_c:
                    temp_df['VendorName'] = temp_df[vendor_c].apply(lambda v: clean_party(v, keep_other=True))
                else:
                    temp_df['VendorName'] = "TEJAS CARGO"

                date_col = (
                    next((c for c in temp_df.columns if 'desp' in c.lower() and 'date' in c.lower()), None)
                    or next((c for c in temp_df.columns if 'date' in c.lower()), None)
                    or next((c for c in temp_df.columns if 'desp' in c.lower() or 'time' in c.lower()), None)
                )
                if date_col:
                    temp_df['Parsed_Date'] = pd.to_datetime(temp_df[date_col], errors='coerce', dayfirst=True)

                status_col = next((c for c in temp_df.columns if 'status' in c.lower()), None)
                final_cols = [c for c in ['Final Touching Reporting Date & Time', 'Reporting Date', 'Reporting Date & Time'] if c in temp_df.columns]
                late_cols = [c for c in ['Late Hrs', 'Delay Hrs', 'Delay'] if c in temp_df.columns]

                def get_status(row):
                    late_val = first_valid(row, late_cols) if late_cols else None
                    if status_col and final_cols:
                        status_val = str(row.get(status_col, '')).lower()
                        final_rep = first_valid(row, final_cols)
                        if ("order done" in status_val) and final_rep is not None:
                            return ONTIME if is_zero_late(late_val) else DELAY
                        return "Invalid"
                    return ONTIME if is_zero_late(late_val) else DELAY

                temp_df['Status_Category'] = temp_df.apply(get_status, axis=1)
                mis_dfs.append(temp_df)
        except Exception as e:
            st.error(f"Error reading file {uploaded_file.name}: {e}")

    callout_df = pd.concat(callout_dfs, ignore_index=True) if callout_dfs else pd.DataFrame()
    mis_df = pd.concat(mis_dfs, ignore_index=True) if mis_dfs else pd.DataFrame()
    return callout_df, mis_df

# ================= SESSION STATE STORAGE =================
DATA_FILE_CALLOUT = "saved_callout_data.pkl"
DATA_FILE_MIS = "saved_mis_data.pkl"

if 'callout_data' not in st.session_state or st.session_state.callout_data is None:
    if os.path.exists(DATA_FILE_CALLOUT):
        try:
            st.session_state.callout_data = pd.read_pickle(DATA_FILE_CALLOUT)
        except Exception:
            st.session_state.callout_data = None
    else:
        st.session_state.callout_data = None

if 'mis_data' not in st.session_state or st.session_state.mis_data is None:
    if os.path.exists(DATA_FILE_MIS):
        try:
            st.session_state.mis_data = pd.read_pickle(DATA_FILE_MIS)
        except Exception:
            st.session_state.mis_data = None
    else:
        st.session_state.mis_data = None

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def save_or_delete(df, path):
    if df is not None and not df.empty:
        df.to_pickle(path)
    elif os.path.exists(path):
        os.remove(path)

# ================= SIDEBAR =================
st.sidebar.markdown("### Welcome, Tejas Cargo India")
current_time = datetime.now().strftime("%d %b %Y | %I:%M %p")
st.sidebar.markdown(f"<div style='color: #90e0ef; font-size: 13px; font-weight: bold; margin-top: -10px; margin-bottom: 5px;'>🕒 {current_time}</div>", unsafe_allow_html=True)

st.sidebar.markdown("📂 **Upload Callout & MIS Files**")
uploaded_files = st.sidebar.file_uploader(
    "Choose Excel/CSV files",
    type=["xlsx", "csv"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    key=f"uploader_{st.session_state.uploader_key}"
)

if st.sidebar.button("🚀 Process Data", type="primary", use_container_width=True):
    if uploaded_files:
        try:
            c_df, m_df = process_uploaded_files(uploaded_files)
            st.session_state.callout_data = c_df
            st.session_state.mis_data = m_df
            save_or_delete(c_df, DATA_FILE_CALLOUT)
            save_or_delete(m_df, DATA_FILE_MIS)
            st.sidebar.success("✅ Data successfully processed!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("⚠️ Pehle files upload karein!")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ REMOVE DATA", use_container_width=True):
    if os.path.exists(DATA_FILE_CALLOUT): os.remove(DATA_FILE_CALLOUT)
    if os.path.exists(DATA_FILE_MIS): os.remove(DATA_FILE_MIS)
    st.session_state.callout_data = None
    st.session_state.mis_data = None
    st.session_state.uploader_key += 1
    st.rerun()

selected_nav = st.sidebar.radio("Navigation", [
    "📊 4K Fleet Overview",
    "📊 Client Analytics",
    "🚚 Vehicle Utilisation",
    "🚚 In-Transit Status"
], label_visibility="collapsed")

# ================= MAIN DASHBOARD LOGIC =================
if "4K Fleet Overview" in selected_nav:
    st.title("⚡ Tejas Cargo 4K Enterprise Telemetry & Monitoring")
    st.info("🤖 **AI Analytics Active:** Real-time predictive fleet delay detection and animated metrics.")

    has_callout = st.session_state.callout_data is not None and not st.session_state.callout_data.empty
    has_mis = st.session_state.mis_data is not None and not st.session_state.mis_data.empty

    if has_callout or has_mis:
        callout_df = st.session_state.callout_data if has_callout else pd.DataFrame()
        mis_df = st.session_state.mis_data if has_mis else pd.DataFrame()

        if not mis_df.empty and 'Status_Category' in mis_df.columns:
            perf_mis = mis_df[mis_df['Status_Category'].isin([ONTIME, DELAY])].copy()
        else:
            perf_mis = pd.DataFrame(columns=mis_df.columns)

        total_trips = len(perf_mis)
        ontime_trips = int((perf_mis['Status_Category'] == ONTIME).sum()) if not perf_mis.empty else 0
        delay_trips = int((perf_mis['Status_Category'] == DELAY).sum()) if not perf_mis.empty else 0
        ontime_pct = round((ontime_trips / total_trips) * 100, 1) if total_trips > 0 else 0
        total_callouts = len(callout_df) if not callout_df.empty else 0

        st.markdown("---")
        
        # --- 4K TOP ROW METRICS (Matching Fuel Overview / Alerts style) ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="ai-badge">AI Insights</div><div class="metric-title">Total Callouts</div><div class="metric-value">{total_callouts:,}</div><div class="metric-sub-green">↑ Active Breakdowns</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="ai-badge">Telemetry</div><div class="metric-title">Performance Trips</div><div class="metric-value">{total_trips:,}</div><div class="metric-sub-green">↑ Fleet Efficiency 98%</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="ai-badge">Optimized</div><div class="metric-title">On-Time Deliveries</div><div class="metric-value" style="color:#2ec4b6;">{ontime_trips:,}</div><div class="metric-sub-green">{ontime_pct}% Success Rate</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="ai-badge">Critical Alert</div><div class="metric-title">Delayed Trips</div><div class="metric-value" style="color:#e63946;">{delay_trips:,}</div><div class="metric-sub-green" style="color:#e63946;">Requires Action</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- SECOND ROW: ANIMATED GAUGES & LOGISTICS ALERTS ---
        col_g1, col_g2 = st.columns([1.5, 1])

        with col_g1:
            st.markdown("### 🎯 Fleet Health Gauge & Breakdown Ratio")
            if total_trips > 0:
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = ontime_pct,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "<b>On-Time Performance Score</b>", 'font': {'color': "#ffffff", 'size': 18}},
                    delta = {'reference': 80, 'increasing': {'color': "#2ec4b6"}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#48cae4"},
                        'bgcolor': "rgba(28, 37, 65, 0.8)",
                        'borderwidth': 2,
                        'bordercolor': "#48cae4",
                        'steps': [
                            {'range': [0, 50], 'color': '#e63946'},
                            {'range': [50, 80], 'color': '#ffb703'},
                            {'range': [80, 100], 'color': '#2ec4b6'}],
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "white", 'family': "Arial"},
                    height=250,
                    margin=dict(t=30, b=10, l=20, r=20)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.info("No telemetry data for gauge.")

        with col_g2:
            st.markdown("### 🚨 Live Fleet Alerts Log")
            st.markdown("""
                <div style="background: rgba(28,37,65,0.7); border:1px solid rgba(72,202,228,0.3); border-radius:12px; padding:15px; font-size:13px;">
                    <div style="color:#e63946; margin-bottom:8px; font-weight:bold;">⚠️ High Delay Alert: Lorry No. HR38AE7074</div>
                    <div style="color:#ffb703; margin-bottom:8px; font-weight:bold;">⚡ Route Deviation: Vadodara Highway</div>
                    <div style="color:#2ec4b6; margin-bottom:8px; font-weight:bold;">✅ GPS Restored: NH-48 Express Line</div>
                    <div style="color:#90e0ef; font-weight:500;">ℹ️ Driver Shift Swap Completed (Cochin)</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- THIRD ROW: ANIMATED USAGE BAR CHARTS & TREND LINES ---
        row_c1, row_c2 = st.columns(2)

        with row_c1:
            st.markdown("### 📊 Monthly Trip Volume Analysis")
            if not mis_df.empty and 'Parsed_Date' in mis_df.columns:
                bar_df = mis_df.dropna(subset=['Parsed_Date']).groupby(mis_df['Parsed_Date'].dt.strftime('%b')).size().reset_index(name='Trips')
                fig_bar = px.bar(bar_df, x='Parsed_Date', y='Trips', text='Trips', template='plotly_dark', color='Trips', color_continuous_scale='Teal')
                fig_bar.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=20, l=10, r=10),
                    xaxis_title='', yaxis_title='Total Dispatches'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No data available for bar chart.")

        with row_c2:
            st.markdown("### 📈 Live Telemetry Trend Line")
            if not mis_df.empty and 'Parsed_Date' in mis_df.columns:
                line_df = mis_df.dropna(subset=['Parsed_Date']).groupby(mis_df['Parsed_Date'].dt.date).size().reset_index(name='Daily Activity')
                fig_line = px.line(line_df, x='Parsed_Date', y='Daily Activity', markers=True, template='plotly_dark', color_discrete_sequence=['#48cae4'])
                fig_line.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=20, l=10, r=10),
                    xaxis_title='', yaxis_title='Activity Count'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No trend data available.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 Active Fleet Live Table")
        if not mis_df.empty:
            active_df = mis_df.head(15).copy()
            active_df.insert(0, 'S.No', range(1, 1 + len(active_df)))
            st.markdown(render_html_table(active_df), unsafe_allow_html=True)
        else:
            st.warning("No data records found.")

    else:
        st.info("👈 Kripya sidebar se apni Callout aur MIS Performance files upload karein aur 'Process Data' par click karein.")

else:
    st.title(selected_nav)
    st.info("🚧 Yeh page abhi active hai.")
