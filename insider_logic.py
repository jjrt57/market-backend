import pandas as pd
import requests
import io

def get_whale_buys():
    print("🐋 Scanning NSE for Institutional Bulk/Block Deals...")
    url = "https://archives.nseindia.com/content/equities/bulk.csv"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        
        # Filter for massive accumulation: Over 500,000 shares bought in a single trade
        massive_buys = df[(df['Quantity'] > 500000) & (df['Buy/Sell'] == 'BUY')]
        
        # Return a clean list of stock symbols that whales are buying
        return massive_buys['Symbol'].unique().tolist()
    except Exception as e:
        print(f"⚠️ Whale scan failed: {e}")
        return []