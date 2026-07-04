import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="VIXRange Pro",
    layout="wide",
    page_icon="📊"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050814, #0b1020, #111827);
    color: white;
}

.main-title {
    font-size: 58px;
    font-weight: 800;
    color: white;
}

.sub-title {
    color: #94a3b8;
    font-size: 18px;
}

.metric-card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0px 10px 25px rgba(0,0,0,0.35);
}

.range-card {
    padding: 28px;
    border-radius: 20px;
    text-align: center;
    color: white;
    font-weight: 700;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.35);
}

.sd1 {
    background: linear-gradient(135deg,#10b981,#059669);
}
.sd2 {
    background: linear-gradient(135deg,#3b82f6,#2563eb);
}
.sd3 {
    background: linear-gradient(135deg,#f59e0b,#d97706);
}

.analytics-box {
    background: rgba(255,255,255,0.04);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
indices = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCAP NIFTY": "^NSEMDCP50",
    "SENSEX": "^BSESN"
}

VIX_SYMBOL = "^INDIAVIX"

# ---------------- HELPERS ----------------
def get_close(symbol):
    data = yf.download(symbol, period="5d", progress=False)
    close_series = data["Close"]

    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    return float(close_series.dropna().iloc[-1])

def next_trading_day():
    today = datetime.today()
    next_day = today + timedelta(days=1)

    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)

    return next_day.strftime("%A, %d %B %Y")

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">📊 VIXRange Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Volatility Intelligence Dashboard</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈 Price Bands", "📉 VIX Analytics"])

# =====================================================
# TAB 1
# =====================================================
with tab1:

    st.markdown("## Probabilistic Price Bands")

    selected_index = st.selectbox(
        "Select Index",
        list(indices.keys())
    )

    spot = get_close(indices[selected_index])
    vix = get_close(VIX_SYMBOL)

    move = spot * (vix / 100) / np.sqrt(252)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h4>Index Level</h4>
        <h1>{spot:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <h4>India VIX</h4>
        <h1>{vix:.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"### Expected Range for {next_trading_day()}")

    c1, c2, c3 = st.columns(3)

    ranges = [
        ("1 SD (~68%)", spot-move, spot+move, "sd1"),
        ("2 SD (~95%)", spot-2*move, spot+2*move, "sd2"),
        ("3 SD (~99.7%)", spot-3*move, spot+3*move, "sd3")
    ]

    for col, (label, low, high, style) in zip([c1,c2,c3], ranges):
        with col:
            st.markdown(f"""
            <div class="range-card {style}">
            <h3>{label}</h3>
            <h2>{low:,.2f}</h2>
            <p>to</p>
            <h2>{high:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# TAB 2
# =====================================================
with tab2:

    st.markdown("## VIX Analytics Dashboard")

    vix_hist = yf.download(VIX_SYMBOL, period="6mo", progress=False)
    close = vix_hist["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:,0]

    current_vix = float(close.iloc[-1])
    avg_vix = float(close.mean())

    percentile = (close.rank(pct=True).iloc[-1])*100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="analytics-box">
        <h4>Current VIX</h4>
        <h1>{current_vix:.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="analytics-box">
        <h4>6-Month Average</h4>
        <h1>{avg_vix:.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="analytics-box">
        <h4>Percentile</h4>
        <h1>{percentile:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)

    # Chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=close.index,
        y=close.values,
        mode='lines',
        line=dict(width=3)
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        title="India VIX Trend (6 Months)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Interpretation
    if current_vix < avg_vix:
        regime = "🟢 Calm Volatility Regime"
        insight = "Market expects lower near-term uncertainty."
    else:
        regime = "🔴 Elevated Volatility Regime"
        insight = "Market expects heightened uncertainty."

    st.markdown(f"""
    <div class="analytics-box">
    <h3>{regime}</h3>
    <p>{insight}</p>
    </div>
    """, unsafe_allow_html=True)