import streamlit as st
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.database import insert_record, get_today_records, get_summary_today
from utils.gemini_helper import chat_with_ai, analyze_image, generate_report

st.set_page_config(page_title="StockAI - Chat", page_icon="💬", layout="wide")

st.markdown("""
<style>
    .user-msg {
        background: #1a237e;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        display: inline-block;
        max-width: 85%;
        float: right;
        clear: both;
    }
    .ai-msg {
        background: #ffffff;
        color: #333;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        display: inline-block;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        border-left: 3px solid #ffd600;
    }
    .clear { clear: both; }
    .status-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
    }
    .running-total {
        background: #e3f2fd;
        border-left: 4px solid #1a237e;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 Chat - Stock Opname")
st.caption("Ketik data stock opname dalam bahasa natural atau upload foto label kain")

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Halo! Saya StockAI, asisten stock opname cerdas.\n\nKetik data stock opname lo, contoh:\n- *\"Mesin 3 jam 10, drill navy party 2405, 350 yard\"*\n- *\"Rangkum hari ini\"*\n- Atau upload foto label kain 📸\n\nSiap bantu! 🏭"
    })

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Image upload
uploaded_file = st.file_uploader("📸 Upload foto label kain (opsional)", type=['jpg', 'jpeg', 'png'], key="img_upload")

if uploaded_file:
    with st.chat_message("user"):
        st.image(uploaded_file, caption="📸 Foto label kain", width=300)
        st.markdown("*Menganalisis foto...*")
    
    st.session_state.messages.append({"role": "user", "content": "📸 [Upload foto label kain]"})
    
    # Analyze with Gemini Vision
    image_bytes = uploaded_file.getvalue()
    mime_type = f"image/{uploaded_file.type.split('/')[-1]}" if '/' in uploaded_file.type else "image/jpeg"
    
    with st.spinner("🔍 Menganalisis foto dengan AI..."):
        result = analyze_image(image_bytes, mime_type)
    
    if result.get('action') == 'insert' and 'data' in result:
        data = result['data']
        data['tanggal'] = str(date.today())
        record_id = insert_record(data)
        
        confirmation = result.get('confirmation', 'Data berhasil dicatat!')
        response = f"✅ **Data dari foto berhasil di-extract!**\n\n"
        response += f"📋 **Detail:**\n"
        response += f"- 🏭 Mesin: {data.get('mesin', '-')}\n"
        response += f"- 🧵 Kode Produksi: {data.get('kode_produksi', '-')}\n"
        response += f"- 🎨 Warna: {data.get('warna', '-')}\n"
        response += f"- ⚙️ Proses: {data.get('proses_produksi', '-')}\n"
        response += f"- 🏷️ Party: {data.get('party', '-')}\n"
        response += f"- 📏 Yard: {data.get('yard', 0)}\n"
        response += f"\n*ID Record: #{record_id}*"
        
        # Running total
        today = get_today_records()
        total_items = len(today)
        total_yard = sum(r['yard'] for r in today)
        response += f"\n\n📊 **Running Total Hari Ini:** {total_items} items | {total_yard:,.0f} yard"
    else:
        response = result.get('response', 'Maaf, tidak bisa membaca foto ini. Coba foto yang lebih jelas.')
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Chat input
if prompt := st.chat_input("Ketik data stock opname atau pertanyaan..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get context
    today_records = get_today_records()
    context = ""
    if today_records:
        total_items = len(today_records)
        total_yard = sum(r['yard'] for r in today_records)
        context = f"Total hari ini: {total_items} items, {total_yard:,.0f} yard.\n"
        context += f"Data: {str(today_records[:10])}"  # Last 10 records for context
    
    # Get AI response
    with st.spinner("🤖 Memproses..."):
        result = chat_with_ai(prompt, context)
    
    # Handle response
    if result.get('action') == 'insert' and 'data' in result:
        data = result['data']
        data['tanggal'] = str(date.today())
        record_id = insert_record(data)
        
        confirmation = result.get('confirmation', 'Data berhasil dicatat!')
        response = f"✅ **Tercatat!**\n\n"
        response += f"📋 **Detail:**\n"
        response += f"- 🏭 Mesin: {data.get('mesin', '-')}\n"
        response += f"- 🧵 Kode Produksi: {data.get('kode_produksi', '-')}\n"
        response += f"- 🎨 Warna: {data.get('warna', '-')}\n"
        response += f"- ⚙️ Proses: {data.get('proses_produksi', '-')}\n"
        response += f"- 🏷️ Party: {data.get('party', '-')}\n"
        response += f"- 📏 Yard: {data.get('yard', 0)}\n"
        response += f"- 🕐 Jam: {data.get('jam', '-')}\n"
        response += f"\n*{confirmation}*"
        
        # Running total
        today = get_today_records()
        total_items = len(today)
        total_yard = sum(r['yard'] for r in today)
        response += f"\n\n📊 **Running Total:** {total_items} items | {total_yard:,.0f} yard"
    
    elif result.get('action') == 'query':
        # Check if it's a report request
        report_keywords = ['rangkum', 'summary', 'laporan', 'report', 'total']
        if any(kw in prompt.lower() for kw in report_keywords) and today_records:
            with st.spinner("📊 Generating report..."):
                response = generate_report(today_records, prompt)
        else:
            response = result.get('response', 'Maaf, saya tidak mengerti. Coba ulangi dengan format yang berbeda.')
    else:
        response = result.get('response', str(result))
    
    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
