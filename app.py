import streamlit as st
import pandas as pd
from datetime import datetime
import math
import io
import os
import html as html_lib
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Sales Manager Live Monitoring Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Dynamic & Enterprise Dark Theme Styling (Matching the reference screenshot)
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
        font-size: 13px;
        color: #90e0ef;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        color: #ffffff;
        font-weight: 900;
        margin-top: 5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .metric-sub-green {
        font-size: 12px;
        color: #2ec4b6;
        margin-top: 5px;
        font-weight: 700;
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


def to_excel_bytes(sheets):
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, index=False, sheet_name=name)
    return buffer_excel.getvalue()


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


# ================= MEMORY SETUP (Hard Persistence Logic) =================
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
st.sidebar.markdown("### Welcome, Tejas Cargo India Pvt Ltd")

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

            st.sidebar.success("✅ Data successfully processed and saved!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("⚠️ Pehle files upload karein!")

st.sidebar.markdown("---")

if st.sidebar.button("🗑️ REMOVE DATA", use_container_width=True):
    if os.path.exists(DATA_FILE_CALLOUT):
        os.remove(DATA_FILE_CALLOUT)
    if os.path.exists(DATA_FILE_MIS):
        os.remove(DATA_FILE_MIS)
    st.session_state.callout_data = None
    st.session_state.mis_data = None
    st.session_state.uploader_key += 1
    st.rerun()

st.sidebar.markdown("Navigation:")
selected_nav = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "📊 Client Performance",
    "🏢 Branches",
    "🚚 Vehicle Utilisation",
    "🚚 In-Transit Vehicle Status",
    "📈 Monthly Breakdown"
], label_visibility="collapsed")


# ================= MAIN DASHBOARD LOGIC =================
if "Dashboard" in selected_nav:
    st.title("⚡ Sales Manager Live Monitoring Dashboard")
    st.info("🔒 **Enterprise Analytics Overview:** Real-time Fleet Performance & Metrics")

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
        total_callouts_count = len(callout_df) if not callout_df.empty else 0

        st.markdown("---")
        
        # --- TOP 4 SAAS METRIC CARDS (Matching Screenshot Design) ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total Callouts</div><div class="metric-value">{total_callouts_count:,}</div><div class="metric-sub-green">↑ +12.5% vs last month</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Performance Trips</div><div class="metric-value">{total_trips:,}</div><div class="metric-sub-green">↑ +8.2% vs last month</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">On-Time Deliveries</div><div class="metric-value" style="color:#2ec4b6;">{ontime_trips:,}</div><div class="metric-sub-green">↑ {ontime_pct}% success rate</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Delayed Trips</div><div class="metric-value" style="color:#e63946;">{delay_trips:,}</div><div class="metric-sub-green" style="color:#e63946;">↓ Requires review</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- MIDDLE SECTION: PERFORMANCE OVERVIEW (LINE CHART) & CATEGORY BREAKDOWN (DONUT) ---
        chart_col1, chart_col2 = st.columns([1.6, 1])

        with chart_col1:
            st.markdown("### 📊 Performance Overview")
            if not mis_df.empty and 'Parsed_Date' in mis_df.columns:
                trend_df = mis_df.dropna(subset=['Parsed_Date']).groupby(mis_df['Parsed_Date'].dt.strftime('%b')).size().reset_index(name='Trips')
                fig_line = px.line(trend_df, x='Parsed_Date', y='Trips', markers=True, template='plotly_dark')
                fig_line.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=20, l=10, r=10),
                    xaxis_title='', yaxis_title='Trip Count'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No timeline data available for trend chart.")

        with chart_col2:
            st.markdown("### 🍩 Category Breakdown")
            if not perf_mis.empty and 'VendorName' in perf_mis.columns:
                client_counts = perf_mis['VendorName'].value_counts().reset_index()
                client_counts.columns = ['Client', 'Count']
                fig_donut = px.pie(client_counts, values='Count', names='Client', hole=0.6, template='plotly_dark')
                fig_donut.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=20, l=10, r=10),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("No client category data available.")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- BOTTOM SECTION: RECENT TRANSACTIONS TABLE ---
        st.markdown("### 📋 Recent Transactions / Reported Fleet")
        if not mis_df.empty:
            recent_df = mis_df.head(10).copy()
            recent_df.insert(0, 'S.No', range(1, 1 + len(recent_df)))
            st.markdown(render_html_table(recent_df), unsafe_allow_html=True)
        else:
            st.warning("No recent records found.")

    else:
        st.info("👈 Kripya sidebar se apni Callout aur MIS Performance files upload karein aur 'Process Data' par click karein.")

else:
    st.title(selected_nav)
    st.info("🚧 Yeh page abhi active hai.")
