import random
import time
from typing import Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Binance Futures Pro Multi-Bot Terminal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 100+ Top Binance Perpetual Futures Pairs
BINANCE_PAIRS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", 
    "LINKUSDT", "DOTUSDT", "SUIUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SHIBUSDT", "FETUSDT",
    "RENDERUSDT", "TIAUSDT", "INJUSDT", "ARBUSDT", "OPUSDT", "ORDIUSDT", "WIFUSDT", "BONKUSDT",
    "FLOKIUSDT", "NOTUSDT", "RUNEUSDT", "FTMUSDT", "SEIUSDT", "STXUSDT", "GALAUSDT", "LDOUSDT",
    "ICPUSDT", "NEARUSDT", "FILUSDT", "MATICUSDT", "ATOMUSDT", "ETCUSDT", "XLMUSDT", "BCHUSDT",
    "LTCUSDT", "UNIUSDT", "AAVEUSDT", "MKRUSDT", "CRVUSDT", "SNXUSDT", "DYDXUSDT", "BLURUSDT",
    "PENDLEUSDT", "ENSUSDT", "AGIXUSDT", "ARKMUSDT", "WLDUSDT", "JUPUSDT", "PYTHUSDT", "MEMEUSDT"
]

BOT_CATALOG = [
    {"id": "SMC_CONFLUENCE", "name": "1. SMC Institutional Confluence Bot", "type": "SMC / Price Action"},
    {"id": "ICT_SILVER_BULLET", "name": "2. ICT Silver Bullet Engine", "type": "ICT / Time-based"},
    {"id": "DYNAMIC_GRID", "name": "3. Dynamic Futures Grid Bot", "type": "Grid / Range"},
    {"id": "TRIANGULAR_ARBITRAGE", "name": "4. Triangular Arbitrage Bot", "type": "Arbitrage"},
    {"id": "AI_SENTIMENT", "name": "5. AI News & Sentiment Velocity Bot", "type": "AI / NLP"},
    {"id": "MEAN_REVERSION", "name": "6. Mean Reversion & Multi-Band Bot", "type": "Mean Reversion"},
    {"id": "TREND_EMBEDDED", "name": "7. Supertrend + EMA Cloud Follower", "type": "Trend Following"},
    {"id": "DCA_MARTINGALE", "name": "8. Volatility DCA / Martingale Bot", "type": "DCA / Martingale"},
    {"id": "ORDER_FLOW_SCALPER", "name": "9. Order Flow & Volume Profile Scalper", "type": "Scalping / Depth"},
    {"id": "AI_REINFORCEMENT", "name": "10. AI RL Regime-Switching Bot", "type": "Machine Learning"}
]

# State Storage
ACTIVE_BOTS = []
ACTIVE_POSITIONS = [
    {
        "id": "POS-001",
        "symbol": "BTCUSDT",
        "side": "SHORT",
        "margin_mode": "Cross",
        "leverage": 20,
        "size": 0.35,
        "entry_price": 64250.00,
        "mark_price": 65120.50,
        "margin": 1124.37,
        "pnl": -304.67,
        "roi": -27.09,
        "liq_price": 67100.00,
        "margin_ratio": 4.12
    },
    {
        "id": "POS-002",
        "symbol": "ETHUSDT",
        "side": "LONG",
        "margin_mode": "Isolated",
        "leverage": 10,
        "size": 4.5,
        "entry_price": 2410.00,
        "mark_price": 2485.30,
        "margin": 1084.50,
        "pnl": +338.85,
        "roi": +31.24,
        "liq_price": 2180.00,
        "margin_ratio": 2.85
    }
]

class CustomBotRequest(BaseModel):
    bot_type: str
    symbol: str
    investment: float
    leverage: int
    custom_params: Dict[str, str]

@app.get("/api/pairs")
def get_pairs():
    return BINANCE_PAIRS

@app.get("/api/futures/state/{symbol}")
def get_futures_state(symbol: str):
    # Dynamic Price Fluctuation Simulation for Real-time Binance feel
    for pos in ACTIVE_POSITIONS:
        delta = random.uniform(-0.002, 0.002)
        pos["mark_price"] = round(pos["mark_price"] * (1 + delta), 2)
        if pos["side"] == "LONG":
            pos["pnl"] = round((pos["mark_price"] - pos["entry_price"]) * pos["size"], 2)
        else:
            pos["pnl"] = round((pos["entry_price"] - pos["mark_price"]) * pos["size"], 2)
        pos["roi"] = round((pos["pnl"] / pos["margin"]) * 100, 2)

    total_pnl = sum(p["pnl"] for p in ACTIVE_POSITIONS)
    total_notional = sum(p["mark_price"] * p["size"] for p in ACTIVE_POSITIONS)

    return {
        "overview": {
            "current_pnl": round(total_pnl, 2),
            "total_notional": round(total_notional, 2),
            "wallet_balance": 10540.25
        },
        "positions": ACTIVE_POSITIONS
    }
@app.get("/api/market/{symbol}")
def get_market_data(symbol: str):
    # Missing endpoint fix for 404 error
    return get_futures_state(symbol)
@app.get("/api/bots/active")
def get_active_bots():
    return ACTIVE_BOTS

@app.post("/api/bots/create")
def create_custom_bot(req: CustomBotRequest):
    bot_id = f"BOT-{req.bot_type}-{random.randint(1000, 9999)}"
    new_bot = {
        "id": bot_id,
        "type": req.bot_type,
        "symbol": req.symbol,
        "investment": req.investment,
        "leverage": f"{req.leverage}x",
        "custom_params": req.custom_params,
        "pnl": round(random.uniform(-5.0, 15.0), 2),
        "status": "RUNNING",
        "created_at": time.strftime("%H:%M:%S")
    }
    ACTIVE_BOTS.append(new_bot)
    return {"status": "SUCCESS", "bot": new_bot}

@app.post("/api/futures/close-position/{pos_id}")
def close_position(pos_id: str):
    global ACTIVE_POSITIONS
    ACTIVE_POSITIONS = [p for p in ACTIVE_POSITIONS if p["id"] != pos_id]
    return {"status": "SUCCESS"}

@app.get("/", response_class=HTMLResponse)
def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
