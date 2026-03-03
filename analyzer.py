import json
import datetime
import feedparser # pip install feedparser
import yfinance as yf # pip install yfinance

def fetch_news():
    # Using Google News RSS for India/Business as a free source
    url = "https://news.google.com/rss/search?q=India+Economy+OR+NSE+OR+BSE&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    headlines = [entry.title for entry in feed.entries[:5]]
    return headlines

def analyze_event(headline):
    # Placeholder for your NLP/FinBERT logic. 
    # For now, we use a simple keyword matcher.
    if "Oil" in headline or "Iran" in headline:
        return {
            "impacted_sector": "Energy",
            "tickers": ["ONGC.NS", "OIL.NS"],
            "historical_insight": "Historically, major oil supply disruptions correlate with a 5-7% short-term gain in domestic upstream oil companies.",
            "historical_probability_up": 0.75
        }
    return None

def generate_api_data():
    headlines = fetch_news()
    insights = []
    
    for idx, headline in enumerate(headlines):
        analysis = analyze_event(headline)
        if analysis:
            insights.append({
                "id": f"evt_{idx}",
                "headline": headline,
                "analysis": analysis
            })
            
    api_response = {
        "meta": {
            "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
        },
        "insights": insights
    }
    
    # Save to the JSON file
    with open("data.json", "w") as f:
        json.dump(api_response, f, indent=2)
    print("data.json updated successfully.")

if __name__ == "__main__":
    generate_api_data()
