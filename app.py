import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
import html as html_lib
import pickle

# 1. Page Configuration
st.set_page_config(
    page_title="Fleet Dashboard - Glassy Motion UI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================= CUSTOM CSS FOR GLASSMORPHIC MOTION UI =================
st.markdown(
    """
    <style>
    /* 1. Deep Futuristic Glassmorphic Background */
    .main, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #131b36 0%, #070a17 70%, #020308 100%) !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* 2. Sleek Glassmorphic Sidebar with Smooth Motion */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 15px 0 35px rgba(0, 0, 0, 0.6);
        animation: slideSidebar 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes slideSidebar {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* 3. Glowing Neon 3D Typography Title */
    .premium-title {
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 15%, #38bdf8 55%, #f97316 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.8px;
        margin-bottom: 0px;
        margin-top: 0px;
        text-shadow: 0 15px 30px rgba(56, 189, 248, 0.25);
        transform: perspective(600px) translateZ(12px);
        transition: transform 0.3s ease;
    }
    
    .premium-title:hover {
        transform: perspective(600px) translateZ(22px) scale(1.01);
    }

    /* 4. Motion HUD News Ticker */
    .news-ticker-container {
        width: 100%;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.35);
        backdrop-filter: blur(20px);
        color: #f1f5f9;
        overflow: hidden;
        white-space: nowrap;
        box-sizing: border-box;
        border-radius: 18px;
        margin-bottom: 25px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(56, 189, 248, 0.08);
        position: relative;
        display: flex;
        align-items: center;
        height: 46px;
    }
    
    .ticker-label {
        background: linear-gradient(135deg, #38bdf8, #0284c7);
        color: #030712;
        font-weight: 900;
        padding: 0 18px;
        height: 100%;
        display: flex;
        align-items: center;
        position: absolute;
        left: 0;
        z-index: 10;
        border-radius: 18px 0 0 18px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 12px;
        box-shadow: 6px 0 20px rgba(0,0,0,0.4);
    }
    
    .ticker-text-wrapper {
        padding-left: 140px; 
        display: inline-block;
        white-space: nowrap;
        animation: marquee 42s linear infinite;
    }
    
    .ticker-item {
        display: inline-block;
        padding: 0 40px;
        font-size: 14px;
        font-weight: 600;
        color: #cbd5e1;
    }
    
    @keyframes marquee {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }

    /* 5. Glassmorphic Floating Selectboxes */
    [data-testid="stSelectbox"] label {
        color: #38bdf8 !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(30, 41, 59, 0.75) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        font-weight: 500;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), inset 0 0 12px rgba(56, 189, 248, 0.08);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #38bdf8 !important;
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 15px 35px rgba(56, 189, 248, 0.35);
    }

    /* 6. Fluid Motion Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #f97316, #ea580c) !important;
        border: none !important;
        color: white !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 25px rgba(249, 115, 22, 0.4), inset 0 2px 6px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        transform: perspective(400px) translateZ(0px);
    }
    
    .stButton > button:hover {
        transform: perspective(400px) translateZ(12px) translateY(-3px) scale(1.02) !important;
        box-shadow: 0 18px 40px rgba(249, 115, 22, 0.7), inset 0 2px 10px rgba(255, 255, 255, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: perspective(400px) translateZ(-5px) translateY(1px) scale(0.98) !important;
    }

    /* 7. Glassmorphic Tables with Smooth Fade-In Animation */
    .custom-table-container {
        overflow-x: auto; 
        max-height: 520px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 20px;
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(25px);
        box-shadow: 0 22px 50px rgba(0, 0, 0, 0.75), inset 0 0 25px rgba(56, 189, 248, 0.08);
        margin-bottom: 25px;
        transform: perspective(1000px);
        animation: fadeInTable 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes fadeInTable {
        from { opacity: 0; transform: perspective(1000px) rotateX(6px) translateY(25px); }
        to { opacity: 1; transform: perspective(1000px) rotateX(0deg) translateY(0); }
    }

    .custom-table { 
        width: 100%; 
        border-collapse: collapse; 
        font-size: 13.5px; 
        white-space: nowrap; 
    }
    
    .custom-table th { 
        background: rgba(30, 41, 59, 0.95); 
        color: #38bdf8; 
        padding: 15px 18px; 
        text-align: left; 
        position: sticky; 
        top: 0; 
        font-weight: 800; 
        z-index: 2; 
        border-bottom: 1px solid rgba(56, 189, 248, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-size: 11px;
    }
    
    .custom-table td { 
        padding: 13px 18px; 
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: #e2e8f0; 
        font-weight: 500;
        transition: all 0.25s ease;
    }
    
    .custom-table tr {
        transition: all 0.25s ease-in-out;
    }
    
    .custom-table tr:hover td { 
        background-color: rgba(56, 189, 248, 0.18); 
        color: #ffffff;
        box-shadow: inset 0 0 15px rgba(56, 189, 248, 0.2);
    }

    /* 8. Modern Glassy Tabs with Smooth Motion */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(15, 23, 42, 0.65);
        padding: 8px;
        border-radius: 18px;
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: inset 0 6px 15px rgba(0,0,0,0.5);
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 14px;
        font-weight: 700;
        color: #94a3b8;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.12);
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #38bdf8, #0284c7) !important;
        color: #030712 !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.55), inset 0 2px 6px rgba(255,255,255,0.5) !important;
        transform: scale(1.02);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ================= CONSTANTS & DIRECTORIES =================
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DATA_DIR = "saved_data"
os.makedirs(DATA_DIR, exist_ok=True)
MIS_PATH = os.path.join(DATA_DIR, "mis.pkl")


# ================= DATA HELPERS =================
def is_blank(v):
    if v is None:
        return True
    try:
        if pd.isna(v):
            return True
    except Exception:
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
    if s in ("0", "0.0", "00:00", "0:00"):
        return 0.0
    try:
        return pd.to_timedelta(s).total_seconds() / 60.0
    except Exception:
        pass
    try:
        return float(s) * 60.0
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
    return next(
        (c for c in df.columns if any(k in c.lower() for k in ("vendor", "party", "client", "customer"))),
        None,
    )


def render_html_table(df_to_show, max_rows=2000):
    clean_df = df_to_show.fillna("").astype(str)
    note = ""
    if len(clean_df) > max_rows:
        note = f'<div style="color:#f97316; font-size:12px; margin-bottom:6px; font-weight:700;">⚡ Showing first {max_rows} rows for performance. Download Excel for full data.</div>'
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
    with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, index=False, sheet_name=name)
    return buffer_excel.getvalue()


# ================= NEWS TICKER COMPONENT =================
def render_news_ticker(df):
    if df.empty:
        ticker_text = "⚡ GLASSY MOTION COCKPIT READY... WAITING FOR DATA UPLOAD... PLEASE UPLOAD MIS FILE FROM SIDEBAR..."
    else:
        late_col = next((c for c in ["Late Hrs", "Delay Hrs", "Delay"] if c in df.columns), None)
        staff_col = next((c for c in df.columns if "controlling" in c.lower() or "staff" in c.lower()), None)
        client_col = vendor_column(df)

        if late_col:
            total = len(df)
            delayed = len(df[~df[late_col].apply(is_zero_late)])
            on_time_pct = round(((total - delayed) / total) * 100, 1) if total > 0 else 0

            staff_text = ""
            if staff_col:
                top_staff = df[staff_col].value_counts()
                if not top_staff.empty:
                    staff_text = f" | 👨‍💼 TOP STAFF: {top_staff.index[0]} ({top_staff.iloc[0]} Trips)"

            client_text = ""
            if client_col:
                top_client = df[client_col].value_counts()
                if not top_client.empty:
                    client_text = f" | 🏢 TOP CLIENT: {top_client.index[0]} ({top_client.iloc[0]} Trips)"

            ticker_text = f"🚀 MOTION HUD STATUS: Total Trips: {total} | ✅ On-Time: {on_time_pct}% | ⚠️ Delayed: {delayed}{staff_text}{client_text}"
        else:
            ticker_text = f"🚀 MOTION HUD: Active Trips: {len(df)} | 🟢 ALL SYSTEMS NORMAL"

    full_text = f"<span class='ticker-item'>{ticker_text}</span>" * 4

    html_out = f"""<div class="news-ticker-container">
<div class="ticker-label">MOTION UI</div>
<div class="ticker-text-wrapper">{full_text}</div>
</div>"""
    st.markdown(html_out, unsafe_allow_html=True)


# ================= REPORTED VEHICLE TABLE & REPORTS =================
def show_reported_vehicle_table(df, unique_key="", staff_filter=None, only_delay=False):
    final_rep_col = next(
        (
            c
            for c in [
                "Final Touching Reporting Date & Time",
                "Reporting Date & Time",
                "Reporting Date",
                "Desp. Date & Time",
            ]
            if c in df.columns
        ),
        None,
    )
    if not final_rep_col:
        final_rep_col = next(
            (c for c in df.columns if "report" in c.lower() or "desp" in c.lower() or "date" in c.lower()),
            None,
        )

    temp_df = df.copy()
    if final_rep_col:
        reported_df = temp_df[~temp_df[final_rep_col].apply(is_blank)].copy()
    else:
        reported_df = temp_df.copy()

    if reported_df.empty:
        st.warning("Selected data khali hai.")
        return

    late_col = next((c for c in ["Late Hrs", "Delay Hrs", "Delay"] if c in reported_df.columns), None)

    if only_delay and late_col:
        reported_df = reported_df[~reported_df[late_col].apply(is_zero_late)].copy()
        if reported_df.empty:
            st.info("No Delay Closed vehicles found.")
            return

    if final_rep_col:
        parsed_rep_dt = pd.to_datetime(reported_df[final_rep_col], errors="coerce", dayfirst=True)
        reported_df["_Rep_Date_Obj"] = parsed_rep_dt.dt.date
        reported_df["_Rep_Date_Str"] = parsed_rep_dt.dt.strftime("%d-%m-%Y")
        reported_df["_Month_Str"] = parsed_rep_dt.dt.strftime("%B %Y")
    else:
        reported_df["_Rep_Date_Obj"] = None
        reported_df["_Rep_Date_Str"] = "ALL"
        reported_df["_Month_Str"] = "ALL"

    current_dt = datetime.now().date()

    def get_relative_week(row_date):
        if pd.isna(row_date):
            return None
        diff = (current_dt - row_date).days
        if diff < 0:
            return "Current / Future"
        elif diff <= 7:
            return "Last 1 Week"
        elif diff <= 14:
            return "Last 2 Weeks"
        elif diff <= 21:
            return "Last 3 Weeks"
        elif diff <= 28:
            return "Last 4 Weeks"
        return None

    reported_df["_Rel_Week"] = reported_df["_Rep_Date_Obj"].apply(get_relative_week)

    valid_dates = (
        reported_df[reported_df["_Rep_Date_Obj"].notna()]
        .drop_duplicates(subset=["_Rep_Date_Str"])
        .sort_values("_Rep_Date_Obj", ascending=False)
    )
    date_options = ["ALL"] + valid_dates["_Rep_Date_Str"].tolist()
    valid_months = (
        reported_df[reported_df["_Rep_Date_Obj"].notna()]
        .drop_duplicates(subset=["_Month_Str"])
        .sort_values("_Rep_Date_Obj", ascending=False)
    )
    month_options = ["ALL"] + valid_months["_Month_Str"].tolist()

    staff_col = next((c for c in reported_df.columns if "controlling" in c.lower() or "staff" in c.lower()), None)
    client_col_name = vendor_column(reported_df) or "VendorName"

    if staff_filter:
        selected_staff = staff_filter
        st.info(f"🔒 Staff View Active: **{selected_staff}**")
        selected_client_report, selected_delay_hours, selected_remarks_filter = "ALL", "ALL", "ALL"
        selected_month, selected_date, delay_filter, selected_weeks = "ALL", "ALL", "ALL Reported Vehicles", []
    else:
        st.markdown(
            "<h3 style='color:#38bdf8; font-size:16px; font-weight:700;'>🔍 Motion UI Filters</h3>",
            unsafe_allow_html=True,
        )
        f_col1, f_col2, f_col3, f_col4, f_col5, f_col6, f_col7 = st.columns(7)
        with f_col1:
            selected_date = st.selectbox("📅 Date", date_options, index=0, key=f"d_{unique_key}")
        with f_col2:
            selected_month = st.selectbox("🗓️ Month", month_options, index=0, key=f"m_{unique_key}")
        with f_col3:
            delay_filter = st.selectbox(
                "🚨 Status", ["ALL Reported Vehicles", "Only Delay", "Only On-Time"], index=0, key=f"s_{unique_key}"
            )
        with f_col4:
            selected_staff = st.selectbox(
                "👨‍💼 Staff",
                ["ALL"]
                + sorted([str(x).strip() for x in reported_df[staff_col].dropna().unique() if str(x).strip() != ""])
                if staff_col
                else ["ALL"],
                index=0,
                key=f"st_{unique_key}",
            )
        with f_col5:
            selected_client_report = st.selectbox(
                "🏢 Client",
                ["ALL"]
                + sorted(
                    [
                        str(x).strip()
                        for x in reported_df[client_col_name].dropna().unique()
                        if str(x).strip() != ""
                    ]
                )
                if client_col_name in reported_df.columns
                else ["ALL"],
                index=0,
                key=f"c_{unique_key}",
            )
        with f_col6:
            selected_delay_hours = st.selectbox(
                "⏱️ Delay Hrs", ["ALL", "Delay < 10 mins", "Delay < 30 mins", "Delay <= 1 hour"], index=0, key=f"dh_{unique_key}"
            )
        with f_col7:
            selected_remarks_filter = st.selectbox(
                "📝 Remarks", ["ALL", "With Remarks", "Without Remarks (Empty)", "Delay + Without Remarks"], index=0, key=f"r_{unique_key}"
            )

        strict_week_options = ["Last 1 Week", "Last 2 Weeks", "Last 3 Weeks", "Last 4 Weeks"]
        available_weeks = [w for w in strict_week_options if w in reported_df["_Rel_Week"].unique()]
        selected_weeks = []
        if available_weeks:
            st.markdown(
                "<div style='font-size: 13px; color: #94a3b8; margin-bottom: 5px; margin-top:10px; font-weight:600;'>Filter by Week:</div>",
                unsafe_allow_html=True,
            )
            chk_cols = st.columns(len(strict_week_options))
            for i, wk in enumerate(strict_week_options):
                with chk_cols[i]:
                    if st.checkbox(wk, key=f"w_{unique_key}_{wk}"):
                        selected_weeks.append(wk)

    filtered_report_df = reported_df.copy()
    remark_col = next((c for c in ["Tracking Remark", "Remark", "Remarks"] if c in filtered_report_df.columns), None)

    if not staff_filter:
        if selected_date != "ALL":
            filtered_report_df = filtered_report_df[filtered_report_df["_Rep_Date_Str"] == selected_date]
        if selected_month != "ALL":
            filtered_report_df = filtered_report_df[filtered_report_df["_Month_Str"] == selected_month]
        if selected_weeks:
            filtered_report_df = filtered_report_df[filtered_report_df["_Rel_Week"].isin(selected_weeks)]

        if late_col and not only_delay:
            if delay_filter == "Only Delay":
                filtered_report_df = filtered_report_df[~filtered_report_df[late_col].apply(is_zero_late)]
            elif delay_filter == "Only On-Time":
                filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(is_zero_late)]

            if selected_delay_hours != "ALL":
                def check_delay(val):
                    mins = get_delay_minutes(val)
                    if mins <= 0:
                        return False
                    if "10" in selected_delay_hours:
                        return mins < 10
                    if "30" in selected_delay_hours:
                        return mins < 30
                    if "1" in selected_delay_hours:
                        return mins <= 60
                    return False

                filtered_report_df = filtered_report_df[filtered_report_df[late_col].apply(check_delay)]

        if selected_remarks_filter != "ALL" and remark_col:
            valid_indices = []
            for idx, row in filtered_report_df.iterrows():
                is_empty = is_blank(row.get(remark_col, None))
                is_delayed = not is_zero_late(row.get(late_col, 0)) if late_col else True
                if selected_remarks_filter == "With Remarks" and not is_empty:
                    valid_indices.append(idx)
                elif selected_remarks_filter == "Without Remarks (Empty)" and is_empty:
                    valid_indices.append(idx)
                elif selected_remarks_filter == "Delay + Without Remarks" and is_delayed and is_empty:
                    valid_indices.append(idx)
            filtered_report_df = filtered_report_df.loc[valid_indices]

        if selected_staff != "ALL" and staff_col:
            filtered_report_df = filtered_report_df[filtered_report_df[staff_col].astype(str).str.strip() == selected_staff]
        if selected_client_report != "ALL" and client_col_name in filtered_report_df.columns:
            filtered_report_df = filtered_report_df[filtered_report_df[client_col_name].astype(str).str.strip() == selected_client_report]
    else:
        if staff_col:
            filtered_report_df = filtered_report_df[filtered_report_df[staff_col].astype(str).str.strip() == staff_filter]

    if filtered_report_df.empty:
        st.warning("No data found for the selected filters.")
        return

    desired_cols = [
        "Lorry No.",
        "Veh.Type",
        "From",
        "Destination",
        "Party",
        "Desp. Date & Time",
        "Hrs. Given",
        "1st Touching",
        "1st Touching Reporting Date & Time",
        "1st Touching Delivery Date & Time",
        "1st Touching Hrs.",
        "2nd Touching",
        "2nd Touching Reporting Date & Time",
        "2nd Touching Delivery Date & Time",
        "2nd Touching Hrs.",
        "Final Touching Reporting Date & Time",
        "Total Touching Hrs.",
        "Hrs. Taken with touching",
        "Hrs. Taken without touching (Dly.)",
        "Late Hrs",
        "Tracking Remark",
        "Group Name",
        "Controlling Staff Name",
        "Foreman Name",
    ]

    actual_display_cols = []
    for col in desired_cols:
        matched_c = next((c for c in filtered_report_df.columns if c.lower().strip() == col.lower().strip()), None)
        if matched_c:
            actual_display_cols.append(matched_c)
        else:
            if col == "Tracking Remark":
                rem_alt = next((c for c in filtered_report_df.columns if "remark" in c.lower()), None)
                if rem_alt:
                    actual_display_cols.append(rem_alt)
            elif col == "Party":
                party_alt = vendor_column(filtered_report_df)
                if party_alt:
                    actual_display_cols.append(party_alt)

    if not actual_display_cols:
        actual_display_cols = [c for c in filtered_report_df.columns if not c.startswith("_")]

    final_report_df = filtered_report_df[actual_display_cols].copy()
    final_report_df.insert(0, "S.No", range(1, 1 + len(final_report_df)))

    st.markdown(render_html_table(final_report_df), unsafe_allow_html=True)

    excel_bytes_reported = to_excel_bytes({"Reported_Vehicles": final_report_df})
    st.download_button(
        label="📥 Download Filtered Excel",
        data=excel_bytes_reported,
        file_name="Reported_Vehicles.xlsx",
        mime=EXCEL_MIME,
        type="primary",
        key=f"dl_{unique_key}",
    )

    if not only_delay:
        # ================= CLIENT-WISE PERFORMANCE SECTION =================
        st.markdown(
            "<br><h3 style='color:#38bdf8; font-size:18px; font-weight:800; margin-bottom:15px;'>🏢 Client-wise Performance HUD</h3>",
            unsafe_allow_html=True,
        )

        if client_col_name and client_col_name in reported_df.columns and late_col:
            client_base_df = reported_df.copy()
            client_base_df["Is_OnTime"] = client_base_df[late_col].apply(is_zero_late)
            client_base_df["Is_Delay"] = ~client_base_df[late_col].apply(is_zero_late)

            client_summary = (
                client_base_df.groupby(client_col_name)
                .agg(Total=("Is_OnTime", "count"), OnTime=("Is_OnTime", "sum"), Delay=("Is_Delay", "sum"))
                .reset_index()
            )

            client_summary["On-Time %"] = client_summary.apply(
                lambda r: f"{round((r['OnTime'] / r['Total']) * 100, 1)}%" if r["Total"] > 0 else "0.0%",
                axis=1,
            )
            client_summary = client_summary.rename(
                columns={
                    client_col_name: "Client Name",
                    "Total": "Total Trips",
                    "OnTime": "On-Time Trips",
                    "Delay": "Delay Trips",
                }
            ).sort_values(by="Total Trips", ascending=False)

            client_summary.insert(0, "S.No", range(1, 1 + len(client_summary)))

            st.markdown(render_html_table(client_summary), unsafe_allow_html=True)

            excel_bytes_client = to_excel_bytes({"Client_Performance": client_summary})
            st.download_button(
                label="📥 Download Client Performance",
                data=excel_bytes_client,
                file_name="Client_Performance.xlsx",
                mime=EXCEL_MIME,
                type="secondary",
                key=f"dl_client_{unique_key}",
            )
        else:
            st.info("Client-wise performance data unavailable.")


# ================= IN-TRANSIT VEHICLE VIEW =================
def show_in_transit_view(mis_df):
    st.markdown(
        "<h2 style='color:#38bdf8; font-weight:800;'>🚚 In-Transit Active Trips HUD</h2>",
        unsafe_allow_html=True,
    )

    final_rep_col = next(
        (c for c in ["Final Touching Reporting Date & Time", "Reporting Date & Time", "Reporting Date"] if c in mis_df.columns),
        None,
    )
    if not final_rep_col:
        final_rep_col = next((c for c in mis_df.columns if "report" in c.lower()), None)

    if not final_rep_col:
        st.warning("MIS data reporting date column missing.")
        return

    in_transit_df = mis_df[mis_df[final_rep_col].apply(is_blank)].copy()

    if in_transit_df.empty:
        st.success("🟢 All trips closed! No vehicles currently In-Transit.")
        return

    st.metric("TOTAL IN-TRANSIT VEHICLES", len(in_transit_df))

    staff_col = next((c for c in in_transit_df.columns if "controlling" in c.lower() or "staff" in c.lower()), None)
    client_col_name = vendor_column(in_transit_df) or "VendorName"

    col1, col2 = st.columns(2)
    with col1:
        selected_staff_it = st.selectbox(
            "Filter by Staff",
            ["ALL"]
            + sorted([str(x).strip() for x in in_transit_df[staff_col].dropna().unique() if str(x).strip() != ""])
            if staff_col
            else ["ALL"],
            key="it_staff",
        )
    with col2:
        selected_client_it = st.selectbox(
            "Filter by Client",
            ["ALL"]
            + sorted(
                [str(x).strip() for x in in_transit_df[client_col_name].dropna().unique() if str(x).strip() != ""]
            )
            if client_col_name in in_transit_df.columns
            else ["ALL"],
            key="it_client",
        )

    filtered_it_df = in_transit_df.copy()
    if selected_staff_it != "ALL" and staff_col:
        filtered_it_df = filtered_it_df[filtered_it_df[staff_col].astype(str).str.strip() == selected_staff_it]
    if selected_client_it != "ALL" and client_col_name in filtered_it_df.columns:
        filtered_it_df = filtered_it_df[filtered_it_df[client_col_name].astype(str).str.strip() == selected_client_it]

    desired_cols = [
        "Lorry No.",
        "Veh.Type",
        "From",
        "Destination",
        "Party",
        "Desp. Date & Time",
        "Hrs. Given",
        "1st Touching",
        "1st Touching Reporting Date & Time",
        "Tracking Remark",
        "Group Name",
        "Controlling Staff Name",
        "Foreman Name",
    ]

    actual_display_cols = []
    for col in desired_cols:
        matched_c = next((c for c in filtered_it_df.columns if c.lower().strip() == col.lower().strip()), None)
        if matched_c:
            actual_display_cols.append(matched_c)

    if not actual_display_cols:
        actual_display_cols = [c for c in filtered_it_df.columns if not c.startswith("_")]

    final_it_df = filtered_it_df[actual_display_cols].copy()
    final_it_df.insert(0, "S.No", range(1, 1 + len(final_it_df)))

    st.markdown(render_html_table(final_it_df), unsafe_allow_html=True)

    excel_bytes_it = to_excel_bytes({"In_Transit_Vehicles": final_it_df})
    st.download_button(
        label="📥 Download In-Transit Excel",
        data=excel_bytes_it,
        file_name="In_Transit_Vehicles.xlsx",
        mime=EXCEL_MIME,
        type="primary",
        key="dl_in_transit",
    )


# ================= FILE PROCESSING =================
def process_uploaded_files(uploaded_files):
    mis_dfs = []
    for uploaded_file in uploaded_files:
        try:
            filename_lower = uploaded_file.name.lower()
            temp_df = None
            if filename_lower.endswith(".csv"):
                for enc in ["utf-8", "latin-1", "cp1252"]:
                    try:
                        uploaded_file.seek(0)
                        temp_df = pd.read_csv(uploaded_file, low_memory=False, encoding=enc)
                        break
                    except Exception:
                        continue
            else:
                temp_df = pd.read_excel(uploaded_file)

            if temp_df is None or temp_df.empty:
                continue
            temp_df.columns = temp_df.columns.astype(str).str.strip()

            vendor_c = vendor_column(temp_df)
            temp_df["VendorName"] = temp_df[vendor_c].apply(lambda x: clean_party(x, True)) if vendor_c else "Other"
            mis_dfs.append(temp_df)

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    return pd.concat(mis_dfs, ignore_index=True) if mis_dfs else pd.DataFrame()


# ================= MAIN APP =================
def main():
    header_col1, header_col2 = st.columns([3, 2])
    with header_col1:
        st.markdown(
            "<h1 class='premium-title' style='padding-top: 5px;'>⚡ Fleet Dashboard</h1>",
            unsafe_allow_html=True,
        )
    with header_col2:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(56, 189, 248, 0.3); padding: 8px 16px; border-radius: 16px; 
                        text-align: right; box-shadow: 0 12px 30px rgba(56, 189, 248, 0.15); display: flex; align-items: center; justify-content: flex-end; gap: 12px;">
                <div style="text-align: right;">
                    <div style="color: #38bdf8; font-weight: 800; font-size: 13px;">TEJAS CARGO INDIA LTD.</div>
                    <div style="color: #94a3b8; font-size: 11px; font-weight: 600;">GLASSY MOTION UI</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border:0; height:1px; background:rgba(56, 189, 248, 0.25); margin: 15px 0 20px 0;'>", unsafe_allow_html=True)

    # Sidebar File Upload & Management
    with st.sidebar:
        st.markdown("<h2 style='color:#38bdf8; font-size: 18px; font-weight:800;'>⚙️ Motion Control Panel</h2>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload MIS Files", type=["xlsx", "xls", "csv"], accept_multiple_files=True)

        if uploaded_files:
            mis_df = process_uploaded_files(uploaded_files)
            if not mis_df.empty:
                with open(MIS_PATH, "wb") as f:
                    pickle.dump(mis_df, f)
            st.success("Files Loaded Successfully!")

        if st.button("Clear Cache"):
            if os.path.exists(MIS_PATH):
                os.remove(MIS_PATH)
            st.rerun()

    # Load Data from Persistence
    mis_df = pd.DataFrame()

    if os.path.exists(MIS_PATH):
        with open(MIS_PATH, "rb") as f:
            mis_df = pickle.load(f)

    # Render Ticker
    render_news_ticker(mis_df)

    # Main Tabs with Glassmorphic Motion
    tab1, tab2, tab3 = st.tabs(["📊 Closed Trips", "🚚 In-Transit Trips", "⚠️ Delay Closed Vehicle"])

    with tab1:
        if not mis_df.empty:
            show_reported_vehicle_table(mis_df, unique_key="main_mis", only_delay=False)
        else:
            st.info("Upload MIS data from sidebar to view Closed Trips.")

    with tab2:
        if not mis_df.empty:
            show_in_transit_view(mis_df)
        else:
            st.info("Upload MIS data from sidebar to view In-Transit status.")

    with tab3:
        if not mis_df.empty:
            show_reported_vehicle_table(mis_df, unique_key="delay_mis", only_delay=True)
        else:
            st.info("Upload MIS data from sidebar to view Delay Closed Vehicle data.")


if __name__ == "__main__":
    main()
