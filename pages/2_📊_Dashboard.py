import streamlit as st
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.database import get_today_records, get_records_by_range, get_all_records
from utils.charts import chart_output_per_mesin, chart_trend_harian, chart_komposisi_warna, chart_items_per_mesin

st.set_page_config(page_title="StockAI - Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.caption("Visualisasi data stock opname real-time")

# Date filter
col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    view_mode = st.selectbox("📅 Periode", ["Hari Ini", "7 Hari Terakhir", "30 Hari Terakhir", "Semua Data"])

# Get data based on filter
today = date.today()
if view_mode == "Hari Ini":
    records = get_today_records()
    period_label = f"Hari Ini ({today.strftime('%d %b %Y')})"
elif view_mode == "7 Hari Terakhir":
    start = str(today - timedelta(days=7))
    records = get_records_by_range(start, str(today))
    period_label = "7 Hari Terakhir"
elif view_mode == "30 Hari Terakhir":
    start = str(today - timedelta(days=30))
    records = get_records_by_range(start, str(today))
    period_label = "30 Hari Terakhir"
else:
    records = get_all_records()
    period_label = "Semua Data"

st.markdown(f"**Periode:** {period_label}")
st.markdown("---")

if not records:
    st.info("📭 Belum ada data untuk periode ini. Mulai input di halaman Chat!")
else:
    # Metric cards
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
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig = chart_output_per_mesin(records)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        fig = chart_komposisi_warna(records)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        fig = chart_trend_harian(records)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col_chart4:
        fig = chart_items_per_mesin(records)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Top performers
    st.markdown("---")
    st.markdown("### 🏆 Top Performers")
    
    import pandas as pd
    df = pd.DataFrame(records)
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        st.markdown("**🏭 Output Tertinggi per Mesin:**")
        mesin_top = df.groupby('mesin')['yard'].sum().sort_values(ascending=False).head(5)
        for mesin, yard in mesin_top.items():
            st.markdown(f"- Mesin **{mesin}**: {yard:,.0f} yard")
    
    with col_top2:
        st.markdown("**🎨 Warna Terbanyak:**")
        warna_top = df.groupby('warna')['yard'].sum().sort_values(ascending=False).head(5)
        for warna, yard in warna_top.items():
            if warna:
                st.markdown(f"- **{warna}**: {yard:,.0f} yard")
