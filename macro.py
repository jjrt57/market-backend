import feedparser
import re

def get_latest_intelligence():
    # 2026 High-impact news feeds
    feeds = [
        "https://www.moneycontrol.com/rss/business.xml",
        "https://www.financialexpress.com/market/feed/"
    ]
    
    intel = {"contracts": [], "sector_alerts": []}
    
    # Advanced 2026 Sector Triggers
    categories = {
        "DEFENSE": ["defense", "ordnance", "shipbuilding", "missile", "aerospace"],
        "INFRA": ["highway", "bridge", "tunnel", "railway", "smart city", "nhai"],
        "ENERGY": ["solar", "green hydrogen", "nuclear", "crude", "grid"],
        "AUTO_TECH": ["ev", "semiconductor", "ai", "lithium", "battery"],
        "FINANCE": ["banking", "nbfc", "fintech", "repo rate", "fii"]
    }

    contract_keywords = ["awarded", "order win", "l1 bidder", "secures", "tender"]

    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:30]:
            title = entry.title.lower()
            
            # 1. Identify Government Contract Wins
            if any(k in title for k in contract_keywords):
                intel["contracts"].append({"title": entry.title, "url": entry.link})

            # 2. Identify Sector Shifts
            for sector, keys in categories.items():
                if any(k in title for k in keys):
                    intel["sector_alerts"].append({
                        "sector": sector,
                        "headline": entry.title,
                        "impact": "HIGH" if any(k in title for k in contract_keywords) else "MEDIUM"
                    })

    return intel