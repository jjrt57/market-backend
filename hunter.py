import os
import time
import json
import pandas as pd
import yfinance as yf
from supabase import create_client
from nsepython import nse_eq

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

# --- 2. Custom Sector Overrides ---
CUSTOM_SECTORS = {
    "RELIANCE": "Conglomerate",
    "ADANIENT": "Conglomerate",
    "BEL": "Defense & Aerospace",
    "TCS": "Information Technology",
    "HDFCBANK": "Financial Services",
    "SBIN": "Public Sector Bank"
}

# --- 3. Fetch Intraday Index Data (5-minute intervals) ---
def fetch_intraday_index(ticker_symbol, index_name):
    print(f"📊 Fetching 5-minute intraday data for {indexName}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Fetch today's data in 5-minute intervals
        df = ticker.history(period="1d", interval="5m")
        
        payloads = []
        for timestamp, row in df.iterrows():
            payloads.append({
                "index_name": index_name,
                "timestamp": timestamp.isoformat(), # Standardized time format for Swift
                "price": round(row['Close'], 2)
            })
        return payloads
    except Exception as e:
        print(f"⚠️ Error fetching {indexName}: {e}")
        return []

# --- 4. Fetch Individual Stock Data ---
def fetch_forensic_data(symbol):
    try:
        nse_data = nse_eq(symbol)
        delivery_pct = nse_data.get('securityWiseDP', {}).get('deliveryToTradedQuantity', 0)
        
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        
        # Calculate Real Percentage Growth
        prev_close = info.get('regularMarketPreviousClose', info.get('previousClose', 0))
        curr_price = info.get('currentPrice', 0)
        pct_change = 0.0
        
        if prev_close > 0 and curr_price > 0:
            pct_change = round(((curr_price - prev_close) / prev_close) * 100, 2)
        
        return {
            "delivery_percentage": float(delivery_pct),
            "is_pledged": info.get('pledgedByPromoter', 0) > 0,
            "price": curr_price,
            "pe": info.get('forwardPE', 0),
            "percent_change": pct_change, # The new growth metric!
            "sector": info.get('sector', 'Unknown')
        }
    except Exception as e:
        print(f"⚠️ Skipping {symbol}: {e}")
        return None

# --- 5. Main Execution Engine ---
def run_daily_hunt():
    print("🚀 Initiating MarketIntel Data Pipeline...")
    
    # 1. Wipe old index data to keep the database light (optional but recommended)
    try:
        supabase.table("index_history").delete().neq("index_name", "dummy").execute()
    except Exception as e:
        pass # If it fails, the table might just be empty
        
    # 2. Fetch and Push Macro Indices
    nifty_data = fetch_intraday_index("^NSEI", "NIFTY 50")
    sensex_data = fetch_intraday_index("^BSESN", "SENSEX")
    
    if nifty_data:
        supabase.table("index_history").insert(nifty_data).execute()
    if sensex_data:
        supabase.table("index_history").insert(sensex_data).execute()

    print("✅ Macro Indices Synced.")

    # 3. Fetch and Push Stock Picks
    watchlist = ["RELIANCE", "TCS", "HDFCBANK", "BEL", "ADANIENT", "SBIN"]
    print(f"🚀 Starting Hunt for {len(watchlist)} stocks...")
    
    for symbol in watchlist:
        data = fetch_forensic_data(symbol)
        if data:
            raw_sector = data['sector']
            final_sector = CUSTOM_SECTORS.get(symbol, raw_sector)
            
            payload = {
                "symbol": symbol,
                "price": data['price'],
                "pe": data['pe'],
                "percent_change": data['percent_change'], # Injects the real growth %
                "sector": final_sector,
                "delivery_percentage": data['delivery_percentage'],
                "is_pledged": data['is_pledged'],
                "sentiment_label": "High Sentiment" 
            }
            
            try:
                supabase.table("market_picks").insert(payload).execute()
                print(f"✅ Logged {symbol} | Growth: {data['percent_change']}% | Sector: {final_sector}")
            except Exception as e:
                print(f"❌ Supabase Error for {symbol}: {e}")
        
        time.sleep(2)

    print("🏁 Market Hunt Complete.")

if __name__ == "__main__":
    run_daily_hunt()
