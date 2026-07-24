import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import streamlit.components.v1 as components
from bot import RealTimeTradingBot

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
        color: #cbd5e1;
    }
    /* Checklist style */
    .checklist-item {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #2e3e4f;
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
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; margin-bottom: 25px;'>پلتفرم معامله‌گری و ترید خودکار طلا، جفت‌ارزها و ارزهای دیجیتال</p>", unsafe_allow_html=True)

# Main Application organized in clean, separate rooms/tabs (Exactly as requested!)
tab_chart, tab_brain, tab_signals, tab_settings = st.tabs([
    "📊 اتاق چارت تریدینگ‌ویو (تمام‌صفحه)", 
    "🧠 اتاق فرمان مغز ربات (AI Brain Room)", 
    "📢 اتاق آرشیو سیگنال‌ها", 
    "⚙️ اتاق تنظیمات پیشرفته سیستم"
])

# ----------------- TAB 1: TRADINGVIEW FULL-SCREEN CHART -----------------
with tab_chart:
    sel_col1, sel_col2 = st.columns([1, 1])
    with sel_col1:
        selected_symbol = st.selectbox("انتخاب نماد معاملاتی جهت تحلیل زنده", config.get("symbols", ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "BRENT/USD", "SOL/USDT"]), index=0, key="chart_sym")
    with sel_col2:
        selected_timeframe = st.selectbox("تایم فریم پیش‌فرض چارت", ["1", "5", "15", "60", "240", "D"], index=2, key="chart_tf")

    symbol_mapping = {
        "XAU/USD": "OANDA:XAUUSD",
        "EUR/USD": "FX:EURUSD",
        "GBP/USD": "FX:GBPUSD",
        "USD/JPY": "FX:USDJPY",
        "BRENT/USD": "TVC:UKOIL",
        "SOL/USDT": "BINANCE:SOLUSDT",
        "BTC/USDT": "BINANCE:BTCUSDT"
    }
    
    tv_symbol = symbol_mapping.get(selected_symbol, "OANDA:XAUUSD")

    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%;background-color:#0f172a;">
      <div id="tradingview_chart" style="height:620px;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "{selected_timeframe}",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
        "container_id": "tradingview_chart"
      }}
      );
      </script>
    </div>
    """
    
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>🌐 <b>اتاق چارت تریدینگ‌ویو:</b> این نمودار کاملاً ریسپانسیو و تمام‌صفحه است. شما می‌توانید در گذشته بازار اسکرول کنید، ابزارهای خط کشی و تحلیل اضافه کرده و اندیکاتورها را شخصی‌سازی کنید.</p>", unsafe_allow_html=True)
    components.html(tradingview_html, height=630)

# ----------------- TAB 2: THE AI TRADING BRAIN ROOM -----------------
with tab_brain:
    st.markdown("### 🧠 پایش مانیتورینگ مغز ربات و وضعیت اندیکاتورها")
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>نمایش زنده امتیازدهی مغز سیستم و تاییده‌های تفکیک‌شده‌ی هر اندیکاتور</p>", unsafe_allow_html=True)
    
    col_cmd1, col_cmd2 = st.columns([3, 1])
    with col_cmd1:
        st.info("ربات در هر ۱۰ ثانیه کل بازار را مجدداً اسکن می‌کند. شما می‌توانید جهت تحلیل آنی دکمه روبرو را فشار دهید:")
    with col_cmd2:
        if st.button("🔥 اجرای فوری آنالیز مغز ربات", use_container_width=True):
            with st.spinner("ربات در حال تحلیل اندیکاتورها..."):
                bot_runner = RealTimeTradingBot()
                bot_runner.run_one_cycle()
                st.success("آنالیز نهایی به اتمام رسید!")
                st.rerun()

    col_intel, col_trades = st.columns([1, 1])
    
    with col_intel:
        st.markdown("#### 📊 تاییده‌های تفکیک‌شده‌ی اندیکاتورها (Isolated Confirmations)")
        
        latest_sig = signals[-1] if len(signals) > 0 else {}
        confirmations = latest_sig.get("confirmations", {
            "EMA 200": "BULLISH 🟢",
            "EMA 20/50": "BULLISH 🟢",
            "Ichimoku Cloud": "BULLISH 🟢",
            "Ichimoku TK Cross": "BULLISH 🟢",
            "RSI": "BULLISH 🟢",
            "MACD": "BULLISH 🟢",
            "Bollinger Bands": "NEUTRAL 🟡"
        })
        
        score = latest_sig.get("brain_score", 85)
        
        score_color = "#10b981" if score >= config.get("brain_score_threshold", 70) else "#ef4444"
        st.markdown(f"""
        <div class='ios-card'>
            <div class='metric-title'>امتیاز فعلی همگرایی اندیکاتورها (Brain Score)</div>
            <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 8px;'>
                <span style='font-size: 28px; font-weight: 700; color: {score_color};'>{score}٪</span>
                <span style='font-size: 13px; color: #94a3b8;'>حد نصاب ورود: {config.get("brain_score_threshold", 70)}٪</span>
            </div>
            <div style='background-color: #334155; border-radius: 10px; height: 10px; width: 100%; margin-top: 10px;'>
                <div style='background-color: {score_color}; border-radius: 10px; height: 10px; width: {score}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='ios-card'>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>چک‌لیست وضعیت اندیکاتورها در آخرین تحلیل:</p>", unsafe_allow_html=True)
        for name, status in confirmations.items():
            st.markdown(f"""
            <div class='checklist-item'>
                <span style='color: #cbd5e1;'>{name}</span>
                <span style='font-weight: 500;'>{status}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_trades:
        st.markdown("#### 💼 گزارش موقعیت‌ها و معاملات زنده")
        
        current_balance = portfolio.get("balance", 10000.0)
        st.markdown(f"""
        <div class='ios-card'>
            <div class='metric-title'>دارایی کل کیف پول آزمایشی (Balance)</div>
            <div class='metric-value'>${current_balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        # Show active trades
        active_trades = portfolio.get("active_trades", [])
        if len(active_trades) == 0:
            st.info("در حال حاضر هیچ معامله فعالی باز نیست.")
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
                        قیمت ورود: {trade['entry_price']} | قیمت زنده: {trade['current_price']}<br>
                        حد ضرر متحرک: <b style='color: #f87171;'>{trade['sl']}</b> | اهداف سود: TP1: {trade['tp1']} | TP2: {trade['tp2']} | TP3: {trade['tp3']}<br>
                        تاییدیه تریلینگ: پله <b>{trade.get('highest_tp_reached', 0)}</b> از ۳ (فری‌ریسک فعال)
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if latest_sig:
            st.markdown("<p style='font-weight: 700; color: #f8fafc; margin-top: 15px;'>📄 بروشور تحلیلی آخرین معامله:</p>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='brochure-card'>
                {latest_sig['reason']}
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 3: SIGNAL ROOM ARCHIVE -----------------
with tab_signals:
    st.markdown("### 📢 اتاق آرشیو سیگنال‌های صادرشده")
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>لیست دائم موقعیت‌های صادر شده توسط مغز سیستم به همراه بروشور علت ورود</p>", unsafe_allow_html=True)
    signals_list = load_signals()
    
    if len(signals_list) == 0:
        st.info("هیچ سیگنالی صادر نشده است.")
    else:
        for sig in reversed(signals_list):
            side_badge = "🟢 BUY (خرید)" if sig["side"] == "BUY" else "🔴 SELL (فروش)"
            color_theme = "#10b981" if sig["side"] == "BUY" else "#ef4444"
            status_fa = "🟡 در جریان" if sig["status"] == "PENDING" else f"🔒 بسته شده ({sig['status']})"
            
            st.markdown(f"""
            <div class='ios-card' style='border-right: 5px solid {color_theme};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 18px; font-weight: 700; color: #f8fafc;'>{sig['symbol']} (تایم‌فریم {config.get('trading_timeframe','15m')})</span>
                    <span style='color: {color_theme}; font-weight: 700; font-size: 15px;'>{side_badge}</span>
                    <span style='font-size: 11px; color: #94a3b8; background-color: #334155; padding: 4px 8px; border-radius: 20px;'>{status_fa}</span>
                </div>
                <div style='margin-top: 15px; font-size: 13px; color: #cbd5e1; line-height: 1.6;'>
                    💵 قیمت ورود: <b>{sig['entry_price']}</b> | 🛡️ حد ضرر اولیه: <b style='color: #f87171;'>{sig['sl']}</b><br>
                    🎯 اهداف سود پله‌ای: اول (TP1): <b>{sig.get('tp1','N/A')}</b> | دوم (TP2): <b>{sig.get('tp2','N/A')}</b> | سوم (TP3): <b>{sig.get('tp3','N/A')}</b>
                </div>
                <div class='brochure-card'>
                    {sig['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 4: SYSTEM SETTINGS -----------------
with tab_settings:
    st.markdown("### ⚙️ تنظیمات فوق‌پیشرفته اندیکاتورها و مغز سیستم")
    
    # 1. Indicator settings (Exactly as requested: individual setups!)
    st.markdown("#### 📊 شخصی‌سازی مجزای اندیکاتورها (Indicator Parameter Controls)")
    
    col_set_ma, col_set_ich = st.columns(2)
    with col_set_ma:
        st.markdown("<p style='font-weight: 700; color: #3b82f6;'>۱. میانگین‌های متحرک (EMAs)</p>", unsafe_allow_html=True)
        ma_s = st.slider("دوره موینگ سریع (Fast EMA)", 5, 30, config.get("ma_short", 20))
        ma_m = st.slider("دوره موینگ میان‌مدت (Medium EMA)", 30, 100, config.get("ma_medium", 50))
        ma_l = st.slider("دوره موینگ بلندمدت روند (Long EMA)", 100, 300, config.get("ma_long", 200))
    with col_set_ich:
        st.markdown("<p style='font-weight: 700; color: #a855f7;'>۲. ابر ایچیموکو (Ichimoku)</p>", unsafe_allow_html=True)
        ich_t = st.number_input("دوره خط تبدیل (Tenkan-sen)", min_value=5, max_value=20, value=config.get("ichimoku_tenkan", 9))
        ich_k = st.number_input("دوره خط پایه (Kijun-sen)", min_value=15, max_value=40, value=config.get("ichimoku_kijun", 26))
        ich_b = st.number_input("دوره خط سنکو ب (Senkou Span B)", min_value=40, max_value=80, value=config.get("ichimoku_senkou_b", 52))

    st.markdown("---")
    col_set_rsi, col_set_macd, col_set_bb = st.columns(3)
    with col_set_rsi:
        st.markdown("<p style='font-weight: 700; color: #f43f5e;'>۳. شاخص قدرت (RSI)</p>", unsafe_allow_html=True)
        rsi_per = st.number_input("دوره زمانی RSI", min_value=5, max_value=30, value=config.get("rsi_period", 14))
        rsi_os = st.slider("مرز اشباع فروش (Oversold)", 10, 40, config.get("rsi_oversold", 30))
        rsi_ob = st.slider("مرز اشباع خرید (Overbought)", 60, 90, config.get("rsi_overbought", 70))
    with col_set_macd:
        st.markdown("<p style='font-weight: 700; color: #10b981;'>۴. اندیکاتور MACD</p>", unsafe_allow_html=True)
        macd_f = st.number_input("موینگ سریع مکدی", min_value=5, max_value=25, value=config.get("macd_fast", 12))
        macd_s = st.number_input("موینگ کند مکدی", min_value=20, max_value=40, value=config.get("macd_slow", 26))
        macd_sig = st.number_input("خط سیگنال مکدی", min_value=5, max_value=15, value=config.get("macd_signal", 9))
    with col_set_bb:
        st.markdown("<p style='font-weight: 700; color: #eab308;'>۵. باندهای بولینگر (Bollinger)</p>", unsafe_allow_html=True)
        bb_per = st.number_input("دوره زمانی باند بولینگر", min_value=5, max_value=40, value=config.get("bb_period", 20))
        bb_std = st.number_input("انحراف معیار (Std Dev)", min_value=1.0, max_value=4.0, value=config.get("bb_std_dev", 2.0), step=0.1)

    # 2. Risk & Symbols Management
    st.markdown("---")
    st.markdown("#### 🛡️ درصد ریسک، اهداف حد سود و بستر معاملاتی")
    
    set_col_risk, set_col_broker = st.columns(2)
    with set_col_risk:
        r_pct = st.slider("درصد ریسک روی کل حساب (%)", 0.1, 5.0, float(config.get("risk_percentage", 1.0)), 0.1)
        lev = st.number_input("ضریب اهرم صرافی (Leverage)", min_value=1, max_value=125, value=config.get("default_leverage", 1))
        sl_rat = st.slider("حد ضرر اولیه درصد (SL Ratio) %", 0.5, 5.0, float(config.get("sl_ratio", 1.5)), 0.1)
        score_thresh = st.slider("حد نصاب امتیاز تاییدیه مغز ربات جهت ترید (Score Threshold) %", 50, 95, config.get("brain_score_threshold", 70))
        
    with set_col_broker:
        current_b = config.get("broker_type", "paper").lower()
        b_idx = 0 if current_b == "paper" else (1 if current_b == "crypto" else 2)
        broker_opt = st.selectbox(
            "انتخاب بستر اتصال و اجرای معاملات (ریل / دمو / پروپ‌فرم / مسابقات)",
            ["شبیه‌ساز تستی (Paper Trading)", "صرافی کریپتو (Binance, Bybit via CCXT)", "بروکر فارکس و پروپ‌فرم‌ها (MetaTrader 5)"],
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
        st.info("🔌 اتصال به کارگزاری فارکس (لایت فایننس، آلپاری، بینگ‌اکس) یا حساب‌های چالش پروپ‌فرم (FundedNext و غیره):")
        m_acc = st.text_input("شماره حساب متاتریدر ۵ (Account ID)", value=m_acc)
        m_pwd = st.text_input("رمز عبور حساب (Password)", type="password", value=m_pwd)
        m_srv = st.text_input("سرور کارگزار (Broker Server - مثلاً FundedNext-Server)", value=m_srv)
        
        # Prop firm drawdown lock settings
        st.markdown("<p style='font-weight: 700; color: #f87171;'>🛡️ سیستم ضد کال‌مارجین و محافظ چالش‌های پروپ‌فرم (Avenix Prop Guard)</p>", unsafe_allow_html=True)
        prop_dd = st.slider("حداکثر دروداون (افت سرمایه) مجاز روزانه حساب در پروپ‌فرم یا مسابقه %", 1.0, 10.0, float(config.get("prop_drawdown_limit", 4.0)), 0.1)
        
        # Unlock button if locked
        if config.get("prop_drawdown_breached", False):
            st.error("🚨 قفل محافظ دروداون روزانه فعال شده است! معاملات موقتاً مسدود هستند.")
            if st.button("🔓 ریست کردن دستی قفل دروداون روزانه ربات"):
                config["prop_drawdown_breached"] = False
                save_config(config)
                st.success("قفل ربات باز شد!")
                time.sleep(1)
                st.rerun()
        else:
            st.success("🟢 محافظ دروداون روزانه فعال و حساب در حاشیه امنیت کامل قرار دارد.")
            prop_dd_val = prop_dd
    else:
        prop_dd_val = config.get("prop_drawdown_limit", 4.0)

    # 3. Dynamic TPs & Telegram
    st.markdown("---")
    st.markdown("🎯 **تنظیم ضرایب ریوارد اهداف سود پله‌ای (Trailing Take Profits)**")
    col_tp1, col_tp2, col_tp3 = st.columns(3)
    with col_tp1:
        tp1_val = st.slider("حد سود اول (TP1 R:R)", 0.5, 2.0, float(config.get("tp1_ratio", 1.0)), 0.1)
    with col_tp2:
        tp2_val = st.slider("حد سود دوم (TP2 R:R)", 1.5, 4.0, float(config.get("tp2_ratio", 2.0)), 0.1)
    with col_tp3:
        tp3_val = st.slider("حد سود سوم (TP3 R:R)", 2.5, 6.0, float(config.get("tp3_ratio", 3.0)), 0.1)

    # 4. Multi-Platform Social Broadcast Room Settings
    st.markdown("---")
    st.markdown("### ✉️ اتاق مدیریت انتشار سیگنال‌ها (Bale, Telegram, WhatsApp)")
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>ارسال فوق‌سریع و همزمان بروشورهای تحلیلی ربات به پیام‌رسان‌های ایرانی و خارجی</p>", unsafe_allow_html=True)
    
    col_tg, col_bale, col_wa = st.columns(3)
    
    with col_tg:
        st.markdown("<p style='font-weight: 700; color: #3b82f6;'>۱. پیام‌رسان تلگرام (Telegram)</p>", unsafe_allow_html=True)
        tg_enabled = st.checkbox("فعال‌سازی ارسال به تلگرام", value=config.get("enable_telegram", False))
        tg_tok = st.text_input("توکن ربات تلگرام", value=config.get("telegram_bot_token", ""))
        tg_chat = st.text_input("آیدی چت / کانال تلگرام", value=config.get("telegram_chat_id", ""))
        
    with col_bale:
        st.markdown("<p style='font-weight: 700; color: #10b981;'>۲. پیام‌رسان ایرانی بله (Bale)</p>", unsafe_allow_html=True)
        bale_enabled = st.checkbox("فعال‌سازی ارسال به بله", value=config.get("enable_bale", False))
        bale_tok = st.text_input("توکن ربات بله (Bale Token)", value=config.get("bale_bot_token", ""))
        bale_chat = st.text_input("آیدی چت / کانال بله", value=config.get("bale_chat_id", ""))
        
    with col_wa:
        st.markdown("<p style='font-weight: 700; color: #eab308;'>۳. پیام‌رسان واتس‌اپ (WhatsApp)</p>", unsafe_allow_html=True)
        wa_enabled = st.checkbox("فعال‌سازی ارسال به واتس‌اپ", value=config.get("enable_whatsapp", False))
        wa_inst = st.text_input("شناسه درگاه (Instance ID)", value=config.get("whatsapp_instance_id", "instance99999"))
        wa_tok = st.text_input("توکن درگاه واتس‌اپ", value=config.get("whatsapp_token", ""))
        wa_phone = st.text_input("شماره تلفن مقصد (مثلاً 989123456789)", value=config.get("whatsapp_phone", ""))

    st.markdown("---")
    symbols_input = st.text_input("نمادهای تحت نظر (با کاما جدا کنید)", value=", ".join(config.get("symbols", ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "BRENT/USD", "SOL/USDT"])))
    symbols_list = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    trading_tf_val = st.selectbox("تایم‌فریم اصلی ورود و تحلیل مغز ربات", ["1m", "5m", "15m", "1h", "4h", "1d"], index=2)

    # Reset Wallet
    st.markdown("---")
    if st.button("🔄 ریست کردن کیف پول معاملاتی دمو", use_container_width=True):
        initial_portfolio = {
            "balance": 10000.0,
            "active_trades": [],
            "completed_trades": []
        }
        save_portfolio(initial_portfolio)
        st.success("کیف پول ریست شد!")
        time.sleep(1)
        st.rerun()

    # Save button
    st.markdown("---")
    if st.button("💾 ذخیره و اعمال نهایی تمام تنظیمات فوق‌پیشرفته آونیکس", use_container_width=True):
        config["symbols"] = symbols_list
        config["trading_timeframe"] = trading_tf_val
        config["risk_percentage"] = r_pct
        config["default_leverage"] = lev
        config["sl_ratio"] = sl_rat
        config["tp1_ratio"] = tp1_val
        config["tp2_ratio"] = tp2_val
        config["tp3_ratio"] = tp3_val
        
        # Save Social Broadcast configs
        config["enable_telegram"] = tg_enabled
        config["telegram_bot_token"] = tg_tok
        config["telegram_chat_id"] = tg_chat
        config["enable_bale"] = bale_enabled
        config["bale_bot_token"] = bale_tok
        config["bale_chat_id"] = bale_chat
        config["enable_whatsapp"] = wa_enabled
        config["whatsapp_instance_id"] = wa_inst
        config["whatsapp_token"] = wa_tok
        config["whatsapp_phone"] = wa_phone
        
        config["sensitivity"] = selected_sens
        config["broker_type"] = selected_b
        config["mt5_account_id"] = m_acc
        config["mt5_password"] = m_pwd
        config["mt5_server"] = m_srv
        config["exchange_api_key"] = c_api
        config["exchange_secret_key"] = c_sec
        config["ma_short"] = ma_s
        config["ma_medium"] = ma_m
        config["ma_long"] = ma_l
        config["ichimoku_tenkan"] = ich_t
        config["ichimoku_kijun"] = ich_k
        config["ichimoku_senkou_b"] = ich_b
        config["rsi_period"] = rsi_per
        config["rsi_oversold"] = rsi_os
        config["rsi_overbought"] = rsi_ob
        config["macd_fast"] = macd_f
        config["macd_slow"] = macd_s
        config["macd_signal"] = macd_sig
        config["bb_period"] = bb_per
        config["bb_std_dev"] = bb_std
        config["brain_score_threshold"] = score_thresh
        config["prop_drawdown_limit"] = prop_dd_val
        save_config(config)
        st.success("تنظیمات با موفقیت ذخیره شدند و هسته ربات در لحظه آپدیت شد!")
        time.sleep(1)
        st.rerun()
