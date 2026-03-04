import yfinance as yf
import valuation
import concurrent.futures # Introduces Multiprocessing

# 2026 Sentiment & Catalyst Keywords (Including PV & 2W Sector Rotation)
CATALYSTS = [
    "l1 bidder", "lowest bidder", "letter of award", 
    "capacity expansion", "order book visibility", 
    "passenger vehicles", "two-wheelers", "pli scheme"
]

def analyze_single_stock(ticker):
    """Analyzes a single stock. Built for parallel processing."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice', 1000)
        # Fail fast if it's over budget
        if price >= 500: 
            return None 
            
        # --- HEALTH GUARDRAILS ---
        # 1. Interest Coverage Ratio (ICR) > 3.0
        ebitda = info.get('ebitda', 0)
        depreciation = info.get('depreciation', 0)
        ebit = ebitda - depreciation if ebitda and depreciation else 0
        interest = info.get('interestExpense', 0)
        
        icr = (ebit / interest) if interest and interest > 0 else 10 # Default pass if no debt
        
        # 2. Working Capital Stress Test (Payables vs Cash)
        payables = info.get('totalLiabilitiesNetMinorityInterest', 0)
        cash = info.get('totalCash', 1)
        cash_stress = (payables / cash) > 5 # Flags if payables are exploding 5x beyond cash
        
        rev_growth = info.get('revenueGrowth', 0)
        summary = info.get('longBusinessSummary', "").lower()
        
        # --- THE PRO FILTER ---
        if icr > 3.0 and rev_growth > 0.15 and not cash_stress:
            if any(word in summary for word in CATALYSTS):
                return {
                    "symbol": ticker.replace(".NS", ""),
                    "price": price,
                    "icr": round(icr, 2),
                    "growth": f"{round(rev_growth * 100)}%",
                    "status": "🔥 PRO APPROVED: Strong Health + L1/Momentum"
                }
    except Exception:
        return None
    return None

def scan_high_potential_budget():
    print("⚡ Running 'Pro' Asynchronous Olectra Hunter...")
    full_market = valuation.get_full_nse_list()
    potential_gems = []
    
    # MULTIPROCESSING: Scans 20 stocks simultaneously to beat the 5-minute GitHub limit
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Scanning top 300 stocks blazing fast
        results = executor.map(analyze_single_stock, full_market[:300])
        
    for res in results:
        if res:
            potential_gems.append(res)
            
    return potential_gems