import yfinance as yf  # <-- This is the missing link!
import valuation
import concurrent.futures

# 2026 Sentiment & Catalyst Keywords
CATALYSTS = [
    "l1 bidder", "lowest bidder", "letter of award", 
    "capacity expansion", "order book visibility", 
    "passenger vehicles", "two-wheelers", "pli scheme"
]

def analyze_single_stock(ticker):
    """Analyzes a single stock. Built for parallel processing."""
    try:
        # yf.Ticker is what goes out and fetches the data
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice', 1000)
        if price >= 500: return None 
            
        # --- HEALTH GUARDRAILS ---
        ebitda = info.get('ebitda', 0)
        depreciation = info.get('depreciation', 0)
        ebit = ebitda - depreciation if ebitda and depreciation else 0
        interest = info.get('interestExpense', 0)
        icr = (ebit / interest) if interest and interest > 0 else 10 
        
        payables = info.get('totalLiabilitiesNetMinorityInterest', 0)
        cash = info.get('totalCash', 1)
        cash_stress = (payables / cash) > 5 
        rev_growth = info.get('revenueGrowth', 0)
        summary = info.get('longBusinessSummary', "").lower()
        
        # --- NEW: INSTITUTIONAL BACKING (FII / DII / Govt) ---
        inst_hold = info.get('heldPercentInstitutions', 0)
        promoter_hold = info.get('heldPercentInsiders', 0)
        
        backing_tags = []
        if inst_hold and inst_hold > 0.15: # >15% held by FIIs/Govt
            backing_tags.append("🌍 STRONG FII/DII")
        if promoter_hold and promoter_hold > 0.50: # >50% held by founders
            backing_tags.append("👔 HIGH CONVICTION")

        # --- THE PRO FILTER ---
        if icr > 3.0 and rev_growth > 0.15 and not cash_stress:
            if any(word in summary for word in CATALYSTS):
                return {
                    "symbol": ticker.replace(".NS", ""),
                    "price": price,
                    "icr": round(icr, 2),
                    "growth": f"{round(rev_growth * 100)}%",
                    "institutional_backing": " | ".join(backing_tags) if backing_tags else "Retail Heavy",
                    "status": "🔥 PRO APPROVED: Strong Health + L1/Momentum"
                }
    except Exception as e:
        # Fails silently and moves to the next stock if Yahoo Finance glitches
        return None
    return None

def scan_high_potential_budget():
    print("⚡ Running 'Pro' Asynchronous Olectra Hunter with FII/DII tracking...")
    full_market = valuation.get_full_nse_list()
    potential_gems = []
    
    # MULTIPROCESSING: Scans 20 stocks simultaneously
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(analyze_single_stock, full_market[:300])
        
    for res in results:
        if res:
            potential_gems.append(res)
            
    return potential_gems