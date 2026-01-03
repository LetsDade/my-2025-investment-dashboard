import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. Configurazione Pagina
st.set_page_config(page_title="2025 Financial Terminal", layout="wide")
st.title("2025 Magnificent Seven: Equity Performance & Risk Analysis")

# --- STEP 1: MOTORE DATI (VERIFICATO) ---
@st.cache_data
def load_financial_data():
    # Elenco esatto delle Magnifiche 7
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    
    # Download dati 2025
    raw_data = yf.download(tickers, start="2025-01-01", end="2025-12-31")
    
    # Estrazione Close Price con gestione MultiIndex
    if isinstance(raw_data.columns, pd.MultiIndex):
        prices = raw_data['Close'].copy()
    else:
        prices = raw_data.copy()
    
    # Assicuriamoci che tutte le colonne siano presenti e nell'ordine corretto
    prices = prices.reindex(columns=tickers)
    
    # Pulizia dati: riempimento buchi e calcolo rendimenti
    prices = prices.ffill().bfill() 
    returns = prices.pct_change().fillna(0)
    
    return prices, returns, raw_data

try:
    prices, returns, full_data = load_financial_data()
    # Verifica immediata nella sidebar
    st.sidebar.success(f"✅ Assets Loaded: {', '.join(prices.columns)}")
except Exception as e:
    st.error(f"Errore nel caricamento: {e}")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.header("Terminal Navigation")
main_page = st.sidebar.radio("Select View:", ["Global Dashboard", "Technical Deep-Dive"])
selected_stock = st.sidebar.selectbox("Focus Stock Analysis:", prices.columns.tolist())

# --- PAGINA 1: GLOBAL DASHBOARD ---
if main_page == "Global Dashboard":
    tab1, tab2, tab3 = st.tabs(["Performance Overview", "Risk-Reward Profile", "Correlation Matrix"])

    with tab1:
        st.subheader("Cumulative Growth of $100 in 2025")
        norm_prices = (prices / prices.iloc[0] * 100)
        fig_line = px.line(norm_prices, template="plotly_dark",
                           color_discrete_sequence=px.colors.qualitative.Prism)
        fig_line.update_layout(hovermode="x unified", yaxis_title="Value ($)")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("Risk vs. Reward")
        st.markdown("Bubble size represents the **Sharpe Ratio** (Investment Efficiency). Axes show the Risk-Return tradeoff.")
        
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
        
        # Dimensione bolla (sempre positiva per evitare errori grafici)
        risk_df['Size'] = risk_df['Sharpe Ratio'].apply(lambda x: float(max(x, 0.1)))

        # GRAFICO SEMPLIFICATO: Colore fisso Deep Blue del portfolio
        fig_risk = px.scatter(risk_df, 
                              x='Volatility (%)', 
                              y='Return (%)',
                              size='Size', 
                              text='Ticker',
                              template="plotly_dark",
                              hover_data=['Sharpe Ratio'])
        
        # Colore coerente con il resto del portfolio (#084594)
        fig_risk.update_traces(marker=dict(color='#084594', line=dict(width=1, color='white')), 
                               textposition='top center')
        
        fig_risk.update_layout(xaxis_title="Risk (Annualized Volatility %)", 
                               yaxis_title="Reward (Annualized Return %)")
        st.plotly_chart(fig_risk, use_container_width=True)

    with tab3:
        st.subheader("Correlation Matrix")
        st.markdown("Statistical relationship between daily returns. **1.00** indicates perfect synchronization.")
    
        corr_matrix = returns.corr()
    
        fig_corr = px.imshow(corr_matrix, 
                         text_auto=".2f", 
                         color_continuous_scale='RdYlGn', 
                         template="plotly_dark",
                         aspect="equal") # Forza la forma quadrata

        fig_corr.update_layout(
        height=750, # Ancora più grande per risaltare nel portfolio
        margin=dict(l=20, r=20, t=30, b=20),
        coloraxis_colorbar=dict(
            title="Correlation",
            thicknessmode="pixels", thickness=20,
            lenmode="fraction", len=0.7,
            x=0.80, # AVVICINA la scala quasi a ridosso del quadrato
            xanchor="left",
            ticks="outside"
            )
        )
    
    # Pulizia assi per look minimale
        fig_corr.update_xaxes(showgrid=False)
        fig_corr.update_yaxes(showgrid=False)
    
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
    
    # --- UPDATE: TECHNICAL DEEP-DIVE LAYOUT ---
    fig_candle.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False, 
        height=650,
        # Aggiunta etichette assi
        xaxis_title="2025 Trading Timeline",
        yaxis_title="Stock Price (USD)",
        # Aumento margini per far spazio alle etichette
        margin=dict(l=60, r=20, t=50, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(size=12)
    )
    st.plotly_chart(fig_candle, use_container_width=True)

st.divider()
st.caption("Market performance (Jan-Dec 2025). Built with yfinance.")
