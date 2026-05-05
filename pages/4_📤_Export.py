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
st.caption("Download data stock opname dalam format Excel atau CSV")

# Filter
col1, col2, col3 = st.columns(3)

with col1:
    export_range = st.selectbox("Periode", ["Hari Ini", "7 Hari Terakhir", "30 Hari Terakhir", "Bulan Ini", "Semua Data"])

# Get data
today = date.today()
if export_range == "Hari Ini":
    records = get_records_by_date(str(today))
    filename_suffix = today.strftime('%Y%m%d')
elif export_range == "7 Hari Terakhir":
    start = str(today - timedelta(days=7))
    records = get_records_by_range(start, str(today))
    filename_suffix = f"{(today - timedelta(days=7)).strftime('%Y%m%d')}-{today.strftime('%Y%m%d')}"
elif export_range == "30 Hari Terakhir":
    start = str(today - timedelta(days=30))
    records = get_records_by_range(start, str(today))
    filename_suffix = f"{(today - timedelta(days=30)).strftime('%Y%m%d')}-{today.strftime('%Y%m%d')}"
elif export_range == "Bulan Ini":
    start = str(today.replace(day=1))
    records = get_records_by_range(start, str(today))
    filename_suffix = today.strftime('%Y%m')
else:
    records = get_all_records()
    filename_suffix = "all"

st.markdown("---")

if not records:
    st.info("📭 Tidak ada data untuk periode ini.")
else:
    df = pd.DataFrame(records)
    
    # Preview
    st.markdown(f"### 👀 Preview ({len(records)} records)")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)
    
    if len(records) > 20:
        st.caption(f"*Menampilkan 20 dari {len(records)} records*")
    
    st.markdown("---")
    
    # Export buttons
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # Excel export
        st.markdown("### 📗 Export Excel")
        buffer_xlsx = io.BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Stock Opname')
        
        st.download_button(
            label="⬇️ Download Excel (.xlsx)",
            data=buffer_xlsx.getvalue(),
            file_name=f"stock_opname_{filename_suffix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_dl2:
        # CSV export
        st.markdown("### 📄 Export CSV")
        csv_data = df.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Download CSV (.csv)",
            data=csv_data,
            file_name=f"stock_opname_{filename_suffix}.csv",
            mime="text/csv"
        )
    
    # Summary section
    st.markdown("---")
    st.markdown("### 📊 Ringkasan Export")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Total Records", len(df))
    col_s2.metric("Total Yard", f"{df['yard'].sum():,.0f}")
    col_s3.metric("Mesin", df['mesin'].nunique())
    col_s4.metric("Warna", df['warna'].nunique())
