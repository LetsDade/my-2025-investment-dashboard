{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww34360\viewh21680\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import plotly.express as px\
import numpy as np\
\
# Configurazione Pagina\
st.set_page_config(page_title="2025 Investment Dashboard", layout="wide")\
\
st.title("\uc0\u55357 \u56520  2025 Global Investment Dashboard")\
st.markdown("Interactive comparison of key assets performance throughout 2025.")\
\
# --- DATI SIMULATI 2025 (Coerenti con i task precedenti) ---\
dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq='D')\
n_days = len(dates)\
\
# Generazione trend basati sui rendimenti finali discussi\
nvidia_prices = 100 * (1 + np.cumsum(np.random.normal(0.0015, 0.02, n_days)))\
gold_prices = 100 * (1 + np.cumsum(np.random.normal(0.002, 0.01, n_days)))\
sp500_prices = 100 * (1 + np.cumsum(np.random.normal(0.0006, 0.012, n_days)))\
\
df = pd.DataFrame(\{\
    'Date': dates,\
    'NVIDIA': nvidia_prices,\
    'Gold': gold_prices,\
    'S&P 500': sp500_prices\
\}).set_index('Date')\
\
# --- SIDEBAR PER FILTRI ---\
st.sidebar.header("Dashboard Settings")\
selected_assets = st.sidebar.multiselect(\
    "Select Assets to Compare:",\
    options=['NVIDIA', 'Gold', 'S&P 500'],\
    default=['NVIDIA', 'Gold', 'S&P 500']\
)\
\
date_range = st.sidebar.date_input(\
    "Select Date Range:",\
    value=(dates[0], dates[-1]),\
    min_value=dates[0],\
    max_value=dates[-1]\
)\
\
# --- LOGICA DI VISUALIZZAZIONE ---\
if selected_assets:\
    # Filtraggio dati\
    filtered_df = df.loc[date_range[0]:date_range[1], selected_assets]\
    \
    # Calcolo Performance Relativa (Normalizzata a 100)\
    normalized_df = (filtered_df / filtered_df.iloc[0] * 100)\
    \
    # Grafico Interattivo Plotly\
    fig = px.line(normalized_df, \
                  title="Cumulative Return (Base 100)",\
                  labels=\{'value': 'Normalized Price', 'Date': 'Timeline'\},\
                  template="plotly_white",\
                  color_discrete_map=\{'NVIDIA': '#084594', 'Gold': '#ef3b2c', 'S&P 500': '#737373'\})\
    \
    fig.update_layout(hovermode="x unified")\
    st.plotly_chart(fig, use_container_width=True)\
    \
    # Metriche Riassuntive\
    col1, col2, col3 = st.columns(3)\
    for i, asset in enumerate(selected_assets):\
        perf = ((filtered_df[asset].iloc[-1] / filtered_df[asset].iloc[0]) - 1) * 100\
        cols = [col1, col2, col3]\
        cols[i % 3].metric(label=f"\{asset\} Perf.", value=f"\{perf:.2f\}%")\
else:\
    st.warning("Please select at least one asset in the sidebar.")\
\
st.info("Source: Simulated data based on Global Carbon Budget and Market Reports 2025.")}