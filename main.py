import valuation
import analyzer500
import macro
import insider_logic
import datetime
import notifier
import db_engine
import logging
import sentiment_engine  # NEW IMPORT

# --- PRO LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
        
        # Only perform sentiment analysis on NEW stocks to save time and API calls
        if stock['symbol'] not in old_symbols:
            logger.info(f"🧠 Analyzing sentiment for new discovery: {clean_symbol}")
            stock['sentiment_score'] = sentiment_engine.get_sentiment(stock['symbol'])
            new_discoveries.append(stock)

    # --- 4. Trigger Alerts and Save ---
    if len(new_discoveries) > 0:
        logger.info(f"🔔 Found {len(new_discoveries)} new stocks! Triggering alerts...")
        notifier.send_alert(new_discoveries)
        db_engine.save_to_cloud(new_discoveries)
    else:
        logger.info("ℹ️ No new stocks found this run. Skipping alerts.")

if __name__ == "__main__":
    orchestrate()
