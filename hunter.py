import os
import time
import json
import pandas as pd
import yfinance as yf
from supabase import create_client
from nsepython import nse_eq

# --- 1. Load Secrets from JSON ---
supabase_data_raw = os.environ.get("SUPABASE_DATA")

if not supabase_data_raw:
    print("❌ Error: SUPABASE_DATA not found in environment.")
    exit(1)

# Unpack the JSON string
try:
    creds = json.loads(supabase_data_raw)
    URL = creds.get("SUPABASE_URL")
    KEY = creds.get("SUPABASE_KEY")
except Exception as e:
    print(f"❌ JSON Parsing Error: Make sure your secret is a valid JSON format. {e}")
    exit(1)

supabase = create_client(URL, KEY)

# --- 2. Custom Sector Overrides ---
# Add any stock symbol here to forcefully change its sector classification
CUSTOM_SECTORS = {
    "RELIANCE": "Conglomerate",
    "ADANIENT": "Conglomerate",
    "BEL": "Defense & Aerospace",
    "TCS": "Information Technology",
    "HDFCBANK": "Financial Services",
    "SBIN": "Public Sector Bank"
}

def fetch_forensic_data(symbol):
    try:
        # NSE India delivery data
        nse_data = nse_eq(symbol)
        delivery_pct = nse_data.get('securityWiseDP', {}).get('deliveryToTradedQuantity', 0)
        
        # Yahoo Finance for Pledging
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        
        return {
            "delivery_percentage": float(delivery_pct),
            "is_pledged": info.get('pledgedByPromoter', 0) > 0,
            "price": info.get('currentPrice', 0),
            "pe": info.get('forwardPE', 0),
            "sector": info.get('sector', 'Unknown')
        }
    except Exception as e:
        print(f"⚠️ Skipping {symbol}: {e}")
        return None

def run_daily_hunt():
    watchlist = ["RELIANCE", "TCS", "HDFCBANK", "BEL", "ADANIENT", "SBIN"]
    print(f"🚀 Starting Hunt for {len(watchlist)} stocks...")
    
    for symbol in watchlist:
        data = fetch_forensic_data(symbol)
        if data:
            
            # --- 3. Apply the Sector Override Here ---
            raw_sector = data['sector']
            final_sector = CUSTOM_SECTORS.get(symbol, raw_sector)
            
            payload = {
                "symbol": symbol,
                "price": data['price'],
                "pe": data['pe'],
                "sector": final_sector, # Using the newly intercepted variable!
                "delivery_percentage": data['delivery_percentage'],
                "is_pledged": data['is_pledged'],
                "sentiment_label": "High Sentiment" 
            }
            
            # Push to Supabase
            try:
                supabase.table("market_picks").insert(payload).execute()
                print(f"✅ Logged {symbol} | Sector: {final_sector} | Delivery: {data['delivery_percentage']}%")
            except Exception as e:
                print(f"❌ Supabase Error for {symbol}: {e}")
        
        time.sleep(2) # Extra buffer for GitHub IP reliability

if __name__ == "__main__":
    run_daily_hunt()

