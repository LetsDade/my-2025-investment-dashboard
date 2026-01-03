import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="2025 Real Market Insights", layout="wide")
st.title("📈 2025 REAL Global Investment Dashboard")
st.markdown("This dashboard uses live historical data for the fiscal year 2025.")

# --- DOWNLOAD DATI REALI ---
@st.cache_data
def get_real_data():
    # NVDA = Nvidia, GC=F = Gold Futures, SPY = S&P 500 ETF
    assets = {"NVIDIA": "NVDA", "Gold": "GC=F", "S&P 500": "SPY"}
    df_raw = yf.download(list(assets.values()), start="2025-01-01", end="2025-12-31")['Close']
    
    # Rinominiamo le colonne per chiarezza
    df_raw = df_raw.rename(columns={v: k for k, v in assets.items()})
    
    # Normalizzazione a base 100 per confronto equo
    df_norm = (df_raw / df_raw.iloc[0] * 100)
    return df_norm.reset_index()

df = get_real_data()

# --- SIDEBAR ---
selected_assets = st.sidebar.multiselect(
    "Select Assets:", options=['NVIDIA', 'Gold', 'S&P 500'], 
    default=['NVIDIA', 'Gold', 'S&P 500']
)

# --- CHART ---
if selected_assets:
    fig = px.line(df, x='Date', y=selected_assets, 
                  title="2025 Growth of $100 (Real Market Data)",
                  template="plotly_white",
                  color_discrete_map={'NVIDIA': '#084594', 'Gold': '#ef3b2c', 'S&P 500': '#737373'})
    
    fig.update_layout(hovermode="x unified", yaxis_title="Normalized Price (Base 100)")
    st.plotly_chart(fig, use_container_width=True)

    # Performance finale reale
    st.subheader("Final 2025 Performance")
    cols = st.columns(len(selected_assets))
    for i, asset in enumerate(selected_assets):
        total_ret = df[asset].iloc[-1] - 100
        cols[i].metric(asset, f"{df[asset].iloc[-1]:.2f}", f"{total_ret:.2f}%")
else:
    st.warning("Please select an asset.")

st.info("Source: Real-time data fetched from Yahoo Finance API (yfinance).")
