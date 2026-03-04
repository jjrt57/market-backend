import valuation
import analyzer500
import macro
import insider_logic
import datetime
import notifier
import db_engine
import logging
import sentiment_engine
import os # NEW IMPORT REQUIRED
from utils import timer_benchmark

# --- PRO LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@timer_benchmark
def orchestrate():
    logger.info("🚀 MULTI-ENGINE SCRIPT STARTING...")
    
    # --- 1. Load Cloud Memory ---
    old_symbols = db_engine.get_existing_symbols()

    # --- 2. Run Engines ---
    logger.info("🔎 Calling standard valuation engine...")
    gems = valuation.get_undervalued_gems()

    logger.info("🔋 Searching for high-potential 'Olectra-style' budget picks...")
    budget_gems = analyzer500.scan_high_potential_budget()

    whale_symbols = insider_logic.get_whale_buys()

    all_current_picks = gems + budget_gems
    
    # --- 3. Check for NEW Discoveries and Analyze Sentiment ---
    new_discoveries = []
    
    for stock in all_current_picks:
        clean_symbol = stock['symbol'].replace(".NS", "")
        
        # Apply Whale Tags to all current picks
        if clean_symbol in whale_symbols:
            stock['whale_alert'] = "🚨 MASSIVE BLOCK DEAL DETECTED TODAY"
        else:
            stock['whale_alert'] = "None"
        
        # Only perform sentiment analysis on NEW stocks
        if stock['symbol'] not in old_symbols:
            logger.info(f"🧠 Analyzing sentiment for new discovery: {clean_symbol}")
            score, label = sentiment_engine.get_sentiment(stock['symbol'])
            
            stock['sentiment_score'] = score
            stock['sentiment_label'] = label
            new_discoveries.append(stock)

    # --- 4. Trigger Alerts and Save ---
    if len(new_discoveries) > 0:
        logger.info(f"🔔 Found {len(new_discoveries)} new stocks! Triggering alerts...")
        # Note: notifier.send_alert now returns elite_picks if you used the last version
        elite_picks = notifier.send_alert(new_discoveries) 
        db_engine.save_to_cloud(new_discoveries)
    else:
        logger.info("ℹ️ No new stocks found this run. Skipping alerts.")
        elite_picks = []

    # --- 5. GitHub Action Summary (Now correctly indented inside the function) ---
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(f"### 🚀 Market Run Summary ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})\n")
            f.write(f"- **Total Discoveries Scanned:** {len(all_current_picks)}\n")
            f.write(f"- **New Stocks Saved to Cloud:** {len(new_discoveries)}\n")
            f.write(f"- **Elite Alerts Sent:** {len(elite_picks) if elite_picks else 0}\n\n")
            f.write("| Symbol | Price | Sentiment | Whale Alert |\n")
            f.write("|--------|-------|-----------|-------------|\n")
            for s in new_discoveries:
                f.write(f"| {s['symbol']} | {s['price']} | {s.get('sentiment_label')} | {s.get('whale_alert')} |\n")

if __name__ == "__main__":
    orchestrate()
