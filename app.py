import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Scarico i dati reali delle "Magnifiche 7" per tutto il 2025
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
data = yf.download(tickers, start="2025-01-01", end="2025-12-31", interval="1mo")['Close']

# 2. Calcolo il rendimento percentuale mensile
monthly_returns = data.pct_change().dropna() * 100
monthly_returns.index = monthly_returns.index.strftime('%b') # Formato 'Jan', 'Feb', etc.
monthly_returns = monthly_returns.T # Trasponiamo per avere le aziende sulle righe

# 3. Visualizzazione Heatmap
plt.figure(figsize=(14, 7))
sns.heatmap(monthly_returns, annot=True, fmt=".1f", cmap="RdYlGn", center=0, linewidths=.5)

plt.title('Magnificent Seven: REAL Monthly Performance 2025 (%)', fontsize=16, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Company', fontsize=12)
plt.tight_layout()
plt.savefig('task6_real_heatmap.png', dpi=300)
plt.show()
