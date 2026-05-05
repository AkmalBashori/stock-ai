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

# Initialize DB on import
init_db()
