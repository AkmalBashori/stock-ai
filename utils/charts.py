import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def chart_output_per_mesin(records: list):
    """Bar chart: total yard per mesin"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    mesin_data = df.groupby('mesin')['yard'].sum().reset_index()
    mesin_data = mesin_data.sort_values('mesin')
    
    fig = px.bar(
        mesin_data, 
        x='mesin', 
        y='yard',
        title='📊 Output per Mesin (Yard)',
        labels={'mesin': 'Mesin', 'yard': 'Total Yard'},
        color='yard',
        color_continuous_scale=['#1a237e', '#ffd600']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1a237e'
    )
    return fig

def chart_trend_harian(records: list):
    """Line chart: daily trend"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    daily_data = df.groupby('tanggal')['yard'].sum().reset_index()
    daily_data = daily_data.sort_values('tanggal')
    
    fig = px.line(
        daily_data,
        x='tanggal',
        y='yard',
        title='📈 Trend Output Harian',
        labels={'tanggal': 'Tanggal', 'yard': 'Total Yard'},
        markers=True
    )
    fig.update_traces(line_color='#1a237e', marker_color='#ffd600')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1a237e'
    )
    return fig

def chart_komposisi_warna(records: list):
    """Pie chart: color composition"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    warna_data = df.groupby('warna')['yard'].sum().reset_index()
    
    fig = px.pie(
        warna_data,
        values='yard',
        names='warna',
        title='🎨 Komposisi Warna',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1a237e'
    )
    return fig

def chart_items_per_mesin(records: list):
    """Bar chart: items count per mesin"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    mesin_count = df.groupby('mesin').size().reset_index(name='items')
    mesin_count = mesin_count.sort_values('mesin')
    
    fig = px.bar(
        mesin_count,
        x='mesin',
        y='items',
        title='📦 Jumlah Item per Mesin',
        labels={'mesin': 'Mesin', 'items': 'Jumlah Item'},
        color='items',
        color_continuous_scale=['#ffd600', '#1a237e']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1a237e'
    )
    return fig
