import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. Configurazione Pagina
st.set_page_config(page_title="2025 Financial Terminal", layout="wide")
st.title("🚀 2025 AI-Sector Alpha Terminal")

# --- STEP 1: DATA ENGINE (ROBUSTO) ---
@st.cache_data
def load_financial_data():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    # Scarichiamo i dati reali 2025
    raw_data = yf.download(tickers, start="2025-01-01", end="2025-12-31")
    
    # Gestione MultiIndex di yfinance
    if isinstance(raw_data.columns, pd.MultiIndex):
        prices = raw_data['Close'].copy()
    else:
        prices = raw_data.copy()
    
    # Pulizia: riempiamo eventuali buchi rari per evitare grafici vuoti
    prices = prices.ffill().bfill() 
    
    # Calcolo rendimenti giornalieri
    returns = prices.pct_change().fillna(0) # Usiamo fillna(0) per non svuotare il DF
    return prices, returns, raw_data

try:
    prices, returns, full_data = load_financial_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# --- SIDEBAR (LOGICA PULITA) ---
st.sidebar.header("Terminal Navigation")
# Abbiamo solo due sezioni principali per evitare duplicati
main_page = st.sidebar.radio("Select View:", ["Global Dashboard", "Technical Deep-Dive"])
selected_stock = st.sidebar.selectbox("Select Focus Stock:", prices.columns.tolist())

# --- PAGINA 1: GLOBAL DASHBOARD (Con i 3 Tab Analitici) ---
if main_page == "Global Dashboard":
    tab1, tab2, tab3 = st.tabs(["📊 Performance Overview", "⚖️ Risk-Reward Profile", "🧩 Correlation Matrix"])

    with tab1:
        st.subheader("Cumulative Growth of $100 in 2025")
        # Normalizzazione: tutto parte da 100
        norm_prices = (prices / prices.iloc[0] * 100)
        fig_line = px.line(norm_prices, template="plotly_dark",
                           labels={'value': 'Normalized Price', 'Date': '2025 Timeline'},
                           color_discrete_sequence=px.colors.qualitative.Prism)
        fig_line.update_layout(hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("2025 Risk vs. Reward")
        st.markdown("Bubble size represents the **Sharpe Ratio** (Efficiency).")
        
        # Calcolo metriche annualizzate
        ann_ret = returns.mean() * 252 * 100
        ann_vol = returns.std() * np.sqrt(252) * 100
        # Evitiamo divisioni per zero
        sharpe = ann_ret / ann_vol.replace(0, np.nan)
        
        risk_df = pd.DataFrame({
            'Ticker': ann_ret.index,
            'Return (%)': ann_ret.values,
            'Volatility (%)': ann_vol.values,
            'Sharpe': sharpe.values
        }).dropna() # Eliminiamo solo qui eventuali errori
        
        # Dimensione bolla sicura
        risk_df['Size'] = risk_df['Sharpe'].apply(lambda x: float(max(x, 0.1)) if pd.notnull(x) else 0.1)

        fig_risk = px.scatter(risk_df, x='Volatility (%)', y='Return (%)',
                              size='Size', text='Ticker', color='Return (%)',
                              color_continuous_scale='Blues', template="plotly_dark",
                              hover_data=['Sharpe'])
        fig_risk.update_traces(textposition='top center')
        st.plotly_chart(fig_risk, use_container_width=True)

    with tab3:
        st.subheader("Sector Correlation Matrix")
        st.markdown("Correlation of daily returns during 2025.")
        corr_matrix = returns.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", 
                             color_continuous_scale='RdYlGn', template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)

# --- PAGINA 2: TECHNICAL DEEP-DIVE ---
else:
    st.subheader(f"Technical Analysis: {selected_stock}")
    
    # Estrazione OHLC
    df_tick = pd.DataFrame({
        'Open': full_data['Open'][selected_stock],
        'High': full_data['High'][selected_stock],
        'Low': full_data['Low'][selected_stock],
        'Close': full_data['Close'][selected_stock]
    }).ffill()
    
    df_tick['SMA20'] = df_tick['Close'].rolling(window=20).mean()

    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(x=df_tick.index, open=df_tick['Open'], 
                         high=df_tick['High'], low=df_tick['Low'], close=df_tick['Close'], name='Price'))
    fig_candle.add_trace(go.Scatter(x=df_tick.index, y=df_tick['SMA20'], 
                         line=dict(color='#084594', width=2), name='SMA 20'))
    
    fig_candle.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig_candle, use_container_width=True)

st.divider()
st.caption("Data Source: Yahoo Finance API. Portfolio Task 11 - Final Version.")
