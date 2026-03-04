# --- Example logic in hunter.py ---

def run_daily_hunt():
    watchlist = ["RELIANCE", "TCS", "HDFCBANK", "BEL"] # Or fetch from an API
    
    for symbol in watchlist:
        # 1. Get standard Momentum/Sentiment data
        stock_data = get_momentum_stats(symbol)
        
        # 2. Get Forensic Scaling data (New Logic)
        forensic = fetch_forensic_data(symbol)
        
        # 3. Consolidate into one payload
        payload = {
            "symbol": symbol,
            "price": stock_data['price'],
            "sentiment_label": stock_data['sentiment'],
            "delivery_percentage": forensic['delivery_percentage'],
            "is_pledged": forensic['is_pledged'],
            # ... other fields
        }
        
        # 4. Push to Supabase
        supabase.table("market_picks").insert(payload).execute()
        
        # 5. Respect NSE rate limits
        time.sleep(1)
