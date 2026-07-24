import streamlit as pd_st
import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from bot import RealTimeTradingBot
from indicators import process_all_indicators

# Page Configuration - Clean & Modern Layout
st.set_page_config(
    page_title="Avenix Smart Trading Suite",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium iOS-like minimalist styling CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
    
    html, body, [data-testid="stSidebar"] {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    .stMarkdown, .stButton, .stText, h1, h2, h3, h4, h5, h6 {
        direction: rtl !important;
        text-align: right !important;
    }
    /* Clean Cards */
    .ios-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #2e3e4f;
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #10b981;
        margin-top: 4px;
    }
    .metric-title {
        font-size: 13px;
        color: #94a3b8;
    }
    /* Tab Styling */
    .stTabs [data-basetab="tab"] {
        font-size: 16px;
        font-weight: 500;
        height: 50px;
        padding: 0 20px;
    }
    /* Brochure card style */
    .brochure-card {
        background-color: #0f172a;
        border-right: 5px solid #3b82f6;
        border-radius: 10px;
        padding: 16px;
        margin-top: 10px;
        line-height: 1.7;
        font-size: 13px;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions to load data
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config_data):
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=2)

def load_portfolio():
    if os.path.exists("portfolio.json"):
        with open("portfolio.json", "r") as f:
            return json.load(f)
    return {"balance": 10000.0, "active_trades": [], "completed_trades": []}

def save_portfolio(portfolio):
    with open("portfolio.json", "w") as f:
        json.dump(portfolio, f, indent=2)

def load_signals():
    if os.path.exists("signal_room.json"):
        with open("signal_room.json", "r") as f:
            return json.load(f)
    return []

config = load_config()
portfolio = load_portfolio()
signals = load_signals()

# Clean Minimalist Header (Brand Avenix)
st.markdown("<h1 style='text-align: center; color: #3b82f6; font-size: 32px; font-weight: 700; margin-bottom: 5px;'>🦅 AVENIX</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; margin-bottom: 25px;'>موتور هوشمند فارکس، فلزات گرانبها و ارزهای دیجیتال با ۳ حد سود و حد ضرر قفل‌شونده</p>", unsafe_allow_html=True)

# Main Application organized in clean Top Tabs (Perfect for Mobile UX)
tab_chart, tab_signals, tab_portfolio, tab_settings = st.tabs([
    "📊 چارت زنده", 
    "📢 اتاق سیگنال (بروشور هوشمند)", 
    "💼 کیف پول و معاملات", 
    "⚙️ تنظیمات سیستم"
])

# Fetch and cache historical candle data
@st.cache_data(ttl=10)
def get_chart_data(symbol, timeframe):
    bot_helper = RealTimeTradingBot()
    df = bot_helper.fetch_historical_ohlcv(symbol, timeframe, limit=100)
    df = process_all_indicators(df, config)
    return df

# ----------------- TAB 1: LIVE CHART (📊 چارت زنده) -----------------
with tab_chart:
    # Setup clean horizontal selectors
    sel_col1, sel_col2, sel_col3 = st.columns([2, 2, 3])
    with sel_col1:
        selected_symbol = st.selectbox("انتخاب نماد معاملاتی (فارکس/طلا/نفت/کریپتو)", config.get("symbols", ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "BRENT/USD", "SOL/USDT"]), index=0, key="chart_sym")
    with sel_col2:
        selected_timeframe = st.selectbox("تایم فریم", ["1m", "5m", "15m", "1h", "4h", "1d"], index=2, key="chart_tf")
    with sel_col3:
        run_simulation = st.checkbox("🔄 فعال‌سازی نوسان زنده و شکل‌گیری ثانیه‌ای کندل‌ها", value=True)

    # Clean expandable section for indicators toggle (Preventing clutter!)
    with st.expander("🛠️ فیلتر و شخصی‌سازی اندیکاتورهای چارت"):
        show_emas = st.checkbox("نمایش میانگین‌های متحرک نمایی (EMA 20, 50, 200)", value=True)
        show_ichimoku = st.checkbox("نمایش خطوط و ابرهای ایچیموکو (Ichimoku)", value=True)
        show_rsi = st.checkbox("نمایش اسیلاتور RSI در کادر پایینی", value=True)

    # Initialize or fetch cached data
    df = get_chart_data(selected_symbol, selected_timeframe)

    # REAL-TIME CANDLE ACCUMULATOR & SHAPER (True Live Charting)
    # To simulate real-time candle formation, we save state
    state_key_df = f"df_{selected_symbol}_{selected_timeframe}"
    state_key_last_time = f"last_time_{selected_symbol}_{selected_timeframe}"
    
    if state_key_df not in st.session_state:
        st.session_state[state_key_df] = df.copy()
        st.session_state[state_key_last_time] = time.time()

    active_df = st.session_state[state_key_df]
    last_time = st.session_state[state_key_last_time]
    
    if run_simulation:
        # 1. Flucluate current close price to form the tick
        last_row_idx = active_df.index[-1]
        current_close = active_df.loc[last_row_idx, 'close']
        
        # Calculate dynamic fluctuations depending on asset scale
        if "XAU" in selected_symbol:
            tick_size = np.random.normal(0, 0.4) # Gold ticks ~$0.40
        elif "EUR" in selected_symbol or "GBP" in selected_symbol:
            tick_size = np.random.normal(0, 0.0001) # Forex ticks ~1 pip
        elif "JPY" in selected_symbol:
            tick_size = np.random.normal(0, 0.02)
        elif "BRENT" in selected_symbol:
            tick_size = np.random.normal(0, 0.05)
        else: # Solana or Bitcoin
            tick_size = np.random.normal(0, 0.08)
            
        new_close = current_close + tick_size
        
        # Update current candle metrics live!
        active_df.loc[last_row_idx, 'close'] = new_close
        if new_close > active_df.loc[last_row_idx, 'high']:
            active_df.loc[last_row_idx, 'high'] = new_close
        if new_close < active_df.loc[last_row_idx, 'low']:
            active_df.loc[last_row_idx, 'low'] = new_close
            
        # 2. Candle completion logic (Create a new candle every 15 seconds for realistic demo!)
        time_elapsed = time.time() - last_time
        if time_elapsed >= 15: # Every 15 seconds, append a new candle
            st.session_state[state_key_last_time] = time.time()
            
            # Create a new row starting from the last close
            new_timestamp = active_df.loc[last_row_idx, 'timestamp'] + pd.Timedelta(minutes=15)
            new_row = {
                'timestamp': new_timestamp,
                'open': new_close,
                'high': new_close,
                'low': new_close,
                'close': new_close,
                'volume': np.random.uniform(50, 500)
            }
            
            # Append new row
            active_df = pd.concat([active_df, pd.DataFrame([new_row])], ignore_index=True)
            # Re-apply indicators to the newly formed data sequence
            active_df = process_all_indicators(active_df, config)
            # Cap at 100 candles to prevent memory bloat
            if len(active_df) > 100:
                active_df = active_df.iloc[-100:].reset_index(drop=True)
                
            st.session_state[state_key_df] = active_df

    # Render Plotly Chart
    if show_rsi:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_width=[0.24, 0.76])
    else:
        fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Candlestick(
        x=active_df['timestamp'], open=active_df['open'], high=active_df['high'], low=active_df['low'], close=active_df['close'], name="قیمت"
    ), row=1, col=1)

    if show_emas:
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df[f"EMA_{config.get('ma_short', 20)}"], line=dict(color='#3b82f6', width=1.3), name=f"EMA {config.get('ma_short', 20)}"), row=1, col=1)
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df[f"EMA_{config.get('ma_medium', 50)}"], line=dict(color='#eab308', width=1.3), name=f"EMA {config.get('ma_medium', 50)}"), row=1, col=1)
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df[f"EMA_{config.get('ma_long', 200)}"], line=dict(color='#ef4444', width=1.8), name=f"EMA {config.get('ma_long', 200)}"), row=1, col=1)

    if show_ichimoku:
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df['tenkan_sen'], line=dict(color='#a855f7', width=1.1), name="Tenkan (9)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df['kijun_sen'], line=dict(color='#14b8a6', width=1.1), name="Kijun (26)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df['senkou_span_a'], line=dict(color='rgba(16, 185, 129, 0.15)'), name="Span A", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df['senkou_span_b'], line=dict(color='rgba(239, 68, 68, 0.15)'), fill='tonexty', fillcolor='rgba(148, 163, 184, 0.08)', name="Span B", showlegend=False), row=1, col=1)

    if show_rsi:
        fig.add_trace(go.Scatter(x=active_df['timestamp'], y=active_df['RSI'], line=dict(color='#f43f5e', width=1.8), name="RSI"), row=2, col=1)
        fig.add_hline(y=config.get("rsi_overbought", 70), line_dash="dash", line_color="#ef4444", row=2, col=1)
        fig.add_hline(y=config.get("rsi_oversold", 30), line_dash="dash", line_color="#10b981", row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(148, 163, 184, 0.3)", row=2, col=1)

    fig.update_layout(
        height=480, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False,
        plot_bgcolor='#0f172a', paper_bgcolor='#0f172a', font_color='#f1f5f9',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------- TAB 2: SIGNAL ROOM (📢 اتاق سیگنال) -----------------
with tab_signals:
    st.markdown("### 📢 آرشیو بروشورهای تحلیلی اتاق سیگنال آونیکس")
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>سیگنال‌های صادر شده با گزارش تفصیلی و گرافیکی علت ورود مغز ربات</p>", unsafe_allow_html=True)
    signals_list = load_signals()
    
    if len(signals_list) == 0:
        st.info("هیچ سیگنالی صادر نشده است.")
    else:
        for sig in reversed(signals_list):
            side_badge = "🟢 BUY (خرید صعودی)" if sig["side"] == "BUY" else "🔴 SELL (فروش نزولی)"
            color_theme = "#10b981" if sig["side"] == "BUY" else "#ef4444"
            status_fa = "🟡 در جریان" if sig["status"] == "PENDING" else f"🔒 بسته شده ({sig['status']})"
            
            st.markdown(f"""
            <div class='ios-card' style='border-right: 5px solid {color_theme};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 18px; font-weight: 700; color: #f8fafc;'>{sig['symbol']}</span>
                    <span style='color: {color_theme}; font-weight: 700; font-size: 15px;'>{side_badge}</span>
                    <span style='font-size: 12px; color: #94a3b8; background-color: #334155; padding: 4px 8px; border-radius: 20px;'>{status_fa}</span>
                </div>
                <div style='margin-top: 15px; font-size: 13px; color: #cbd5e1; line-height: 1.6;'>
                    💵 قیمت ورود: <b>{sig['entry_price']}</b> | 🛡️ حد ضرر اولیه: <b style='color: #f87171;'>{sig['sl']}</b><br>
                    🎯 اهداف سود: اول (TP1): <b>{sig.get('tp1','N/A')}</b> | دوم (TP2): <b>{sig.get('tp2','N/A')}</b> | سوم (TP3): <b>{sig.get('tp3','N/A')}</b>
                </div>
                <div class='brochure-card'>
                    {sig['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 3: WALLET & PORTFOLIO (💼 معاملات و پورتفوی) -----------------
with tab_portfolio:
    st.markdown("### 💰 وضعیت موجودی و کیف پول")
    
    col_bal1, col_bal2, col_bal3 = st.columns(3)
    with col_bal1:
        st.markdown(f"""
        <div class='ios-card'>
            <div class='metric-title'>موجودی حساب آزمایشی (Balance)</div>
            <div class='metric-value'>${portfolio.get("balance", 10000.0):,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_bal2:
        active_trades_count = len(portfolio.get("active_trades", []))
        st.markdown(f"""
        <div class='ios-card'>
            <div class='metric-title'>معاملات فعال بازار</div>
            <div class='metric-value' style='color: #3b82f6;'>{active_trades_count} پوزیشن باز</div>
        </div>
        """, unsafe_allow_html=True)
    with col_bal3:
        broker_type_fa = "شبیه‌ساز (دمو)" if config.get("broker_type") == "paper" else "حساب واقعی بروکر"
        st.markdown(f"""
        <div class='ios-card'>
            <div class='metric-title'>بستر معاملاتی متصل</div>
            <div class='metric-value' style='color: #f59e0b; font-size: 20px;'>{broker_type_fa}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 💼 موقعیت‌های معاملاتی")
    sub_tab_active, sub_tab_closed = st.tabs(["🔒 پوزیشن‌های فعال", "✅ تاریخچه معاملات بسته شده"])
    
    with sub_tab_active:
        active_trades = portfolio.get("active_trades", [])
        if len(active_trades) == 0:
            st.info("در حال حاضر هیچ موقعیت فعالی باز نیست.")
        else:
            for trade in active_trades:
                color_t = "#10b981" if trade["side"] == "BUY" else "#ef4444"
                st.markdown(f"""
                <div class='ios-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b>{trade['symbol']} ({trade['side']})</b>
                        <span style='color: {color_t}; font-weight: 700;'>سود زنده: ${trade['pnl']} ({trade['pnl_percent']}%)</span>
                    </div>
                    <div style='margin-top: 10px; font-size: 13px; color: #cbd5e1;'>
                        ورود: {trade['entry_price']} | قیمت زنده: {trade['current_price']}<br>
                        حد ضرر فعلی: <b>{trade['sl']}</b> | حد سود نهایی (TP3): {trade['tp3']}<br>
                        وضعیت حد ضرر شناور: پله <b>{trade.get('highest_tp_reached', 0)}</b> از ۳
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with sub_tab_closed:
        completed_trades = portfolio.get("completed_trades", [])
        if len(completed_trades) == 0:
            st.info("تاریخچه معاملات بسته شده خالی است.")
        else:
            for trade in reversed(completed_trades):
                color_pnl = "#10b981" if trade["pnl"] >= 0 else "#ef4444"
                sign = "+" if trade["pnl"] >= 0 else ""
                st.markdown(f"""
                <div class='ios-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b>{trade['symbol']} | {trade['side']}</b>
                        <span style='color: {color_pnl}; font-weight: 700;'>نتیجه: {sign}${trade['pnl']} ({trade['pnl_percent']}%)</span>
                    </div>
                    <div style='margin-top: 8px; font-size: 12px; color: #94a3b8;'>
                        خروج با: <b>{trade['close_reason']}</b> در قیمت {trade['close_price']}<br>
                        زمان خروج: {trade['close_time']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ----------------- TAB 4: SYSTEM SETTINGS (⚙️ تنظیمات سیستم) -----------------
with tab_settings:
    st.markdown("### ⚙️ پیکربندی سیستم معاملاتی آونیکس")
    
    # 1. Sensitivity and Broker Connection
    set_col1, set_col2 = st.columns(2)
    with set_col1:
        current_sensitivity = config.get("sensitivity", "medium").lower()
        sens_idx = 1 if current_sensitivity == "medium" else (0 if current_sensitivity == "low" else 2)
        sensitivity_opt = st.selectbox(
            "درجه حساسیت و تاییده‌های ورود ربات",
            ["کم (بسیار ایمن و محافظه‌کارانه)", "متوسط (متعادل و منطقی)", "زیاد (تهاجمی و شکار نوسانات ریز)"],
            index=sens_idx
        )
        selected_sens = "low" if "کم" in sensitivity_opt else ("medium" if "متوسط" in sensitivity_opt else "high")
        
    with set_col2:
        current_b = config.get("broker_type", "paper").lower()
        b_idx = 0 if current_b == "paper" else (1 if current_b == "crypto" else 2)
        broker_opt = st.selectbox(
            "انتخاب بستر اتصال و اجرای معاملات",
            ["شبیه‌ساز تستی (Paper Trading)", "صرافی کریپتو (Binance, Bybit via CCXT)", "بروکر فارکس (MetaTrader 5)"],
            index=b_idx
        )
        selected_b = "paper" if "شبیه‌ساز" in broker_opt else ("crypto" if "صرافی" in broker_opt else "forex_mt5")

    # Dynamic inputs depending on Broker type
    m_acc = config.get("mt5_account_id", "")
    m_pwd = config.get("mt5_password", "")
    m_srv = config.get("mt5_server", "Exness-MT5-Trial")
    c_api = config.get("exchange_api_key", "")
    c_sec = config.get("exchange_secret_key", "")

    if selected_b == "forex_mt5":
        st.info("🔑 اطلاعات حساب متاتریدر ۵ را وارد کنید:")
        m_acc = st.text_input("شماره حساب (Account ID)", value=m_acc)
        m_pwd = st.text_input("رمز عبور (Password)", type="password", value=m_pwd)
        m_srv = st.text_input("سرور بروکر", value=m_srv)
    elif selected_b == "crypto":
        st.info("🔑 کلیدهای API صرافی خود را وارد کنید:")
        c_api = st.text_input("API Key صرافی", value=c_api)
        c_sec = st.text_input("Secret Key صرافی", type="password", value=c_sec)

    # 2. Risk & Symbols Management
    st.markdown("---")
    set_col3, set_col4 = st.columns(2)
    with set_col3:
        symbols_input = st.text_input("نمادهای تحت نظر (با کاما جدا کنید)", value=", ".join(config.get("symbols", ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "BRENT/USD", "SOL/USDT"])))
        symbols_list = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
        
        trading_tf_val = st.selectbox("تایم‌فریم اصلی ورود و تحلیل", ["1m", "5m", "15m", "1h", "4h", "1d"], index=2)
        
    with set_col4:
        r_pct = st.slider("درصد ریسک روی هر معامله (%)", 0.1, 5.0, float(config.get("risk_percentage", 1.0)), 0.1)
        default_lev = st.number_input("اهرم (Leverage)", min_value=1, max_value=125, value=config.get("default_leverage", 1))
        initial_sl = st.slider("حد ضرر اولیه درصد (SL Ratio) %", 0.5, 5.0, float(config.get("sl_ratio", 1.5)), 0.1)

    # 3. Dynamic Take Profits
    st.markdown("---")
    st.markdown("🎯 **تنظیم ضرایب ریوارد اهداف سود (Trailing Take Profits)**")
    col_tp1, col_tp2, col_tp3 = st.columns(3)
    with col_tp1:
        tp1_val = st.slider("حد سود اول (TP1 R:R)", 0.5, 2.0, float(config.get("tp1_ratio", 1.0)), 0.1)
    with col_tp2:
        tp2_val = st.slider("حد سود دوم (TP2 R:R)", 1.5, 4.0, float(config.get("tp2_ratio", 2.0)), 0.1)
    with col_tp3:
        tp3_val = st.slider("حد سود سوم (TP3 R:R)", 2.5, 6.0, float(config.get("tp3_ratio", 3.0)), 0.1)

    # 4. Telegram Signal Room Integration
    st.markdown("---")
    st.markdown("✉️ **اتصال تلگرام به اتاق سیگنال همراه شما**")
    tg_enabled = st.checkbox("ارسال سیگنال‌ها به تلگرام", value=config.get("enable_telegram", False))
    tg_tok = st.text_input("توکن ربات تلگرام", value=config.get("telegram_bot_token", ""))
    tg_chat = st.text_input("آیدی چت / کانال تلگرام", value=config.get("telegram_chat_id", ""))

    # Save button
    st.markdown("---")
    if st.button("💾 ذخیره و اعمال نهایی تنظیمات آونیکس", use_container_width=True):
        config["symbols"] = symbols_list
        config["trading_timeframe"] = trading_tf_val
        config["risk_percentage"] = r_pct
        config["default_leverage"] = default_lev
        config["sl_ratio"] = initial_sl
        config["tp1_ratio"] = tp1_val
        config["tp2_ratio"] = tp2_val
        config["tp3_ratio"] = tp3_val
        config["enable_telegram"] = tg_enabled
        config["telegram_bot_token"] = tg_tok
        config["telegram_chat_id"] = tg_chat
        config["sensitivity"] = selected_sens
        config["broker_type"] = selected_b
        config["mt5_account_id"] = m_acc
        config["mt5_password"] = m_pwd
        config["mt5_server"] = m_srv
        config["exchange_api_key"] = c_api
        config["exchange_secret_key"] = c_sec
        save_config(config)
        st.success("تنظیمات با موفقیت ذخیره شدند و هسته ربات در لحظه آپدیت شد!")
        time.sleep(1)
        st.rerun()

# Auto-rerun trick to simulate 1-second ticking charts
if run_simulation:
    time.sleep(1)
    st.rerun()
