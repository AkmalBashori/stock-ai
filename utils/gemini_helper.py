import google.generativeai as genai
import json
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY') or st.secrets.get('GEMINI_API_KEY', '')
genai.configure(api_key=api_key)

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

RULES:
- Bahasa Indonesia casual tapi profesional
- Jika ada field yang tidak disebutkan user, isi dengan string kosong
- Yard harus berupa angka (number), bukan string
- Jika user bilang mesin 3 maka mesin: 3
- Jika user bilang jam 10 maka jam: 10:00
- Selalu konfirmasi data yang tercatat
"""

def get_model():
    return genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=SYSTEM_PROMPT
    )

def parse_ai_response(response_text):
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

def chat_with_ai(user_message, context=""):
    model = get_model()
    prompt = user_message
    if context:
        prompt = f"KONTEKS DATA HARI INI:\n{context}\n\nUSER: {user_message}"
    response = model.generate_content(prompt)
    return parse_ai_response(response.text)

def analyze_image(image_bytes, mime_type="image/jpeg"):
    model = get_model()
    image_part = {"mime_type": mime_type, "data": image_bytes}
    prompt = "Lihat foto label kain ini. Extract semua informasi: party number, warna, yard, mesin, jenis kain, proses produksi. Respond dalam format JSON insert."
    response = model.generate_content([prompt, image_part])
    return parse_ai_response(response.text)
  def generate_report(records, query=""):
    model = get_model()
    records_text = json.dumps(records, indent=2, ensure_ascii=False)
    prompt = f"""Berikut data stock opname:
{records_text}

{query if query else "Buatkan rangkuman lengkap: total items, total yard, breakdown per mesin, per warna, dan insight jika ada."}
Respond sebagai teks biasa, format rapi. Gunakan emoji."""
    response = model.generate_content(prompt)
    return response.text

