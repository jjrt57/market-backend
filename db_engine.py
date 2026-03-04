import os
from supabase import create_client, Client

def save_to_cloud(picks):
    print("☁️ Connecting to Supabase Cloud Database...")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("⚠️ Supabase keys not found in environment. Skipping database upload.")
        return

    try:
        supabase: Client = create_client(url, key)
        
        # Loop through the new discoveries and insert them into your table
        for stock in picks:
            data = {
                "symbol": stock.get("symbol", "UNKNOWN"),
                "price": stock.get("price", 0.0),
                "growth": stock.get("growth", "N/A"),
                "icr": stock.get("icr", 0.0),
                "volume_status": stock.get("volume_status", "Normal"),
                "institutional_backing": stock.get("institutional_backing", "Retail"),
                "whale_alert": stock.get("whale_alert", "None"),
                "engine_source": stock.get("status", "System Pick")
            }
            # Insert the row into the 'market_picks' table we created
            supabase.table("market_picks").insert(data).execute()
            
        print(f"✅ Successfully saved {len(picks)} high-potential gems to the cloud database!")
    except Exception as e:
        print(f"❌ Failed to save to database: {e}")