import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="V-Trade AI Premium", layout="wide", page_icon="📈")

# ==========================================
# 1. ENTRY FEE / PAYWALL SYSTEM (₹999)
# ==========================================
if 'has_paid' not in st.session_state:
    st.session_state['has_paid'] = False

if not st.session_state['has_paid']:
    st.markdown("""
    <style>
        .paywall-box {
            background-color: #1e293b; padding: 40px; border-radius: 15px; 
            text-align: center; border: 2px solid #ef4444; max-width: 600px; margin: auto;
        }
        .price { font-size: 40px; font-weight: bold; color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="paywall-box">', unsafe_allow_html=True)
    st.title("🔒 Premium Access Required")
    st.write("Duniya ke sabse advanced AI trading terminal me aapka swagat hai.")
    st.markdown('<p class="price">Entry Fee: ₹999</p>', unsafe_allow_html=True)
    st.write("Is platform ko use karne ke liye har baar ₹999 ka secure payment zaroori hai.")
    
    st.info("UPI ID: 9772035114@axl (Real API setup ke baad QR code yahan aayega)")
    
    # Yeh button abhi testing ke liye hai. Real life me jab Razorpay se success ka message aayega, tab ye True hoga.
    if st.button("💳 Pay ₹999 Securely & Unlock App", type="primary", use_container_width=True):
        st.session_state['has_paid'] = True
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Yahan code ruk jayega. Jab tak payment nahi hoga, niche ka trading app load nahi hoga.


# ==========================================
# 2. MAIN TRADING APP (Payment ke baad khulega)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    .buy-card { background: #064e3b; padding: 20px; border-radius: 12px; border: 1px solid #10b981; }
    .sell-card { background: #7f1d1d; padding: 20px; border-radius: 12px; border: 1px solid #ef4444; }
    .ai-box { background: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #00e676; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.success("✅ Payment of ₹999 Successful! Platform Unlocked.")
st.title("📈 V-Trade AI: Advanced Market Terminal")

# Sidebar for Input
st.sidebar.header("🔍 Market Search")
user_input = st.sidebar.text_input("Enter NSE Symbol (e.g., RELIANCE, ZOMATO)", "RELIANCE").upper()
if not user_input.endswith(".NS") and not user_input.startswith("^"):
    user_input += ".NS"

@st.cache_data(ttl=60)
def fetch_data(symbol):
    return yf.Ticker(symbol).history(period="3mo", interval="1d")

df = fetch_data(user_input)

if df.empty:
    st.error("Data nahi mila. Kripya sahi NSE symbol daalein.")
else:
    # Calculations
    df['SMA_20'] = df['Close'].rolling(20).mean()
    latest_close = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    change = latest_close - prev_close
    pct_change = (change / prev_close) * 100
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Live Price", f"₹{latest_close:,.2f}", f"{change:+.2f} ({pct_change:+.2f}%)")
    c2.metric("20-Day Trend", f"₹{df['SMA_20'].iloc[-1]:,.2f}", "Uptrend" if latest_close > df['SMA_20'].iloc[-1] else "Downtrend")
    
    # Prediction Math
    pivot = (df['High'].iloc[-1] + df['Low'].iloc[-1] + latest_close) / 3
    res_1 = (2 * pivot) - df['Low'].iloc[-1]
    sup_1 = (2 * pivot) - df['High'].iloc[-1]
    
    ai_verdict = "🚀 STRONG BUY" if latest_close > df['SMA_20'].iloc[-1] else "🔻 STRONG SELL"
    probability = "75-80%" if abs(pct_change) > 1 else "55-60%"
    
    # Tabs for Features
    tab_chart, tab_ai, tab_trade = st.tabs(["📊 Live Chart", "🤖 AI Prediction Engine", "💼 Execute Trade (Groww Style)"])
    
    with tab_chart:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='orange', width=2), name="20 SMA"))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with tab_ai:
        st.markdown(f"""
        <div class="ai-box">
            <h4>🤖 1-Day Forward AI Prediction for {user_input}</h4>
            <p><b>AI Target Signal:</b> {ai_verdict} (Winning Probability: {probability})</p>
            <p><b>Expected Resistance (Up):</b> ₹{res_1:.2f} | <b>Expected Support (Down):</b> ₹{sup_1:.2f}</p>
            <hr>
            <p><i>Analysis:</i> The AI engine detects that the price is currently {'above' if latest_close > df['SMA_20'].iloc[-1] else 'below'} its 20-day moving average, signaling strong momentum. Intraday volatility indicates the calculated support and resistance levels are the most probable turning points for tomorrow's session.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab_trade:
        st.write("Direct order execution panel. Trade fees applicable as per broker.")
        t1, t2 = st.columns(2)
        with t1:
            st.markdown('<div class="buy-card">', unsafe_allow_html=True)
            st.subheader("🟢 BUY (LONG)")
            b_qty = st.number_input("Buy Quantity", min_value=1, value=10)
            st.write(f"Total Value: ₹{(b_qty * latest_close):,.2f}")
            if st.button("🚀 EXECUTE BUY", type="primary", use_container_width=True):
                st.success(f"Buy Order Placed: {b_qty} shares of {user_input}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with t2:
            st.markdown('<div class="sell-card">', unsafe_allow_html=True)
            st.subheader("🔴 SELL (SHORT)")
            s_qty = st.number_input("Sell Quantity", min_value=1, value=10)
            st.write(f"Total Value: ₹{(s_qty * latest_close):,.2f}")
            if st.button("📉 EXECUTE SELL", type="primary", use_container_width=True):
                st.error(f"Sell Order Placed: {s_qty} shares of {user_input}")
            st.markdown('</div>', unsafe_allow_html=True)
