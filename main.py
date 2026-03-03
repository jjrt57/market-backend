import json
import datetime
from valuation import get_undervalued_gems
from macro import get_market_intelligence

def orchestrate():
    print(f"🚀 Started Analysis at {datetime.datetime.now()}")

    # 1. Run Value Engine (Scouts for cheap stocks)
    print("🔎 Scanning Nifty for Value Gems...")
    gems = get_undervalued_gems()

    # 2. Run Macro Engine (Scouts for Contracts & Global News)
    print("🌎 Scanning Global News & Govt Contracts...")
    intel = get_market_intelligence()

    # 3. Consolidate Data
    final_data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_status": "ACTIVE" if 9 <= datetime.datetime.now().hour < 16 else "CLOSED",
        "value_picks": gems,
        "govt_contracts": intel["contracts"],
        "global_alerts": intel["global_alerts"]
    }

    # 4. Save to Private JSON
    with open('data.json', 'w') as f:
        json.dump(final_data, f, indent=4)
    
    print(f"✅ Success! data.json updated with {len(gems)} gems and {len(intel['contracts'])} contracts.")

if __name__ == "__main__":
    orchestrate()