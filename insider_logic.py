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
        
        # --- THE FIX ---
        # 1. Strip all invisible spaces from the column names
        df.columns = df.columns.str.strip()
        
        # 2. Force the column to be named 'Quantity' just in case NSE renamed it
        if 'Quantity Traded' in df.columns:
            df.rename(columns={'Quantity Traded': 'Quantity'}, inplace=True)
        elif 'Qty' in df.columns:
            df.rename(columns={'Qty': 'Quantity'}, inplace=True)
            
        # 3. Clean up the 'Buy/Sell' and 'Symbol' columns just to be safe
        if 'Buy / Sell' in df.columns:
            df.rename(columns={'Buy / Sell': 'Buy/Sell'}, inplace=True)
        # ---------------
        
        # Filter for massive accumulation: Over 500,000 shares bought in a single trade
        massive_buys = df[(df['Quantity'] > 500000) & (df['Buy/Sell'] == 'BUY')]
        
        # Return a clean list of stock symbols that whales are buying
        return massive_buys['Symbol'].unique().tolist()
    except Exception as e:
        print(f"⚠️ Whale scan failed: {e}")
        return []
