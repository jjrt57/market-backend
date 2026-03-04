import valuation
import analyzer500
import macro
import insider_logic # NEW IMPORT
import json
import datetime
import notifier
import os

print("🚀 MULTI-ENGINE SCRIPT STARTING...")

def orchestrate():
    print(f"⏰ Execution Time: {datetime.datetime.now()}")
    
    # 1. Load Old Data (Memory)
    # ... (Keep your existing memory logic here) ...
    old_symbols = set()
    # ... (Keep your old_symbols logic) ...

    # 2. Run Engines
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

    # 3. Check for NEW Discoveries
    new_discoveries = [stock for stock in all_current_picks if stock['symbol'] not in old_symbols]
    
    if len(new_discoveries) > 0 and len(old_symbols) > 0:
        print(f"🔔 Found {len(new_discoveries)} new stocks! Triggering email...")
        notifier.send_alert(new_discoveries)
    else:
        print("ℹ️ No new stocks found this run. No email sent.")

    # 4. Consolidate and Save
    output = {
        "meta": {"last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        "premium_value_picks": gems,
        "high_potential_budget_under_500": budget_gems,
        "market_intelligence": macro.get_latest_intelligence()
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print("💾 data.json successfully updated.")

if __name__ == "__main__":
    orchestrate()