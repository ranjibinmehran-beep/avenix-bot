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

    def add_signal(self, symbol, side, entry_price, sl, tp1, tp2, tp3, reason, indicators, brain_score=85, confirmations=None):
        """
        Adds a new multi-target signal to the local database and transmits it to multiple
        platforms: Telegram, Bale (Iranian), and WhatsApp.
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
            "brain_score": brain_score,
            "confirmations": confirmations or {},
            "status": "PENDING"
        }
        
        self.signals.append(new_signal)
        self.save_signals()
        
        # Dispatch to configured channels simultaneously!
        if self.config.get("enable_telegram", False):
            self.send_telegram_alert(new_signal)
            
        if self.config.get("enable_bale", False):
            self.send_bale_alert(new_signal)
            
        if self.config.get("enable_whatsapp", False):
            self.send_whatsapp_alert(new_signal)
            
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

    def generate_message_text(self, signal):
        """
        Generates a standard beautifully formatted Persian message for all broadcast channels.
        """
        direction_emoji = "🟢 BUY (LONG) | خرید صعودی" if signal["side"] == "BUY" else "🔴 SELL (SHORT) | فروش نزولی"
        
        message = (
            f"🔔 *سیگنال جدید از مغز معاملاتی آونیکس* 🔔\n\n"
            f"📈 *نماد معاملاتی:* {signal['symbol']}\n"
            f"↕️ *جهت معامله:* {direction_emoji}\n"
            f"💵 *نقطه ورود مناسب:* {signal['entry_price']}\n"
            f"🛡️ *حد ضرر اولیه (SL):* {signal['sl']}\n\n"
            f"🎯 *اهداف حد سود پله‌ای (Take Profits):*\n"
            f" ├ 🎯 پله اول (TP1): {signal['tp1']}\n"
            f" ├ 🎯 پله دوم (TP2): {signal['tp2']}\n"
            f" └ 🎯 پله سوم (TP3): {signal['tp3']}\n\n"
            f"⚠️ *مدیریت ریسک متحرک (Trailing Stop):*\n"
            f" └ با لمس هر پله حد سود، استاپ لاس به طور خودکار جهت قفل سود بالا کشیده می‌شود (سیستم فری‌ریسک فعال).\n\n"
            f"🧠 *گزارش بروشور تحلیل مغز ربات (Brain Score: {signal.get('brain_score', 80)}%):*\n"
            f"{signal['reason']}\n\n"
            f"⏰ *زمان صدور سیگنال:* {signal['time']}\n"
            f"🤖 _سیستم فعال و مدیریت خودکار ریسک برقرار است_"
        )
        return message

    def send_telegram_alert(self, signal):
        token = self.config.get("telegram_bot_token")
        chat_id = self.config.get("telegram_chat_id")
        
        if not token or not chat_id or token == "YOUR_TELEGRAM_BOT_TOKEN":
            print("[Telegram] Skip: Missing credentials.")
            return

        message = self.generate_message_text(signal)
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        
        try:
            r = requests.post(url, json=payload, timeout=5)
            if r.status_code == 200:
                print(f"[Telegram] Broadcast successful for {signal['symbol']}.")
        except Exception as e:
            print(f"[Telegram] Connection failed: {e}")

    def send_bale_alert(self, signal):
        """
        Sends formatted message to Bale messenger bot API (fully compatible with Telegram API schema!).
        """
        token = self.config.get("bale_bot_token")
        chat_id = self.config.get("bale_chat_id")
        
        if not token or not chat_id or token == "YOUR_BALE_BOT_TOKEN":
            print("[Bale] Skip: Missing credentials.")
            return

        # Bale bot API uses exactly the same payload structure as Telegram!
        message = self.generate_message_text(signal)
        url = f"https://tapi.bale.ai/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        
        try:
            r = requests.post(url, json=payload, timeout=5)
            if r.status_code == 200:
                print(f"[Bale] Broadcast successful for {signal['symbol']}.")
            else:
                print(f"[Bale] Error: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"[Bale] Connection failed: {e}")

    def send_whatsapp_alert(self, signal):
        """
        Sends formatted message to WhatsApp using a clean, universal HTTP API gateway (e.g., UltraMsg).
        """
        instance_id = self.config.get("whatsapp_instance_id")
        token = self.config.get("whatsapp_token")
        phone = self.config.get("whatsapp_phone")
        
        if not instance_id or not token or not phone or token == "YOUR_WHATSAPP_GATEWAY_TOKEN":
            print("[WhatsApp] Skip: Missing credentials.")
            return

        message = self.generate_message_text(signal)
        url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
        payload = {
            "token": token,
            "to": phone,
            "body": message
        }
        
        try:
            r = requests.post(url, data=payload, timeout=5)
            if r.status_code == 200:
                print(f"[WhatsApp] Broadcast successful to {phone} for {signal['symbol']}.")
            else:
                print(f"[WhatsApp] Error: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"[WhatsApp] Connection failed: {e}")
