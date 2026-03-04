import pandas as pd
import requests
import io
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Get the logger inherited from main.py
logger = logging.getLogger(__name__)

def get_whale_buys():
    logger.info("🐋 Scanning NSE for Institutional Bulk/Block Deals...")
    url = "https://archives.nseindia.com/content/equities/bulk.csv"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    try:
        response = http.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = df.columns.str.strip()
        
        # Standardize column names
        if 'Quantity Traded' in df.columns:
            df.rename(columns={'Quantity Traded': 'Quantity'}, inplace=True)
        elif 'Qty' in df.columns:
            df.rename(columns={'Qty': 'Quantity'}, inplace=True)
            
        if 'Buy / Sell' in df.columns:
            df.rename(columns={'Buy / Sell': 'Buy/Sell'}, inplace=True)
        
        massive_buys = df[(df['Quantity'] > 500000) & (df['Buy/Sell'] == 'BUY')]
        symbols = massive_buys['Symbol'].unique().tolist()
        
        logger.info(f"✅ Whale scan successful. Found {len(symbols)} major deals.")
        return symbols

    except Exception as e:
        logger.error(f"❌ Whale scan failed: {e}")
        return []
