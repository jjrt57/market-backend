import os
import time
import yfinance as yf
from supabase import create_client
from nsepython import nse_eq

# --- Initialize Supabase from GitHub Secrets ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def fetch_forensic_data(symbol):
    """Fetches NSE-specific delivery data and pledging status."""
    try:
        # NSE India delivery data
        nse_data = nse_eq(symbol)
        delivery_pct = nse_data.get('securityWiseDP', {}).get('deliveryToTradedQuantity', 0)
        
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        is_pledged = info.get('pledgedByPromoter', 0) > 0 # Forensic check
        
        return {
            "delivery_percentage": float(delivery_pct),
            "is_pledged": is_pledged,
            "price": info.get('currentPrice', 0),
            "pe": info.get('forwardPE', 0),
            "sector": info.get('sector', 'Unknown')
        }
    except:
        return {"delivery_percentage": 0, "is_pledged": False, "price": 0, "pe": 0, "sector": "N/A"}

def run_daily_hunt():
    # You can also fetch the Nifty 50 symbols list here to scale beyond 4 stocks
    watchlist = ["RELIANCE", "TCS", "HDFCBANK", "BEL", "ADANIENT", "SBIN"] 
    
    for symbol in watchlist:
        # Get Forensic and Momentum data
        data = fetch_forensic_data(symbol)
        
        payload = {
            "symbol": symbol,
            "price": data['price'],
            "pe": data['pe'],
            "sector": data['sector'],
            "delivery_percentage": data['delivery_percentage'],
            "is_pledged": data['is_pledged'],
            "sentiment_label": "High Sentiment" # Replace with your sentiment logic
        }
        
        # Push to Supabase
        supabase.table("market_picks").insert(payload).execute()
        
        # Respect NSE rate limits to avoid IP blocks
        time.sleep(1)

if __name__ == "__main__":
    run_daily_hunt()
