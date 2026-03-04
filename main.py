import valuation
import analyzer500
import macro
import insider_logic
import datetime
import notifier
import db_engine
import logging
import sentiment_engine
import os
from utils import timer_benchmark

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@timer_benchmark
def orchestrate():
    logger.info("🚀 MULTI-ENGINE SCRIPT STARTING...")
    
    old_symbols = db_engine.get_existing_symbols()
    gems = valuation.get_undervalued_gems()
    budget_gems = analyzer500.scan_high_potential_budget()
    whale_symbols = insider_logic.get_whale_buys()

    all_current_picks = gems + budget_gems
    new_discoveries = []
    
    for stock in all_current_picks:
        clean_symbol = stock['symbol'].replace(".NS", "")
        if clean_symbol in whale_symbols:
            stock['whale_alert'] = "🚨 MASSIVE BLOCK DEAL DETECTED TODAY"
        else:
            stock['whale_alert'] = "None"
        
        if stock['symbol'] not in old_symbols:
            logger.info(f"🧠 Analyzing sentiment: {clean_symbol}")
            score, label = sentiment_engine.get_sentiment(stock['symbol'])
            stock['sentiment_score'] = score
            stock['sentiment_label'] = label
            new_discoveries.append(stock)

    if len(new_discoveries) > 0:
        logger.info(f"🔔 Found {len(new_discoveries)} new stocks! Triggering alerts...")
        elite_picks = notifier.send_alert(new_discoveries) # Return elite_picks for summary
        db_engine.save_to_cloud(new_discoveries)
    else:
        logger.info("ℹ️ No new stocks found this run. Skipping alerts.")
        elite_picks = []

    # --- THE UI COMPONENT: GitHub Step Summary with Mermaid Chart ---
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(f"### 🚀 Market Run Summary ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})\n")
            f.write(f"- **Elite Alerts Sent:** {len(elite_picks) if elite_picks else 0}\n\n")
            
            # Mermaid Pie Chart
            f.write("### 📊 Institutional Accumulation by Sector\n")
            f.write("```mermaid\npie title Whale Activity\n")
            sector_counts = {}
            for s in new_discoveries:
                if s.get('whale_alert') != "None":
                    sec = s.get('sector', 'Misc')
                    sector_counts[sec] = sector_counts.get(sec, 0) + 1
            
            if not sector_counts:
                f.write('    "No Whale Activity" : 1\n')
            else:
                for sector, count in sector_counts.items():
                    f.write(f'    "{sector}" : {count}\n')
            f.write("```\n")

if __name__ == "__main__":
    orchestrate()
