import streamlit as st
from datetime import date
import sys
import os

# Add the circle_diagram_component to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'circle_diagram_component'))
from circle_diagram_component import circle_diagram
from database_sqlite import log_defect_to_database, get_defect_count

st.set_page_config(
    page_title="Defect Logger | Brembo QC",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern professional styling
st.markdown("""
<style>
    /* Main app background and layout */
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header styling */
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
    
    /* Input fields styling */
    .stDateInput, .stSelectbox, .stTextInput {
        background-color: white;
    }
    
    .stDateInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
        font-weight: 500 !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }
    
    .stDateInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextInput > div > div > input:focus {
        border-color: #dc2626 !important;
        box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1) !important;
    }
    
    /* Input section background */
    [data-testid="column"] {
        background: rgba(30, 41, 59, 0.6);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Labels */
    .stDateInput > label,
    .stSelectbox > label,
    .stTextInput > label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        margin-bottom: 8px !important;
        display: block !important;
        background: rgba(220, 38, 38, 0.2);
        padding: 6px 10px;
        border-radius: 6px;
        border-left: 3px solid #dc2626;
    }
    
    /* Cards and containers */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stInfo {
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    /* Divider */
    hr {
        margin: 30px 0;
        border: none;
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Stats badge */
    .stats-badge {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 15px 25px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-top: 20px;
    }
    
    .stats-badge .number {
        font-size: 32px;
        font-weight: 700;
        color: #fbbf24;
        display: block;
    }
    
    .stats-badge .label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.8;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="company-name">BREMBO</div>
    <h1>Internal Scrap Tracking System</h1>
    <p>Manufacturing Quality Control | Real-time Defect Logging</p>
</div>
""", unsafe_allow_html=True)

part_numbers = [
    "19.A956.04", "18.A957.04", "18.N233.03", "18.N276.00_M", "18.N325.02", 
    "18.N352.00_M", "18.N353.00_M", "19.9921.03", "19.9922.03", "19.9923.03", 
    "19.9924.03", "19.9925.03", "19.A958.04", "19.A959.04", "19.A960.04", 
    "19.A961.04", "19.D328.00", "19.D329.00", "19.N222.03", "19.N234.00_M", 
    "19.N235.00_M", "19.N236.00_M", "19.N248.02", "19.N265.00_M", "19.N268.02", 
    "19.N274.03", "19.N278.03", "19.N284.03", "19.N349.02", "19.N366.00", 
    "19.N367.00", "19.N397.00", "19.N398.00", "19.N400.00", "19.N371.00", 
    "19.N372.00", "19.N402.00", "19.N423.00", "19.N385.01", "19.N426.00", 
    "19.N427.00", "19.N408.00", "19.N429.00", "19.N367.01", "18.N424.00", 
    "19.N425.00", "19.N428.02", "19.N428.01", "XC1.A9.00", "19.N403.02", 
    "19.E396.00", "18.N456.00", "19.E394.00", "19.E395.00", "19.N402.02", 
    "19.N400.02", "19.N360.00", "19.N454.02", "19.N473.02", "19.N453.02", 
    "19.N481.02", "18.N277.03", "19.N216.01", "XC5.94.00", "XC5.95.00", 
    "XC5.96.00"
]

# Initialize session state
if 'inspection_date' not in st.session_state:
    st.session_state.inspection_date = date.today()
if 'part_number' not in st.session_state:
    st.session_state.part_number = ""
if 'batch_number' not in st.session_state:
    st.session_state.batch_number = ""
if 'date_code' not in st.session_state:
    st.session_state.date_code = ""
if 'notes' not in st.session_state:
    st.session_state.notes = ""

# Session Information Form
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    inspection_date = st.date_input("Inspection Date", value=st.session_state.inspection_date)
    st.session_state.inspection_date = inspection_date

with col2:
    idx = ([""] + part_numbers).index(st.session_state.part_number) if st.session_state.part_number in ([""] + part_numbers) else 0
    part_number = st.selectbox("Part Number", options=[""] + part_numbers, index=idx)
    st.session_state.part_number = part_number

with col3:
    batch_number = st.text_input("Batch Number", value=st.session_state.batch_number)
    st.session_state.batch_number = batch_number

with col4:
    date_code = st.text_input("Date Code", value=st.session_state.date_code)
    st.session_state.date_code = date_code

with col5:
    notes = st.text_input("Notes", value=st.session_state.notes)
    st.session_state.notes = notes

st.markdown("---")

# Circle diagram
click_data = circle_diagram(key="diagram")

# Handle data logging
if click_data:
    session_info = {
        'date': str(inspection_date),
        'part_number': part_number,
        'batch_number': batch_number,
        'date_code': date_code,
        'notes': notes
    }
    
    if not batch_number:
        st.error("⚠️ Batch Number is required to log defects")
    elif not part_number:
        st.error("⚠️ Part Number is required to log defects")
    else:
        success, message = log_defect_to_database(click_data, session_info)
        if success:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")

# Stats display
total = get_defect_count()
st.markdown(f"""
<div class="stats-badge">
    <span class="number">{total}</span>
    <span class="label">Total Defects Logged</span>
</div>
""", unsafe_allow_html=True)