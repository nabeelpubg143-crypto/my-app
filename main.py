import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random

app = FastAPI(title="Binance Enterprise AI Terminal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MARKET_DATA = {
    "BTCUSDT": {"price": 91250.00, "high": 92500.00, "low": 89800.00, "vol": "2.4B", "tv": "BINANCE:BTCUSDT"},
    "ETHUSDT": {"price": 3340.50, "high": 3410.00, "low": 3280.00, "vol": "1.1B", "tv": "BINANCE:ETHUSDT"},
    "SOLUSDT": {"price": 185.20, "high": 192.00, "low": 179.50, "vol": "850M", "tv": "BINANCE:SOLUSDT"},
    "BNBUSDT": {"price": 580.40, "high": 595.00, "low": 572.00, "vol": "420M", "tv": "BINANCE:BNBUSDT"},
    "XRPUSDT": {"price": 0.5820, "high": 0.6100, "low": 0.5650, "vol": "310M", "tv": "BINANCE:XRPUSDT"},
    "DOGEUSDT": {"price": 0.1240, "high": 0.1320, "low": 0.1180, "vol": "290M", "tv": "BINANCE:DOGEUSDT"},
    "ADAUSDT": {"price": 0.3850, "high": 0.4020, "low": 0.3710, "vol": "180M", "tv": "BINANCE:ADAUSDT"},
    "NEARUSDT": {"price": 4.85, "high": 5.10, "low": 4.60, "vol": "140M", "tv": "BINANCE:NEARUSDT"},
    "XAUUSDT": {"price": 2720.80, "high": 2740.00, "low": 2705.00, "vol": "950M", "tv": "OANDA:XAUUSD"}
}

active_positions = []
open_orders = []
order_history = []
active_bots = {}

class OrderRequest(BaseModel):
    symbol: str
    mode: str
    side: str
    order_type: str  # MARKET, LIMIT, STOP_MARKET
    price: Optional[float] = None
    stop_price: Optional[float] = None
    amount_usdt: float
    leverage: int = 1
    tp: Optional[float] = None
    sl: Optional[float] = None

class AIBotRequest(BaseModel):
    symbol: str
    bot_type: str
    grid_mode: str
    direction: str
    lower_price: Optional[float] = None
    upper_price: Optional[float] = None
    grid_count: Optional[int] = 10
    investment: float

@app.get("/api/market/{symbol}")
def get_market_data(symbol: str):
    data = MARKET_DATA.get(symbol, MARKET_DATA["BTCUSDT"])
    change = random.uniform(-0.05, 0.05) / 100.0
    data["price"] = round(data["price"] * (1 + change), 4 if data["price"] < 10 else 2)

    step = 0.001 if data["price"] < 10 else 1.5
    bids = [{"price": round(data["price"] - (i * step), 4 if data["price"] < 10 else 2), "qty": round(random.uniform(0.5, 10.0), 2)} for i in range(1, 8)]
    asks = [{"price": round(data["price"] + (i * step), 4 if data["price"] < 10 else 2), "qty": round(random.uniform(0.5, 10.0), 2)} for i in range(1, 8)]

    # Check and trigger STOP_MARKET / LIMIT conditional orders
    global open_orders, active_positions
    remaining_orders = []
    for ord in open_orders:
        if ord["symbol"] == symbol:
            triggered = False
            if ord["type"] == "LIMIT" and ((ord["side"] == "BUY" and data["price"] <= ord["price"]) or (ord["side"] == "SELL" and data["price"] >= ord["price"])):
                triggered = True
            elif ord["type"] == "STOP_MARKET" and ((ord["side"] == "BUY" and data["price"] >= ord["stop_price"]) or (ord["side"] == "SELL" and data["price"] <= ord["stop_price"])):
                triggered = True

            if triggered:
                exec_p = ord["price"] if ord["type"] == "LIMIT" else data["price"]
                pos = {
                    "id": ord["id"], "symbol": ord["symbol"], "mode": ord["mode"], "side": ord["side"],
                    "entry_price": exec_p, "amount_usdt": ord["amount"], "leverage": ord["leverage"],
                    "size": round((ord["amount"] * ord["leverage"]) / exec_p, 4),
                    "liq_price": round(exec_p * (1 - (0.9 / ord["leverage"])) if ord["side"] == "BUY" else exec_p * (1 + (0.9 / ord["leverage"])), 4 if exec_p < 10 else 2),
                    "tp": ord.get("tp"), "sl": ord.get("sl"), "status": "OPEN"
                }
                active_positions.append(pos)
                order_history.append({"id": ord["id"], "symbol": ord["symbol"], "type": f"{ord['mode']}_{ord['type']}_{ord['side']}", "price": exec_p, "amount": ord["amount"], "status": "FILLED"})
            else:
                remaining_orders.append(ord)
        else:
            remaining_orders.append(ord)
    open_orders = remaining_orders

    return {"symbol": symbol, "market": data, "orderbook": {"bids": bids, "asks": asks}}

@app.post("/api/order/execute")
def execute_order(req: OrderRequest):
    current_p = MARKET_DATA.get(req.symbol, {"price": 100.0})["price"]
    order_id = f"ORD-{random.randint(10000, 99999)}"

    if req.order_type == "MARKET":
        position = {
            "id": order_id, "symbol": req.symbol, "mode": req.mode, "side": req.side,
            "entry_price": current_p, "amount_usdt": req.amount_usdt, "leverage": req.leverage,
            "size": round((req.amount_usdt * req.leverage) / current_p, 4),
            "liq_price": round(current_p * (1 - (0.9 / req.leverage)) if req.side == "BUY" else current_p * (1 + (0.9 / req.leverage)), 4 if current_p < 10 else 2),
            "tp": req.tp, "sl": req.sl, "status": "OPEN"
        }
        active_positions.append(position)
        order_history.append({"id": order_id, "symbol": req.symbol, "type": f"{req.mode}_MARKET_{req.side}", "price": current_p, "amount": req.amount_usdt, "status": "FILLED"})
        return {"status": "SUCCESS", "data": position}
    else:
        pending = {
            "id": order_id, "symbol": req.symbol, "mode": req.mode, "side": req.side,
            "type": req.order_type, "price": req.price, "stop_price": req.stop_price,
            "amount": req.amount_usdt, "leverage": req.leverage, "tp": req.tp, "sl": req.sl, "status": "PENDING"
        }
        open_orders.append(pending)
        return {"status": "SUCCESS", "data": pending}

@app.post("/api/bot/launch")
def launch_bot(req: AIBotRequest):
    bot_id = f"AI-BOT-{random.randint(1000, 9999)}"
    bot_info = {
        "id": bot_id, "symbol": req.symbol, "type": req.bot_type, "grid_mode": req.grid_mode,
        "direction": req.direction, "investment": req.investment,
        "lower": req.lower_price, "upper": req.upper_price, "grids": req.grid_count,
        "pnl": round(random.uniform(3.5, 62.0), 2), "status": "ACTIVE_RUNNING"
    }
    active_bots[f"{req.symbol}_{bot_id}"] = bot_info
    return {"status": "SUCCESS", "bot": bot_info}

@app.post("/api/position/close/{pos_id}")
def close_pos(pos_id: str):
    global active_positions
    active_positions = [p for p in active_positions if p["id"] != pos_id]
    return {"status": "SUCCESS"}

@app.post("/api/order/cancel/{ord_id}")
def cancel_order(ord_id: str):
    global open_orders
    open_orders = [o for o in open_orders if o["id"] != ord_id]
    return {"status": "SUCCESS"}

@app.get("/api/dashboard/{symbol}")
def get_dashboard(symbol: str):
    mark_p = MARKET_DATA.get(symbol, {"price": 0.0})["price"]
    pos_out = []
    for p in active_positions:
        if p["symbol"] == symbol:
            pnl = (mark_p - p["entry_price"]) * p["size"] if p["side"] == "BUY" else (p["entry_price"] - mark_p) * p["size"]
            pnl_pct = (pnl / p["amount_usdt"]) * 100
            pos_out.append({**p, "mark_price": mark_p, "pnl": round(pnl, 2), "pnl_pct": round(pnl_pct, 2)})

    bot_list = [v for k, v in active_bots.items() if v["symbol"] == symbol]

    return {
        "symbol": symbol, "mark_price": mark_p, "positions": pos_out, "bots": bot_list,
        "open_orders": [o for o in open_orders if o["symbol"] == symbol],
        "history": [h for h in order_history if h["symbol"] == symbol]
    }

@app.get("/", response_class=HTMLResponse)
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
