import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Configurazione Dashboard Professionale
st.set_page_config(page_title="2025 Alpha Terminal", layout="wide", initial_sidebar_state="expanded")

# Custom CSS per un look "Bloomberg Terminal"
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 2025 AI-Sector Risk-Reward Terminal")
st.markdown("Advanced analytics for the Magnificent Seven during the 2025 Fiscal Year.")

# --- STEP 1: DATA ENGINE ---
@st.cache_data
def load_financial_data():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    # Scarichiamo dati giornalieri reali per tutto il 2025
    data = yf.download(tickers, start="2025-01-01", end="2025-12-31")
    
    # Gestione MultiIndex e pulizia
    if 'Adj Close' in data.columns:
        prices = data['Adj Close']
    else:
        prices = data['Close']
    
    # Calcolo rendimenti giornalieri
    returns = prices.pct_change().dropna()
    return prices, returns, data

prices, returns, full_data = load_financial_data()

# --- SIDEBAR DI NAVIGAZIONE ---
st.sidebar.header("Terminal Controls")
page = st.sidebar.radio("Select View:", ["Market Overview", "Risk-Reward Analysis", "Technical Deep-Dive"])
selected_stock = st.sidebar.selectbox("Focus Stock:", prices.columns)
