import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import init_db

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="StockAI - Asisten Stok Opname Cerdas",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        color: #ffd600;
        margin: 0;
        font-size: 2.2rem;
    }
    
    .main-header p {
        color: #e8eaf6;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid #1a237e;
    }
    
    .metric-card h3 {
        color: #1a237e;
        font-size: 2rem;
        margin: 0;
    }
    
    .metric-card p {
        color: #666;
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a237e 0%, #0d1442 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Chat bubbles */
    .user-bubble {
        background: #1a237e;
        color: white;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .ai-bubble {
        background: white;
        color: #333;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin: 8px 0;
        max-width: 80%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        border-left: 3px solid #ffd600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🏭 StockAI")
    st.markdown("*Asisten Stok Opname Cerdas*")
    st.markdown("---")
    st.markdown("""
    ### 📍 Navigasi
    Gunakan menu di atas untuk berpindah halaman:
    - 💬 **Chat** — Input & tanya data
    - 📊 **Dashboard** — Visualisasi
    - 📋 **Riwayat** — Lihat semua data
    - 📤 **Export** — Download data
    """)
    st.markdown("---")
    st.markdown("""
    ### 💡 Tips
    - Ketik natural: *"Mesin 3, drill navy, 350 yard"*
    - Upload foto label kain
    - Tanya: *"Rangkum hari ini"*
    - Analisis: *"Mesin mana paling produktif?"*
    """)
    st.markdown("---")
    st.markdown("Made with ❤️ for Indonesian Textile Industry")

# Main page - Landing
st.markdown("""
<div class="main-header">
    <h1>🏭 StockAI</h1>
    <p>Asisten Stok Opname Cerdas untuk Produksi Tekstil</p>
</div>
""", unsafe_allow_html=True)

# Quick stats
from utils.database import get_today_records, get_all_records

today_records = get_today_records()
all_records = get_all_records()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{len(today_records)}</h3>
        <p>📦 Items Hari Ini</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_yard_today = sum(r['yard'] for r in today_records) if today_records else 0
    st.markdown(f"""
    <div class="metric-card">
        <h3>{total_yard_today:,.0f}</h3>
        <p>📏 Yard Hari Ini</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    mesin_aktif = len(set(r['mesin'] for r in today_records)) if today_records else 0
    st.markdown(f"""
    <div class="metric-card">
        <h3>{mesin_aktif}</h3>
        <p>⚙️ Mesin Aktif</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_all = len(all_records)
    st.markdown(f"""
    <div class="metric-card">
        <h3>{total_all}</h3>
        <p>📚 Total Records</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick start guide
st.markdown("### 🚀 Mulai Cepat")
st.markdown("""
| Langkah | Cara |
|---------|------|
| 1️⃣ | Buka halaman **💬 Chat** di sidebar |
| 2️⃣ | Ketik data stock opname dalam bahasa natural |
| 3️⃣ | AI akan parse & simpan otomatis |
| 4️⃣ | Lihat **📊 Dashboard** untuk visualisasi |
""")

st.markdown("### 📝 Contoh Input")
st.code('Mesin 3 jam 10, drill navy party 2405, 350 yard, finishing', language=None)
st.code('Rangkum stock opname hari ini', language=None)
st.code('Mesin mana yang output-nya paling tinggi minggu ini?', language=None)
