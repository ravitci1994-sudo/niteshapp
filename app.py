import streamlit as st
import pandas as pd
import io

# Page setup
st.set_page_config(page_title="Vendor Dashboard", layout="wide")

# ================= SIDEBAR =================
st.sidebar.title("Welcome, Tejas Cargo India")
st.sidebar.markdown("*ID:* TEJAS | *Role:* Vendor")

if st.sidebar.button("Logout"):
    st.sidebar.warning("Aap log out ho gaye hain!")

st.sidebar.markdown("---")
st.sidebar.radio("Navigation:", ["🚚 Vendor Performance"])

# ================= MAIN PAGE =================
st.title("Vendor Performance Dashboard")
st.info("🔒 Apni data file upload karein aur automatic report payein.")

# ================= FILE UPLOAD =================
uploaded_file = st.file_uploader("Apni Excel (.xlsx) ya CSV file yahan upload karein", type=["csv", "xlsx"])

if uploaded_file is not None:
    # File padhne ka code
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("✅ File successfully upload ho gayi!")
        
        # Quick Search Filter
        search_term = st.text_input("🔍 Quick Search:", placeholder="Data mein kuch bhi search karein...")
        
        if search_term:
            # Search logic
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df
            
        # Download Excel Button ke liye data prepare karna
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Report')
        
        st.download_button(
            label="📥 Download Filtered Report (Excel)",
            data=buffer.getvalue(),
            file_name="Vendor_Report.xlsx",
            mime="application/vnd.ms-excel",
            type="primary"
        )

        # Data Table dikhana
        st.subheader("📊 Vendor Performance Summary")
        st.dataframe(filtered_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"File open karne mein error: {e}")
else:
    st.warning("⚠️ Data dekhne ke liye upar apni file upload karein.")
