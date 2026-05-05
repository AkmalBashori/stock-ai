import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
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
- Jika user bilang "mesin 3" → mesin: "3"
- Jika user bilang "jam 10" → jam: "10:00"
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
    """Extract JSON from AI response"""
    try:
        # Try to find JSON in <json> tags
        if '<json>' in response_text and '</json>' in response_text:
            json_str = response_text.split('<json>')[1].split('</json>')[0].strip()
            return json.loads(json_str)
        
        # Try to find JSON in code blocks
        if '```json' in response_text:
            json_str = response_text.split('```json')[1].split('```')[0].strip()
            return json.loads(json_str)
        
        if '```' in response_text:
            json_str = response_text.split('```')[1].split('```')[0].strip()
            return json.loads(json_str)
        
        # Try direct JSON parse
        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError):
        return {"action": "query", "response": response_text}

def chat_with_ai(user_message: str, context: str = ""):
    """Send message to Gemini and get structured response"""
    model = get_model()
    
    prompt = user_message
    if context:
        prompt = f"KONTEKS DATA HARI INI:\n{context}\n\nUSER: {user_message}"
    
    response = model.generate_content(prompt)
    return parse_ai_response(response.text)

def analyze_image(image_bytes, mime_type="image/jpeg"):
    """Analyze image of fabric label using Gemini Vision"""
    model = get_vision_model()
    
    image_part = {
        "mime_type": mime_type,
        "data": image_bytes
    }
    
    prompt = "Lihat foto label kain ini. Extract semua informasi yang bisa kamu baca: party number, warna, yard/meter, mesin, jenis kain, proses produksi. Respond dalam format JSON insert seperti di system prompt."
    
    response = model.generate_content([prompt, image_part])
    return parse_ai_response(response.text)

def generate_report(records: list, query: str = ""):
    """Generate report/analysis from records"""
    model = get_model()
    
    records_text = json.dumps(records, indent=2, ensure_ascii=False)
    
    prompt = f"""Berikut data stock opname:
{records_text}

{query if query else "Buatkan rangkuman lengkap: total items, total yard, breakdown per mesin, per warna, dan insight/anomali jika ada."}

Respond sebagai teks biasa (bukan JSON), format yang rapi dan mudah dibaca. Gunakan emoji untuk visual."""
    
    response = model.generate_content(prompt)
    return response.text
