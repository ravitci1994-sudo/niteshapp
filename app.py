import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
import html as html_lib
import pickle

# 1. Page Configuration
st.set_page_config(
    page_title="AI Offline 3D Delay & Resolution Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================= CUSTOM CSS FOR 3D FUTURISTIC HUD THEME =================
st.markdown(
    """
    <style>
    .main, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #151b3b 0%, #080b1e 70%, #03040a 100%) !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15);
    }

    .premium-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #ffffff 20%, #38bdf8 60%, #ff7630 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
        margin-top: 0px;
        text-shadow: 0 0 30px rgba(56, 189, 248, 0.2);
    }

    /* 3D Glass Card Container */
    .ai-card-3d {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(56, 189, 248, 0.1);
        backdrop-filter: blur(15px);
    }

    .custom-table-container {
        overflow-x: auto; 
        max-height: 450px;
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(20px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
        margin-bottom: 25px;
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
        padding: 12px 16px; 
        text-align: left; 
        position: sticky; 
        top: 0; 
        font-weight: 800; 
        z-index: 2; 
        border-bottom: 1px solid rgba(56, 189, 248, 0.3);
        text-transform: uppercase;
        font-size: 11px;
    }
    
    .custom-table td { 
        padding: 11px 16px; 
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        color: #e2e8f0; 
        font-weight: 500;
    }
    
    .custom-table tr:hover td { 
        background-color: rgba(56, 189, 248, 0.12); 
        color: #ffffff; 
    }

    .stButton > button {
        background: linear-gradient(135deg, #ff7630, #f97316) !important;
        border: none !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 0 15px rgba(249, 115, 22, 0.4) !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(249, 115, 22, 0.7) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 10px;
        font-weight: 700;
        color: #94a3b8;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #38bdf8, #0284c7) !important;
        color: #0f172a !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_DIR = "saved_data"
os.makedirs(DATA_DIR, exist_ok=True)
MIS_PATH = os.path.join(DATA_DIR, "mis.pkl")


# ================= HELPERS & OFFLINE AI ENGINE =================
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


def vendor_column(df):
    return next(
        (c for c in df.columns if any(k in c.lower() for k in ("vendor", "party", "client", "customer"))),
        None,
    )


def render_html_table(df_to_show, max_rows=2000):
    clean_df = df_to_show.fillna("").astype(str)
    note = ""
    if len(clean_df) > max_rows:
        note = f'<div style="color:#ff7630; font-size:12px; margin-bottom:6px; font-weight:700;">⚡ Showing first {max_rows} rows. Download Excel for full data.</div>'
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


# ================= OFFLINE AI RESOLUTION GENERATOR =================
def generate_offline_ai_insights(df):
    late_col = next((c for c in ["Late Hrs", "Delay Hrs", "Delay"] if c in df.columns), None)
    from_col = next((c for c in df.columns if c.lower().strip() in ["from", "source", "origin"]), None)
    dest_col = next((c for c in df.columns if c.lower().strip() in ["destination", "to"]), None)
    staff_col = next((c for c in df.columns if "controlling" in c.lower() or "staff" in c.lower()), None)

    if not late_col:
        return pd.DataFrame(), pd.DataFrame(), "Delay column nahi mila."

    # Filter delayed trips
    delayed_df = df[~df[late_col].apply(is_zero_late)].copy()
    if delayed_df.empty:
        return pd.DataFrame(), pd.DataFrame(), "No delay records found to analyze."

    # 1. Route-wise Analysis
    if from_col and dest_col:
        delayed_df["Route"] = delayed_df[from_col].astype(str).str.strip() + " ➔ " + delayed_df[dest_col].astype(str).str.strip()
    else:
        delayed_df["Route"] = "Unknown Route"

    route_summary = delayed_df.groupby("Route").size().reset_index(name="Delay Count")
    route_summary = route_summary.sort_values(by="Delay Count", ascending=False)

    # AI Resolution Logic for Routes
    def ai_route_resolution(count):
        if count >= 10:
            return "🔴 Critical Bottleneck: Route par traffic ya transit check points par severe delay hai. Buffer time 4 hours badhayein aur alternative highway allocate karein."
        elif count >= 5:
            return "🟡 Moderate Delay: Driver coordination check karein aur intermediate halting points minimize karein."
        else:
            return "🟢 Minor Delay: Route normal hai, standard monitoring sufficient hai."

    route_summary["AI Suggested Resolution"] = route_summary["Delay Count"].apply(ai_route_resolution)

    # 2. Staff-wise Analysis
    if staff_col:
        staff_summary = delayed_df.groupby(staff_col).size().reset_index(name="Delay Count")
        staff_summary = staff_summary.rename(columns={staff_col: "Staff Name"})
        staff_summary = staff_summary.sort_values(by="Delay Count", ascending=False)

        def ai_staff_resolution(count):
            if count >= 8:
                return "⚠️ High Delay Volume: Is staff ke under active trips ka load zyada hai ya tracking follow-up weak hai. Immediate daily briefing aur checkpoint logging enforce karein."
            else:
                return "✅ Balanced Performance: Standard follow-up maintain rakhein."

        staff_summary["AI Recommended Action"] = staff_summary["Delay Count"].apply(ai_staff_resolution)
    else:
        staff_summary = pd.DataFrame()

    return route_summary, staff_summary, None


# ================= MAIN APP =================
def main():
    st.markdown("<h1 class='premium-title'>🤖 Offline AI 3D Delay & Resolution Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:14px;'>In-built offline AI engine jo aapke delay data ko read karke Route-wise aur Staff-wise intelligent resolutions deta hai.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border:0; height:1px; background:rgba(56, 189, 248, 0.2); margin: 15px 0 20px 0;'>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='color:#38bdf8; font-size: 18px; font-weight:800;'>⚙️ Data Control Panel</h2>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload MIS File (Excel/CSV)", type=["xlsx", "xls", "csv"])

        if uploaded_file:
            try:
                if uploaded_file.name.lower().endswith('.csv'):
                    mis_df = pd.read_csv(uploaded_file, low_memory=False)
                else:
                    mis_df = pd.read_excel(uploaded_file)
                
                mis_df.columns = mis_df.columns.astype(str).str.strip()
                with open(MIS_PATH, "wb") as f:
                    pickle.dump(mis_df, f)
                st.success("MIS Data Loaded & Saved!")
            except Exception as e:
                st.error(f"Error: {e}")

        if st.button("Clear Cache"):
            if os.path.exists(MIS_PATH):
                os.remove(MIS_PATH)
            st.rerun()

    # Load Data
    mis_df = pd.DataFrame()
    if os.path.exists(MIS_PATH):
        with open(MIS_PATH, "rb") as f:
            mis_df = pickle.load(f)

    if mis_df.empty:
        st.info("👈 Please upload your MIS dataset via sidebar to activate the Offline AI Assistant.")
        return

    # Tabs for UI
    tab1, tab2, tab3 = st.tabs(["🧠 AI Offline Insights & Resolutions", "⚠️ Delay Closed Vehicles", "📊 All Closed Trips"])

    with tab1:
        st.markdown("<h3 style='color:#38bdf8;'>Offline AI Automated Delay Diagnosis</h3>", unsafe_allow_html=True)
        route_res, staff_res, err = generate_offline_ai_insights(mis_df)

        if err:
            st.warning(err)
        else:
            st.markdown("<div class='ai-card-3d'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#ff7630; margin-top:0;'>🛣️ Route-wise AI Resolutions & Bottlenecks</h4>", unsafe_allow_html=True)
            route_res.insert(0, "S.No", range(1, 1 + len(route_res)))
            st.markdown(render_html_table(route_res), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if not staff_res.empty:
                st.markdown("<div class='ai-card-3d'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color:#38bdf8; margin-top:0;'>👨‍💼 Staff-wise Performance & AI Action Plan</h4>", unsafe_allow_html=True)
                staff_res.insert(0, "S.No", range(1, 1 + len(staff_res)))
                st.markdown(render_html_table(staff_res), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<h3 style='color:#38bdf8;'>Delay Closed Vehicles Data</h3>", unsafe_allow_html=True)
        late_col = next((c for c in ["Late Hrs", "Delay Hrs", "Delay"] if c in mis_df.columns), None)
        if late_col:
            delay_df = mis_df[~mis_df[late_col].apply(is_zero_late)].copy()
            if not delay_df.empty:
                delay_df.insert(0, "S.No", range(1, 1 + len(delay_df)))
                st.markdown(render_html_table(delay_df), unsafe_allow_html=True)
                
                excel_bytes = to_excel_bytes({"Delay_Closed": delay_df})
                st.download_button("📥 Download Delay Closed Excel", data=excel_bytes, file_name="Delay_Closed_Vehicles.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.success("No delayed records found.")

    with tab3:
        st.markdown("<h3 style='color:#38bdf8;'>All Closed Trips Data</h3>", unsafe_allow_html=True)
        display_df = mis_df.copy()
        display_df.insert(0, "S.No", range(1, 1 + len(display_df)))
        st.markdown(render_html_table(display_df), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
