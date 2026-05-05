import google.generativeai as genai
import json
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY') or st.secrets.get('GEMINI_API_KEY', '')
genai.configure(api_key=api_key)

SYSTEM_PROMPT = "Kamu adalah StockAI, asisten stock opname cerdas untuk pabrik tekstil. Parse input user menjadi data terstruktur. Respond dalam JSON dengan format: {\"action\": \"insert\", \"data\": {\"jam\": \"\", \"mesin\": \"\", \"kode_produksi\": \"\", \"warna\": \"\", \"proses_produksi\": \"\", \"party\": \"\", \"yard\": 0}, \"confirmation\": \"pesan\"}. Untuk pertanyaan: {\"action\": \"query\", \"response\": \"jawaban\"}. Bahasa Indonesia. Yard harus number."


def get_model():
    return genai.GenerativeModel(model_name='gemini-2.0-flash', system_instruction=SYSTEM_PROMPT)


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
    prompt = "Extract info dari foto label kain ini: party, warna, yard, mesin, jenis kain, proses. Respond JSON."
    response = model.generate_content([prompt, image_part])
    return parse_ai_response(response.text)


def generate_report(records, query=""):
    model = get_model()
    records_text = json.dumps(records, indent=2, ensure_ascii=False)
    prompt = f"Data stock opname:\n{records_text}\n\n{query if query else 'Rangkum: total items, yard, per mesin, per warna, insight.'}\n\nRespond teks biasa, rapi, pake emoji."
    response = model.generate_content(prompt)
    return response.text
