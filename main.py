import valuation
import analyzer500
import macro
import insider_logic
import datetime
import notifier
import db_engine

print("🚀 MULTI-ENGINE SCRIPT STARTING...")

def orchestrate():
    print(f"⏰ Execution Time: {datetime.datetime.now()}")
    
    # --- 1. Load Cloud Memory (Replaces data.json) ---
    # This calls Supabase to see which symbols we have already saved
    old_symbols = db_engine.get_existing_symbols()

    # --- 2. Run Engines ---
    print("🔎 Calling standard valuation engine...")
    gems = valuation.get_undervalued_gems()

    print("🔋 Searching for high-potential 'Olectra-style' budget picks...")
    budget_gems = analyzer500.scan_high_potential_budget()

    whale_symbols = insider_logic.get_whale_buys()

    # Apply Whale Tags to current discoveries
    all_current_picks = gems + budget_gems
    for stock in all_current_picks:
        clean_symbol = stock['symbol'].replace(".NS", "")
        if clean_symbol in whale_symbols:
            stock['whale_alert'] = "🚨 MASSIVE BLOCK DEAL DETECTED TODAY"

    # --- 3. Check for NEW Discoveries ---
    # We only care about stocks that ARE NOT in our old_symbols set
    new_discoveries = [stock for stock in all_current_picks if stock['symbol'] not in old_symbols]
    
    if len(new_discoveries) > 0:
        print(f"🔔 Found {len(new_discoveries)} new stocks! Triggering email and cloud save...")
        notifier.send_alert(new_discoveries)
        db_engine.save_to_cloud(new_discoveries)
    else:
        print("ℹ️ No new stocks found this run. No email or cloud save sent.")

if __name__ == "__main__":
    orchestrate()
