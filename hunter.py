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

# --- 2. Fetch Macro Index History ---
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

# --- 3. Dynamic Sector Sync (Nifty 500 Classification) ---
def sync_sectors_dynamic():
    print("🌐 Syncing official NSE sectors...")
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        df = pd.read_csv(io.StringIO(response.text))
        unique_sectors = sorted(df['Industry'].unique().tolist())
        sector_payloads = [{"name": s} for s in unique_sectors]
        supabase.table("market_sectors").upsert(sector_payloads).execute()
        print(f"✅ Synced {len(unique_sectors)} official NSE sectors.")
    except Exception as e:
        print(f"🛑 Sector Sync Error: {e}")

# --- 4. Live News Scraper (NSE Corporate Announcements) ---
def sync_news_dynamic():
    print("📰 Fetching live NSE announcements...")
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-announcements'
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers) # Set cookies
        response = session.get(url, headers=headers)
        raw_news = response.json()
        
        news_payloads = []
        for item in raw_news[:15]: # Capture top 15
            news_payloads.append({
                "headline": item.get('desc', 'N/A'),
                "source": item.get('symbol', 'NSE'),
                "time": item.get('att_date', datetime.now().strftime("%d-%b-%Y")),
                "external_url": "https://www.nseindia.com" + item.get('attachment', '')
            })
        
        if news_payloads:
            # Matches by 'headline' as Primary Key to avoid duplicates
            supabase.table("market_news").upsert(news_payloads).execute()
            print(f"✅ Logged {len(news_payloads)} corporate news items.")
    except Exception as e:
        print(f"🛑 News Sync Error: {e}")

# --- 5. NIFTY 50 Stock Prices Sync ---
def sync_nifty_50_dynamic():
    print("🌐 Syncing NIFTY 50 live data...")
    url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        df_list = pd.read_csv(io.StringIO(response.text))
        yf_tickers = [f"{s}.NS" for s in df_list['Symbol']]
        data = yf.download(yf_tickers, period="5d", interval="1d", group_by='ticker')
        
        stock_payloads = []
        for ticker in yf_tickers:
            try:
                ticker_data = data[ticker].dropna()
                curr = ticker_data['Close'].iloc[-1]
                prev = ticker_data['Close'].iloc[-2]
                pct = ((curr - prev) / prev) * 100
                stock_payloads.append({
                    "symbol": ticker.replace(".NS", ""),
                    "price": round(curr, 2),
                    "percent_change": round(pct, 2),
                    "last_updated": datetime.now().isoformat()
                })
            except: continue
        
        supabase.table("nifty_50_stocks").upsert(stock_payloads).execute()
        print(f"🚀 Synced {len(stock_payloads)} NIFTY stocks.")
    except Exception as e:
        print(f"🛑 NIFTY Sync Error: {e}")

# --- 6. Execution ---
def run_daily_hunt():
    print("🚀 Running MarketIntel Pipeline...")
    
    # Indices
    nifty_h = fetch_index_history("^NSEI", "NIFTY 50")
    sensex_h = fetch_index_history("^BSESN", "SENSEX")
    if nifty_h: 
        supabase.table("index_history").delete().eq("index_name", "NIFTY 50").execute()
        supabase.table("index_history").insert(nifty_h).execute()
    if sensex_h: 
        supabase.table("index_history").delete().eq("index_name", "SENSEX").execute()
        supabase.table("index_history").insert(sensex_h).execute()

    sync_sectors_dynamic()
    sync_news_dynamic()
    sync_nifty_50_dynamic()
    print("🏁 Pipeline Finish.")

if __name__ == "__main__":
    run_daily_hunt()
