import random
from typing import Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Binance Style Pro Trading Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock State Storage
ACCOUNT_STATE = {
    "futures_balance": 10000.00,
    "spot_balance": 5000.00,
    "margin_ratio": 1.25,
    "unrealized_pnl": 42.50
}

ACTIVE_POSITIONS = [
    {
        "symbol": "BTCUSDT",
        "type": "Perpetual Long",
        "size": 0.15,
        "entry_price": 64800.00,
        "mark_price": 65120.50,
        "liq_price": 58200.00,
        "margin": 486.00,
        "leverage": "20x",
        "pnl": +48.075,
        "roe": 9.89
    }
]

ACTIVE_BOTS = [
    {
        "id": "BOT-1092",
        "type": "Spot Grid",
        "pair": "BTCUSDT",
        "investment": 1000.0,
        "status": "RUNNING",
        "total_profit": 24.50,
        "grids": "10/10",
        "lower_price": 60000,
        "upper_price": 70000
    }
]

BINANCE_PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY / SELL
    type: str  # LIMIT / MARKET
    quantity: float
    leverage: int
    price: Optional[float] = None

class BotLaunchRequest(BaseModel):
    bot_type: str  # Spot Grid, Custom Strategy (SMC/Silver Bullet)
    symbol: str
    investment: float
    leverage: Optional[int] = 1
    lower_price: Optional[float] = None
    upper_price: Optional[float] = None
    grids: Optional[int] = None

@app.get("/api/account")
def get_account():
    return ACCOUNT_STATE

@app.get("/api/pairs")
def get_pairs():
    return BINANCE_PAIRS

@app.get("/api/positions")
def get_positions():
    # Live Price Fluctuation Simulation
    for pos in ACTIVE_POSITIONS:
        delta = random.uniform(-15.0, 15.0)
        pos["mark_price"] = round(pos["mark_price"] + delta, 2)
        price_diff = pos["mark_price"] - pos["entry_price"]
        pos["pnl"] = round(price_diff * pos["size"], 2)
        pos["roe"] = round((pos["pnl"] / pos["margin"]) * 100, 2)
    return ACTIVE_POSITIONS

@app.get("/api/bots")
def get_bots():
    return ACTIVE_BOTS

@app.post("/api/order/place")
def place_order(order: OrderRequest):
    new_pos = {
        "symbol": order.symbol,
        "type": f"Perpetual {order.side}",
        "size": order.quantity,
        "entry_price": order.price if order.price else 65120.50,
        "mark_price": 65120.50,
        "liq_price": 55000.00,
        "margin": round((order.quantity * 65120.50) / order.leverage, 2),
        "leverage": f"{order.leverage}x",
        "pnl": 0.0,
        "roe": 0.0
    }
    ACTIVE_POSITIONS.append(new_pos)
    return {"status": "SUCCESS", "message": "Futures Order Executed", "data": new_pos}

@app.post("/api/bot/launch")
def launch_bot(bot_req: BotLaunchRequest):
    new_bot = {
        "id": f"BOT-{random.randint(1000, 9999)}",
        "type": bot_req.bot_type,
        "pair": bot_req.symbol,
        "investment": bot_req.investment,
        "status": "RUNNING",
        "total_profit": 0.0,
        "grids": f"{bot_req.grids}/{bot_req.grids}" if bot_req.grids else "N/A",
        "lower_price": bot_req.lower_price,
        "upper_price": bot_req.upper_price
    }
    ACTIVE_BOTS.append(new_bot)
    return {"status": "SUCCESS", "message": "Bot Initialized", "bot": new_bot}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Binance Pro Trading UI</title>
        <style>
            :root {
                --bg-dark: #12161c;
                --panel-bg: #1e2329;
                --text-gray: #848e9c;
                --text-white: #eaecef;
                --binance-yellow: #f0b90b;
                --green: #0ecb81;
                --red: #f6465d;
                --border-color: #2b313a;
            }
            body { margin:0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg-dark); color: var(--text-white); }
            header { background: var(--panel-bg); padding: 10px 16px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
            .logo { color: var(--binance-yellow); font-weight: bold; font-size: 18px; }
            .container { padding: 12px; }
            .tabs { display: flex; gap: 15px; border-bottom: 1px solid var(--border-color); margin-bottom: 12px; }
            .tab { padding: 8px 12px; cursor: pointer; color: var(--text-gray); font-weight: 600; }
            .tab.active { color: var(--binance-yellow); border-bottom: 2px solid var(--binance-yellow); }
            .panel { background: var(--panel-bg); border-radius: 4px; padding: 12px; margin-bottom: 12px; }
            .metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; }
            .metric-box { background: #2b313a; padding: 8px; border-radius: 4px; }
            .metric-title { font-size: 11px; color: var(--text-gray); }
            .metric-val { font-size: 14px; font-weight: bold; margin-top: 4px; }
            table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; }
            th { color: var(--text-gray); padding: 8px 4px; font-weight: normal; }
            td { padding: 10px 4px; border-top: 1px solid var(--border-color); }
            .green { color: var(--green); }
            .red { color: var(--red); }
            .btn-yellow { background: var(--binance-yellow); color: #000; font-weight: bold; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 8px; }
            input, select { width: 100%; background: #2b313a; border: 1px solid var(--border-color); color: #fff; padding: 8px; border-radius: 4px; box-sizing: border-box; margin-top: 4px; margin-bottom: 8px; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">BINANCE PRO DEMO</div>
            <div id="acc-bal" style="font-size: 12px; color: var(--binance-yellow);">Balance: $10,000.00</div>
        </header>
        <div class="container">
            <div class="metrics">
                <div class="metric-box">
                    <div class="metric-title">Futures Margin Ratio</div>
                    <div class="metric-val green" id="margin-ratio">1.25%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Unrealized PnL (USDT)</div>
                    <div class="metric-val green" id="total-pnl">+42.50</div>
                </div>
            </div>

            <div class="tabs">
                <div class="tab active" onclick="switchTab('positions')">Positions</div>
                <div class="tab" onclick="switchTab('bots')">Active Bots</div>
                <div class="tab" onclick="switchTab('trade')">Trade / Launch Bot</div>
            </div>

            <!-- POSITIONS TAB -->
            <div id="positions-view" class="panel">
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Size</th>
                            <th>Entry / Mark</th>
                            <th>PnL (ROE%)</th>
                        </tr>
                    </thead>
                    <tbody id="positions-table">
                        <!-- Loaded Dynamically -->
                    </tbody>
                </table>
            </div>

            <!-- BOTS TAB -->
            <div id="bots-view" class="panel" style="display:none;">
                <table>
                    <thead>
                        <tr>
                            <th>Bot ID / Type</th>
                            <th>Pair</th>
                            <th>Investment</th>
                            <th>Profit</th>
                        </tr>
                    </thead>
                    <tbody id="bots-table">
                        <!-- Loaded Dynamically -->
                    </tbody>
                </table>
            </div>

            <!-- TRADE / BOT LAUNCH TAB -->
            <div id="trade-view" class="panel" style="display:none;">
                <label>Select Strategy Engine</label>
                <select id="bot-type">
                    <option value="Futures Manual Order">Futures Manual Order (Leverage 1x-125x)</option>
                    <option value="Spot Grid">Spot Grid Bot (Auto Buy/Sell Range)</option>
                    <option value="SMC Confluence Bot">SMC Institutional Bot (FVG + OB + Fib)</option>
                    <option value="ICT Silver Bullet">ICT Silver Bullet Strategy Bot</option>
                </select>

                <label>Pair</label>
                <select id="pair-select">
                    <option value="BTCUSDT">BTCUSDT Perpetual</option>
                    <option value="ETHUSDT">ETHUSDT Perpetual</option>
                </select>

                <label>Investment Amount (USDT)</label>
                <input type="number" id="invest-amt" value="500">

                <label>Leverage (For Futures / Margin)</label>
                <input type="number" id="leverage-val" value="20" min="1" max="125">

                <button class="btn-yellow" onclick="submitBotOrder()">EXECUTE ORDER / LAUNCH BOT</button>
            </div>
        </div>

        <script>
            function switchTab(tabName) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.getElementById('positions-view').style.display = 'none';
                document.getElementById('bots-view').style.display = 'none';
                document.getElementById('trade-view').style.display = 'none';

                if (tabName === 'positions') {
                    document.querySelectorAll('.tab')[0].classList.add('active');
                    document.getElementById('positions-view').style.display = 'block';
                } else if (tabName === 'bots') {
                    document.querySelectorAll('.tab')[1].classList.add('active');
                    document.getElementById('bots-view').style.display = 'block';
                } else {
                    document.querySelectorAll('.tab')[2].classList.add('active');
                    document.getElementById('trade-view').style.display = 'block';
                }
            }

            async function fetchPositions() {
                try {
                    const res = await fetch('/api/positions');
                    const data = await res.json();
                    let html = '';
                    data.forEach(p => {
                        const pnlClass = p.pnl >= 0 ? 'green' : 'red';
                        html += `<tr>
                            <td><b>${p.symbol}</b><br><small style="color:var(--text-gray)">${p.type} ${p.leverage}</small></td>
                            <td>${p.size}</td>
                            <td>${p.entry_price}<br><small style="color:var(--text-gray)">${p.mark_price}</small></td>
                            <td class="${pnlClass}">${p.pnl} USDT<br><small>(${p.roe}%)</small></td>
                        </tr>`;
                    });
                    document.getElementById('positions-table').innerHTML = html;
                } catch (e) { console.error(e); }
            }

            async function fetchBots() {
                try {
                    const res = await fetch('/api/bots');
                    const data = await res.json();
                    let html = '';
                    data.forEach(b => {
                        html += `<tr>
                            <td><b>${b.id}</b><br><small style="color:var(--text-gray)">${b.type}</small></td>
                            <td>${b.pair}</td>
                            <td>$${b.investment}</td>
                            <td class="green">+$${b.total_profit}</td>
                        </tr>`;
                    });
                    document.getElementById('bots-table').innerHTML = html;
                } catch (e) { console.error(e); }
            }

            async function submitBotOrder() {
                const botType = document.getElementById('bot-type').value;
                const pair = document.getElementById('pair-select').value;
                const invest = parseFloat(document.getElementById('invest-amt').value);
                const lev = parseInt(document.getElementById('leverage-val').value);

                if (botType === 'Futures Manual Order') {
                    await fetch('/api/order/place', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            symbol: pair, side: 'LONG', type: 'MARKET', quantity: 0.1, leverage: lev
                        })
                    });
                    alert('Futures Position Opened Successfully!');
                    switchTab('positions');
                } else {
                    await fetch('/api/bot/launch', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            bot_type: botType, symbol: pair, investment: invest, leverage: lev, grids: 10
                        })
                    });
                    alert('Automated Strategy Bot Deployed Successfully!');
                    switchTab('bots');
                }
                fetchPositions();
                fetchBots();
            }

            // Real-time Update Loop
            setInterval(fetchPositions, 2000);
            setInterval(fetchBots, 5000);
            fetchPositions();
            fetchBots();
        </script>
    </body>
    </html>
    """
        
