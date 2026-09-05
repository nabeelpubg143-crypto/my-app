from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from binance.client import Client
import os

app = FastAPI(title="Binance Advanced Grid & Multi-Strategy Bot Engine")

class APIKeyCredentials(BaseModel):
    api_key: str
    api_secret: str
    testnet: bool = True

class BotConfig(BaseModel):
    trading_mode: str          # 'demo' or 'live'
    symbol: str                # 'BTCUSDT', 'ETHUSDT', 'PAXGUSDT'
    strategy: str              # 'grid', 'combo', 'smc', 'silver_bullet', 'dca'
    total_investment: float = 1000.0
    lower_price: float = 50000.0
    upper_price: float = 70000.0
    grids: int = 10

bot_state = {
    "is_running": False,
    "mode": "demo",
    "strategy": None,
    "symbol": None,
    "client": None,
    "active_orders": [],
    "position": {
        "entry_price": 0.0,
        "market_price": 0.0,
        "pnl": 0.0,
        "pnl_percent": 0.0
    }
}

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found!</h1>"

@app.post("/api/connect")
def connect_binance(creds: APIKeyCredentials):
    try:
        client = Client(creds.api_key, creds.api_secret, testnet=creds.testnet)
        bot_state["client"] = client
        return {"status": "success", "message": "Live Binance Account Connected!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Live Connection Failed: {str(e)}")

@app.post("/api/start-bot")
def start_bot(config: BotConfig):
    if config.trading_mode == "live" and not bot_state["client"]:
        raise HTTPException(status_code=400, detail="Live trading ke liye Binance API Keys connect karna zaroori hai.")

    bot_state["is_running"] = True
    bot_state["mode"] = config.trading_mode
    bot_state["strategy"] = config.strategy
    bot_state["symbol"] = config.symbol

    # Fake Market Calculation for Visualizing Position
    entry_p = (config.lower_price + config.upper_price) / 2
    market_p = entry_p * 1.015  # Simulated +1.5% price movement
    pnl_val = (config.total_investment * 0.015)
    
    bot_state["position"] = {
        "entry_price": entry_p,
        "market_price": market_p,
        "pnl": pnl_val,
        "pnl_percent": 1.5
    }

    # Grid Orders Calculation
    orders = []
    if config.strategy in ["grid", "combo"]:
        price_step = (config.upper_price - config.lower_price) / config.grids
        per_grid_amount = config.total_investment / config.grids
        
        for i in range(config.grids + 1):
            grid_price = config.lower_price + (i * price_step)
            order_type = "BUY" if grid_price < entry_p else "SELL"
            orders.append({
                "grid_num": i + 1,
                "type": order_type,
                "price": grid_price,
                "amount": per_grid_amount
            })
        
    bot_state["active_orders"] = orders

    return {
        "status": "started",
        "message": f"Bot Active on {config.symbol}",
        "config": config,
        "position": bot_state["position"],
        "grid_orders": orders
    }

@app.post("/api/stop-bot")
def stop_bot():
    bot_state["is_running"] = False
    bot_state["active_orders"] = []
    return {"status": "stopped", "message": "Bot Execution Halted Safely."}

@app.get("/api/status")
def get_status():
    return {
        "is_running": bot_state["is_running"],
        "mode": bot_state["mode"],
        "strategy": bot_state["strategy"],
        "symbol": bot_state["symbol"],
        "position": bot_state["position"],
        "active_orders": bot_state["active_orders"]
    }
    
