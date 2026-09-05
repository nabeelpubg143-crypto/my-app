import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random

app = FastAPI(title="Binance Pro Trading Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Memory Data Store
MARKET_PRICES = {
    "BTCUSDT": 91250.00,
    "ETHUSDT": 3340.50,
    "XAUUSDT": 2720.80
}

# State for Manual Positions & Active Bots
active_positions = []
order_history = []
active_bots = {}

class PositionRequest(BaseModel):
    symbol: str
    side: str  # "BUY" or "SELL"
    order_type: str  # "MARKET" or "LIMIT"
    price: Optional[float] = None
    amount_usdt: float
    leverage: int = 10

class BotStartRequest(BaseModel):
    symbol: str
    strategy: str  # "Grid Trading", "Institutional Confluence (SMC)", "ICT Silver Bullet"
    lower_price: float
    upper_price: float
    grid_count: int
    investment: float

@app.get("/api/prices")
def get_prices():
    # Simulate slight market price movement like live Binance ticker
    for symbol in MARKET_PRICES:
        change = random.uniform(-0.15, 0.15) / 100.0
        MARKET_PRICES[symbol] = round(MARKET_PRICES[symbol] * (1 + change), 2)
    return MARKET_PRICES

@app.post("/api/position/open")
def open_position(req: PositionRequest):
    current_price = MARKET_PRICES.get(req.symbol, 1000.0)
    entry_price = req.price if req.order_type == "LIMIT" and req.price else current_price
    
    pos_id = f"POS-{random.randint(1000, 9999)}"
    position = {
        "id": pos_id,
        "symbol": req.symbol,
        "side": req.side,
        "type": req.order_type,
        "entry_price": entry_price,
        "amount_usdt": req.amount_usdt,
        "leverage": req.leverage,
        "size": round((req.amount_usdt * req.leverage) / entry_price, 4),
        "status": "OPEN" if req.order_type == "MARKET" else "PENDING_LIMIT"
    }
    active_positions.append(position)
    order_history.append({
        "id": pos_id,
        "symbol": req.symbol,
        "type": f"MANUAL_{req.side}_{req.order_type}",
        "price": entry_price,
        "amount": req.amount_usdt,
        "status": "EXECUTED" if req.order_type == "MARKET" else "OPEN"
    })
    return {"status": "SUCCESS", "position": position}

@app.post("/api/bot/start")
def start_bot(req: BotStartRequest):
    step = (req.upper_price - req.lower_price) / req.grid_count
    grids = []
    
    for i in range(req.grid_count + 1):
        grid_price = round(req.lower_price + (i * step), 2)
        current_p = MARKET_PRICES.get(req.symbol, grid_price)
        side = "BUY" if grid_price < current_p else "SELL"
        grids.append({
            "grid_num": i + 1,
            "price": grid_price,
            "side": side,
            "qty": round((req.investment / req.grid_count) / grid_price, 4),
            "status": "OPEN"
        })

    bot_info = {
        "symbol": req.symbol,
        "strategy": req.strategy,
        "lower_price": req.lower_price,
        "upper_price": req.upper_price,
        "grid_count": req.grid_count,
        "investment": req.investment,
        "avg_entry": round((req.lower_price + req.upper_price) / 2, 2),
        "grids": grids,
        "status": "RUNNING",
        "realized_pnl": 0.00
    }
    active_bots[req.symbol] = bot_info
    return {"status": "SUCCESS", "bot": bot_info}

@app.post("/api/bot/stop/{symbol}")
def stop_bot(symbol: str):
    if symbol in active_bots:
        active_bots[symbol]["status"] = "STOPPED"
        del active_bots[symbol]
        return {"status": "SUCCESS", "message": f"Bot for {symbol} stopped."}
    raise HTTPException(status_code=404, detail="Bot not found")

@app.get("/api/dashboard/summary/{symbol}")
def get_dashboard_summary(symbol: str):
    market_price = MARKET_PRICES.get(symbol, 0.0)
    bot = active_bots.get(symbol, None)
    
    # Calculate Live UnPnL for Manual Positions
    positions_summary = []
    for pos in active_positions:
        if pos["symbol"] == symbol and pos["status"] == "OPEN":
            if pos["side"] == "BUY":
                pnl = (market_price - pos["entry_price"]) * pos["size"]
            else:
                pnl = (pos["entry_price"] - market_price) * pos["size"]
            
            pnl_pct = (pnl / pos["amount_usdt"]) * 100
            positions_summary.append({
                **pos,
                "current_price": market_price,
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2)
            })

    # Bot Grid Updates
    bot_summary = None
    if bot:
        grid_pnl = 0.0
        for g in bot["grids"]:
            if g["side"] == "BUY" and market_price <= g["price"]:
                g["status"] = "FILLED"
            elif g["side"] == "SELL" and market_price >= g["price"]:
                g["status"] = "FILLED"
            
            if g["status"] == "FILLED":
                grid_pnl += random.uniform(0.5, 2.5) # Simulated Grid Arbitrage Profit

        bot_summary = {
            "symbol": bot["symbol"],
            "strategy": bot["strategy"],
            "status": bot["status"],
            "investment": bot["investment"],
            "avg_entry": bot["avg_entry"],
            "grid_count": bot["grid_count"],
            "realized_pnl": round(grid_pnl, 2),
            "grids": bot["grids"]
        }

    return {
        "symbol": symbol,
        "market_price": market_price,
        "active_positions": positions_summary,
        "bot": bot_summary,
        "history": [h for h in order_history if h["symbol"] == symbol]
    }

@app.get("/", response_class=HTMLResponse)
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
