import yfinance as yf
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
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice', 1000)
        if price >= 500: return None 
            
        # --- 1. HEALTH GUARDRAILS ---
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
        
        # --- 2. INSTITUTIONAL BACKING ---
        inst_hold = info.get('heldPercentInstitutions', 0)
        promoter_hold = info.get('heldPercentInsiders', 0)
        
        backing_tags = []
        if inst_hold and inst_hold > 0.15: 
            backing_tags.append("🌍 STRONG FII/DII")
        if promoter_hold and promoter_hold > 0.50: 
            backing_tags.append("👔 HIGH CONVICTION")

        # --- 3. THE VOLUME SHOCK INDICATOR ---
        current_volume = info.get('volume', 0)
        # Use 10-day average, fallback to regular average, default to 1 to avoid ZeroDivisionError
        avg_volume = info.get('averageVolume10days', info.get('averageVolume', 1))
        if avg_volume == 0 or avg_volume is None: 
            avg_volume = 1
            
        volume_ratio = current_volume / avg_volume
        
        vol_tag = "Normal"
        if volume_ratio > 3.0:
            vol_tag = f"🧨 MASSIVE VOLUME SHOCK ({round(volume_ratio)}x Avg)"
        elif volume_ratio > 1.5:
            vol_tag = f"📈 High Volume ({round(volume_ratio, 1)}x Avg)"

        # --- 4. THE MASTER PRO FILTER ---
        # Must pass financial health checks first!
        if icr > 3.0 and rev_growth > 0.15 and not cash_stress:
            # It gets approved IF it has a keyword catalyst OR if the volume is exploding
            if any(word in summary for word in CATALYSTS) or volume_ratio > 2.0:
                return {
                    "symbol": ticker.replace(".NS", ""),
                    "price": price,
                    "icr": round(icr, 2),
                    "growth": f"{round(rev_growth * 100)}%",
                    "volume_status": vol_tag,
                    "institutional_backing": " | ".join(backing_tags) if backing_tags else "Retail Heavy",
                    "status": "🔥 PRO APPROVED"
                }
    except Exception as e:
        return None
    return None

def scan_high_potential_budget():
    print("⚡ Running 'Pro' Hunter with FII/DII & Volume Shock tracking...")
    full_market = valuation.get_full_nse_list()
    potential_gems = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(analyze_single_stock, full_market[:300])
        
    for res in results:
        if res:
            potential_gems.append(res)
            
    return potential_gems