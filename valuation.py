import yfinance as yf
import pandas as pd
import requests
import io
import time
from utils import timer_benchmark

def get_full_nse_list():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    try:
        print("📥 Downloading NSE list...")
        response = requests.get(url, headers=headers, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        return [f"{row['SYMBOL']}.NS" for _, row in df.iterrows()]
    except:
        return ["RELIANCE.NS", "TCS.NS", "SBIN.NS"]

@timer_benchmark
def get_undervalued_gems():
    full_market = get_full_nse_list()
    picks = []
    # Scanning top 100 for speed
    for ticker in full_market[:100]: 
        try:
            stock = yf.Ticker(ticker)
            if full_market.index(ticker) % 5 == 0: time.sleep(1) # Rate limit
            
            info = stock.info
            # Resilient P/E logic: Check forward, then trailing, then default to 100
            pe = info.get('forwardPE') or info.get('trailingPE') or 100
            
            if pe < 30: 
                picks.append({
                    "symbol": ticker.replace(".NS", ""),
                    "price": info.get('currentPrice'),
                    "pe": round(pe, 1),
                    "sector": info.get('sector', 'Miscellaneous'),
                    "industry": info.get('industry', 'N/A'),      
                    "market_cap": info.get('marketCap', 0),       
                    "status": "Undervalued Gem"
                })
        except: 
            continue
    return picks
