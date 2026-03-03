# 1. These imports are the most important part!
import valuation  # This looks for valuation.py
import macro      # This looks for macro.py
import json
import datetime

print("🚀 SCRIPT STARTING...")

def orchestrate():
    print(f"⏰ Execution Time: {datetime.datetime.now()}")
    
    # 2. Now these will work because they are imported above
    print("🔎 Calling valuation engine...")
    gems = valuation.get_undervalued_gems()
    print(f"✅ Found {len(gems)} gems.")

    print("🌎 Calling macro intelligence...")
    intel = macro.get_latest_intelligence()
    
    # 3. Consolidate and Save
    output = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ai_picks": gems,
        "market_intelligence": intel
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print("💾 data.json updated successfully.")

# This tells Python to actually run the orchestrate function
if __name__ == "__main__":
    orchestrate()