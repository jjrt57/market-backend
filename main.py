import json
import datetime
from valuation import get_undervalued_gems
from macro import get_market_intelligence

def orchestrate():
    print(f"🚀 Execution Started: {datetime.datetime.now()}")
    
    # 1. Test Valuation
    print("🔎 Calling valuation.scan_for_value()...")
    value_picks = valuation.scan_for_value()
    print(f"✅ Found {len(value_picks)} undervalued stocks.")

    # 2. Test Macro
    print("🌎 Calling macro.get_latest_intelligence()...")
    market_intel = macro.get_latest_intelligence()
    print(f"✅ Found {len(market_intel['contracts'])} new contracts.")

    # 3. Final Check
    if not value_picks and not market_intel['contracts']:
        print("⚠️ WARNING: No data found to update! data.json will remain the same.")
        final_output = {
        "meta": {
            "last_updated": datetime.datetime.now().isoformat(),
            "run_id": str(uuid.uuid4())[:8] # Adds a unique 8-character code
        },
        "ai_picks": value_picks, 
        "insights": market_intel["sector_alerts"]
    }
if __name__ == "__main__":
    orchestrate()