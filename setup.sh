#!/bin/bash
# StockAI Setup Script
# Jalankan: bash setup.sh
# Semua file akan dibuat otomatis di folder ./stock-ai/

echo "🏭 Setting up StockAI..."

mkdir -p stock-ai/pages stock-ai/utils
cd stock-ai

# requirements.txt
cat > requirements.txt << 'EOF'
streamlit==1.45.0
google-generativeai==0.8.0
python-dotenv==1.0.0
pandas==2.2.0
plotly==5.18.0
openpyxl==3.1.2
Pillow==10.2.0
EOF

# .env.example
cat > .env.example << 'EOF'
GEMINI_API_KEY=your_api_key_here
EOF

# .gitignore
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
*.db
.streamlit/
venv/
.venv/
EOF

# Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]
EOF

# utils/__init__.py
cat > utils/__init__.py << 'EOF'
# utils package
EOF

# utils/database.py
cat > utils/database.py << 'DBEOF'
import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stock_opname.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_opname (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            jam TEXT,
            mesin TEXT,
            kode_produksi TEXT,
            warna TEXT,
            proses_produksi TEXT,
            party TEXT,
            yard REAL DEFAULT 0,
            status TEXT DEFAULT 'counted',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_record(data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO stock_opname (tanggal, jam, mesin, kode_produksi, warna, proses_produksi, party, yard, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('tanggal', str(date.today())),
        data.get('jam', ''),
        data.get('mesin', ''),
        data.get('kode_produksi', ''),
        data.get('warna', ''),
        data.get('proses_produksi', ''),
        data.get('party', ''),
        data.get('yard', 0),
        data.get('status', 'counted'),
        data.get('notes', '')
    ))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_today_records():
    conn = get_connection()
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute('SELECT * FROM stock_opname WHERE tanggal = ? ORDER BY created_at DESC', (today,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_records_by_date(target_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stock_opname WHERE tanggal = ? ORDER BY created_at DESC', (target_date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_records_by_range(start_date: str, end_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stock_opname WHERE tanggal BETWEEN ? AND ? ORDER BY tanggal DESC, created_at DESC', (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stock_opname ORDER BY tanggal DESC, created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_summary_today():
    records = get_today_records()
    if not records:
        return None
    total_items = len(records)
    total_yard = sum(r['yard'] for r in records)
    mesin_summary = {}
    warna_summary = {}
    for r in records:
        mesin = r['mesin'] or 'Unknown'
        warna = r['warna'] or 'Unknown'
        if mesin not in mesin_summary:
            mesin_summary[mesin] = {'items': 0, 'yard': 0}
        mesin_summary[mesin]['items'] += 1
        mesin_summary[mesin]['yard'] += r['yard']
        if warna not in warna_summary:
            warna_summary[warna] = 0
        warna_summary[warna] += r['yard']
    return {
        'tanggal': str(date.today()),
        'total_items': total_items,
        'total_yard': total_yard,
        'mesin_summary': mesin_summary,
        'warna_summary': warna_summary,
        'records': records
    }

def delete_record(record_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM stock_opname WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()

init_db()
DBEOF

# utils/gemini_helper.py
cat > utils/gemini_helper.py << 'GEMEOF'
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM_PROMPT = """Kamu adalah StockAI, asisten stock opname cerdas untuk pabrik tekstil.

TUGAS UTAMA:
1. Parse input user menjadi data terstruktur stock opname
2. Jawab pertanyaan tentang data stok
3. Berikan insight dan analisis

KETIKA USER INPUT DATA STOCK OPNAME:
Selalu respond dalam format JSON yang valid di dalam tag <json></json>, dengan field:
{
  "action": "insert",
  "data": {
    "jam": "HH:MM",
    "mesin": "nomor/nama mesin",
    "kode_produksi": "jenis kain",
    "warna": "warna kain",
    "proses_produksi": "proses",
    "party": "nomor party",
    "yard": angka_yard_sebagai_number
  },
  "confirmation": "pesan konfirmasi dalam bahasa Indonesia"
}

KETIKA USER BERTANYA/MINTA LAPORAN:
Respond dengan format:
{
  "action": "query",
  "response": "jawaban lengkap dalam bahasa Indonesia"
}

KETIKA USER UPLOAD FOTO:
Extract data dari foto label kain dan respond dengan format insert di atas.

RULES:
- Bahasa Indonesia casual tapi profesional
- Jika ada field yang tidak disebutkan user, isi dengan string kosong ""
- Yard harus berupa angka (number), bukan string
- Jika user bilang "mesin 3" maka mesin: "3"
- Jika user bilang "jam 10" maka jam: "10:00"
- Selalu konfirmasi data yang tercatat
- Jika input ambigu, tanya balik untuk klarifikasi
"""

def get_model():
    return genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=SYSTEM_PROMPT
    )

def get_vision_model():
    return genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=SYSTEM_PROMPT
    )

def parse_ai_response(response_text: str):
    try:
        if '<json>' in response_text and '</json>' in response_text:
            json_str = response_text.split('<json>')[1].split('</json>')[0].strip()
            return json.loads(json_str)
        if '```json' in response_text:
            json_str = response_text.split('```json')[1].split('```')[0].strip()
            return json.loads(json_str)
        if '```' in response_text:
            json_str = response_text.split('```')[1].split('```')[0].strip()
            return json.loads(json_str)
        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError):
        return {"action": "query", "response": response_text}

def chat_with_ai(user_message: str, context: str = ""):
    model = get_model()
    prompt = user_message
    if context:
        prompt = f"KONTEKS DATA HARI INI:\n{context}\n\nUSER: {user_message}"
    response = model.generate_content(prompt)
    return parse_ai_response(response.text)

def analyze_image(image_bytes, mime_type="image/jpeg"):
    model = get_vision_model()
    image_part = {"mime_type": mime_type, "data": image_bytes}
    prompt = "Lihat foto label kain ini. Extract semua informasi yang bisa kamu baca: party number, warna, yard/meter, mesin, jenis kain, proses produksi. Respond dalam format JSON insert seperti di system prompt."
    response = model.generate_content([prompt, image_part])
    return parse_ai_response(response.text)

def generate_report(records: list, query: str = ""):
    model = get_model()
    records_text = json.dumps(records, indent=2, ensure_ascii=False)
    prompt = f"""Berikut data stock opname:
{records_text}

{query if query else "Buatkan rangkuman lengkap: total items, total yard, breakdown per mesin, per warna, dan insight/anomali jika ada."}

Respond sebagai teks biasa (bukan JSON), format yang rapi dan mudah dibaca. Gunakan emoji untuk visual."""
    response = model.generate_content(prompt)
    return response.text
GEMEOF

# utils/charts.py
cat > utils/charts.py << 'CHARTEOF'
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def chart_output_per_mesin(records: list):
    if not records:
        return None
    df = pd.DataFrame(records)
    mesin_data = df.groupby('mesin')['yard'].sum().reset_index()
    mesin_data = mesin_data.sort_values('mesin')
    fig = px.bar(mesin_data, x='mesin', y='yard', title='Output per Mesin (Yard)',
                 labels={'mesin': 'Mesin', 'yard': 'Total Yard'},
                 color='yard', color_continuous_scale=['#1a237e', '#ffd600'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#1a237e')
    return fig

def chart_trend_harian(records: list):
    if not records:
        return None
    df = pd.DataFrame(records)
    daily_data = df.groupby('tanggal')['yard'].sum().reset_index()
    daily_data = daily_data.sort_values('tanggal')
    fig = px.line(daily_data, x='tanggal', y='yard', title='Trend Output Harian',
                  labels={'tanggal': 'Tanggal', 'yard': 'Total Yard'}, markers=True)
    fig.update_traces(line_color='#1a237e', marker_color='#ffd600')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#1a237e')
    return fig

def chart_komposisi_warna(records: list):
    if not records:
        return None
    df = pd.DataFrame(records)
    warna_data = df.groupby('warna')['yard'].sum().reset_index()
    fig = px.pie(warna_data, values='yard', names='warna', title='Komposisi Warna',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#1a237e')
    return fig

def chart_items_per_mesin(records: list):
    if not records:
        return None
    df = pd.DataFrame(records)
    mesin_count = df.groupby('mesin').size().reset_index(name='items')
    mesin_count = mesin_count.sort_values('mesin')
    fig = px.bar(mesin_count, x='mesin', y='items', title='Jumlah Item per Mesin',
                 labels={'mesin': 'Mesin', 'items': 'Jumlah Item'},
                 color='items', color_continuous_scale=['#ffd600', '#1a237e'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#1a237e')
    return fig
CHARTEOF

# app.py
cat > app.py << 'APPEOF'
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.database import init_db, get_today_records, get_all_records

init_db()

st.set_page_config(page_title="StockAI - Asisten Stok Opname Cerdas", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #1a237e 0%, #283593 100%); padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem; }
    .main-header h1 { color: #ffd600; margin: 0; font-size: 2.2rem; }
    .main-header p { color: #e8eaf6; margin: 0.5rem 0 0 0; font-size: 1.1rem; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; border-left: 4px solid #1a237e; }
    .metric-card h3 { color: #1a237e; font-size: 2rem; margin: 0; }
    .metric-card p { color: #666; margin: 0.3rem 0 0 0; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏭 StockAI")
    st.markdown("*Asisten Stok Opname Cerdas*")
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("- Ketik: *\"Mesin 3, drill navy, 350 yard\"*")
    st.markdown("- Upload foto label kain")
    st.markdown("- Tanya: *\"Rangkum hari ini\"*")

st.markdown('<div class="main-header"><h1>🏭 StockAI</h1><p>Asisten Stok Opname Cerdas untuk Produksi Tekstil</p></div>', unsafe_allow_html=True)

today_records = get_today_records()
all_records = get_all_records()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><h3>{len(today_records)}</h3><p>📦 Items Hari Ini</p></div>', unsafe_allow_html=True)
with col2:
    total_yard = sum(r['yard'] for r in today_records) if today_records else 0
    st.markdown(f'<div class="metric-card"><h3>{total_yard:,.0f}</h3><p>📏 Yard Hari Ini</p></div>', unsafe_allow_html=True)
with col3:
    mesin_aktif = len(set(r['mesin'] for r in today_records)) if today_records else 0
    st.markdown(f'<div class="metric-card"><h3>{mesin_aktif}</h3><p>⚙️ Mesin Aktif</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><h3>{len(all_records)}</h3><p>📚 Total Records</p></div>', unsafe_allow_html=True)

st.markdown("### 🚀 Mulai Cepat")
st.markdown("1️⃣ Buka halaman **💬 Chat** di sidebar")
st.markdown("2️⃣ Ketik data stock opname dalam bahasa natural")
st.markdown("3️⃣ AI akan parse & simpan otomatis")
st.markdown("4️⃣ Lihat **📊 Dashboard** untuk visualisasi")
APPEOF

# pages/1_Chat.py
cat > "pages/1_💬_Chat.py" << 'CHATEOF'
import streamlit as st
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from utils.database import insert_record, get_today_records
from utils.gemini_helper import chat_with_ai, analyze_image, generate_report

st.set_page_config(page_title="StockAI - Chat", page_icon="💬", layout="wide")
st.title("💬 Chat - Stock Opname")
st.caption("Ketik data stock opname dalam bahasa natural atau upload foto label kain")

if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Halo! Saya StockAI, asisten stock opname cerdas.\n\nContoh input:\n- *\"Mesin 3 jam 10, drill navy party 2405, 350 yard\"*\n- *\"Rangkum hari ini\"*\n- Atau upload foto label kain 📸"
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

uploaded_file = st.file_uploader("📸 Upload foto label kain (opsional)", type=['jpg', 'jpeg', 'png'], key="img_upload")

if uploaded_file:
    with st.chat_message("user"):
        st.image(uploaded_file, caption="📸 Foto label kain", width=300)
    st.session_state.messages.append({"role": "user", "content": "📸 [Upload foto label kain]"})
    
    image_bytes = uploaded_file.getvalue()
    mime_type = "image/jpeg"
    
    with st.spinner("🔍 Menganalisis foto..."):
        result = analyze_image(image_bytes, mime_type)
    
    if result.get('action') == 'insert' and 'data' in result:
        data = result['data']
        data['tanggal'] = str(date.today())
        record_id = insert_record(data)
        response = f"✅ **Data dari foto berhasil di-extract!**\n\n"
        response += f"- 🏭 Mesin: {data.get('mesin', '-')}\n"
        response += f"- 🧵 Kode: {data.get('kode_produksi', '-')}\n"
        response += f"- 🎨 Warna: {data.get('warna', '-')}\n"
        response += f"- 🏷️ Party: {data.get('party', '-')}\n"
        response += f"- 📏 Yard: {data.get('yard', 0)}\n"
        today = get_today_records()
        response += f"\n📊 **Running Total:** {len(today)} items | {sum(r['yard'] for r in today):,.0f} yard"
    else:
        response = result.get('response', 'Tidak bisa membaca foto. Coba yang lebih jelas.')
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

if prompt := st.chat_input("Ketik data stock opname atau pertanyaan..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    today_records = get_today_records()
    context = ""
    if today_records:
        context = f"Total hari ini: {len(today_records)} items, {sum(r['yard'] for r in today_records):,.0f} yard.\nData: {str(today_records[:10])}"
    
    with st.spinner("🤖 Memproses..."):
        result = chat_with_ai(prompt, context)
    
    if result.get('action') == 'insert' and 'data' in result:
        data = result['data']
        data['tanggal'] = str(date.today())
        record_id = insert_record(data)
        response = f"✅ **Tercatat!**\n\n"
        response += f"- 🏭 Mesin: {data.get('mesin', '-')}\n"
        response += f"- 🧵 Kode: {data.get('kode_produksi', '-')}\n"
        response += f"- 🎨 Warna: {data.get('warna', '-')}\n"
        response += f"- ⚙️ Proses: {data.get('proses_produksi', '-')}\n"
        response += f"- 🏷️ Party: {data.get('party', '-')}\n"
        response += f"- 📏 Yard: {data.get('yard', 0)}\n"
        response += f"- 🕐 Jam: {data.get('jam', '-')}\n"
        response += f"\n*{result.get('confirmation', 'Berhasil!')}*"
        today = get_today_records()
        response += f"\n\n📊 **Running Total:** {len(today)} items | {sum(r['yard'] for r in today):,.0f} yard"
    elif result.get('action') == 'query':
        report_keywords = ['rangkum', 'summary', 'laporan', 'report', 'total']
        if any(kw in prompt.lower() for kw in report_keywords) and today_records:
            with st.spinner("📊 Generating report..."):
                response = generate_report(today_records, prompt)
        else:
            response = result.get('response', 'Maaf, coba ulangi.')
    else:
        response = result.get('response', str(result))
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
CHATEOF

# pages/2_Dashboard.py
cat > "pages/2_📊_Dashboard.py" << 'DASHEOF'
import streamlit as st
import sys
import os
import pandas as pd
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from utils.database import get_today_records, get_records_by_range, get_all_records
from utils.charts import chart_output_per_mesin, chart_trend_harian, chart_komposisi_warna, chart_items_per_mesin

st.set_page_config(page_title="StockAI - Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")

view_mode = st.selectbox("📅 Periode", ["Hari Ini", "7 Hari Terakhir", "30 Hari Terakhir", "Semua Data"])

today = date.today()
if view_mode == "Hari Ini":
    records = get_today_records()
elif view_mode == "7 Hari Terakhir":
    records = get_records_by_range(str(today - timedelta(days=7)), str(today))
elif view_mode == "30 Hari Terakhir":
    records = get_records_by_range(str(today - timedelta(days=30)), str(today))
else:
    records = get_all_records()

if not records:
    st.info("📭 Belum ada data. Mulai input di halaman Chat!")
else:
    total_items = len(records)
    total_yard = sum(r['yard'] for r in records)
    mesin_aktif = len(set(r['mesin'] for r in records if r['mesin']))
    avg_yard = total_yard / total_items if total_items > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Items", f"{total_items:,}")
    col2.metric("📏 Total Yard", f"{total_yard:,.0f}")
    col3.metric("⚙️ Mesin Aktif", mesin_aktif)
    col4.metric("📐 Rata-rata/Item", f"{avg_yard:,.0f} yd")
    
    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig = chart_output_per_mesin(records)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with col_chart2:
        fig = chart_komposisi_warna(records)
        if fig: st.plotly_chart(fig, use_container_width=True)
    
    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        fig = chart_trend_harian(records)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with col_chart4:
        fig = chart_items_per_mesin(records)
        if fig: st.plotly_chart(fig, use_container_width=True)
DASHEOF

# pages/3_Riwayat.py
cat > "pages/3_📋_Riwayat.py" << 'HISTEOF'
import streamlit as st
import sys
import os
import pandas as pd
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from utils.database import get_all_records, get_records_by_date, get_records_by_range, delete_record

st.set_page_config(page_title="StockAI - Riwayat", page_icon="📋", layout="wide")
st.title("📋 Riwayat Stock Opname")

col1, col2, col3 = st.columns(3)
with col1:
    filter_type = st.selectbox("Filter", ["Hari Ini", "Pilih Tanggal", "Semua"])
with col2:
    if filter_type == "Pilih Tanggal":
        selected_date = st.date_input("Tanggal", value=date.today())

if filter_type == "Hari Ini":
    records = get_records_by_date(str(date.today()))
elif filter_type == "Pilih Tanggal":
    records = get_records_by_date(str(selected_date))
else:
    records = get_all_records()

if not records:
    st.info("📭 Tidak ada data.")
else:
    df = pd.DataFrame(records)
    search = st.text_input("🔍 Cari (party, warna, mesin...)")
    if search:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        df = df[mask]
    
    display_cols = [c for c in ['id','tanggal','jam','mesin','kode_produksi','warna','proses_produksi','party','yard','notes'] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Total Items", len(df))
    col_s2.metric("Total Yard", f"{df['yard'].sum():,.0f}")
    col_s3.metric("Mesin", f"{df['mesin'].nunique()} aktif")
    
    with st.expander("🗑️ Hapus Record"):
        del_id = st.number_input("ID record", min_value=1, step=1)
        if st.button("Hapus"):
            delete_record(int(del_id))
            st.success(f"✅ Record #{del_id} dihapus!")
            st.rerun()
HISTEOF

# pages/4_Export.py
cat > "pages/4_📤_Export.py" << 'EXPEOF'
import streamlit as st
import sys
import os
import pandas as pd
from datetime import date, timedelta
import io

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from utils.database import get_all_records, get_records_by_date, get_records_by_range

st.set_page_config(page_title="StockAI - Export", page_icon="📤", layout="wide")
st.title("📤 Export Data")

export_range = st.selectbox("Periode", ["Hari Ini", "7 Hari Terakhir", "30 Hari Terakhir", "Semua Data"])

today = date.today()
if export_range == "Hari Ini":
    records = get_records_by_date(str(today))
    suffix = today.strftime('%Y%m%d')
elif export_range == "7 Hari Terakhir":
    records = get_records_by_range(str(today - timedelta(days=7)), str(today))
    suffix = "7days"
elif export_range == "30 Hari Terakhir":
    records = get_records_by_range(str(today - timedelta(days=30)), str(today))
    suffix = "30days"
else:
    records = get_all_records()
    suffix = "all"

if not records:
    st.info("📭 Tidak ada data.")
else:
    df = pd.DataFrame(records)
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Stock Opname')
        st.download_button("⬇️ Download Excel", buffer.getvalue(), f"stock_opname_{suffix}.xlsx",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        csv_data = df.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv_data, f"stock_opname_{suffix}.csv", "text/csv")
EXPEOF

# README.md
cat > README.md << 'READMEEOF'
# StockAI 🏭 — Asisten Stok Opname Cerdas untuk Produksi Tekstil

> Mengubah proses stock opname tekstil yang manual menjadi percakapan sederhana dengan AI.

## 🚀 Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env → masukkan GEMINI_API_KEY dari aistudio.google.com
streamlit run app.py
```

## ✨ Fitur
- 💬 Input via chat natural language
- 📸 Scan foto label kain (Gemini Vision)
- 📊 Dashboard & grafik real-time
- 📋 Laporan otomatis
- 📤 Export Excel/CSV

## 🛠️ Tech Stack
- Streamlit + Google Gemini 2.0 Flash + SQLite + Plotly

## 🐳 Deploy ke Cloud Run
```bash
gcloud run deploy stock-ai --source . --region asia-southeast1 --allow-unauthenticated --set-env-vars GEMINI_API_KEY=your_key
```

Built for #JuaraVibeCoding 2026
READMEEOF

echo ""
echo "✅ StockAI berhasil dibuat!"
echo "📁 Folder: ./stock-ai/"
echo ""
echo "Langkah selanjutnya:"
echo "1. cd stock-ai"
echo "2. pip install -r requirements.txt"
echo "3. cp .env.example .env (isi API key)"
echo "4. streamlit run app.py"
echo ""
echo "🔥 Good luck di hackathon!"
