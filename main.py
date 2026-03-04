import valuation
import analyzer500
import macro
import json
import datetime
import notifier # NEW: Import your email notifier
import os

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

    # --- 3. Check for NEW Discoveries ---
    all_current_picks = gems + budget_gems
    new_discoveries = [stock for stock in all_current_picks if stock['symbol'] not in old_symbols]
    
    if len(new_discoveries) > 0 and len(old_symbols) > 0:
        print(f"🔔 Found {len(new_discoveries)} completely new stocks! Triggering email...")
        notifier.send_alert(new_discoveries)
    else:
        print("ℹ️ No new stocks found this run. No email sent.")

    # --- 4. Consolidate and Save ---
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