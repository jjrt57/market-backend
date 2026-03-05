import streamlit as st
import pandas as pd
import yfinance as yf
from supabase import create_client
import json
import urllib.parse
from streamlit_lightweight_charts import renderLightweightCharts

# --- 1. Page Configuration ---
st.set_page_config(page_title="Market Intelligence Screener", page_icon="🚀", layout="wide")

# --- 2. Database Connection ---
@st.cache_resource
def init_connection():
    try:
        creds_raw = st.secrets["SUPABASE_DATA"]
        creds = json.loads(creds_raw)
        return create_client(creds["SUPABASE_URL"], creds["SUPABASE_KEY"])
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

supabase = init_connection()

# --- 3. Data Logic (TradingView & Quant Algorithm) ---
@st.cache_data(ttl=600)
def get_tv_data(symbol, period, interval):
    ticker = yf.Ticker(f"{symbol}.NS")
    df = ticker.history(period=period, interval=interval)
    df = df.reset_index()
    
    # Simple Moving Average for trend confirmation
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    price_data, sma_data, volume_data = [], [], []
    for _, row in df.iterrows():
        t = row['Date'].timestamp() if 'Date' in row else row['Datetime'].timestamp()
        price_data.append({"time": t, "open": float(row['Open']), "high": float(row['High']), "low": float(row['Low']), "close": float(row['Close'])})
        if not pd.isna(row['SMA_20']):
            sma_data.append({"time": t, "value": float(row['SMA_20'])})
        volume_data.append({
            "time": t, "value": float(row['Volume']),
            "color": 'rgba(38, 166, 154, 0.3)' if row['Close'] >= row['Open'] else 'rgba(239, 83, 80, 0.3)'
        })
    return price_data, sma_data, volume_data, ticker.info, ticker.news

def manage_watchlist(symbol=None, action="get", note=""):
    if action == "get":
        res = supabase.table("user_watchlist").select("*").execute()
        return pd.DataFrame(res.data)
    elif action == "add":
        supabase.table("user_watchlist").upsert({"symbol": symbol, "evaluation_note": note}).execute()
        st.success(f"📌 Saved {symbol} to Watchlist!")
    elif action == "delete":
        supabase.table("user_watchlist").delete().eq("symbol", symbol).execute()
        st.rerun()

# --- 4. Sidebar: Persistent Conviction Watchlist ---
with st.sidebar:
    st.header("📌 My Watchlist")
    watch_df = manage_watchlist(action="get")
    if not watch_df.empty:
        for _, row in watch_df.iterrows():
            with st.expander(f"🔹 {row['symbol']}"):
                st.write(f"**Note:** {row['evaluation_note']}")
                if st.button(f"🗑️ Remove", key=f"del_{row['symbol']}"):
                    manage_watchlist(symbol=row['symbol'], action="delete")
    else:
        st.caption("No stocks saved yet.")

# --- 5. Main Dashboard ---
st.title("🚀 Market Intelligence Screener")

try:
    # Querying the High-Performance Materialized View
    res = supabase.table("elite_leaderboard_fast").select("*").execute()
    df_leader = pd.DataFrame(res.data)
except:
    df_leader = pd.DataFrame()

if not df_leader.empty:
    st.subheader("🏆 Elite Discoveries (Forensic-Filtered)")
    
    # Adding Risk Badges visually
    df_leader['display_symbol'] = df_leader.apply(
        lambda x: f"🚩 {x['symbol']}" if x['is_pledged'] or x['has_litigation'] else x['symbol'], axis=1
    )
    
    st.dataframe(df_leader[['display_symbol', 'price', 'power_score', 'sentiment_label', 'delivery_percentage', 'sector']], 
                 use_container_width=True, hide_index=True)
    
    selected_symbol = st.selectbox("🎯 Research Symbol:", df_leader['symbol'].tolist())
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    st.divider()

    if selected_symbol:
        # Timeframe Selector
        tf_choice = st.radio("🕒 Timeframe", ["1D", "1W", "1M", "1Y"], horizontal=True)
        tf_map = {"1D": ("1d", "1m"), "1W": ("5d", "15m"), "1M": ("1mo", "1d"), "1Y": ("1y", "1d")}
        period, interval = tf_map[tf_choice]

        price_data, sma_data, volume_data, info, news = get_tv_data(selected_symbol, period, interval)

        # Layout for Chart and Metadata
        col_chart, col_side = st.columns([2.5, 0.5])
        
        with col_chart:
            st.subheader(f"📊 {info.get('longName', selected_symbol)} Analysis")
            chartOptions = {
                "layout": {"background": {"type": "solid", "color": "#131722"}, "textColor": "#d1d4dc"},
                "grid": {"vertLines": {"color": "#363c4e"}, "horzLines": {"color": "#363c4e"}},
                "width": 1050, "height": 600
            }
            renderLightweightCharts(charts=[{
                "chart": chartOptions,
                "series": [
                    {"type": "Candlestick", "data": price_data, "options": {"upColor": "#26a69a", "downColor": "#ef5350"}},
                    {"type": "Line", "data": sma_data, "options": {"color": "#E91E63", "lineWidth": 2}},
                    {"type": "Histogram", "data": volume_data, "options": {"priceScaleId": "vol", "priceFormat": {"type": "volume"}}}
                ]
            }], key=f"tv_{selected_symbol}_{tf_choice}")

        with col_side:
            st.subheader("👤 Leadership")
            officers = info.get('companyOfficers', [])
            if officers:
                for off in officers[:6]:
                    name, role = off.get('name', 'Unknown'), off.get('title', 'Executive')
                    col_n, col_i = st.columns([0.8, 0.2])
                    with col_n: st.markdown(f"**{role}**: {name}")
                    with col_i:
                        with st.popover("ℹ️"):
                            pol_query = urllib.parse.quote(f'"{name}" (relative OR politician OR MLA OR MP OR minister)')
                            st.markdown(f"🔗 [LinkedIn](https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(name)})")
                            st.markdown(f"🔍 [Check Political Connections](https://www.google.com/search?q={pol_query})")
                    st.write("---")

            # Analyst Evaluation Module
            st.subheader("📝 Evaluation")
            eval_input = st.text_area("Thesis/Notes:", placeholder="Why save this stock?", key="eval_box")
            if st.button("💾 Save to Watchlist"):
                manage_watchlist(symbol=selected_symbol, action="add", note=eval_input)

        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
        st.divider()
        
        col_about, col_news = st.columns([1.2, 0.8])
        with col_about:
            st.subheader("📖 Business Overview")
            st.write(info.get('longBusinessSummary', "No summary available."))
        with col_news:
            st.subheader("📰 Market Sentiment")
            for item in news[:5]:
                st.markdown(f"**[{item.get('title')}]({item.get('link')})**")
                st.write("---")
else:
    st.info("Leaderboard is empty. Check your Hunter bot!")
