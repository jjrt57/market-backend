import streamlit as st
import pandas as pd
import yfinance as yf
from supabase import create_client
import json
import os

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Market Intelligence Screener",
    page_icon="🚀",
    layout="wide"
)

# --- 2. Database Connection ---
@st.cache_resource
def init_connection():
    """Connects to Supabase using your existing JSON credentials."""
    try:
        # Pulls from Streamlit Secrets (Cloud) or .streamlit/secrets.toml (Local)
        creds_raw = st.secrets["SUPABASE_DATA"]
        creds = json.loads(creds_raw)
        return create_client(creds["SUPABASE_URL"], creds["SUPABASE_KEY"])
    except Exception as e:
        st.error(f"❌ Connection Error: Ensure SUPABASE_DATA is set in secrets. {e}")
        return None

supabase = init_connection()

# --- 3. Data Logic ---
def get_leaderboard():
    """Fetches the fresh 3-day filtered list from your SQL View."""
    try:
        response = supabase.table("elite_leaderboard").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"⚠️ Error fetching leaderboard: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache company details for 1 hour
def get_company_details(symbol):
    """Fetches live deep-dive metadata from Yahoo Finance."""
    ticker = yf.Ticker(f"{symbol}.NS")
    return ticker.info, ticker.news[:5], ticker

# --- 4. Sidebar & Controls ---
st.sidebar.title("🛠️ Control Panel")
if st.sidebar.button("🔄 Refresh Leaderboard"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    "This dashboard shows stocks discovered by your Hunter bot over the last 3 days. "
    "Only stocks with a high Power Score appear here."
)

# --- 5. Main UI ---
st.title("🚀 Market Intelligence Screener")

df = get_leaderboard()

if not df.empty:
    # --- Top Section: The Discovery Feed ---
    st.subheader("🏆 Elite Discoveries (Last 3 Days)")
    
    # Logic to select a stock for the "Screener" deep-dive
    symbols = df['symbol'].unique().tolist()
    selected_symbol = st.selectbox("🎯 Select a symbol for deep-dive research:", symbols)
    
    # Display overview table with color formatting
    st.dataframe(
        df[['symbol', 'price', 'power_score', 'sentiment_label', 'whale_alert', 'sector']],
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()

    # --- Bottom Section: The "Screener" Research Hub ---
    if selected_symbol:
        with st.spinner(f"🔍 Fetching latest research for {selected_symbol}..."):
            info, news, ticker_obj = get_company_details(selected_symbol)
            
            # Layout Columns: Fundamentals on left, metrics on right
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.header(f"🏢 {info.get('longName', selected_symbol)}")
                st.caption(f"📍 {info.get('sector')} | {info.get('industry')} | [Official Website]({info.get('website')})")
                
                # Business Profile
                with st.expander("📖 View Company Business Summary", expanded=True):
                    st.write(info.get('longBusinessSummary', "Summary not available."))
                
                # Founder / Executive details
                st.subheader("👤 Leadership Team (Founders/Execs)")
                officers = info.get('companyOfficers', [])
                if officers:
                    # Create a clean table for leaders
                    off_df = pd.DataFrame(officers)[['name', 'title']].head(6)
                    st.table(off_df)
                else:
                    st.write("Specific leadership details not currently available.")

                # Technical Confirmation Chart
                st.subheader("📈 Price Action (Last 30 Days)")
                history
