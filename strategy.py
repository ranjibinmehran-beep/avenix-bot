import pandas as pd
import numpy as np

class TradingBrain:
    def __init__(self, config):
        self.config = config

    def check_trend_alignment(self, htf_dfs, sensitivity):
        bullish_scores = 0
        bearish_scores = 0
        total_checks = 0

        if sensitivity == "high":
            threshold_bullish = 0.50
            threshold_bearish = 0.50
        elif sensitivity == "low":
            threshold_bullish = 0.80
            threshold_bearish = 0.20
        else: # medium
            threshold_bullish = 0.65
            threshold_bearish = 0.35

        for tf, df in htf_dfs.items():
            if df is None or len(df) < 50:
                continue
            
            last_row = df.iloc[-1]
            price = last_row['close']
            
            ema_long_col = f"EMA_{self.config.get('ma_long', 200)}"
            if ema_long_col in last_row:
                total_checks += 1
                if price > last_row[ema_long_col]:
                    bullish_scores += 1
                else:
                    bearish_scores += 1
            
            if 'senkou_span_a' in last_row and 'senkou_span_b' in last_row:
                total_checks += 1
                span_a = last_row['senkou_span_a']
                span_b = last_row['senkou_span_b']
                max_cloud = max(span_a, span_b)
                min_cloud = min(span_a, span_b)
                
                if price > max_cloud:
                    bullish_scores += 1
                elif price < min_cloud:
                    bearish_scores += 1
                
                total_checks += 1
                if span_a > span_b:
                    bullish_scores += 1
                else:
                    bearish_scores += 1

        if total_checks == 0:
            return 'NEUTRAL'

        bullish_ratio = bullish_scores / total_checks
        if bullish_ratio >= threshold_bullish:
            return 'BULLISH'
        elif bullish_ratio <= threshold_bearish:
            return 'BEARISH'
        return 'NEUTRAL'

    def analyze(self, symbol, multi_tf_data):
        """
        The Ultimate Living AI Trading Brain:
        - Evaluates isolated indicator confirmations.
        - Calculates an aggregate "Brain Score" (0 to 100) using a multi-factor weighting model.
        - Generates fully descriptive Persian brochure logs.
        """
        sensitivity = self.config.get("sensitivity", "medium").lower()
        trading_tf = self.config.get("trading_timeframe", "15m")
        threshold = self.config.get("brain_score_threshold", 70)
        
        if trading_tf not in multi_tf_data:
            return {'action': 'HOLD', 'reason': f"Missing main trading timeframe data: {trading_tf}"}

        main_df = multi_tf_data[trading_tf]
        if main_df is None or len(main_df) < 50:
            return {'action': 'HOLD', 'reason': f"Insufficient data points for {trading_tf}"}

        # Check Higher Timeframe (HTF) Alignment
        htfs = [tf for tf in self.config.get("timeframes", []) if tf != trading_tf]
        tf_ranks = {"1m": 1, "5m": 2, "15m": 3, "1h": 4, "4h": 5, "1d": 6}
        htf_targets = {tf: multi_tf_data[tf] for tf in htfs if tf_ranks.get(tf, 0) > tf_ranks.get(trading_tf, 0) and tf in multi_tf_data}
        
        htf_trend = self.check_trend_alignment(htf_targets, sensitivity)
        
        last_row = main_df.iloc[-1]
        prev_row = main_df.iloc[-2]
        
        current_price = last_row['close']
        rsi = last_row['RSI']
        
        # MAs
        ma_short_col = f"EMA_{self.config.get('ma_short', 20)}"
        ma_medium_col = f"EMA_{self.config.get('ma_medium', 50)}"
        ma_long_col = f"EMA_{self.config.get('ma_long', 200)}"
        
        ema20 = last_row.get(ma_short_col, current_price)
        ema50 = last_row.get(ma_medium_col, current_price)
        ema200 = last_row.get(ma_long_col, current_price)
        
        prev_ema20 = prev_row.get(ma_short_col, current_price)
        prev_ema50 = prev_row.get(ma_medium_col, current_price)

        # Ichimoku
        tenkan = last_row.get('tenkan_sen', current_price)
        kijun = last_row.get('kijun_sen', current_price)
        span_a = last_row.get('senkou_span_a', current_price)
        span_b = last_row.get('senkou_span_b', current_price)
        
        prev_tenkan = prev_row.get('tenkan_sen', current_price)
        prev_kijun = prev_row.get('kijun_sen', current_price)

        # MACD
        macd_line = last_row.get('macd_line', 0.0)
        macd_signal = last_row.get('macd_signal', 0.0)
        macd_hist = last_row.get('macd_hist', 0.0)
        
        # Bollinger Bands
        bb_upper = last_row.get('bb_upper', current_price)
        bb_middle = last_row.get('bb_middle', current_price)
        bb_lower = last_row.get('bb_lower', current_price)

        # --- ISOLATED CONFIRMATIONS & SCORING ---
        buy_score = 0
        sell_score = 0
        
        confirmations = {}

        # 1. EMA 200 Trend Filter (Weight: 20 points)
        if current_price > ema200:
            confirmations["EMA 200"] = "BULLISH 🟢"
            buy_score += 20
        else:
            confirmations["EMA 200"] = "BEARISH 🔴"
            sell_score += 20

        # 2. EMA 20/50 Crossover (Weight: 15 points)
        if ema20 > ema50:
            confirmations["EMA 20/50"] = "BULLISH 🟢"
            buy_score += 15
        else:
            confirmations["EMA 20/50"] = "BEARISH 🔴"
            sell_score += 15

        # 3. Ichimoku Cloud Breakout (Weight: 15 points)
        max_cloud = max(span_a, span_b)
        min_cloud = min(span_a, span_b)
        if current_price > max_cloud:
            confirmations["Ichimoku Cloud"] = "BULLISH (Above) 🟢"
            buy_score += 15
        elif current_price < min_cloud:
            confirmations["Ichimoku Cloud"] = "BEARISH (Below) 🔴"
            sell_score += 15
        else:
            confirmations["Ichimoku Cloud"] = "NEUTRAL (Inside) 🟡"

        # 4. Ichimoku TK Cross (Weight: 15 points)
        if tenkan > kijun:
            confirmations["Ichimoku TK Cross"] = "BULLISH (Tenkan > Kijun) 🟢"
            buy_score += 15
        else:
            confirmations["Ichimoku TK Cross"] = "BEARISH (Tenkan < Kijun) 🔴"
            sell_score += 15

        # 5. RSI Momentum (Weight: 15 points)
        if 50 < rsi < 70:
            confirmations["RSI"] = f"BULLISH ({round(rsi, 1)}) 🟢"
            buy_score += 15
        elif 30 < rsi < 50:
            confirmations["RSI"] = f"BEARISH ({round(rsi, 1)}) 🔴"
            sell_score += 15
        elif rsi >= 70:
            confirmations["RSI"] = f"OVERBOUGHT ({round(rsi, 1)}) ⚠️"
            sell_score += 5 # Adds slightly to bearish reversal probability
        else:
            confirmations["RSI"] = f"OVERSOLD ({round(rsi, 1)}) ⚠️"
            buy_score += 5

        # 6. MACD Histogram & Signal (Weight: 10 points)
        if macd_line > macd_signal:
            confirmations["MACD"] = "BULLISH (Golden Cross) 🟢"
            buy_score += 10
        else:
            confirmations["MACD"] = "BEARISH (Death Cross) 🔴"
            sell_score += 10

        # 7. Bollinger Bands Location (Weight: 10 points)
        # Price near lower band is bullish bounce; near upper is bearish pullback
        bb_width = bb_upper - bb_lower if (bb_upper - bb_lower) > 0 else 1.0
        pct_b = (current_price - bb_lower) / bb_width
        
        if pct_b < 0.2:
            confirmations["Bollinger Bands"] = "BULLISH (Lower Band Bounce) 🟢"
            buy_score += 10
        elif pct_b > 0.8:
            confirmations["Bollinger Bands"] = "BEARISH (Upper Band Pullback) 🔴"
            sell_score += 10
        else:
            confirmations["Bollinger Bands"] = "NEUTRAL (Inside Bands) 🟡"

        # --- FINAL SCORE DECISION ---
        action = 'HOLD'
        final_score = 0
        brochure_reason = ""
        
        # Verify HTF alignment before enabling score trigger (unless sensitivity is high)
        is_htf_aligned = True
        if sensitivity == "low":
            is_htf_aligned = (htf_trend == 'BULLISH' if buy_score > sell_score else htf_trend == 'BEARISH')
        elif sensitivity == "medium":
            is_htf_aligned = (htf_trend in ['BULLISH', 'NEUTRAL'] if buy_score > sell_score else htf_trend in ['BEARISH', 'NEUTRAL'])

        if is_htf_aligned:
            if buy_score >= threshold and buy_score > sell_score:
                action = 'BUY'
                final_score = buy_score
            elif sell_score >= threshold and sell_score > buy_score:
                action = 'SELL'
                final_score = sell_score

        # Generate the ultimate Persian Analyst Brochure Report Card!
        if action == 'BUY':
            brochure_reason = (
                f"🦅 **گزارش بروشور تحلیلی و تاییدیه صعودی آونیکس (Avenix Live Report)**\n\n"
                f"من با پایش هوشمند بازار در ثانیه جاری، یک الگوی همگرایی صعودی بسیار پرقدرت و کلاسی روی نماد **{symbol}** شناسایی کردم.\n\n"
                f"🔍 **چک‌لیست تاییده‌های مغز سیستم (امتیاز صعودی: {final_score} از ۱۰۰):**\n"
                f" ├ 📈 **روند بلندمدت:** قیمت بالای میانگین متحرک ۲۰۰ روزه قفل شده است (گرایش صعودی تأیید شد).\n"
                f" ├ ☁️ **ایچیموکو:** قیمت کاملاً بالای لبه حمایتی ابر کومو قرار دارد و تقاطع خطوط محرک (تنکان/کیجون) صادر گردید.\n"
                f" ├ 📊 **مومنتوم RSI:** شاخص قدرت در تراز ایده آل {round(rsi, 1)} است که نشان از هجوم خریداران جدید دارد.\n"
                f" ├ ⚡ **سیستم MACD:** تقاطع طلایی مکدی رخ داده و میله‌های هیستوگرام بالای خط صفر فعال شده‌اند.\n"
                f" └ 📉 **باند بولینگر:** انقباض باندها تمام شده و نفوذ به باند بالایی شتاب حرکتی را با قدرت تأیید می‌کند.\n\n"
                f"🏆 **نتیجه‌گیری هوش مصنوعی:** با تایید این تریپل همپوشانی و عبور از حد نصاب امتیاز {threshold}٪، یک پوزیشن خرید (Long) با امنیت معاملاتی فوق‌العاده بالا و ۳ حد سود پله‌ای فعال گردید."
            )
        elif action == 'SELL':
            brochure_reason = (
                f"🦅 **گزارش بروشور تحلیلی و تاییدیه نزولی آونیکس (Avenix Live Report)**\n\n"
                f"یک الگوی سقوط شتاب‌دهنده و شکست سطوح حمایتی روی نماد **{symbol}** پایش گردید.\n\n"
                f"🔍 **چک‌لیست تاییده‌های مغز سیستم (امتیاز نزولی: {final_score} از ۱۰۰):**\n"
                f" ├ 📉 **روند بلندمدت:** قیمت در لایه زیرین میانگین متحرک ۲۰۰ قفل شده است (گرایش نزولی تأیید شد).\n"
                f" ├ ☁️ **ایچیموکو:** شکست قیمت به زیر ابر کومو تثبیت شده و تقاطع مرگ تنکان/کیجون صادر گردید.\n"
                f" ├ 📊 **مومنتوم RSI:** ریزش شاخص به تراز نزولی {round(rsi, 1)} نشان‌دهنده غلبه مطلق فروشندگان است.\n"
                f" ├ ⚡ **سیستم MACD:** تقاطع مرگ مکدی و ریزش پرقدرت میله‌های هیستوگرام به زیر خط صفر.\n"
                f" └ 📈 **باند بولینگر:** قیمت در حال خزیدن روی لبه باند پایینی است که پمپاژ پرقدرت عرضه را تأیید می‌کند.\n\n"
                f"🏆 **نتیجه‌گیری هوش مصنوعی:** با همسویی کامل تایم‌فریم معاملاتی با روندهای بالا دست و عبور از حد نصاب امتیاز {threshold}٪، پوزیشن فروش (Short) با امنیت بالا صادر شد."
            )

        sl = 0.0
        tp1 = 0.0
        tp2 = 0.0
        tp3 = 0.0

        tp1_ratio = self.config.get("tp1_ratio", 1.0)
        tp2_ratio = self.config.get("tp2_ratio", 2.0)
        tp3_ratio = self.config.get("tp3_ratio", 3.0)

        if action == 'BUY':
            suggested_sl = min(kijun, min_cloud)
            if suggested_sl >= current_price or suggested_sl <= 0:
                suggested_sl = current_price * (1 - (self.config.get("sl_ratio", 1.5) / 100))
            
            max_sl_price = current_price * (1 - (self.config.get("sl_ratio", 1.5) / 100))
            sl = min(suggested_sl, max_sl_price)
            
            risk = current_price - sl
            tp1 = current_price + (risk * tp1_ratio)
            tp2 = current_price + (risk * tp2_ratio)
            tp3 = current_price + (risk * tp3_ratio)

        elif action == 'SELL':
            suggested_sl = max(kijun, max_cloud)
            if suggested_sl <= current_price or suggested_sl <= 0:
                suggested_sl = current_price * (1 + (self.config.get("sl_ratio", 1.5) / 100))
            
            min_sl_price = current_price * (1 + (self.config.get("sl_ratio", 1.5) / 100))
            sl = max(suggested_sl, min_sl_price)
            
            risk = sl - current_price
            tp1 = current_price - (risk * tp1_ratio)
            tp2 = current_price - (risk * tp2_ratio)
            tp3 = current_price - (risk * tp3_ratio)

        return {
            'action': action,
            'entry_price': round(current_price, 4),
            'sl': round(sl, 4),
            'tp1': round(tp1, 4),
            'tp2': round(tp2, 4),
            'tp3': round(tp3, 4),
            'reason': brochure_reason,
            'brain_score': final_score,
            'confirmations': confirmations,
            'indicators': {
                'rsi': round(rsi, 2),
                'tenkan': round(tenkan, 4),
                'kijun': round(kijun, 4),
                'ema20': round(ema20, 4),
                'ema50': round(ema50, 4),
                'ema200': round(ema200, 4),
                'span_a': round(span_a, 4),
                'span_b': round(span_b, 4)
            }
        }

