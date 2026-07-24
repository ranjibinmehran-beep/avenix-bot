import json
import os
import time
import requests

class SignalRoom:
    def __init__(self, config_path="config.json", signals_path="signal_room.json"):
        self.config_path = config_path
        self.signals_path = signals_path
        self.config = self.load_json(self.config_path)
        self.signals = self.load_signals()

    def load_json(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_signals(self):
        if not os.path.exists(self.signals_path):
            initial = []
            self.save_json(self.signals_path, initial)
            return initial
        return self.load_json(self.signals_path)

    def save_signals(self):
        self.save_json(self.signals_path, self.signals)

    def add_signal(self, symbol, side, entry_price, sl, tp1, tp2, tp3, reason, indicators):
        """
        Adds a new multi-target signal to the local database and transmits it to Telegram.
        """
        signal_id = int(time.time() * 1000)
        signal_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        new_signal = {
            "id": signal_id,
            "time": signal_time,
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "reason": reason,
            "indicators": indicators,
            "status": "PENDING"
        }
        
        self.signals.append(new_signal)
        self.save_signals()
        
        if self.config.get("enable_telegram", False):
            self.send_telegram_alert(new_signal)
            
        return new_signal

    def update_signal_status(self, symbol, status, close_price, pnl_percent):
        updated = False
        for sig in self.signals:
            if sig["symbol"] == symbol and sig["status"] == "PENDING":
                sig["status"] = status
                sig["close_price"] = close_price
                sig["pnl_percent"] = pnl_percent
                sig["close_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                updated = True
                
        if updated:
            self.save_signals()

    def send_telegram_alert(self, signal):
        token = self.config.get("telegram_bot_token")
        chat_id = self.config.get("telegram_chat_id")
        
        if not token or not chat_id or token == "YOUR_TELEGRAM_BOT_TOKEN":
            print("[Telegram] Skip: Missing Bot credentials in config.")
            return

        direction_emoji = "🟢 BUY (LONG) | خرید" if signal["side"] == "BUY" else "🔴 SELL (SHORT) | فروش"
        
        message = (
            f"🔔 *سیگنال جدید در اتاق معاملات (کاملاً هوشمند)* 🔔\n\n"
            f"📈 *نماد:* {signal['symbol']}\n"
            f"↕️ *جهت معامله:* {direction_emoji}\n"
            f"💵 *نقطه ورود:* {signal['entry_price']}\n"
            f"🛡️ *حد ضرر اولیه (SL):* {signal['sl']}\n\n"
            f"🎯 *اهداف حد سود (Take Profit Targets):*\n"
            f" ├ 🎯 هدف اول (TP1): {signal['tp1']}\n"
            f" ├ 🎯 هدف دوم (TP2): {signal['tp2']}\n"
            f" └ 🎯 هدف سوم (TP3): {signal['tp3']}\n\n"
            f"⚠️ *استراتژی حد ضرر شناور (Trailing Stop):*\n"
            f" └ با رسیدن قیمت به TP1 حد ضرر به نقطه ورود، با رسیدن به TP2 حد ضرر به TP1 و با رسیدن به TP3 حد ضرر به TP2 جابجا می‌شود.\n\n"
            f"🧠 *دلیل تحلیل مغز سیستم:* {signal['reason']}\n\n"
            f"📊 *اندیکاتورها:*\n"
            f" └ RSI: {signal['indicators'].get('rsi')}\n"
            f" └ EMA 20: {signal['indicators'].get('ema20')}\n"
            f" └ EMA 50: {signal['indicators'].get('ema50')}\n"
            f" └ EMA 200: {signal['indicators'].get('ema200')}\n"
            f" └ Ichimoku Tenkan: {signal['indicators'].get('tenkan')}\n"
            f" └ Ichimoku Kijun: {signal['indicators'].get('kijun')}\n\n"
            f"⏰ *زمان صدور:* {signal['time']}\n"
            f"🤖 _سیستم فعال و مدیریت خودکار ریسک فعال است_"
        )
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            r = requests.post(url, json=payload, timeout=5)
            if r.status_code == 200:
                print(f"[Telegram] Signal successfully posted for {signal['symbol']}.")
            else:
                print(f"[Telegram] Error: Received status code {r.status_code}. Response: {r.text}")
        except Exception as e:
            print(f"[Telegram] Failed to connect: {e}")
