import yfinance as yf
import pandas as pd
import requests
import io

def get_full_nse_list():
    """Downloads the official EQUITY_L.csv from NSE to get all listed tickers."""
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("📥 Downloading official NSE Equity list...")
        response = requests.get(url, headers=headers, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        
        # Yahoo Finance requires '.NS' suffix for NSE stocks
        symbols = [f"{row['SYMBOL']}.NS" for _, row in df.iterrows()]
        print(f"✅ Found {len(symbols)} active tickers.")
        return symbols
    except Exception as e:
        print(f"❌ Failed to download NSE list: {e}")
        # Fallback to a small list if download fails
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]

def scan_for_value():
    # 1. Dynamically discover the entire market
    full_market = get_full_nse_list()
    
    picks = []
    # 2. Analyze a subset (e.g., first 100) to stay within GitHub Action limits
    # You can increase this, but be mindful of the 30-min window
    for ticker in full_market[:150]: 
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            pe = info.get('forwardPE', 100)
            growth = info.get('earningsGrowth', 0)
            
            # Logic: PE < 25 and Growth > 15% (Adjust for 2026 market)
            if pe < 25 and growth > 0.15:
                picks.append({
                    "symbol": ticker.replace(".NS", ""),
                    "price": info.get('currentPrice'),
                    "pe": round(pe, 1),
                    "sector": info.get('sector', 'N/A'),
                    "reason": "Discovery: High Growth / Low Valuation"
                })
        except: continue
        
    return picks