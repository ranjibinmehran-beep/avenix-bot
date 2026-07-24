import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import streamlit.components.v1 as components
from bot import RealTimeTradingBot
from execution import OrderExecutionEngine

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
    /* Disclaimer layout */
    .disclaimer-text {
        font-size: 13px;
        color: #e2e8f0;
        line-height: 1.8;
        text-align: justify;
    }
    /* Live HUD Bar */
    .hud-banner {
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: 700;
        font-size: 15px;
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

# Initialize Session State for Legal Welcome Gate
if "terms_accepted" not in st.session_state:
    st.session_state.terms_accepted = False

# ----------------- MULTI-LANGUAGE ENGINE (فارسی / ENGLISH / العربية / TÜRKÇE) -----------------
# Setup language selector on the top-right header
lang_col1, lang_col2 = st.columns([7, 3])
with lang_col2:
    selected_lang = st.selectbox("🌐 Choose Language / انتخاب زبان", ["English", "فارسی", "العربية", "Türkçe"], index=1)

lang_code = "fa" if selected_lang == "فارسی" else ("en" if selected_lang == "English" else ("ar" if selected_lang == "العربية" else "tr"))

# Complete 4-Language UI Dictionary
TXT = {
    "fa": {
        "title": "🦅 پلتفرم معاملاتی هوشمند آونیکس",
        "sub": "پلتفرم معامله‌گری و ترید خودکار طلا، جفت‌ارزها و ارزهای دیجیتال",
        "tab_chart": "📊 اتاق چارت تریدینگ‌ویو (تمام‌صفحه)",
        "tab_brain": "🧠 اتاق فرمان مغز ربات (AI Brain)",
        "tab_signals": "📢 اتاق آرشیو سیگنال‌ها",
        "tab_settings": "⚙️ اتاق تنظیمات پیشرفته سیستم",
        "selector_symbol": "انتخاب نماد معاملاتی جهت تحلیل زنده",
        "selector_tf": "تایم فریم چارت",
        "tv_caption": "🌐 <b>اتاق چارت تریدینگ‌ویو:</b> این نمودار کاملاً ریسپانسیو و تمام‌صفحه است. شما می‌توانید در گذشته بازار اسکرول کنید، ابزارهای ترسیمی اضافه کنید و اندیکاتورها را شخصی‌سازی کنید.",
        "brain_telemetry": "🧠 پایش مانیتورینگ مغز ربات و وضعیت اندیکاتورها",
        "brain_sub": "نمایش زنده امتیازدهی مغز سیستم و تاییده‌های تفکیک‌شده‌ی هر اندیکاتور",
        "force_scan_desc": "ربات در هر ۱۰ ثانیه کل بازار را مجدداً اسکن می‌کند. شما می‌توانید جهت تحلیل آنی دکمه روبرو را فشار دهید:",
        "force_scan_btn": "🔥 اجرای فوری آنالیز مغز ربات",
        "isolated_checklist": "📊 تاییده‌های تفکیک‌شده‌ی اندیکاتورها",
        "brain_score_title": "امتیاز فعلی همگرایی اندیکاتورها (Brain Score)",
        "score_threshold_desc": "حد نصاب ورود",
        "checklist_title": "وضعیت تک‌تک اندیکاتورها در آخرین تحلیل:",
        "pnl_report": "💼 گزارش موقعیت‌ها و معاملات زنده",
        "balance_title": "دارایی کل حساب دمو (Balance)",
        "active_trades_title": "معاملات فعال بازار",
        "broker_badge_title": "بستر معاملاتی متصل",
        "paper_badge": "شبیه‌ساز (دمو)",
        "real_badge": "حساب واقعی بروکر",
        "active_pnl": "سود زنده",
        "entry_price": "قیمت ورود",
        "live_price": "قیمت زنده",
        "current_sl": "حد ضرر فعلی",
        "original_sl": "حد ضرر اولیه",
        "targets": "اهداف حد سود",
        "trailing_step": "پله حد ضرر شناور",
        "completed_history": "✅ تاریخچه معاملات بسته شده",
        "exit_reason": "خروج با",
        "exit_time": "زمان خروج",
        "pnl_result": "نتیجه سود/زیان",
        "no_active_trades": "در حال حاضر هیچ معامله فعالی باز نیست.",
        "no_completed_trades": "تاریخچه معاملات بسته شده خالی است.",
        "settings_title": "⚙️ تنظیمات فوق‌پیشرفته اندیکاتورها و مغز سیستم",
        "ind_custom": "📊 شخصی‌سازی مجزای اندیکاتورها",
        "emas_title": "۱. میانگین‌های متحرک (EMAs)",
        "fast_ema": "دوره موینگ سریع (Fast EMA)",
        "medium_ema": "دوره موینگ میان‌مدت (Medium EMA)",
        "long_ema": "دوره موینگ بلندمدت روند (Long EMA)",
        "ich_title": "۲. ابر ایچیموکو (Ichimoku)",
        "tenkan_val": "دوره خط تبدیل (Tenkan-sen)",
        "kijun_val": "دوره خط پایه (Kijun-sen)",
        "span_b_val": "دوره خط سنکو ب (Senkou Span B)",
        "rsi_title": "۳. شاخص قدرت (RSI)",
        "rsi_period": "دوره زمانی RSI",
        "rsi_os": "مرز اشباع فروش (Oversold)",
        "rsi_ob": "مرز اشباع خرید (Overbought)",
        "macd_title": "۴. اندیکاتور MACD",
        "macd_fast": "موینگ سریع مکدی",
        "macd_slow": "موینگ کند مکدی",
        "macd_signal": "خط سیگنال مکدی",
        "bb_title": "۵. باندهای بولینگر (Bollinger)",
        "bb_period": "دوره زمانی باند بولینگر",
        "bb_std": "انحراف معیار (Std Dev)",
        "risk_title": "🛡️ درصد ریسک، اهداف حد سود و بستر معاملاتی",
        "risk_pct": "درصد ریسک روی کل حساب (%)",
        "leverage": "ضریب اهرم صرافی (Leverage)",
        "score_thresh": "حد نصاب امتیاز تاییدیه مغز ربات جهت ترید %",
        "broker_connect_title": "انتخاب بستر اتصال و اجرای معاملات (ریل / دمو)",
        "mt5_desc": "🔌 اتصال به کارگزاری فارکس (لایت فایننس، آلپاری) یا حساب‌های چالش پروپ‌فرم (FundedNext):",
        "prop_guard_title": "🛡️ سیستم ضد کال‌مارجین و محافظ چالش‌های پروپ‌فرم (Avenix Prop Guard)",
        "prop_limit_desc": "حداکثر دروداون (افت سرمایه) مجاز روزانه حساب %",
        "prop_locked_err": "🚨 قفل محافظ دروداون روزانه فعال شده است! معاملات موقتاً مسدود هستند.",
        "prop_unlock_btn": "🔓 ریست کردن دستی قفل دروداون روزانه ربات",
        "prop_safe": "🟢 محافظ دروداون روزانه فعال و حساب در حاشیه امنیت کامل قرار دارد.",
        "tp_reward": "🎯 تنظیم ضرایب ریوارد اهداف سود پله‌ای (Trailing Take Profits)",
        "social_broadcast_title": "### ✉️ اتاق مدیریت انتشار سیگنال‌ها (Bale, Telegram, WhatsApp)",
        "social_broadcast_sub": "ارسال فوق‌سریع و همزمان بروشورهای تحلیلی ربات به پیام‌رسان‌های ایرانی و خارجی",
        "tg_title": "۱. پیام‌رسان تلگرام (Telegram)",
        "tg_enable": "فعال‌سازی ارسال به تلگرام",
        "tg_token": "توکن ربات تلگرام",
        "tg_chat": "آیدی چت / کانال تلگرام",
        "bale_title": "۲. پیام‌رسان ایرانی بله (Bale)",
        "bale_enable": "فعال‌سازی ارسال به بله",
        "bale_token": "توکن ربات بله (Bale Token)",
        "bale_chat": "آیدی چت / کانال بله",
        "wa_title": "۳. پیام‌رسان واتس‌اپ (WhatsApp)",
        "wa_enable": "فعال‌سازی ارسال به واتس‌اپ",
        "wa_inst": "شناسه درگاه (Instance ID)",
        "wa_token": "توکن درگاه واتس‌اپ",
        "wa_phone": "شماره تلفن مقصد (مثلاً 989123456789)",
        "symbols_under_watch": "نمادهای تحت نظر (با کاما جدا کنید)",
        "main_tf_scan": "تایم‌فریم اصلی ورود و تحلیل مغز ربات",
        "reset_wallet_btn": "🔄 ریست کردن کیف پول معاملاتی دمو",
        "save_settings_btn": "💾 ذخیره و اعمال نهایی تمام تنظیمات فوق‌پیشرفته آونیکس",
        "manual_term_title": "🚀 پایانه معاملات دستی (Manual Trade Terminal)",
        "manual_term_sub": "ثبت مستقیم و آنی پوزیشن‌های شخصی شما روی صرافی یا متاتریدر ۵ کارگزاری",
        "btn_buy": "🚀 خرید دستی (BUY)",
        "btn_sell": "🚨 فروش دستی (SELL)",
        "btn_close_trade": "❌ بستن فوری و دستی معامله (Emergency Close)",
        "disclaimer_title": "⚠️ بیانیه قوانین و سلب مسئولیت حقوقی (Terms of Service & Disclaimer)",
        "disclaimer_body": "فعالیت در بازارهای مالی بین‌المللی اعم از فارکس، طلا، جفت‌ارزها و ارزهای دیجیتال دارای ریسک بسیار بالایی است و ممکن است منجر به از دست رفتن بخشی یا تمام سرمایه شما شود. پلتفرم معاملاتی آونیکس (Avenix) یک نرم‌افزار تحلیلی، الگوریتمی و محاسباتی ریاضی است. تمامی سیگنال‌ها، تاییده‌ها، گزارش‌های بروشوری و تحلیل‌های صادر شده در این نرم‌افزار، صرفاً جهت پیشنهاد تحلیل بازار و اهداف آموزشی شبیه‌سازی شده‌اند و به هیچ عنوان توصیه سرمایه‌گذاری، سیگنال خرید یا فروش قطعی یا مشاوره‌ی مالی به حساب نمی‌آیند. مالک، طراح و توسعه‌دهندگان این نرم‌افزار هیچ‌گونه مسئولیت حقوقی، مالی یا قانونی در قبال سودها، زیان‌ها، دروداون‌ها، افت سرمایه، مسدود شدن حساب‌های پروپ‌فرم یا هرگونه خسارت ناشی از استفاده از این برنامه در بازار واقعی و دمو ندارند. استفاده شما از این نرم‌افزار به معنای پذیرش کامل و بدون قید و شرط این قوانین سلب مسئولیت است.",
        "sl_ratio": "حد ضرر اولیه درصد (SL Ratio) %",
        "btn_accept_terms": "✅ قوانین و سلب مسئولیت را به طور کامل خواندم و می‌پذیرم",
        "locked_terms_desc": "🔒 لطفا برای دسترسی به اتاق معاملات و چارت زنده، ابتدا قوانین سلب مسئولیت حقوقی را تأیید کنید:"
    },
    "en": {
        "title": "🦅 AVENIX SMART TRADING SUITE",
        "sub": "Algorithmic Trading & Automated Risk Management for Forex, Metals, & Crypto",
        "tab_chart": "📊 TradingView Live Chart",
        "tab_brain": "🧠 AI Trading Brain Room",
        "tab_signals": "📢 Signal Room Archive",
        "tab_settings": "⚙️ Advanced System Settings",
        "selector_symbol": "Select Asset for Live Analysis",
        "selector_tf": "Chart Timeframe",
        "tv_caption": "🌐 <b>TradingView Terminal:</b> This chart is fully interactive. You can scroll back, add drawing tools, and customize indicators natively.",
        "brain_telemetry": "🧠 Robot Telemetry & Indicator Status",
        "brain_sub": "Live scoring and isolated status configurations for each technical indicator",
        "force_scan_desc": "The robot scans the market every 10 seconds. You can trigger an instant scan below:",
        "force_scan_btn": "🔥 Trigger Instant AI Brain Scan",
        "isolated_checklist": "📊 Isolated Indicator Confirmations",
        "brain_score_title": "Consolidated Convergence Score (Brain Score)",
        "score_threshold_desc": "Threshold Limit",
        "checklist_title": "Individual indicator readings in the last scan:",
        "pnl_report": "💼 Live Positions & Orders Telemetry",
        "balance_title": "Demo Wallet Equity (Balance)",
        "active_trades_title": "Active Positions",
        "broker_badge_title": "Connected Execution Bridge",
        "paper_badge": "Simulated Demo (Paper)",
        "real_badge": "Live Broker Server",
        "active_pnl": "Floating Profit",
        "entry_price": "Entry Price",
        "live_price": "Live Price",
        "current_sl": "Current Stop Loss",
        "original_sl": "Original Stop Loss",
        "targets": "Take Profit Targets",
        "trailing_step": "Trailing Step",
        "completed_history": "✅ Completed Trades History",
        "exit_reason": "Closed by",
        "exit_time": "Exit Time",
        "pnl_result": "Resulting PnL",
        "no_active_trades": "There are currently no active trades.",
        "no_completed_trades": "Completed trade history is empty.",
        "settings_title": "⚙️ Advanced Indicator & System Config",
        "ind_custom": "📊 Individual Indicator Setups",
        "emas_title": "1. Exponential Moving Averages (EMAs)",
        "fast_ema": "Fast EMA Period",
        "medium_ema": "Medium EMA Period",
        "long_ema": "Long EMA Trend Filter",
        "ich_title": "2. Ichimoku Kinko Hyo",
        "tenkan_val": "Tenkan-sen (Conversion) Period",
        "kijun_val": "Kijun-sen (Base) Period",
        "span_b_val": "Senkou Span B Period",
        "rsi_title": "3. Relative Strength Index (RSI)",
        "rsi_period": "RSI Period",
        "rsi_os": "Oversold Boundary",
        "rsi_ob": "Overbought Boundary",
        "macd_title": "4. MACD Configuration",
        "macd_fast": "MACD Fast EMA",
        "macd_slow": "MACD Slow EMA",
        "macd_signal": "MACD Signal Line",
        "bb_title": "5. Bollinger Bands",
        "bb_period": "Bollinger Period",
        "bb_std": "Standard Deviation (Std Dev)",
        "risk_title": "🛡️ Risk Sizing, Target Profits, & Broker Bridge",
        "risk_pct": "Account Risk Percentage (%)",
        "leverage": "Margin Leverage Factor",
        "score_thresh": "Consolidated Score Entrance Threshold %",
        "broker_connect_title": "Connected Account Connection Setup (Real/Demo)",
        "mt5_desc": "🔌 Connect to Forex Broker (LiteFinance, Alpari) or Prop-Firm account challenge (FundedNext):",
        "prop_guard_title": "🛡️ Drawdown Protection Guard (Avenix Prop Guard)",
        "prop_limit_desc": "Maximum Daily Allowed Account Loss %",
        "prop_locked_err": "🚨 Daily Drawdown limit breached! Trading is locked for today.",
        "prop_unlock_btn": "🔓 Reset Daily Drawdown Lock",
        "prop_safe": "🟢 Daily drawdown guard is active. Account margins are highly secure.",
        "tp_reward": "🎯 Trailing Profit Ratios (Risk-to-Reward)",
        "social_broadcast_title": "### Social Broadcast Management (Bale, Telegram, WhatsApp)",
        "social_broadcast_sub": "Broadcast analytical brochure signal reports simultaneously across social platforms",
        "tg_title": "1. Telegram Messenger API",
        "tg_enable": "Enable Telegram Broadcast",
        "tg_token": "Telegram Bot Token",
        "tg_chat": "Telegram Chat / Channel ID",
        "bale_title": "2. Bale Messenger API (Iranian)",
        "bale_enable": "Enable Bale Broadcast",
        "bale_token": "Bale Bot Token",
        "bale_chat": "Bale Sohbet / Channel ID",
        "wa_title": "3. WhatsApp API Gateway",
        "wa_enable": "Enable WhatsApp Broadcast",
        "wa_inst": "WhatsApp Instance ID",
        "wa_token": "WhatsApp Token",
        "wa_phone": "Target Phone Number (e.g. 989123456789)",
        "symbols_under_watch": "Symbols Under Watch (Comma separated)",
        "main_tf_scan": "Main Scan Timeframe",
        "reset_wallet_btn": "🔄 Reset Demo Portfolio",
        "save_settings_btn": "💾 Save & Apply All Configs",
        "manual_term_title": "🚀 Manual Trade Terminal",
        "manual_term_sub": "Submit manual positions with custom SL and TP.",
        "btn_buy": "🚀 Place Manual BUY (Long)",
        "btn_sell": "🚨 Place Manual SELL (Short)",
        "btn_close_trade": "Manual Emergency Close Trade",
        "disclaimer_title": "⚠️ Legal Disclaimer & Terms of Service",
        "disclaimer_body": "Trading in international financial markets involves high risk. Avenix is an analytical software for educational simulation purposes only.",
        "sl_ratio": "Initial Stop Loss Ratio %",
        "btn_accept_terms": "✅ I fully read and accept the Terms of Service & Disclaimer",
        "locked_terms_desc": "🔒 Please accept the Legal Disclaimer first to unlock Avenix Charts and Brain rooms:"
    },
    "ar": {
        "title": "🦅 منصة أفينيكس للتداول الذكي (Avenix)",
        "sub": "التداول الآلي وإدارة المخاطر لأسواق الفوركس والذهب والعملات الرقمية",
        "tab_chart": "📊 مخطط تریدینغ‌ویو (شاشة كاملة)",
        "tab_brain": "🧠 غرفة قيادة عقل الروبوت (AI Brain)",
        "tab_signals": "📢 أرشيف إشارات التداول",
        "tab_settings": "⚙️ الإعدادات المتقدمة للنظام",
        "selector_symbol": "اختر الرمز للتحليل المباشر",
        "selector_tf": "إطار المخطط الزمني",
        "tv_caption": "🌐 <b>مخطط TradingView:</b> هذا المخطط تفاعلي بالكامل.",
        "brain_telemetry": "🧠 مانیتور الروبوت وحالة المؤشرات الفنية",
        "brain_sub": "قراءة مباشرة لتقييم عقل الروبوت",
        "force_scan_desc": "يقوم الروبوت بمسح السوق كل 10 ثوانٍ.",
        "force_scan_btn": "🔥 تشغيل مسح عقل الروبوت الفوري",
        "isolated_checklist": "📊 تأكيدات المؤشرات المنفصلة",
        "brain_score_title": "التقييم الإجمالي لقوة الاتجاه (Brain Score)",
        "score_threshold_desc": "الحد الأدنى للدخول",
        "checklist_title": "حالة كل مؤشر في التحليل الأخير:",
        "pnl_report": "💼 الصفقات والمراكز المفتوحة",
        "balance_title": "إجمالي رصيد المحفظة التجريبية (Balance)",
        "active_trades_title": "الصفقات النشطة",
        "broker_badge_title": "منصة التداول المتصلة",
        "paper_badge": "محاكاة تجريبية (Paper)",
        "real_badge": "حساب حقيقي وسيط",
        "active_pnl": "الأرباح العائمة",
        "entry_price": "سعر الدخول",
        "live_price": "السعر المباشر",
        "current_sl": "وقف الخسارة الحالي",
        "original_sl": "وقف الخسارة الأولي",
        "targets": "أهداف جني الأرباح",
        "trailing_step": "خطوة الوقف المتحرك",
        "completed_history": "✅ تاريخ الصفقات المغلقة",
        "exit_reason": "أغلقت بسبب",
        "exit_time": "وقت الإغلاق",
        "pnl_result": "الربح/الخسارة النهائية",
        "no_active_trades": "لا توجد صفقات نشطة حالياً.",
        "no_completed_trades": "أرشيف الصفقات المغلقة فارغ.",
        "settings_title": "⚙️ الإعدادات المتقدمة للمؤشرات والنظام",
        "ind_custom": "📊 تكوين المؤشرات المنفردة",
        "emas_title": "1. المتوسطات المتحركة الأسية (EMAs)",
        "fast_ema": "فترة المتوسط السريع",
        "medium_ema": "فترة المتوسط المتوسط",
        "long_ema": "فترة المتوسط الطويل",
        "ich_title": "2. مؤشر إيشيموكو (Ichimoku)",
        "tenkan_val": "فترة خط التحويل",
        "kijun_val": "فترة خط الأساس",
        "span_b_val": "فترة خط سنكو ب",
        "rsi_title": "3. مؤشر القوة النسبية (RSI)",
        "rsi_period": "فترة RSI",
        "rsi_os": "حد منطقة البيع المفرط (Oversold)",
        "rsi_ob": "حد منطقة الشراء المفرط (Overbought)",
        "macd_title": "4. مؤشر الماكد (MACD)",
        "macd_fast": "ماكد المتوسط السريع",
        "macd_slow": "ماكد المتوسط البطيء",
        "macd_signal": "خط إشارة الماكد",
        "bb_title": "5. حزم بولينجر (Bollinger)",
        "bb_period": "فترة حزمة بولينجر",
        "bb_std": "الانحراف المعياري (Std Dev)",
        "risk_title": "🛡️ حجم المخاطرة، أهداف الربح، ومنصة التداول",
        "risk_pct": "نسبة المخاطرة للحساب (%)",
        "leverage": "رافعة الهامش المالي",
        "score_thresh": "عتبة دخول تقييم عقل الروبوت %",
        "broker_connect_title": "تكوين حساب التداول المتصل (حقيقي/تجريبي)",
        "mt5_desc": "🔌 الاتصال بوسطاء الفوركس أو حسابات تحدي البروب (FundedNext):",
        "prop_guard_title": "🛡️ حارس حماية الحساب (Avenix Prop Guard)",
        "prop_limit_desc": "أقصى تراجع يومي مسموح به للحساب %",
        "prop_locked_err": "🚨 تم اختراق الحد الأقصى للتراجع اليومي!",
        "prop_unlock_btn": "🔓 إعادة ضبط قفل التراجع اليومي",
        "prop_safe": "🟢 حارس التراجع اليومي نشط.",
        "tp_reward": "🎯 نسب جني الأرباح المتحركة",
        "social_broadcast_title": "### NŞ",
        "social_broadcast_sub": "بث تقارير تحليل الروبوت",
        "tg_title": "1. واجهة تلجرام (Telegram)",
        "tg_enable": "تفعيل البث المباشر إلى تلجرام",
        "tg_token": "رمز بوت تلجرام",
        "tg_chat": "معرف قناة تلجرام",
        "bale_title": "2. واجهة بله الإيرانية (Bale)",
        "bale_enable": "تفعيل البث المباشر إلى بله",
        "bale_token": "رمز بوت بله",
        "bale_chat": "معرف قناة بله",
        "wa_title": "3. بوابة واتساب (WhatsApp)",
        "wa_enable": "تفعيل البث المباشر إلى واتساب",
        "wa_inst": "معرف مثيل واتساب",
        "wa_token": "رمز بوابة واتساب",
        "wa_phone": "رقم الهاتف",
        "symbols_under_watch": "الرموز تحت المراقبة",
        "main_tf_scan": "الإطار الزمني الرئيسي للمسح",
        "reset_wallet_btn": "🔄 إعادة ضبط المحفظة التجريبية",
        "save_settings_btn": "💾 حفظ وتطبيق جميع الإعدادات",
        "manual_term_title": "🚀 محطة التداول اليدوي",
        "manual_term_sub": "إرسال صفقات يدوية فورية.",
        "btn_buy": "🚀 شراء (BUY)",
        "btn_sell": "🚨 بيع (SELL)",
        "btn_close_trade": "❌ إغلاق طوارئ",
        "disclaimer_title": "⚠️ إخلاء المسؤولية القانونية وشروط الخدمة",
        "disclaimer_body": "التداول في الأسواق المالية الدولية ينطوي على مخاطر عالية جداً.",
        "sl_ratio": "نسبة وقف الخسارة الأولي %",
        "btn_accept_terms": "✅ أوافق على شروط الخدمة وإخلاء المسؤولية القانونية",
        "locked_terms_desc": "🔒 يرجى قبول إخلاء المسؤولية أولاً لفتح قفل منصة Avenix:"
    },
    "tr": {
        "title": "🦅 Avenix Akıllı Algoritmik Ticaret Platformu",
        "sub": "Forex, Değerli Metaller ve Kripto Piyasaları için Otomatik İşlem ve Risk Yönetimi",
        "tab_chart": "📊 TradingView Canlı Grafik (Tam Ekran)",
        "tab_brain": "🧠 Robot Komuta Odası (AI Brain)",
        "tab_signals": "📢 Sinyal Arşivi",
        "tab_settings": "⚙️ Gelişmiş Sistem Ayarları",
        "selector_symbol": "Canlı Analiz İçin Varlık Seçin",
        "selector_tf": "Grafik Zaman Dilimi",
        "tv_caption": "🌐 <b>TradingView Terminali:</b> Bu grafik tamamen etkileşimlidir.",
        "brain_telemetry": "🧠 Robot Telemetrisi ve Gösterge Durumu",
        "brain_sub": "Robotun karar mekanizması ve her teknik gösterge için onay durumları",
        "force_scan_desc": "Robot her 10 saniyede bir piyasayı tarar.",
        "force_scan_btn": "🔥 Anında Robot Taraması Başlat",
        "isolated_checklist": "📊 Bağımsız Gösterge Onayları",
        "brain_score_title": "Konsolide Güç Skoru (Brain Score)",
        "score_threshold_desc": "Giriş Eşiği",
        "checklist_title": "Son taramadaki bireysel gösterge durumları:",
        "pnl_report": "💼 Canlı Pozisyonlar ve Emirler",
        "balance_title": "Demo Cüzdan Bakiyesi (Balance)",
        "active_trades_title": "Aktif Pozisyonlar",
        "broker_badge_title": "Bağlı İşlem Köprüsü",
        "paper_badge": "Simüle Demo (Paper)",
        "real_badge": "Gerçek Broker Sunucusu",
        "active_pnl": "Anlık Kâr/Zarar",
        "entry_price": "Giriş Fiyatı",
        "live_price": "Canlı Fiyat",
        "current_sl": "Mevcut Durdurma Noktası",
        "original_sl": "İlk Durdurma Noktası",
        "targets": "Kâr Hedefleri",
        "trailing_step": "Takip Eden Adım",
        "completed_history": "✅ Kapatılan İşlemler Geçmişi",
        "exit_reason": "Kapatılma Nedeni",
        "exit_time": "Kapatılma Zamanı",
        "pnl_result": "Net Kâr/Zarar",
        "no_active_trades": "Şu anda aktif işlem bulunmamaktadır.",
        "no_completed_trades": "Kapatılan işlem geçmişi boş.",
        "settings_title": "⚙️ Gelişmiş Gösterge ve Sistem Yapılandırması",
        "ind_custom": "📊 Bireysel Gösterge Kurulumları",
        "emas_title": "1. Üstel Hareketli Ortalamalar (EMAs)",
        "fast_ema": "Hızlı EMA Periyodu",
        "medium_ema": "Orta EMA Periyodu",
        "long_ema": "Uzun EMA Trend Filtresi",
        "ich_title": "2. Ichimoku Kinko Hyo",
        "tenkan_val": "Tenkan-sen Periyodu",
        "kijun_val": "Kijun-sen Periyodu",
        "span_b_val": "Senkou Span B Periyodu",
        "rsi_title": "3. Göreceli Güç Endeksi (RSI)",
        "rsi_period": "RSI Periyodu",
        "rsi_os": "Aşırı Satım Sınırı",
        "rsi_ob": "Aşırı Alım Sınırı",
        "macd_title": "4. MACD Yapılandırması",
        "macd_fast": "MACD Hızlı EMA",
        "macd_slow": "MACD Yavaş EMA",
        "macd_signal": "MACD Sinyal Çizgisi",
        "bb_title": "5. Bollinger Bantları",
        "bb_period": "Bollinger Periyodu",
        "bb_std": "Standart Sapma (Std Dev)",
        "risk_title": "🛡️ Risk Sınırları, Hedef Kârlar ve Broker Köprüsü",
        "risk_pct": "Hesap Risk Yüzdesi (%)",
        "leverage": "Kaldıraç Faktörü",
        "score_thresh": "Robot Giriş Skor Eşiği %",
        "broker_connect_title": "Bağlantılı Hesap Kurulumu (Gerçek/Demo)",
        "mt5_desc": "🔌 Forex Brokerine veya Prop-Firm hesap mücadelesine (FundedNext) bağlanın:",
        "prop_guard_title": "🛡️ Günlük Kayıp Limiti Koruyucusu (Avenix Prop Guard)",
        "prop_limit_desc": "İzin Verilen Maksimum Günlük Hesap Kaybı %",
        "prop_locked_err": "🚨 Günlük kayıp sınırı aşıldı!",
        "prop_unlock_btn": "🔓 Günlük Kayıp Kilidini Sıfırla",
        "prop_safe": "🟢 Günlük kayıp koruması aktif.",
        "tp_reward": "🎯 Takip Eden Kâr Oranları",
        "social_broadcast_title": "### Sosyal Platform Yayın Yönetimi",
        "social_broadcast_sub": "Robot analiz raporlarını yayınlayın",
        "tg_title": "1. Telegram Messenger API",
        "tg_enable": "Telegram Yayınını Etkinleştir",
        "tg_token": "Telegram Bot Token",
        "tg_chat": "Telegram Kanal Kimliği",
        "bale_title": "2. Bale Messenger API",
        "bale_enable": "Bale Yayınını Etkinleştir",
        "bale_token": "Bale Bot Token",
        "bale_chat": "Bale Sohbet Kimliği",
        "wa_title": "3. WhatsApp API Ağ Geçidi",
        "wa_enable": "WhatsApp Yayınını Etkinleştir",
        "wa_inst": "WhatsApp Instance ID",
        "wa_token": "WhatsApp Token",
        "wa_phone": "Hedef Telefon Numarası",
        "symbols_under_watch": "İzlenen Semboller",
        "main_tf_scan": "Ana Tarama Zaman Dilimi",
        "reset_wallet_btn": "🔄 Demo Cüzdanı Sıfırla",
        "save_settings_btn": "💾 Ayarları Kaydet ve Uygula",
        "manual_term_title": "🚀 Manuel İşlem Terminali",
        "manual_term_sub": "Manuel işlem gönderin.",
        "btn_buy": "🚀 Manuel SATIN AL (BUY)",
        "btn_sell": "🚨 Manuel SAT (SELL)",
        "btn_close_trade": "❌ Manuel Acil Kapat",
        "disclaimer_title": "⚠️ Yasal Uyarı ve Hizmet Şartları",
        "disclaimer_body": "Uluslararası finansal piyasalarda işlem yapmak yüksek risk taşır.",
        "sl_ratio": "İlk Durdurma Noktası Oranı %",
        "btn_accept_terms": "✅ Kullanım Şartlarını ve Yasal Uyarıyı kabul ediyorum",
        "locked_terms_desc": "🔒 Avenix grafiklerini ve komuta odasını açmak için lütfen önce Yasal Uyarıyı onaylayın:"
    }
}

t = TXT[lang_code]

with lang_col1:
    st.markdown(f"<h1 style='color: #3b82f6; font-size: 24px; font-weight: 700; margin-top: 5px;'>{t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748b; font-size: 13px;'>{t['sub']}</p>", unsafe_allow_html=True)

# Initialize execution engine
executor = OrderExecutionEngine()

# ----------------- ⚠️ WELCOME LEGAL GATE (قفل پذیرش قوانین سلب مسئولیت) -----------------
if not st.session_state.terms_accepted:
    st.markdown(f"### {t['disclaimer_title']}")
    st.markdown(f"<p style='color: #f87171; font-weight: 500; font-size: 14px;'>{t['locked_terms_desc']}</p>", unsafe_allow_html=True)
    
    # Render full Legal Disclaimer in selected language
    st.markdown(f"""
    <div class='ios-card' style='border-right: 5px solid #ef4444; max-height: 380px; overflow-y: auto;'>
        <p class='disclaimer-text'>{t['disclaimer_body']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Checkbox to Accept Terms
    accept_checkbox = st.checkbox(t["btn_accept_terms"], value=False)
    
    if accept_checkbox:
        st.session_state.terms_accepted = True
        st.success("🎉 Welcome to Avenix!")
        time.sleep(1)
        st.rerun()

else:
    # ----------------- 🟢 LIVE FLOATING PNL HUD BANNER (نمایش لحظه‌ای سود و زیان کل بالای برنامه) -----------------
    active_trades = portfolio.get("active_trades", [])
    total_floating_pnl = 0.0
    total_pnl_percent = 0.0
    
    if len(active_trades) > 0:
        for trade in active_trades:
            total_floating_pnl += trade.get("pnl", 0.0)
            total_pnl_percent += trade.get("pnl_percent", 0.0)
            
        # Glowing HUD Banner
        hud_bg = "rgba(16, 185, 129, 0.15)" if total_floating_pnl >= 0 else "rgba(239, 68, 68, 0.15)"
        hud_border = "#10b981" if total_floating_pnl >= 0 else "#ef4444"
        hud_text_color = "#10b981" if total_floating_pnl >= 0 else "#ef4444"
        sign = "+" if total_floating_pnl >= 0 else ""
        
        hud_msg_fa = f"🟢 سود زنده در جریان کل معاملات: {sign}${total_floating_pnl:,.2f} ({sign}{total_pnl_percent:.2f}%)" if total_floating_pnl >= 0 else f"🔴 زیان زنده در جریان کل معاملات: ${total_floating_pnl:,.2f} ({total_pnl_percent:.2f}%)"
        hud_msg_en = f"🟢 LIVE FLOATING PROFIT: {sign}${total_floating_pnl:,.2f} ({sign}{total_pnl_percent:.2f}%)" if total_floating_pnl >= 0 else f"🔴 LIVE FLOATING LOSS: ${total_floating_pnl:,.2f} ({total_pnl_percent:.2f}%)"
        hud_display = hud_msg_fa if lang_code == "fa" else hud_msg_en
        
        st.markdown(f"""
        <div class='hud-banner' style='background-color: {hud_bg}; border: 1px solid {hud_border}; color: {hud_text_color};'>
            {hud_display}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Gray dormant HUD
        st.markdown(f"""
        <div class='hud-banner' style='background-color: rgba(148, 163, 184, 0.08); border: 1px solid #475569; color: #94a3b8;'>
            ⚪ { "هیچ معامله فعال تکنیکالی در جریان نیست" if lang_code == "fa" else "NO ACTIVE POSITION IN TARGETS" }
        </div>
        """, unsafe_allow_html=True)

    # ----------------- ACTIVE MAIN TABS (Renders only after Accept) -----------------
    # ----------------- TAB 1: TRADINGVIEW CHART -----------------
    with tab_chart_view:
        sel_col1, sel_col2 = st.columns([1, 1])
        with sel_col1:
            selected_symbol = st.selectbox(t["selector_symbol"], config.get("symbols", ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "BRENT/USD", "SOL/USDT"]), index=0, key="chart_sym")
        with sel_col2:
            selected_timeframe = st.selectbox(t["selector_tf"], ["1", "5", "15", "60", "240", "D"], index=2, key="chart_tf")

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

        # NATIVELY SUPPORT COUNTDOWN TIMER ON THE Y-AXIS (countdown: true)
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
            "countdown": true,  /* ENABLE NATIVE CANDLE COUNTDOWN TIMER */
            "container_id": "tradingview_chart"
          }}
          );
          </script>
        </div>
        """
        
        st.markdown(f"<p style='color: #94a3b8; font-size: 13px;'>{t['tv_caption']}</p>", unsafe_allow_html=True)
        components.html(tradingview_html, height=630)

    # ----------------- TAB 2: THE AI TRADING BRAIN ROOM -----------------
    with tab_brain_view:
        st.markdown(f"### {t['brain_telemetry']}")
        st.markdown(f"<p style='color: #94a3b8; font-size: 13px;'>{t['brain_sub']}</p>", unsafe_allow_html=True)
        
        col_cmd1, col_cmd2 = st.columns([3, 1])
        with col_cmd1:
            st.info(t["force_scan_desc"])
        with col_cmd2:
            if st.button(t["force_scan_btn"], use_container_width=True):
                with st.spinner("Analyzing..."):
                    bot_runner = RealTimeTradingBot()
                    bot_runner.run_one_cycle()
                    st.success("Analysis complete!")
                    st.rerun()

        col_intel, col_trades = st.columns([1, 1])
        
        with col_intel:
            st.markdown(f"#### {t['isolated_checklist']}")
            
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
                <div class='metric-title'>{t['brain_score_title']}</div>
                <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 8px;'>
                    <span style='font-size: 28px; font-weight: 700; color: {score_color};'>{score}٪</span>
                    <span style='font-size: 13px; color: #94a3b8;'>{t['score_threshold_desc']}: {config.get("brain_score_threshold", 70)}٪</span>
                </div>
                <div style='background-color: #334155; border-radius: 10px; height: 10px; width: 100%; margin-top: 10px;'>
                    <div style='background-color: {score_color}; border-radius: 10px; height: 10px; width: {score}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='ios-card'>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>{t['checklist_title']}</p>", unsafe_allow_html=True)
            for name, status in confirmations.items():
                st.markdown(f"""
                <div class='checklist-item'>
                    <span style='color: #cbd5e1;'>{name}</span>
                    <span style='font-weight: 500;'>{status}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_trades:
            st.markdown(f"#### {t['pnl_report']}")
            
            current_balance = portfolio.get("balance", 10000.0)
            st.markdown(f"""
            <div class='ios-card'>
                <div class='metric-title'>{t['balance_title']}</div>
                <div class='metric-value'>${current_balance:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            # Show active trades with Emergency Close buttons
            if len(active_trades) == 0:
                st.info(t["no_active_trades"])
            else:
                for trade in active_trades:
                    color_t = "#10b981" if trade["side"] == "BUY" else "#ef4444"
                    
                    st.markdown(f"""
                    <div class='ios-card'>
                        <div style='display: flex; justify-content: space-between;'>
                            <b>{trade['symbol']} ({trade['side']})</b>
                            <span style='color: {color_t}; font-weight: 700;'>{t['active_pnl']}: ${trade['pnl']} ({trade['pnl_percent']}%)</span>
                        </div>
                        <div style='margin-top: 10px; font-size: 13px; color: #cbd5e1; margin-bottom: 12px;'>
                            {t['entry_price']}: {trade['entry_price']} | {t['live_price']}: {trade['current_price']}<br>
                            {t['current_sl']}: <b style='color: #f87171;'>{trade['sl']}</b> | {t['targets']}: TP1: {trade['tp1']} | TP2: {trade['tp2']} | TP3: {trade['tp3']}<br>
                            {t['trailing_step']}: <b>{trade.get('highest_tp_reached', 0)}</b> of 3
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Manual emergency position close button!
                    if st.button(f"{t['btn_close_trade']} ({trade['symbol']})", key=f"close_{trade['id']}"):
                        with st.spinner("Closing..."):
                            closed_pos = executor.close_trade_manually(trade["id"], trade["current_price"])
                            if closed_pos:
                                st.success(f"Position Closed manually at {closed_pos['close_price']}!")
                                time.sleep(1)
                                st.rerun()

            if latest_sig:
                st.markdown(f"<p style='font-weight: 700; color: #f8fafc; margin-top: 15px;'>📄 Analysis Brochure:</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class='brochure-card'>
                    {latest_sig['reason']}
                </div>
                """, unsafe_allow_html=True)

    # ----------------- TAB 3: SIGNALS ROOM ARCHIVE & MANUAL TERMINAL -----------------
    with tab_signals_view:
        st.markdown(f"### {t['manual_term_title']}")
        st.markdown(f"<p style='color: #94a3b8; font-size: 13px;'>{t['manual_term_sub']}</p>", unsafe_allow_html=True)
        
        with st.expander("💼 " + t["manual_term_title"]):
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                m_sym = st.selectbox("نماد معامله", config.get("symbols", ["XAU/USD"]), key="m_sym")
                m_price = st.number_input("قیمت ورود فعلی بازار", value=2420.0, step=0.1, key="m_price")
            with m_col2:
                m_side = st.selectbox("جهت معامله", ["BUY", "SELL"], key="m_side")
                m_sl = st.number_input("حد ضرر (Stop Loss)", value=2410.0, step=0.1, key="m_sl")
            with m_col3:
                m_tp1 = st.number_input("حد سود اول (TP1)", value=2430.0, step=0.1, key="m_tp1")
                m_tp2 = st.number_input("حد سود دوم (TP2)", value=2440.0, step=0.1, key="m_tp2")
                m_tp3 = st.number_input("حد سود سوم (TP3)", value=2450.0, step=0.1, key="m_tp3")
                
            m_btn_label = t["btn_buy"] if m_side == "BUY" else t["btn_sell"]
            if st.button(m_btn_label, use_container_width=True):
                with st.spinner("Submitting Order..."):
                    res = executor.open_trade(m_sym, m_side, m_price, m_sl, m_tp1, m_tp2, m_tp3, "معامله دستی کاربر", is_manual=True)
                    if res.get("status") == "success":
                        st.success("Manual Position established successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(res.get("reason", "Order failed"))

        st.markdown("---")
        st.markdown(f"### {t['tab_signals']}")
        signals_list = load_signals()
        
        if len(signals_list) == 0:
            st.info("No signals found.")
        else:
            for sig in reversed(signals_list):
                side_badge = "🟢 BUY" if sig["side"] == "BUY" else "🔴 SELL"
                color_theme = "#10b981" if sig["side"] == "BUY" else "#ef4444"
                status_fa = "🟡 PENDING" if sig["status"] == "PENDING" else f"🔒 CLOSED ({sig['status']})"
                
                st.markdown(f"""
                <div class='ios-card' style='border-right: 5px solid {color_theme};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-size: 18px; font-weight: 700; color: #f8fafc;'>{sig['symbol']} (TF: {config.get('trading_timeframe','15m')})</span>
                        <span style='color: {color_theme}; font-weight: 700; font-size: 15px;'>{side_badge}</span>
                        <span style='font-size: 11px; color: #94a3b8; background-color: #334155; padding: 4px 8px; border-radius: 20px;'>{status_fa}</span>
                    </div>
                    <div style='margin-top: 15px; font-size: 13px; color: #cbd5e1; line-height: 1.6;'>
                        💵 {t['entry_price']}: <b>{sig['entry_price']}</b> | 🛡️ {t['original_sl']}: <b style='color: #f87171;'>{sig['sl']}</b><br>
                        🎯 {t['targets']}: TP1: <b>{sig.get('tp1','N/A')}</b> | TP2: <b>{sig.get('tp2','N/A')}</b> | TP3: <b>{sig.get('tp3','N/A')}</b>
                    </div>
                    <div class='brochure-card'>
                        {sig['reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ----------------- TAB 4: SYSTEM SETTINGS -----------------
    with tab_settings_view:
        st.markdown(f"### {t['settings_title']}")
        
        # Disclaimer box (Exactly as requested!)
        with st.expander(t["disclaimer_title"]):
            st.markdown(f"<p class='disclaimer-text'>{t['disclaimer_body']}</p>", unsafe_allow_html=True)
            
        # 1. Indicator settings (Organized in Clean Expanders - "تفکیک تنظیمات سیستم"!)
        st.markdown("---")
        with st.expander("🤖 ۱. تنظیمات پیشرفته هوش اندیکاتورها (MACD, Bollinger, RSI, EMAs)"):
            col_set_ma, col_set_ich = st.columns(2)
            with col_set_ma:
                st.markdown(f"<p style='font-weight: 700; color: #3b82f6;'>{t['emas_title']}</p>", unsafe_allow_html=True)
                ma_s = st.slider(t["fast_ema"], 5, 30, config.get("ma_short", 20))
                ma_m = st.slider(t["medium_ema"], 30, 100, config.get("ma_medium", 50))
                ma_l = st.slider(t["long_ema"], 100, 300, config.get("ma_long", 200))
            with col_set_ich:
                st.markdown(f"<p style='font-weight: 700; color: #a855f7;'>{t['ich_title']}</p>", unsafe_allow_html=True)
                ich_t = st.number_input(t["tenkan_val"], min_value=5, max_value=20, value=config.get("ichimoku_tenkan", 9))
                ich_k = st.number_input(t["kijun_val"], min_value=15, max_value=40, value=config.get("ichimoku_kijun", 26))
                ich_b = st.number_input(t["span_b_val"], min_value=40, max_value=80, value=config.get("ichimoku_senkou_b", 52))

            st.markdown("---")
            col_set_rsi, col_set_macd, col_set_bb = st.columns(3)
            with col_set_rsi:
                st.markdown(f"<p style='font-weight: 700; color: #f43f5e;'>{t['rsi_title']}</p>", unsafe_allow_html=True)
                rsi_per = st.number_input(t["rsi_period"], min_value=5, max_value=30, value=config.get("rsi_period", 14))
                rsi_os = st.slider(t["rsi_os"], 10, 40, config.get("rsi_oversold", 30))
                rsi_ob = st.slider(t["rsi_ob"], 60, 90, config.get("rsi_overbought", 70))
            with col_set_macd:
                st.markdown(f"<p style='font-weight: 700; color: #10b981;'>{t['macd_title']}</p>", unsafe_allow_html=True)
                macd_f = st.number_input(t["macd_fast"], min_value=5, max_value=25, value=config.get("macd_fast", 12))
                macd_s = st.number_input(t["macd_slow"], min_value=20, max_value=40, value=config.get("macd_slow", 26))
                macd_sig = st.number_input(t["macd_signal"], min_value=5, max_value=15, value=config.get("macd_signal", 9))
            with col_set_bb:
                st.markdown(f"<p style='font-weight: 700; color: #eab308;'>{t['bb_title']}</p>", unsafe_allow_html=True)
                bb_per = st.number_input(t["bb_period"], min_value=5, max_value=40, value=config.get("bb_period", 20))
                bb_std = st.number_input(t["bb_std"], min_value=1.0, max_value=4.0, value=config.get("bb_std_dev", 2.0), step=0.1)

        # 2. Risk & Broker
        with st.expander("🛡️ ۲. تنظیمات مدیریت سرمایه، ریسک و اهداف سود پله‌ای"):
            col_set_r1, col_set_r2 = st.columns(2)
            with col_set_r1:
                r_pct = st.slider(t["risk_pct"], 0.1, 5.0, float(config.get("risk_percentage", 1.0)), 0.1)
                lev = st.number_input(t["leverage"], min_value=1, max_value=125, value=config.get("default_leverage", 1))
                sl_rat = st.slider(t["sl_ratio"], 0.5, 5.0, float(config.get("sl_ratio", 1.5)), 0.1)
                score_thresh = st.slider(t["score_thresh"], 50, 95, config.get("brain_score_threshold", 70))
            with col_set_r2:
                st.markdown(f"🎯 **{t['tp_reward']}**")
                tp1_val = st.slider("TP1 R:R", 0.5, 2.0, float(config.get("tp1_ratio", 1.0)), 0.1)
                tp2_val = st.slider("TP2 R:R", 1.5, 4.0, float(config.get("tp2_ratio", 2.0)), 0.1)
                tp3_val = st.slider("TP3 R:R", 2.5, 6.0, float(config.get("tp3_ratio", 3.0)), 0.1)

        # 3. Connection Expanders
        with st.expander("🔌 ۳. اتصال صرافی کریپتو / بروکر فارکس و سپر امنیتی پروپ‌فرم"):
            broker_opt = st.selectbox(
                t["broker_connect_title"],
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
                st.info(t["mt5_desc"])
                m_acc = st.text_input("Account ID", value=m_acc)
                m_pwd = st.text_input("Password", type="password", value=m_pwd)
                m_srv = st.text_input("Broker Server", value=m_srv)
                
                # Prop firm drawdown lock settings
                st.markdown(f"<p style='font-weight: 700; color: #f87171;'>{t['prop_guard_title']}</p>", unsafe_allow_html=True)
                prop_dd = st.slider(t["prop_limit_desc"], 1.0, 10.0, float(config.get("prop_drawdown_limit", 4.0)), 0.1)
                
                if config.get("prop_drawdown_breached", False):
                    st.error(t["prop_locked_err"])
                    if st.button(t["prop_unlock_btn"]):
                        config["prop_drawdown_breached"] = False
                        save_config(config)
                        st.success("Unlocked!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.success(t["prop_safe"])
                    prop_dd_val = prop_dd
            else:
                prop_dd_val = config.get("prop_drawdown_limit", 4.0)
                
            if selected_b == "crypto":
                c_api = st.text_input("API Key صرافی", value=c_api)
                c_sec = st.text_input("Secret Key صرافی", type="password", value=c_sec)

        # 4. Social Broadcast Settings
        with st.expander("✉️ ۴. اتاق مدیریت انتشار سیگنال‌ها (Bale, Telegram, WhatsApp)"):
            col_tg, col_bale, col_wa = st.columns(3)
            with col_tg:
                st.markdown(f"<p style='font-weight: 700; color: #3b82f6;'>{t['tg_title']}</p>", unsafe_allow_html=True)
                tg_enabled = st.checkbox(t["tg_enable"], value=config.get("enable_telegram", False))
                tg_tok = st.text_input(t["tg_token"], value=config.get("telegram_bot_token", ""))
                tg_chat = st.text_input(t["tg_chat"], value=config.get("telegram_chat_id", ""))
            with col_bale:
                st.markdown(f"<p style='font-weight: 700; color: #10b981;'>{t['bale_title']}</p>", unsafe_allow_html=True)
                bale_enabled = st.checkbox(t["bale_enable"], value=config.get("enable_bale", False))
                bale_tok = st.text_input(t["bale_token"], value=config.get("bale_bot_token", ""))
                bale_chat = st.text_input(t["bale_chat"], value=config.get("bale_chat_id", ""))
            with col_wa:
                st.markdown(f"<p style='font-weight: 700; color: #eab308;'>{t['wa_title']}</p>", unsafe_allow_html=True)
                wa_enabled = st.checkbox(t["wa_enable"], value=config.get("enable_whatsapp", False))
                wa_inst = st.text_input(t["wa_inst"], value=config.get("whatsapp_instance_id", "instance99999"))
                wa_tok = st.text_input(t["wa_token"], value=config.get("whatsapp_token", ""))
                wa_phone = st.text_input(t["wa_phone"], value=config.get("whatsapp_phone", ""))

        with st.expander("📊 ۵. جفت‌ارزهای فعال تحت نظر و تایم‌فریم اسکن"):
            symbols_input = st.text_input(t["symbols_under_watch"], value=", ".join(config.get("symbols", ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "BRENT/USD", "SOL/USDT"])))
            symbols_list = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
            trading_tf_val = st.selectbox(t["main_tf_scan"], ["1m", "5m", "15m", "1h", "4h", "1d"], index=2)

        # Save button
        st.markdown("---")
        if st.button(t["save_settings_btn"], use_container_width=True):
            config["symbols"] = symbols_list
            config["trading_timeframe"] = trading_tf_val
            config["risk_percentage"] = r_pct
            config["default_leverage"] = lev
            config["sl_ratio"] = sl_rat
            config["tp1_ratio"] = tp1_val
            config["tp2_ratio"] = tp2_val
            config["tp3_ratio"] = tp3_val
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
            st.success("Settings Saved!")
            time.sleep(1)
            st.rerun()
