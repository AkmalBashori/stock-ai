# StockAI — Asisten Stok Opname Cerdas untuk Produksi Tekstil 🏭

> Mengubah proses stock opname tekstil yang manual menjadi percakapan sederhana dengan AI.

## 🎯 Problem

Pabrik tekstil melakukan stock opname harian secara manual — tulis di kertas, pindah ke Excel. Proses ini memakan waktu 1-2 jam per shift, rawan error, dan data sulit dianalisis.

## 💡 Solution

StockAI adalah asisten berbasis chat yang menggunakan Google Gemini AI untuk:
- **Parse input natural language** → data terstruktur otomatis
- **Scan foto label kain** → extract data via Gemini Vision
- **Generate laporan otomatis** → rangkuman per shift/hari/minggu
- **Analisis & insight** → deteksi anomali, trend, rekomendasi

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API Key (gratis di [aistudio.google.com](https://aistudio.google.com))

### Installation

```bash
# Clone repo
git clone https://github.com/yourusername/stock-ai.git
cd stock-ai

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env dan masukkan GEMINI_API_KEY

# Run
streamlit run app.py
```

### Deploy ke Google Cloud Run

```bash
# Build & deploy
gcloud run deploy stock-ai \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

## 📸 Screenshots

| Chat Interface | Dashboard |
|---|---|
| Input via natural language | Visualisasi real-time |

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI:** Google Gemini 2.0 Flash (Text + Vision)
- **Database:** SQLite
- **Charts:** Plotly
- **Deploy:** Google Cloud Run

## 📝 Contoh Penggunaan

```
Input: "Mesin 3 jam 10, drill navy party 2405, 350 yard, finishing"
→ AI parse otomatis, simpan ke database, tampilkan konfirmasi

Input: "Rangkum stock opname hari ini"
→ AI generate laporan lengkap dengan breakdown per mesin & warna

Input: [Upload foto label kain]
→ Gemini Vision extract data dari foto otomatis
```

## 👤 Author

Built for #JuaraVibeCoding Hackathon 2026

## 📄 License

MIT
