import valuation
import analyzer500
import macro
import insider_logic
import json
import datetime
import notifier
import os
import db_engine # NEW IMPORT

print("🚀 MULTI-ENGINE SCRIPT STARTING...")

def orchestrate():
    print(f"⏰ Execution Time: {datetime.datetime.now()}")
    
    # --- 1. Load Old Data (The "Memory") ---
    old_symbols = set()
    if os.path.exists('data.json'):
        try:
            with open('data.json', 'r') as f:
                old_data = json.load(f)
                # Remember what stocks we already knew about
                for stock in old_data.get('premium_value_picks', []):
                    old_symbols.add(stock['symbol'])
                for stock in old_data.get('high_potential_budget_under_500', []):
                    old_symbols.add(stock['symbol'])
        except Exception:
            pass

    # --- 2. Run Engines ---
    print("🔎 Calling standard valuation engine...")
    gems = valuation.get_undervalued_gems()

    print("🔋 Searching for high-potential 'Olectra-style' budget picks...")
    budget_gems = analyzer500.scan_high_potential_budget()

    # --- NEW: GET WHALE DEALS ---
    whale_symbols = insider_logic.get_whale_buys()

    # Apply Whale Tags to our discoveries
    all_current_picks = gems + budget_gems
    for stock in all_current_picks:
        clean_symbol = stock['symbol'].replace(".NS", "")
        if clean_symbol in whale_symbols:
            stock['whale_alert'] = "🚨 MASSIVE BLOCK DEAL DETECTED TODAY"

    # --- 3. Check for NEW Discoveries ---
    new_discoveries = [stock for stock in all_current_picks if stock['symbol'] not in old_symbols]
    
    # ---> THE FIX IS HERE <---
    if len(new_discoveries) > 0 and len(old_symbols) > 0:
        print(f"🔔 Found {len(new_discoveries)} new stocks! Triggering email and cloud save...")
        notifier.send_alert(new_discoveries)
        db_engine.save_to_cloud(new_discoveries) # Placed safely inside the condition!
    elif len(new_discoveries) > 0 and len(old_symbols) == 0:
        print(f"🌱 First run detected! Saving {len(new_discoveries)} initial stocks to cloud...")
        db_engine.save_to_cloud(new_discoveries)
    else:
        print("ℹ️ No new stocks found this run. No email or cloud save sent.")

    # --- 4. Consolidate and Save Locally ---
    output = {
        "meta": {"last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        "premium_value_picks": gems,
        "high_potential_budget_under_500": budget_gems,
        "market_intelligence": macro.get_latest_intelligence()
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print("💾 data.json successfully updated locally.")

if __name__ == "__main__":
    orchestrate()