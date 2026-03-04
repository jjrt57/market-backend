import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import logging
from utils import timer_benchmark

logger = logging.getLogger(__name__)

@timer_benchmark
def get_sentiment(symbol):
    """Scrapes news and returns a (score, label) tuple."""
    clean_symbol = symbol.replace(".NS", "")
    url = f"https://www.google.com/search?q={clean_symbol}+stock+news&tbm=nws"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('div', attrs={'class': 'vv779c'}) or soup.find_all('div', attrs={'class': 'BNeawe'})
        
        if not headlines:
            return 0.0, "Neutral"
            
        total_score = 0
        count = 0
        for h in headlines[:5]:
            analysis = TextBlob(h.get_text())
            total_score += analysis.sentiment.polarity
            count += 1
            
        avg_score = round(total_score / count, 2)
        
        # --- NEW: Sentiment Classification Logic ---
        if avg_score >= 0.15:
            label = "High Sentiment"
        elif avg_score <= -0.05:
            label = "Low Sentiment"
        else:
            label = "Neutral"
        # -------------------------------------------

        logger.info(f"📰 {clean_symbol}: {avg_score} ({label})")
        return avg_score, label
        
    except Exception as e:
        logger.error(f"⚠️ Sentiment failed for {clean_symbol}: {e}")
        return 0.0, "Neutral"
