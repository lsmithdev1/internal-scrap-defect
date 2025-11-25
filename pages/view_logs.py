import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="View Logs | Brembo QC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
        padding: 30px 40px;
        border-radius: 0;
        margin: -80px -80px 40px -80px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border-bottom: 4px solid #dc2626;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(220, 38, 38, 0.1) 50%, transparent 100%);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0%, 100% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
    }
    
    .company-name {
        color: #dc2626;
        font-size: 18px;
        font-weight: 900;
        letter-spacing: 4px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    .main-header h1 {
        color: white;
        font-size: 36px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
        text-transform: uppercase;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.7);
        font-size: 13px;
        margin: 8px 0 0 0;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 500;
    }
    
    /* Data frame */
    .stDataFrame {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Success/Info messages */
    .stSuccess, .stInfo, .stError {
        border-radius: 10px !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Record count */
    .record-count {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 15px 25px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 20px 0;
        font-size: 16px;
        font-weight: 600;
    }
    
    .record-count .number {
        color: #fbbf24;
        font-weight: 700;
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="company-name">BREMBO</div>
    <h1>Defect Logs Database</h1>
    <p>View All Logged Defects</p>
</div>
""", unsafe_allow_html=True)

# Connect to database
try:
    conn = sqlite3.connect('defect_logs.db')
    
    # Get all defects
    df = pd.read_sql_query("SELECT * FROM PA_InternalScrap ORDER BY ID DESC", conn)
    
    if len(df) > 0:
        st.success(f"✅ Successfully loaded {len(df):,} records from database")
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            height=600
        )
        
        # Download as CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Data (CSV)",
            data=csv,
            file_name=f"brembo_defects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.info("ℹ️ No defects have been logged yet. Start logging defects on the Home page!")
    
    conn.close()
    
except Exception as e:
    st.error(f"❌ Database Error: {e}")
    st.info("💡 Make sure you've logged at least one defect on the Home page first.")