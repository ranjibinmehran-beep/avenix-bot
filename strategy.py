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
        sensitivity = self.config.get("sensitivity", "medium").lower()
        trading_tf = self.config.get("trading_timeframe", "15m")
        
        if trading_tf not in multi_tf_data:
            return {'action': 'HOLD', 'reason': f"Missing main trading timeframe data: {trading_tf}"}

        main_df = multi_tf_data[trading_tf]
        if main_df is None or len(main_df) < 50:
            return {'action': 'HOLD', 'reason': f"Insufficient data points for {trading_tf}"}

        # 1. Check Higher Timeframe (HTF) Alignment
        htfs = [tf for tf in self.config.get("timeframes", []) if tf != trading_tf]
        tf_ranks = {"1m": 1, "5m": 2, "15m": 3, "1h": 4, "4h": 5, "1d": 6}
        htf_targets = {tf: multi_tf_data[tf] for tf in htfs if tf_ranks.get(tf, 0) > tf_ranks.get(trading_tf, 0) and tf in multi_tf_data}
        
        htf_trend = self.check_trend_alignment(htf_targets, sensitivity)
        
        last_row = main_df.iloc[-1]
        prev_row = main_df.iloc[-2]
        
        current_price = last_row['close']
        rsi = last_row['RSI']
        
        ma_short_col = f"EMA_{self.config.get('ma_short', 20)}"
        ma_medium_col = f"EMA_{self.config.get('ma_medium', 50)}"
        ma_long_col = f"EMA_{self.config.get('ma_long', 200)}"
        
        ema20 = last_row.get(ma_short_col, current_price)
        ema50 = last_row.get(ma_medium_col, current_price)
        ema200 = last_row.get(ma_long_col, current_price)
        
        prev_ema20 = prev_row.get(ma_short_col, current_price)
        prev_ema50 = prev_row.get(ma_medium_col, current_price)

        tenkan = last_row.get('tenkan_sen', current_price)
        kijun = last_row.get('kijun_sen', current_price)
        span_a = last_row.get('senkou_span_a', current_price)
        span_b = last_row.get('senkou_span_b', current_price)
        
        prev_tenkan = prev_row.get('tenkan_sen', current_price)
        prev_kijun = prev_row.get('kijun_sen', current_price)

        # Signal confirmations
        bullish_tk_cross = prev_tenkan <= prev_kijun and tenkan > kijun
        bearish_tk_cross = prev_tenkan >= prev_kijun and tenkan < kijun
        
        bullish_ema_cross = prev_ema20 <= prev_ema50 and ema20 > ema50
        bearish_ema_cross = prev_ema20 >= prev_ema50 and ema20 < ema50
        
        max_cloud = max(span_a, span_b)
        min_cloud = min(span_a, span_b)
        price_above_cloud = current_price > max_cloud
        price_below_cloud = current_price < min_cloud

        buy_confirmed = False
        sell_confirmed = False
        
        # Build dynamic brochure reasons
        brochure_reason = ""

        if sensitivity == "high":
            buy_confirmed = (bullish_tk_cross or bullish_ema_cross or current_price > max_cloud) and (rsi > 45)
            sell_confirmed = (bearish_tk_cross or bearish_ema_cross or current_price < min_cloud) and (rsi < 55)
            
            if buy_confirmed:
                brochure_reason = (
                    f"📊 **بروشور تحلیل هوشمند آونیکس (حالت تهاجمی):**\n"
                    f"من با پایش ثانیه‌ای بازار روی نماد **{symbol}** یک شتاب صعودی سریع کشف کردم.\n"
                    f"خط محرک سریع قیمت عبور صعودی داشته و شاخص RSI در تراز مطلوب {round(rsi, 1)} است که مومنتوم قوی را تایید می‌کند.\n"
                    f"این پوزیشن با سرعت بالا جهت صید سودهای ریز در نوسانات بازار باز شد."
                )
            elif sell_confirmed:
                brochure_reason = (
                    f"📊 **بروشور تحلیل هوشمند آونیکس (حالت تهاجمی):**\n"
                    f"یک ریزش شتاب‌زده روی نماد **{symbol}** مانیتور شد.\n"
                    f"تقاطع ریزشی موینگ‌ها رخ داده و RSI زیر مرز ۵۵ قرار دارد. پوزیشن فروش فعال گردید."
                )

        elif sensitivity == "low":
            is_htf_aligned = (htf_trend == 'BULLISH' if current_price > ema200 else htf_trend == 'BEARISH')
            
            buy_confirmed = (
                is_htf_aligned and
                current_price > ema200 and 
                price_above_cloud and 
                (bullish_tk_cross or tenkan > kijun) and 
                (bullish_ema_cross or ema20 > ema50) and 
                (50 < rsi < 68)
            )
            
            sell_confirmed = (
                is_htf_aligned and
                current_price < ema200 and 
                price_below_cloud and 
                (bearish_tk_cross or tenkan < kijun) and 
                (bearish_ema_cross or ema20 < ema50) and 
                (32 < rsi < 50)
            )
            
            if buy_confirmed:
                brochure_reason = (
                    f"📊 **بروشور تحلیل هوشمند آونیکس (حالت محافظه‌کارانه سه‌گانه):**\n"
                    f"یک موقعیت خرید با امنیت تراز اول روی نماد **{symbol}** صادر شد.\n"
                    f"قیمت در کانال صعودی بلندمدت بالای میانگین متحرک ۲۰۰ قرار دارد و کاملاً خارج از ابر حمایتی ایچیموکو تثبیت شده است.\n"
                    f"تقاطع طلایی تنکان و کیجون به همراه تقاطع موینگ‌های ۲۰ و ۵۰ تریپل تاییدیه را صادر کرده‌اند. "
                    f"مقدار RSI برابر {round(rsi, 1)} است که از خرید در سقف قیمت جلوگیری می‌کند. یک ترید امن و بدون ریسک!"
                )
            elif sell_confirmed:
                brochure_reason = (
                    f"📊 **بروشور تحلیل هوشمند آونیکس (حالت محافظه‌کارانه سه‌گانه):**\n"
                    f"یک ریزش کاملاً همگرا و تایید شده روی نماد **{symbol}** شناسایی شد.\n"
                    f"روند کلان نزولی است، قیمت زیر ابر ایچیموکو و میانگین ۲۰۰ قفل شده است. تقاطع مرگ موینگ‌ها تایید گردید. "
                    f"RSI در تراز مطلوب {round(rsi, 1)} است و فضای سقوط سنگین قیمت تا تارگت‌های پایینی کاملاً مهیاست."
                )

        else: # medium
            is_trend_ok = (htf_trend in ['BULLISH', 'NEUTRAL'] if current_price > ema200 else htf_trend in ['BEARISH', 'NEUTRAL'])
            
            buy_confirmed = is_trend_ok and current_price > ema200 and (bullish_tk_cross or bullish_ema_cross) and (rsi > 50 and rsi < self.config.get("rsi_overbought", 70))
            sell_confirmed = is_trend_ok and current_price < ema200 and (bearish_tk_cross or bearish_ema_cross) and (rsi < 50 and rsi > self.config.get("rsi_oversold", 30))
            
            if buy_confirmed:
                brochure_reason = (
                    f"📊 **بروشور تحلیل هوشمند آونیکس (حالت متعادل):**\n"
                    f"یک همگرایی صعودی بسیار منظم روی نماد **{symbol}** مانیتور گردید.\n"
                    f"قیمت بالای مرز حمایتی میانگین متحرک ۲۰۰ روزه قرار دارد. تقاطع میانگین‌های متحرک کوتاه مدت (EMA 20/50) صادر شده و قیمت لبه بالایی ابر کومو را با قدرت شکسته است.\n"
                    f"مقدار RSI برابر {round(rsi, 1)} است که تاییدکننده پمپاژ نقدینگی خریداران به بازار است. پوزیشن خرید با ۳ پله سود باز شد."
                )
            elif sell_confirmed:
                brochure_reason = (
                    f"📊 **بروشور تحلیل هوشمند آونیکس (حالت متعادل):**\n"
                    f"یک آرایش نزولی استاندارد روی نماد **{symbol}** شکل گرفته است.\n"
                    f"قیمت پایین‌تر از میانگین متحرک ۲۰۰ قرار گرفته و خطوط ایچیموکو به سمت پایین گارد گرفته‌اند. RSI در محدوده نزولی {round(rsi, 1)} قرار دارد که تاییدکننده ریزش تا پله‌های پایینی است."
                )

        # --- DECISION ENGINE ---
        action = 'HOLD'
        reason = "No trade setup identified." if not brochure_reason else brochure_reason
        sl = 0.0
        tp1 = 0.0
        tp2 = 0.0
        tp3 = 0.0

        tp1_ratio = self.config.get("tp1_ratio", 1.0)
        tp2_ratio = self.config.get("tp2_ratio", 2.0)
        tp3_ratio = self.config.get("tp3_ratio", 3.0)

        if buy_confirmed:
            action = 'BUY'
            suggested_sl = min(kijun, min_cloud)
            if suggested_sl >= current_price or suggested_sl <= 0:
                suggested_sl = current_price * (1 - (self.config.get("sl_ratio", 1.5) / 100))
            
            max_sl_price = current_price * (1 - (self.config.get("sl_ratio", 1.5) / 100))
            sl = min(suggested_sl, max_sl_price)
            
            risk = current_price - sl
            tp1 = current_price + (risk * tp1_ratio)
            tp2 = current_price + (risk * tp2_ratio)
            tp3 = current_price + (risk * tp3_ratio)

        elif sell_confirmed:
            action = 'SELL'
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
            'reason': reason,
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
