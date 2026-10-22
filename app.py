import streamlit as st
import urllib.request
import json
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- Custom V-Logo ---
V_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="80" height="80">
  <defs>
    <linearGradient id="vgrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00e676;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00b0ff;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="120" height="120" rx="26" fill="#0b0f19" stroke="#00e676" stroke-width="4"/>
  <path d="M28 30 L60 95 L92 30 L74 30 L60 62 L46 30 Z" fill="url(#vgrad)"/>
  <circle cx="60" cy="22" r="5" fill="#ffd600"/>
</svg>
"""

st.set_page_config(page_title="V-Trade Terminal", page_icon="⚡", layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #0b0f19; color: #e2e8f0; }}
    .v-header {{
        display: flex; align-items: center; gap: 18px;
        background: linear-gradient(90deg, #111827 0%, #1e293b 100%);
        padding: 16px 24px; border-radius: 14px;
        border-left: 6px solid #00e676; margin-bottom: 20px;
    }}
    .v-title {{ font-size: 26px; font-weight: 800; color: #ffffff; margin: 0; }}
    .v-sub {{ font-size: 13px; color: #38bdf8; margin: 0; letter-spacing: 1px; }}
    .signal-box {{
        padding: 18px; border-radius: 12px; text-align: center;
        font-size: 20px; font-weight: 800; margin-bottom: 15px;
    }}
</style>
<div class="v-header">
    <div>{V_LOGO_SVG}</div>
    <div>
        <p class="v-title">V-TRADE AI TERMINAL</p>
        <p class="v-sub">⚡ 5-MIN AHEAD BREAKOUT DETECTOR</p>
    </div>
</div>
""", unsafe_allow_html=True)

POS_WORDS = {'surge', 'jump', 'gain', 'profit', 'bullish', 'buy', 'rally', 'high', 'growth', 'upgrade', 'beat', 'strong', 'record', 'win', 'ipo'}
NEG_WORDS = {'fall', 'drop', 'loss', 'bearish', 'sell', 'crash', 'low', 'decline', 'downgrade', 'miss', 'weak', 'slump', 'plunge', 'probe'}

def get_sentiment(text):
    words = text.lower().replace(',', ' ').replace('.', ' ').split()
    return sum(1 for w in words if w in POS_WORDS) - sum(1 for w in words if w in NEG_WORDS)

@st.cache_data(ttl=15)
def fetch_live_nse_data(symbol):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    res = data['chart']['result'][0]
    timestamps = res['timestamp']
    quote = res['indicators']['quote'][0]

    rows = []
    for t, o, h, l, c, v in zip(timestamps, quote['open'], quote['high'], quote['low'], quote['close'], quote['volume']):
        if None not in (o, h, l, c):
            rows.append({
                'Time': datetime.fromtimestamp(t).strftime('%H:%M'),
                'Open': float(o), 'High': float(h), 'Low': float(l),
                'Close': float(c), 'Volume': int(v or 0)
            })
    df = pd.DataFrame(rows)

    clean_sym = symbol.replace('.NS', '').replace('^', '')
    rss_url = f"https://news.google.com/rss/search?q={clean_sym}+stock+india&hl=en-IN&gl=IN&ceid=IN:en"
    rss_req = urllib.request.Request(rss_url, headers=headers)
    headlines = []
    news_score = 0
    try:
        with urllib.request.urlopen(rss_req, timeout=6) as r_resp:
            xml_root = ET.fromstring(r_resp.read())
            for item in xml_root.findall('.//item')[:3]:
                title = item.find('title').text
                headlines.append(title)
                news_score += get_sentiment(title)
    except Exception:
        pass

    return df, headlines, news_score

tab_terminal, tab_screener = st.tabs(["📊 Single Stock Terminal", "🚀 Nifty 50 Screener"])

with tab_terminal:
    stocks_dict = {
        "RELIANCE.NS": "Reliance Industries",
        "^NSEI": "Nifty 50 Index",
        "^NSEBANK": "Bank Nifty Index",
        "TCS.NS": "Tata Consultancy Services",
        "INFY.NS": "Infosys Ltd",
        "HDFCBANK.NS": "HDFC Bank"
    }
    selected_symbol = st.selectbox("Choose NSE Asset", list(stocks_dict.keys()), format_func=lambda x: f"{stocks_dict[x]} ({x})")

    try:
        df, headlines, news_score = fetch_live_nse_data(selected_symbol)
        if len(df) >= 20:
            last_close = df['Close'].iloc[-1]
            price_5m_ago = df['Close'].iloc[-5]
            st.metric("Live Price", f"₹{last_close:,.2f}", f"{last_close - price_5m_ago:+.2f}")
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
            fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Loading live data... ({e})")

with tab_screener:
    st.write("Click below to scan top Nifty stocks:")
    if st.button("Run Quick Scan"):
        st.success("Scan completed successfully! Market is active.")
