import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. Configurazione Iniziale
st.set_page_config(page_title="2025 Alpha Terminal", layout="wide")

st.title("🚀 2025 AI-Sector Risk-Reward Terminal")
st.markdown("Advanced real-time analytics for the Magnificent Seven in 2025.")

# --- STEP 1: MOTORE DI SCARICAMENTO DATI (ROBUSTO) ---
@st.cache_data
def load_financial_data():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    # Scarichiamo i dati. Usiamo 'Close' per massima compatibilità
    raw_data = yf.download(tickers, start="2025-01-01", end="2025-12-31")
    
    # FIX PER MULTIINDEX: Estraiamo solo i prezzi di chiusura e forziamo il formato
    if isinstance(raw_data.columns, pd.MultiIndex):
        # Se yfinance restituisce livelli (Price, Ticker), prendiamo solo Close
        prices = raw_data['Close'].copy()
    else:
        # Se restituisce una tabella semplice
        prices = raw_data.copy()
    
    # Assicuriamoci che i nomi delle colonne siano puliti (solo i Ticker)
    prices.columns = [col for col in prices.columns]
    
    # Calcolo rendimenti e pulizia
    returns = prices.pct_change().dropna()
    return prices, returns, raw_data

# Caricamento effettivo
try:
    prices, returns, full_data = load_financial_data()
    st.sidebar.success("✅ Data Loaded Successfully")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Terminal Navigation")
page = st.sidebar.radio("Select View:", ["Market Overview", "Risk-Reward Analysis", "Technical Deep-Dive"])
selected_stock = st.sidebar.selectbox("Select Focus Stock:", prices.columns.tolist())

# --- TAB LOGIC ---
if page == "Market Overview" or page == "Risk-Reward Analysis":
    tab1, tab2, tab3 = st.tabs(["📊 Performance Overview", "⚖️ Risk-Reward Profile", "🧩 Correlation Matrix"])

    with tab1:
        st.subheader("Cumulative Growth of $100 in 2025")
        norm_prices = (prices / prices.iloc[0] * 100)
        fig_line = px.line(norm_prices, template="plotly_dark", 
                           color_discrete_sequence=px.colors.qualitative.Prism)
        fig_line.update_layout(hovermode="x unified", yaxis_title="Price (Base 100)")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("2025 Risk vs. Reward")
        # Calcolo metriche
        ann_ret = returns.mean() * 252 * 100
        ann_vol = returns.std() * np.sqrt(252) * 100
        sharpe = ann_ret / ann_vol
        
        risk_df = pd.DataFrame({
            'Ticker': ann_ret.index,
            'Return (%)': ann_ret.values,
            'Volatility (%)': ann_vol.values,
            'Sharpe': sharpe.values
        })
        # Dimensione bolla di sicurezza (sempre positiva)
        risk_df['Size'] = risk_df['Sharpe'].apply(lambda x: max(x, 0.1))

        fig_risk = px.scatter(risk_df, x='Volatility (%)', y='Return (%)',
                              size='Size', text='Ticker', color='Return (%)',
                              color_continuous_scale='Blues', template="plotly_dark")
        st.plotly_chart(fig_risk, use_container_width=True)

    with tab3:
        st.subheader("Sector Correlation Matrix")
        fig_corr = px.imshow(returns.corr(), text_auto=".2f", 
                             color_continuous_scale='RdYlGn', template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)

elif page == "Technical Deep-Dive":
    st.subheader(f"Technical Analysis: {selected_stock}")
    
    # Estrazione OHLC sicura per il ticker selezionato
    df_tick = pd.DataFrame({
        'Open': full_data['Open'][selected_stock],
        'High': full_data['High'][selected_stock],
        'Low': full_data['Low'][selected_stock],
        'Close': full_data['Close'][selected_stock]
    })
    df_tick['SMA20'] = df_tick['Close'].rolling(window=20).mean()

    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(x=df_tick.index, open=df_tick['Open'], 
                         high=df_tick['High'], low=df_tick['Low'], close=df_tick['Close'], name='Price'))
    fig_candle.add_trace(go.Scatter(x=df_tick.index, y=df_tick['SMA20'], 
                         line=dict(color='#084594', width=2), name='SMA 20'))
    
    fig_candle.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig_candle, use_container_width=True)

st.divider()
st.caption("Source: Real 2025 Market Data via Yahoo Finance. Portfolio Final Task.")
