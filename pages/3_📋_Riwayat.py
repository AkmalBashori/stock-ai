import streamlit as st
import sys
import os
import pandas as pd
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.database import get_all_records, get_records_by_date, get_records_by_range, delete_record

st.set_page_config(page_title="StockAI - Riwayat", page_icon="📋", layout="wide")

st.title("📋 Riwayat Stock Opname")
st.caption("Lihat dan kelola semua data stock opname")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    filter_type = st.selectbox("Filter", ["Hari Ini", "Pilih Tanggal", "Range Tanggal", "Semua"])

with col2:
    if filter_type == "Pilih Tanggal":
        selected_date = st.date_input("Tanggal", value=date.today())
    elif filter_type == "Range Tanggal":
        start_date = st.date_input("Dari", value=date.today() - timedelta(days=7))

with col3:
    if filter_type == "Range Tanggal":
        end_date = st.date_input("Sampai", value=date.today())

# Get data
if filter_type == "Hari Ini":
    records = get_records_by_date(str(date.today()))
elif filter_type == "Pilih Tanggal":
    records = get_records_by_date(str(selected_date))
elif filter_type == "Range Tanggal":
    records = get_records_by_range(str(start_date), str(end_date))
else:
    records = get_all_records()

st.markdown("---")

if not records:
    st.info("📭 Tidak ada data untuk filter ini.")
else:
    st.markdown(f"**Menampilkan {len(records)} records**")
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Display columns
    display_cols = ['id', 'tanggal', 'jam', 'mesin', 'kode_produksi', 'warna', 'proses_produksi', 'party', 'yard', 'notes']
    available_cols = [c for c in display_cols if c in df.columns]
    
    # Search
    search = st.text_input("🔍 Cari (party, warna, mesin...)")
    if search:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        df = df[mask]
        st.markdown(f"*Hasil pencarian: {len(df)} records*")
    
    # Display table
    st.dataframe(
        df[available_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "tanggal": st.column_config.TextColumn("Tanggal", width="medium"),
            "jam": st.column_config.TextColumn("Jam", width="small"),
            "mesin": st.column_config.TextColumn("Mesin", width="small"),
            "kode_produksi": st.column_config.TextColumn("Kode Produksi"),
            "warna": st.column_config.TextColumn("Warna"),
            "proses_produksi": st.column_config.TextColumn("Proses"),
            "party": st.column_config.TextColumn("Party"),
            "yard": st.column_config.NumberColumn("Yard", format="%.0f"),
            "notes": st.column_config.TextColumn("Notes"),
        }
    )
    
    # Summary
    st.markdown("---")
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Total Items", len(df))
    col_s2.metric("Total Yard", f"{df['yard'].sum():,.0f}")
    col_s3.metric("Mesin", f"{df['mesin'].nunique()} aktif")
    
    # Delete option
    st.markdown("---")
    with st.expander("🗑️ Hapus Record"):
        del_id = st.number_input("Masukkan ID record yang mau dihapus", min_value=1, step=1)
        if st.button("Hapus", type="secondary"):
            delete_record(int(del_id))
            st.success(f"✅ Record #{del_id} berhasil dihapus!")
            st.rerun()
