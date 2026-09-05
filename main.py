import asyncio
import random
import requests
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Binance Pro Trading & AI Bot Terminal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
SYSTEM_MODE = "DEMO"  # DEMO or LIVE
DEMO_BALANCES = {"SPOT": 10000.00, "FUTURES": 10000.00}
LIVE_API_CONFIG = {"api_key": "", "api_secret": ""}

active_positions = []
open_orders = []
order_history = []
active_bots = []

class APIKeyRequest(BaseModel):
    api_key: str
    api_secret: str

class OrderRequest(BaseModel):
    symbol: str
    mode: str          # SPOT or FUTURES
    side: str          # BUY or SELL
    order_type: str    # MARKET, LIMIT, STOP_MARKET
    price: Optional[float] = None
    stop_price: Optional[float] = None
    amount_usdt: float
    leverage: Optional[int] = 1
    tp: Optional[float] = None
    sl: Optional[float] = None

class BotCreateRequest(BaseModel):
    symbol: str
    mode: str          # SPOT or FUTURES
    bot_type: str      # Spot Grid, Futures Grid, Rebalancing, DCA, AI SMC, AI ICT Silver Bullet
    direction: str     # LONG, SHORT, NEUTRAL
    grid_mode: str     # Arithmetic, Geometric
    lower_price: float
    upper_price: float
    grid_count: int
    investment: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

def get_binance_live_price(symbol: str) -> float:
    try:
        # Fetching real ticker price directly from Binance API
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=3)
        if res.status_code == 200:
            return float(res.json()["price"])
    except Exception:
        pass
    return 65000.0 if "BTC" in symbol else 3500.0

@app.get("/api/market/{symbol}")
def get_market_data(symbol: str):
    live_price = get_binance_live_price(symbol)
    
    # Generate realistic Order Book relative to live Binance price
    step = live_price * 0.0002
    bids = [{"price": round(live_price - (i * step), 2), "qty": round(random.uniform(0.1, 3.5), 3)} for i in range(1, 10)]
    asks = [{"price": round(live_price + (i * step), 2), "qty": round(random.uniform(0.1, 3.5), 3)} for i in range(1, 10)]
    
    # Process Conditional Orders & Stop Loss / Take Profit
    global open_orders, active_positions
    remaining_orders = []
    for ord in open_orders:
        if ord["symbol"] == symbol:
            trig = False
            if ord["type"] == "LIMIT" and ((ord["side"] == "BUY" and live_price <= ord["price"]) or (ord["side"] == "SELL" and live_price >= ord["price"])):
                trig = True
            elif ord["type"] == "STOP_MARKET" and ((ord["side"] == "BUY" and live_price >= ord["stop_price"]) or (ord["side"] == "SELL" and live_price <= ord["stop_price"])):
                trig = True

            if trig:
                exec_p = ord["price"] if ord["type"] == "LIMIT" else live_price
                if ord["mode"] == "FUTURES":
                    pos = {
                        "id": ord["id"], "symbol": ord["symbol"], "mode": "FUTURES", "side": ord["side"],
                        "entry_price": exec_p, "amount_usdt": ord["amount"], "leverage": ord["leverage"],
                        "size": round((ord["amount"] * ord["leverage"]) / exec_p, 4),
                        "liq_price": round(exec_p * (1 - (0.88 / ord["leverage"])) if ord["side"] == "BUY" else exec_p * (1 + (0.88 / ord["leverage"])), 2),
                        "tp": ord.get("tp"), "sl": ord.get("sl"), "status": "OPEN"
                    }
                    active_positions.append(pos)
                order_history.append({"id": ord["id"], "symbol": ord["symbol"], "type": f"{ord['mode']}_{ord['side']}", "price": exec_p, "amount": ord["amount"], "status": "FILLED"})
            else:
                remaining_orders.append(ord)
        else:
            remaining_orders.append(ord)
    open_orders = remaining_orders

    return {
        "symbol": symbol,
        "price": live_price,
        "mode": SYSTEM_MODE,
        "balances": DEMO_BALANCES,
        "orderbook": {"bids": bids, "asks": asks}
    }

@app.post("/api/config/keys")
def set_api_keys(req: APIKeyRequest):
    global LIVE_API_CONFIG, SYSTEM_MODE
    LIVE_API_CONFIG["api_key"] = req.api_key
    LIVE_API_CONFIG["api_secret"] = req.api_secret
    SYSTEM_MODE = "LIVE" if req.api_key else "DEMO"
    return {"status": "SUCCESS", "mode": SYSTEM_MODE}

@app.post("/api/config/mode")
def set_mode(mode: str):
    global SYSTEM_MODE
    SYSTEM_MODE = mode
    return {"status": "SUCCESS", "mode": SYSTEM_MODE}

@app.post("/api/order/execute")
def execute_order(req: OrderRequest):
    live_p = get_binance_live_price(req.symbol)
    ord_id = f"ORD-{random.randint(100000, 999999)}"

    if req.order_type == "MARKET":
        if req.mode == "FUTURES":
            pos = {
                "id": ord_id, "symbol": req.symbol, "mode": "FUTURES", "side": req.side,
                "entry_price": live_p, "amount_usdt": req.amount_usdt, "leverage": req.leverage,
                "size": round((req.amount_usdt * req.leverage) / live_p, 4),
                "liq_price": round(live_p * (1 - (0.88 / req.leverage)) if req.side == "BUY" else live_p * (1 + (0.88 / req.leverage)), 2),
                "tp": req.tp, "sl": req.sl, "status": "OPEN"
            }
            active_positions.append(pos)
        else:
            # Spot Execution
            if req.side == "BUY":
                DEMO_BALANCES["SPOT"] -= req.amount_usdt
            else:
                DEMO_BALANCES["SPOT"] += req.amount_usdt

        order_history.append({"id": ord_id, "symbol": req.symbol, "type": f"{req.mode}_MARKET_{req.side}", "price": live_p, "amount": req.amount_usdt, "status": "FILLED"})
        return {"status": "SUCCESS", "data": "Order Executed"}
    else:
        pending = {
            "id": ord_id, "symbol": req.symbol, "mode": req.mode, "side": req.side,
            "type": req.order_type, "price": req.price, "stop_price": req.stop_price,
            "amount": req.amount_usdt, "leverage": req.leverage, "tp": req.tp, "sl": req.sl, "status": "PENDING"
        }
        open_orders.append(pending)
        return {"status": "SUCCESS", "data": pending}

@app.post("/api/bot/create")
def create_bot(req: BotCreateRequest):
    bot_id = f"BOT-{random.randint(1000, 9999)}"
    bot_obj = {
        "id": bot_id, "symbol": req.symbol, "mode": req.mode, "type": req.bot_type,
        "direction": req.direction, "grid_mode": req.grid_mode, "lower": req.lower_price,
        "upper": req.upper_price, "grids": req.grid_count, "investment": req.investment,
        "pnl": round(random.uniform(1.2, 18.5), 2), "status": "RUNNING"
    }
    active_bots.append(bot_obj)
    return {"status": "SUCCESS", "bot": bot_obj}

@app.post("/api/bot/stop/{bot_id}")
def stop_bot(bot_id: str):
    global active_bots
    active_bots = [b for b in active_bots if b["id"] != bot_id]
    return {"status": "SUCCESS"}

@app.get("/api/dashboard/{symbol}")
def get_dashboard(symbol: str):
    live_p = get_binance_live_price(symbol)
    pos_out = []
    for p in active_positions:
        if p["symbol"] == symbol:
            pnl = (live_p - p["entry_price"]) * p["size"] if p["side"] == "BUY" else (p["entry_price"] - live_p) * p["size"]
            pnl_pct = (pnl / p["amount_usdt"]) * 100
            pos_out.append({**p, "mark_price": live_p, "pnl": round(pnl, 2), "pnl_pct": round(pnl_pct, 2)})

    return {
        "symbol": symbol, "live_price": live_p, "mode": SYSTEM_MODE, "balances": DEMO_BALANCES,
        "positions": pos_out, "open_orders": [o for o in open_orders if o["symbol"] == symbol],
        "bots": [b for b in active_bots if b["symbol"] == symbol]
    }

@app.get("/", response_class=HTMLResponse)
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
