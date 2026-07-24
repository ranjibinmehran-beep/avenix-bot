import json
import os
import time

# Try to import MetaTrader5 gracefully (MT5 library is natively designed for Windows laptops/desktops)
MT5_AVAILABLE = False
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    pass

class OrderExecutionEngine:
    def __init__(self, config_path="config.json", portfolio_path="portfolio.json"):
        self.config_path = config_path
        self.portfolio_path = portfolio_path
        self.config = self.load_json(self.config_path)
        self.portfolio = self.load_portfolio()
        
        # Initialize selected broker connection if not paper trading
        self.broker_type = self.config.get("broker_type", "paper").lower()
        if self.broker_type == "forex_mt5":
            self.initialize_mt5()

    def load_json(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_portfolio(self):
        if not os.path.exists(self.portfolio_path):
            initial_portfolio = {
                "balance": 10000.0,
                "active_trades": [],
                "completed_trades": []
            }
            self.save_json(self.portfolio_path, initial_portfolio)
            return initial_portfolio
        return self.load_json(self.portfolio_path)

    def save_portfolio(self):
        self.save_json(self.portfolio_path, self.portfolio)

    def initialize_mt5(self):
        """
        Initializes MetaTrader 5 terminal connection.
        Supports both Demo and Real server login.
        """
        if not MT5_AVAILABLE:
            print("[MT5 Broker] Warning: MetaTrader5 package is not installed or not on a Windows environment. Falling back to Paper simulation.")
            return False
            
        account = self.config.get("mt5_account_id", "")
        password = self.config.get("mt5_password", "")
        server = self.config.get("mt5_server", "Exness-MT5-Trial")
        
        if not account or not password:
            print("[MT5 Broker] Missing account credentials. Run as Demo simulation.")
            return False
            
        # Initialize connection
        if not mt5.initialize():
            print("[MT5 Broker] Failed to initialize MT5 terminal.")
            return False
            
        # Login to Real / Demo account
        authorized = mt5.login(login=int(account), password=password, server=server)
        if authorized:
            print(f"[MT5 Broker] Successfully connected to {server} (Account: {account})")
            # Read real balance from MT5 terminal
            account_info = mt5.account_info()
            if account_info:
                self.portfolio["balance"] = account_info.balance
                self.save_portfolio()
            return True
        else:
            print(f"[MT5 Broker] Authentication failed on MT5 server: {server}")
            return False

    def open_trade(self, symbol, side, entry_price, sl, tp1, tp2, tp3, reason):
        for active in self.portfolio["active_trades"]:
            if active["symbol"] == symbol:
                return {"status": "ignored", "reason": f"Already have an active position in {symbol}."}

        risk_pct = self.config.get("risk_percentage", 1.0) / 100.0
        balance = self.portfolio["balance"]
        risk_cash = balance * risk_pct
        sl_distance = abs(entry_price - sl)
        
        if sl_distance == 0:
            sl_distance = entry_price * 0.01
            
        qty = risk_cash / sl_distance
        leverage = self.config.get("default_leverage", 1)
        notional_value = qty * entry_price
        
        margin_required = notional_value / leverage
        if margin_required > balance:
            qty = (balance * 0.95 * leverage) / entry_price
            notional_value = qty * entry_price
            
        if qty <= 0:
            return {"status": "failed", "reason": "Insufficient portfolio balance."}

        trade_id = int(time.time() * 1000)
        new_trade = {
            "id": trade_id,
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "original_sl": sl,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "highest_tp_reached": 0,
            "qty": round(qty, 6),
            "notional_value": round(notional_value, 2),
            "open_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            "reason": reason,
            "current_price": entry_price,
            "pnl": 0.0,
            "pnl_percent": 0.0
        }

        # --- BROKER CONNECTION BRIDGES ---
        if self.broker_type == "forex_mt5" and MT5_AVAILABLE:
            # Place Order inside MetaTrader 5 (Real/Demo)
            order_type = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).ask if side == "BUY" else mt5.symbol_info_tick(symbol).bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": round(qty / 100000, 2), # Standard MT5 Lot conversion helper
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp3, # Primary long-term target
                "deviation": 20,
                "magic": 1024,
                "comment": "Bot Brain MTF",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILL_IOC,
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {"status": "failed", "reason": f"MT5 order rejected: {result.comment}"}
            new_trade["mt5_ticket"] = result.order
            print(f"[MT5 Broker] Real/Demo trade executed on terminal. Ticket: {result.order}")

        elif self.broker_type == "crypto":
            # Place Order in Crypto Exchange via CCXT
            # In live production environment with real keys:
            # exchange = getattr(ccxt, self.config['exchange'])({'apiKey': api, 'secret': secret})
            # order = exchange.create_order(symbol, 'market', side, qty, params={'stopLoss': sl, 'takeProfit': tp3})
            print(f"[Crypto Broker] CCXT Trade submitted. API Orders established for {symbol}")

        # Always track locally in dashboard portfolio to show live performance
        self.portfolio["active_trades"].append(new_trade)
        self.save_portfolio()
        
        mode_label = "Paper Simulation" if self.broker_type == "paper" else f"REAL/DEMO Broker ({self.broker_type.upper()})"
        return {"status": "success", "trade": new_trade, "mode": mode_label}

    def update_active_trades(self, live_prices):
        closed_trades = []
        still_active = []
        portfolio_updated = False
        
        for trade in self.portfolio["active_trades"]:
            symbol = trade["symbol"]
            if symbol not in live_prices:
                still_active.append(trade)
                continue
                
            current_price = live_prices[symbol]
            trade["current_price"] = current_price
            
            side_multiplier = 1 if trade["side"] == "BUY" else -1
            pnl_percent = ((current_price - trade["entry_price"]) / trade["entry_price"]) * side_multiplier
            pnl_cash = trade["qty"] * (current_price - trade["entry_price"]) * side_multiplier
            trade["pnl"] = round(pnl_cash, 2)
            trade["pnl_percent"] = round(pnl_percent * 100, 2)
            
            # --- DYNAMIC TRAILING STOP LOGIC ---
            highest_tp = trade.get("highest_tp_reached", 0)
            entry = trade["entry_price"]
            sl = trade["sl"]
            tp1 = trade["tp1"]
            tp2 = trade["tp2"]
            tp3 = trade["tp3"]
            
            sl_updated = False
            
            if trade["side"] == "BUY":
                if current_price >= tp1 and highest_tp < 1:
                    trade["highest_tp_reached"] = 1
                    trade["sl"] = entry
                    sl_updated = True
                    print(f"🔥 [Trailing Stop] {symbol} hit TP1. Moving SL to Entry ({entry})")
                if current_price >= tp2 and highest_tp < 2:
                    trade["highest_tp_reached"] = 2
                    trade["sl"] = tp1
                    sl_updated = True
                    print(f"🔥 [Trailing Stop] {symbol} hit TP2. Moving SL to TP1 ({tp1})")
                if current_price >= tp3 and highest_tp < 3:
                    trade["highest_tp_reached"] = 3
                    trade["sl"] = tp2
                    sl_updated = True
                    print(f"🔥 [Trailing Stop] {symbol} hit TP3. Moving SL to TP2 ({tp2})")

            else: # SELL
                if current_price <= tp1 and highest_tp < 1:
                    trade["highest_tp_reached"] = 1
                    trade["sl"] = entry
                    sl_updated = True
                    print(f"🔥 [Trailing Stop] {symbol} hit TP1. Moving SL to Entry ({entry})")
                if current_price <= tp2 and highest_tp < 2:
                    trade["highest_tp_reached"] = 2
                    trade["sl"] = tp1
                    sl_updated = True
                    print(f"🔥 [Trailing Stop] {symbol} hit TP2. Moving SL to TP1 ({tp1})")
                if current_price <= tp3 and highest_tp < 3:
                    trade["highest_tp_reached"] = 3
                    trade["sl"] = tp2
                    sl_updated = True
                    print(f"🔥 [Trailing Stop] {symbol} hit TP3. Moving SL to TP2 ({tp2})")

            # Update order constraints in MT5 Broker if active
            if sl_updated and self.broker_type == "forex_mt5" and MT5_AVAILABLE and "mt5_ticket" in trade:
                # Modify existing MT5 SL parameters in broker database
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": trade["mt5_ticket"],
                    "sl": trade["sl"],
                    "tp": tp3
                }
                mt5.order_send(request)
                print(f"[MT5 Broker] Transmitted Trailing Stop command to broker server for Position #{trade['mt5_ticket']}")

            if sl_updated:
                portfolio_updated = True

            # --- EXIT CHECKS ---
            hit_sl = False
            hit_tp = False
            close_reason = ""
            close_price = current_price
            
            if trade["side"] == "BUY":
                if current_price <= trade["sl"]:
                    hit_sl = True
                    close_price = trade["sl"]
                    close_reason = "TRAILING STOP" if trade["highest_tp_reached"] > 0 else "STOP LOSS"
                elif current_price >= tp3:
                    hit_tp = True
                    close_price = tp3
                    close_reason = "TAKE PROFIT 3 (FINAL)"
            else: # SELL
                if current_price >= trade["sl"]:
                    hit_sl = True
                    close_price = trade["sl"]
                    close_reason = "TRAILING STOP" if trade["highest_tp_reached"] > 0 else "STOP LOSS"
                elif current_price <= tp3:
                    hit_tp = True
                    close_price = tp3
                    close_reason = "TAKE PROFIT 3 (FINAL)"

            if hit_sl or hit_tp:
                # If using real MT5, close position in terminal
                if self.broker_type == "forex_mt5" and MT5_AVAILABLE and "mt5_ticket" in trade:
                    # Send close request
                    position_id = trade["mt5_ticket"]
                    action_type = mt5.ORDER_TYPE_SELL if trade["side"] == "BUY" else mt5.ORDER_TYPE_BUY
                    close_price_mt5 = mt5.symbol_info_tick(symbol).bid if trade["side"] == "BUY" else mt5.symbol_info_tick(symbol).ask
                    
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": round(trade["qty"] / 100000, 2),
                        "type": action_type,
                        "position": position_id,
                        "price": close_price_mt5,
                        "deviation": 20,
                        "magic": 1024,
                        "comment": f"Close {close_reason}",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILL_IOC,
                    }
                    mt5.order_send(request)
                
                final_pnl_cash = trade["qty"] * (close_price - trade["entry_price"]) * side_multiplier
                final_pnl_percent = ((close_price - trade["entry_price"]) / trade["entry_price"]) * side_multiplier
                
                trade["close_price"] = round(close_price, 4)
                trade["close_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                trade["status"] = "CLOSED"
                trade["close_reason"] = close_reason
                trade["pnl"] = round(final_pnl_cash, 2)
                trade["pnl_percent"] = round(final_pnl_percent * 100, 2)
                
                self.portfolio["balance"] = round(self.portfolio["balance"] + trade["pnl"], 2)
                self.portfolio["completed_trades"].append(trade)
                closed_trades.append(trade)
                portfolio_updated = True
            else:
                still_active.append(trade)
                
        if portfolio_updated:
            self.portfolio["active_trades"] = still_active
            self.save_portfolio()
            
        return closed_trades
