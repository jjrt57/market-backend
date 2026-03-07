import os
import time
import json
import pandas as pd
import yfinance as yf
import requests
import io
from datetime import datetime
from supabase import create_client

# --- 1. Load Secrets ---
supabase_data_raw = os.environ.get("SUPABASE_DATA")

if not supabase_data_raw:
    print("❌ Error: SUPABASE_DATA not found in environment.")
    exit(1)

try:
    creds = json.loads(supabase_data_raw)
    URL = creds.get("SUPABASE_URL")
    KEY = creds.get("SUPABASE_KEY")
except Exception as e:
    print(f"❌ JSON Parsing Error: {e}")
    exit(1)

supabase = create_client(URL, KEY)

# --- 2. Fetch Macro Index History (6-Months) ---
def fetch_index_history(ticker_symbol, index_name):
    print(f"📊 Fetching 6-month historical data for {index_name}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="6mo", interval="1d")
        
        payloads = []
        for timestamp, row in df.iterrows():
            payloads.append({
                "index_name": index_name,
                "timestamp": timestamp.isoformat(), 
                "price": round(row['Close'], 2)
            })
        return payloads
    except Exception as e:
        print(f"⚠️ Error fetching {index_name}: {e}")
        return []

# --- 3. Dynamic Sector Sync (NSE Official Classification) ---
def sync_sectors_dynamic():
    print("🌐 Fetching official NSE Industry Classification...")
    # Nifty 500 contains the most comprehensive list of active sectors in India
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        df = pd.read_csv(io.StringIO(response.text))
        
        # Extract unique industries (NSE uses 'Industry' for Sector)
        unique_sectors = sorted(df['Industry'].unique().tolist())
        
        # Format for Supabase
        sector_payloads = [{"name": s} for s in unique_sectors]
        
        # Upsert into market_sectors table
        if sector_payloads:
            supabase.table("market_sectors").upsert(sector_payloads).execute()
            print(f"✅ Successfully synced {len(unique_sectors)} official NSE sectors.")
            
    except Exception as e:
        print(f"🛑 Error syncing sectors: {e}")

# --- 4. Dynamic NIFTY 50 Sync ---
def sync_nifty_50_dynamic():
    print("🌐 Fetching official NIFTY 50 constituent list from NSE...")
    url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        df_list = pd.read_csv(io.StringIO(response.text))
        raw_symbols = df_list['Symbol'].tolist()
        yf_tickers = [f"{s}.NS" for s in raw_symbols]
        
        print(f"✅ Found {len(yf_tickers)} stocks. Fetching batch data...")
        data = yf.download(yf_tickers, period="5d", interval="1d", group_by='ticker')
        
        stock_payloads = []
        for ticker in yf_tickers:
            symbol = ticker.replace(".NS", "")
            try:
                ticker_data = data[ticker].dropna()
                if ticker_data.empty: continue
                
                current_price = ticker_data['Close'].iloc[-1]
                prev_price = ticker_data['Close'].iloc[-2]
                pct_change = ((current_price - prev_price) / prev_price) * 100
                
                stock_payloads.append({
                    "symbol": symbol,
                    "price": round(current_price, 2),
                    "percent_change": round(pct_change, 2),
                    "last_updated": datetime.now().isoformat()
                })
            except:
                continue

        if stock_payloads:
            supabase.table("nifty_50_stocks").upsert(stock_payloads).execute()
            print(f"🚀 Successfully synced {len(stock_payloads)} NIFTY 50 stocks.")

    except Exception as e:
        print(f"🛑 Error syncing NIFTY list: {e}")

# --- 5. Main Execution Engine ---
def run_daily_hunt():
    print("🚀 Initiating MarketIntel Data Pipeline...")
    
    # 1. Sync Macro Indices
    nifty_h = fetch_index_history("^NSEI", "NIFTY 50")
    sensex_h = fetch_index_history("^BSESN", "SENSEX")
    
    if nifty_h:
        supabase.table("index_history").delete().eq("index_name", "NIFTY 50").execute()
        supabase.table("index_history").insert(nifty_h).execute()
    if sensex_h:
        supabase.table("index_history").delete().eq("index_name", "SENSEX").execute()
        supabase.table("index_history").insert(sensex_h).execute()

    # 2. Sync Official Sectors
    sync_sectors_dynamic()

    # 3. Sync NIFTY 50 Stocks
    sync_nifty_50_dynamic()
    
    print("🏁 Market Hunt Complete.")

if __name__ == "__main__":
    run_daily_hunt()
