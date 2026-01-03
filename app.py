import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. Configurazione Pagina
st.set_page_config(page_title="2025 Financial Terminal", layout="wide")
st.title("🚀 2025 AI-Sector Alpha Terminal")

# --- STEP 1: DATA ENGINE (EXTRA ROBUST) ---
@st.cache_data
def load_financial_data():
    # Definiamo i ticker e forziamo l'ordine
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    
    # Scarichiamo i dati reali 2025
    raw_data = yf.download(tickers, start="2025-01-01", end="2025-12-31")
    
    # Estrazione prezzi di chiusura
    if isinstance(raw_data.columns, pd.MultiIndex):
        prices = raw_data['Close'].copy()
    else:
        prices = raw_data.copy()
    
    # FORZATURA: Assicuriamoci di avere tutte le colonne richieste
    # Se un ticker manca, yfinance lo avrà messo come colonna di NaN, noi lo vogliamo vedere
    for t in tickers:
        if t not in prices.columns:
            prices[t] = np.nan
            
    # Riordiniamo le colonne secondo la nostra lista
    prices = prices[tickers]
    
    # Pulizia dati per evitare grafici vuoti
    prices = prices.ffill().bfill() 
    returns = prices.pct_change().fillna(0)
    
    return prices, returns, raw_data

try:
    prices, returns, full_data = load_financial_data()
    st.sidebar.success(f"✅ Loaded {len(prices.columns)} Assets")
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("Terminal Navigation")
main_page = st.sidebar.radio("Select View:", ["Global Dashboard", "Technical Deep-Dive"])
selected_stock = st.sidebar.selectbox("Select Focus Stock:", prices.columns.tolist())

# --- PAGINA 1: GLOBAL DASHBOARD ---
if main_page == "Global Dashboard":
    tab1, tab2, tab3 = st.tabs(["📊 Performance Overview", "⚖️ Risk-Reward Profile", "🧩 Correlation Matrix"])

    with tab1:
        st.subheader("Cumulative Growth of $100 in 2025")
        norm_prices = (prices / prices.iloc[0] * 100)
        fig_line = px.line(norm_prices, template="plotly_dark",
                           labels={'value': 'Normalized Price', 'Date': '2025 Timeline'},
                           color_discrete_sequence=px.colors.qualitative.Prism)
        fig_line.update_layout(hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("2025 Risk vs. Reward")
        st.markdown("Bubble size and color represent the **Sharpe Ratio** (Investment Efficiency).")
        
        # Calcolo metriche annualizzate
        ann_ret = returns.mean() * 252 * 100
        ann_vol = returns.std() * np.sqrt(252) * 100
        sharpe = ann_ret / ann_vol.replace(0, np.nan)
        
        risk_df = pd.DataFrame({
            'Ticker': ann_ret.index,
            'Return (%)': ann_ret.values,
            'Volatility (%)': ann_vol.values,
            'Sharpe Ratio': sharpe.values
        }).dropna()
        
        # Dimensione bolla sicura
        risk_df['Bubble_Size'] = risk_df['Sharpe Ratio'].apply(lambda x: float(max(x, 0.1)) if pd.notnull(x) else 0.1)

        # FIX: Colore mappato su Sharpe Ratio invece che su Return
        fig_risk = px.scatter(risk_df, 
                              x='Volatility (%)', 
                              y='Return (%)',
                              size='Bubble_Size', 
                              text='Ticker', 
                              color='Sharpe Ratio', # Cambiato da Return a Sharpe Ratio
                              color_continuous_scale='Blues', 
                              template="plotly_dark",
                              hover_data=['Return (%)', 'Volatility (%)'])
        
        fig_risk.update_traces(textposition='top center')
        st.plotly_chart(fig_risk, use_container_width=True)

    with tab3:
        st.subheader("Sector Correlation Matrix")
        corr_matrix = returns.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", 
                             color_continuous_scale='RdYlGn', template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)

# --- PAGINA 2: TECHNICAL DEEP-DIVE ---
else:
    st.subheader(f"Technical Analysis: {selected_stock}")
    
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
st.caption("Data Source: Yahoo Finance API. Portfolio Final Task - Verified Version.")
