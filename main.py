from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from binance.client import Client
import uvicorn
import os

app = FastAPI(title="Multi-Strategy Binance Trading & Demo Bot")

class APIKeyCredentials(BaseModel):
    api_key: str
    api_secret: str
    testnet: bool = True

class BotConfig(BaseModel):
    trading_mode: str  # 'demo' or 'live'
    symbol: str
    strategy: str      # 'smc', 'silver_bullet', 'dca', 'grid', 'combo'
    amount: float
    lower_price: float = None
    upper_price: float = None
    grids: int = None

bot_state = {
    "is_running": False,
    "mode": "demo",
    "strategy": None,
    "symbol": None,
    "client": None,
    "demo_wallet": {
        "USDT": 10000.00,
        "positions": []
    }
}

# Direct Web Dashboard Serve
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html file not found!</h1>"

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

    mode_label = "DEMO (Paper Trading - Virtual $10,000)" if config.trading_mode == "demo" else "LIVE BINANCE"

    if config.strategy == "smc":
        msg = f"SMC Strategy (FVG/OB/Fib) active in [{mode_label}] on {config.symbol}"
    elif config.strategy == "silver_bullet":
        msg = f"ICT Silver Bullet Strategy active in [{mode_label}] on {config.symbol}"
    elif config.strategy == "dca":
        msg = f"DCA Bot started in [{mode_label}] for {config.symbol} with trade amount ${config.amount}"
    elif config.strategy == "grid":
        msg = f"Grid Bot setup in [{mode_label}] on {config.symbol} ({config.lower_price} - {config.upper_price})"
    elif config.strategy == "combo":
        msg = f"Combo Bot (Grid + DCA) active in [{mode_label}] on {config.symbol}"
    else:
        bot_state["is_running"] = False
        raise HTTPException(status_code=400, detail="Invalid Strategy Selected.")

    return {"status": "started", "message": msg, "active_config": config}

@app.post("/api/stop-bot")
def stop_bot():
    bot_state["is_running"] = False
    bot_state["strategy"] = None
    bot_state["symbol"] = None
    return {"status": "stopped", "message": "Bot execution halted safely."}

@app.get("/api/status")
def get_status():
    return {
        "is_running": bot_state["is_running"],
        "mode": bot_state["mode"],
        "strategy": bot_state["strategy"],
        "symbol": bot_state["symbol"],
        "demo_balance": bot_state["demo_wallet"]["USDT"]
    }
  
