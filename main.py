import json
import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# Fallback endpoint to catch legacy front-end requests
@app.get("/api/market/{symbol}")
def fallback_market_api(symbol: str):
    return {"symbol": symbol, "price": 65120.50, "status": "active"}

# Full Binance Mobile App Style Web Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Binance Pro Mobile Trading App</title>
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        :root {
            --bg-dark: #181a20;
            --card-bg: #1e2329;
            --accent-yellow: #f0b90b;
            --text-main: #eaecef;
            --text-muted: #848e9c;
            --green: #0ecb81;
            --red: #f6465d;
            --border-color: #2b313a;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); padding-bottom: 70px; user-select: none; }

        /* Top Header */
        .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--card-bg); border-bottom: 1px solid var(--border-color); }
        .logo-title { color: var(--accent-yellow); font-weight: bold; font-size: 16px; }
        .balance-badge { background: #2b313a; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }

        /* Main Mode Switcher */
        .mode-tabs { display: flex; background: var(--card-bg); border-bottom: 1px solid var(--border-color); }
        .mode-btn { flex: 1; padding: 12px; text-align: center; font-size: 14px; font-weight: 600; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; }
        .mode-btn.active { color: var(--accent-yellow); border-bottom-color: var(--accent-yellow); }

        .container { padding: 12px; }

        /* Chart Section */
        .chart-box { background: var(--card-bg); border-radius: 8px; padding: 10px; margin-bottom: 12px; height: 260px; position: relative; border: 1px solid var(--border-color); }

        /* Bot Cards */
        .bot-card { background: var(--card-bg); border-radius: 8px; padding: 14px; margin-bottom: 10px; border: 1px solid var(--border-color); }
        .bot-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .bot-title { font-weight: bold; font-size: 14px; color: var(--accent-yellow); }
        .bot-type { font-size: 11px; background: #2b313a; padding: 2px 6px; border-radius: 4px; color: var(--text-muted); }

        .metric-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 12px; margin: 8px 0; }
        .metric-label { color: var(--text-muted); }
        .metric-val { text-align: right; font-weight: 600; }

        .btn-launch { width: 100%; padding: 8px; background: var(--accent-yellow); color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; margin-top: 6px; }

        /* Position / Active Cards */
        .pos-badge { font-size: 11px; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
        .bg-long { background: rgba(14, 203, 129, 0.2); color: var(--green); }
        .bg-short { background: rgba(246, 70, 93, 0.2); color: var(--red); }

        /* Bottom Navigation */
        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: var(--card-bg); display: flex; border-top: 1px solid var(--border-color); height: 55px; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 11px; color: var(--text-muted); cursor: pointer; }
        .nav-item.active { color: var(--accent-yellow); }
    </style>
</head>
<body>

    <div class="top-nav">
        <div class="logo-title">BINANCE PRO AI</div>
        <div class="balance-badge">Wallet: $10,000.00 USDT</div>
    </div>

    <!-- Main Navigation Bar -->
    <div class="mode-tabs">
        <div class="mode-btn active" onclick="switchMainTab('spot')">Spot Trade</div>
        <div class="mode-btn" onclick="switchMainTab('futures')">Futures Trade</div>
        <div class="mode-btn" onclick="switchMainTab('bots')">AI Trading Bots</div>
    </div>

    <div class="container">
        <!-- Live Market Chart -->
        <div class="chart-box">
            <div style="display:flex; justify-content:space-between; margin-bottom: 5px; font-size: 12px;">
                <span><b>BTC/USDT</b> <span style="color:var(--green)">$65,142.80 +2.45%</span></span>
                <span style="color: var(--text-muted);">1m Candlestick</span>
            </div>
            <div id="chart" style="width: 100%; height: 210px;"></div>
        </div>

        <!-- Section Content Container -->
        <div id="content-area"></div>
    </div>

    <script>
        // Interactive Candlestick Chart
        let chart, candlestickSeries;
        function initChart() {
            const chartElement = document.getElementById('chart');
            chart = LightweightCharts.createChart(chartElement, {
                layout: { backgroundColor: '#1e2329', textColor: '#848e9c' },
                grid: { vertLines: { color: '#2b313a' }, horzLines: { color: '#2b313a' } },
                timeScale: { timeVisible: true, secondsVisible: false }
            });
            candlestickSeries = chart.addCandlestickSeries({
                upColor: '#0ecb81', downColor: '#f6465d', borderVisible: false, wickUpColor: '#0ecb81', wickDownColor: '#f6465d'
            });

            let baseTime = Math.floor(Date.now() / 1000) - 3600 * 5;
            let data = [];
            let price = 64800;
            for (let i = 0; i < 60; i++) {
                let open = price + (Math.random() - 0.5) * 50;
                let high = open + Math.random() * 40;
                let low = open - Math.random() * 40;
                let close = (high + low) / 2;
                price = close;
                data.push({ time: baseTime + i * 60, open, high, low, close });
            }
            candlestickSeries.setData(data);
        }

        const botData = [
            { id: 1, name: "1. AI Spot Grid Strategy", type: "Spot Grid", desc: "Auto low-buy high-sell grid engine based on volatility." },
            { id: 2, name: "2. AI Futures Grid (Long/Short)", type: "Futures Grid", desc: "Leveraged grid execution with stop-loss protection." },
            { id: 3, name: "3. AI Smart Money (SMC) Bot", type: "Order Block", desc: "Identifies institutional Liquidity & Order Block entries." },
            { id: 4, name: "4. AI ICT Silver Bullet Bot", type: "Fair Value Gap", desc: "Executes micro-timeframe FVG imbalance trades." },
            { id: 5, name: "5. AI DCA Investment Bot", type: "Automated DCA", desc: "Time-weighted average price accumulation." },
            { id: 6, name: "6. AI Arbitrage Delta Neutral", type: "Arbitrage", desc: "Risk-free funding rate arbitrage between spot & futures." },
            { id: 7, name: "7. AI Infinity Grid Engine", type: "Bull Market Grid", desc: "Uncapped upside grid designed for long-term trends." },
            { id: 8, name: "8. AI Momentum Breakout Bot", type: "Trend Following", desc: "Captures high volume key support/resistance breaks." },
            { id: 9, name: "9. AI Rebalancing Index Bot", type: "Portfolio Balancer", desc: "Auto-adjusts crypto weights dynamically." },
            { id: 10, name: "10. AI Scalping High-Frequency", type: "Scalper (1m/5m)", desc: "Fast-execution micro trades targeting small spreads." }
        ];

        function switchMainTab(tab) {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            const area = document.getElementById('content-area');

            if (tab === 'spot') {
                area.innerHTML = `
                    <div class="bot-card">
                        <div class="bot-title">Spot Trade Engine</div>
                        <div class="metric-grid">
                            <span class="metric-label">Available Balance:</span><span class="metric-val">$10,000.00 USDT</span>
                            <span class="metric-label">Order Type:</span><span class="metric-val">Limit / Market</span>
                        </div>
                        <button class="btn-launch" onclick="alert('Spot Order Executed!')">Buy BTC (Spot)</button>
                    </div>`;
            } else if (tab === 'futures') {
                area.innerHTML = `
                    <div class="bot-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span class="bot-title">BTCUSDT Perpetual</span>
                            <span class="pos-badge bg-long">20x Leverage</span>
                        </div>
                        <div class="metric-grid" style="margin-top:10px;">
                            <span class="metric-label">Position Size:</span><span class="metric-val">0.150 BTC ($9,771.00)</span>
                            <span class="metric-label">Entry Price:</span><span class="metric-val">$64,800.00</span>
                            <span class="metric-label">Mark Price:</span><span class="metric-val">$65,142.80</span>
                            <span class="metric-label">Est. Liquidation Price:</span><span class="metric-val" style="color:var(--red);">$61,850.00</span>
                            <span class="metric-label">Margin Ratio:</span><span class="metric-val" style="color:var(--green);">1.25%</span>
                            <span class="metric-label">Unrealized PnL:</span><span class="metric-val" style="color:var(--green);">+$51.42 (+10.58%)</span>
                        </div>
                    </div>`;
            } else if (tab === 'bots') {
                let html = `
                    <div class="bot-card" style="border-color: var(--accent-yellow);">
                        <div class="bot-header">
                            <span class="bot-title">ACTIVE BOT: AI Futures Grid</span>
                            <span class="pos-badge bg-long">RUNNING</span>
                        </div>
                        <div class="metric-grid">
                            <span class="metric-label">Pair & Mode:</span><span class="metric-val">BTCUSDT Long 10x</span>
                            <span class="metric-label">Total Investment:</span><span class="metric-val">$1,200.00 USDT</span>
                            <span class="metric-label">Total Grids:</span><span class="metric-val">20 Grids</span>
                            <span class="metric-label">Filled / Pending Grids:</span><span class="metric-val" style="color:var(--green);">14 Filled / 6 Pending</span>
                            <span class="metric-label">Liquidation Price:</span><span class="metric-val" style="color:var(--red);">$58,200.00</span>
                            <span class="metric-label">Grid Arbitrage Profit:</span><span class="metric-val" style="color:var(--green);">+$84.20 (+7.01%)</span>
                        </div>
                    </div>
                    <h3 style="font-size: 14px; margin: 12px 0 8px 0; color:var(--accent-yellow);">Select & Launch AI Bot (10 Strategies)</h3>`;

                botData.forEach(bot => {
                    html += `
                        <div class="bot-card">
                            <div class="bot-header">
                                <span class="bot-title">${bot.name}</span>
                                <span class="bot-type">${bot.type}</span>
                            </div>
                            <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">${bot.desc}</p>
                            <button class="btn-launch" onclick="alert('Launching ${bot.name}...')">Configure & Launch AI Bot</button>
                        </div>`;
                });
                area.innerHTML = html;
            }
        }

        window.onload = function() {
            initChart();
            switchMainTab('spot');
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE
    
