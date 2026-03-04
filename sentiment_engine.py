import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import logging
from utils import timer_benchmark

@timer_benchmark
def get_sentiment(symbol):

logger = logging.getLogger(__name__)

def get_sentiment(symbol):
    """Scrapes news headlines and returns a sentiment score between -1 and 1."""
    # Remove .NS for cleaner news searches
    clean_symbol = symbol.replace(".NS", "")
    url = f"https://www.google.com/search?q={clean_symbol}+stock+news&tbm=nws"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all headline containers (Google News often uses 'div' with specific classes)
        headlines = soup.find_all('div', attrs={'class': 'vv779c'}) or soup.find_all('div', attrs={'class': 'BNeawe'})
        
        if not headlines:
            return 0.0 # Neutral if no news found
            
        total_score = 0
        count = 0
        
        for h in headlines[:5]: # Analyze top 5 news items
            text = h.get_text()
            analysis = TextBlob(text)
            total_score += analysis.sentiment.polarity
            count += 1
            
        avg_score = round(total_score / count, 2)
        logger.info(f"📰 Sentiment for {clean_symbol}: {avg_score}")
        return avg_score
        
    except Exception as e:
        logger.error(f"⚠️ Sentiment check failed for {clean_symbol}: {e}")
        return 0.0
