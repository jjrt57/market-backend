import yfinance as yf
# We can use nsetools to get all active NSE codes
from nsetools import Nse
nse = Nse()

def scan_entire_market():
    # 1. Automatically get all stock symbols from NSE
    all_stock_codes = nse.get_stock_codes() 
    symbols = [f"{code}.NS" for code in all_stock_codes.keys()]
    
    undervalued_gems = []
    
    # 2. Scan each stock (we'll limit this to avoid rate limits)
    # For now, let's scan the top 100
    for ticker in symbols[:100]:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Advanced Undervalued Logic
            pe = info.get('forwardPE', 100)
            sector_pe = info.get('sector', "Unknown")
            
            # Alert if P/E is historically low
            if pe < 15: 
                undervalued_gems.append({
                    "ticker": ticker,
                    "sector": sector_pe,
                    "price": info.get('currentPrice'),
                    "reason": "Low P/E Ratio"
                })
        except:
            continue
            
    return undervalued_gems