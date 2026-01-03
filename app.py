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

# --- STEP 2: CALCOLO METRICHE AVANZATE (FIXED) ---
annualized_return = returns.mean() * 252 * 100
annualized_vol = returns.std() * np.sqrt(252) * 100

# Calcolo Sharpe Ratio
sharpe_ratio = annualized_return / annualized_vol

# Creiamo il DataFrame e PULIAMO i dati
risk_df = pd.DataFrame({
    'Ticker': annualized_return.index,
    'Annualized Return (%)': annualized_return.values,
    'Annualized Volatility (%)': annualized_vol.values,
    'Sharpe Ratio': sharpe_ratio.values
})

# FIX: Gestione valori negativi o NaN per la dimensione delle bolle
# Creiamo una colonna specifica per la dimensione che sia sempre positiva e non nulla
risk_df['Bubble_Size'] = risk_df['Sharpe Ratio'].apply(lambda x: max(x, 0.1) if pd.notnull(x) else 0.1)
# Rimuoviamo eventuali righe con valori infiniti o NaN
risk_df = risk_df.replace([np.inf, -np.inf], np.nan).dropna()

# --- INTERFACCIA A SCHEDE (TABS) ---
tab1, tab2, tab3 = st.tabs(["📊 Performance Overview", "⚖️ Risk-Reward Analysis", "🧩 Correlation Matrix"])

with tab1:
    st.subheader("Cumulative Growth of $100 in 2025")
    normalized_prices = (prices / prices.iloc[0] * 100)
    fig_line = px.line(normalized_prices, 
                       template="plotly_dark",
                       color_discrete_sequence=px.colors.qualitative.Prism)
    fig_line.update_layout(hovermode="x unified", yaxis_title="Normalized Price (Base 100)")
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.subheader("2025 Risk vs. Reward Profile")
    st.markdown("Bubble size represents the **Sharpe Ratio** (Efficiency).")
    
    # FIX: Usiamo 'Bubble_Size' per il parametro size
    fig_risk = px.scatter(risk_df, 
                          x='Annualized Volatility (%)', 
                          y='Annualized Return (%)',
                          size='Bubble_Size', # Ora è sicuro!
                          text='Ticker',
                          color='Annualized Return (%)',
                          color_continuous_scale='Blues',
                          template="plotly_dark",
                          hover_data=['Sharpe Ratio']) # Mostriamo comunque il valore reale nel tooltip
    
    fig_risk.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
    st.plotly_chart(fig_risk, use_container_width=True)

with tab3:
    st.subheader("Sector Correlation Matrix")
    corr_matrix = returns.corr()
    fig_corr = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale='RdYlGn', template="plotly_dark")
    st.plotly_chart(fig_corr, use_container_width=True)
# --- STEP 3: TECHNICAL DEEP-DIVE (CANDLESTICK + SMA) ---
if page == "Technical Deep-Dive":
    st.subheader(f"Technical Analysis: {selected_stock} (Full Year 2025)")
    st.markdown(f"Detailed view of price action with a **20-day Moving Average** to smooth out volatility.")

    # Estraiamo i dati OHLC specifici per il ticker selezionato dal 'full_data' dello Step 1
    # Nota: full_data ha un MultiIndex, quindi accediamo con (Metrica, Ticker)
    df_ticker = pd.DataFrame({
        'Open': full_data['Open'][selected_stock],
        'High': full_data['High'][selected_stock],
        'Low': full_data['Low'][selected_stock],
        'Close': full_data['Close'][selected_stock]
    })

    # Calcolo della Media Mobile a 20 giorni (SMA20)
    df_ticker['SMA20'] = df_ticker['Close'].rolling(window=20).mean()

    # Creazione del grafico Candlestick con Plotly Graph Objects
    fig_candle = go.Figure()

    # 1. Aggiunta delle Candele
    fig_candle.add_trace(go.Candlestick(
        x=df_ticker.index,
        open=df_ticker['Open'],
        high=df_ticker['High'],
        low=df_ticker['Low'],
        close=df_ticker['Close'],
        name='Price Action'
    ))

    # 2. Aggiunta della Media Mobile (Coerenza visiva con il Deep Blue del portfolio)
    fig_candle.add_trace(go.Scatter(
        x=df_ticker.index,
        y=df_ticker['SMA20'],
        line=dict(color='#084594', width=2),
        name='20-day Moving Average'
    ))

    # Styling professionale "Dark Terminal"
    fig_candle.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False, # Pulizia visiva
        yaxis_title="Stock Price (USD)",
        xaxis_title="2025 Timeline",
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_candle, use_container_width=True)

    # Sidebar Insights (Aggiunta di dati dinamici sulla sidebar)
    st.sidebar.divider()
    st.sidebar.write(f"**{selected_stock} Stats:**")
    st.sidebar.write(f"Max Price: ${df_ticker['High'].max():.2f}")
    st.sidebar.write(f"Min Price: ${df_ticker['Low'].min():.2f}")
    st.sidebar.write(f"Volatility (Daily): {returns[selected_stock].std()*100:.2f}%")

# --- FOOTER ---
st.divider()
st.caption("Final Project for Data Analytics Portfolio 2025. All market data is real and fetched via yfinance API.")
