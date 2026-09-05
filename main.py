from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Binance Mobile Pro</title>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <style>
        :root {
            --bg-dark: #121418;
            --card-bg: #1e2329;
            --accent-yellow: #f0b90b;
            --text-main: #eaecef;
            --text-muted: #848e9c;
            --green: #0ecb81;
            --red: #f6465d;
            --border-color: #2b313a;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); padding-bottom: 60px; user-select: none; }

        .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: var(--card-bg); border-bottom: 1px solid var(--border-color); }
        .logo-title { color: var(--accent-yellow); font-weight: 800; font-size: 15px; }
        .mode-badge { font-size: 10px; background: rgba(240, 185, 11, 0.15); color: var(--accent-yellow); padding: 3px 8px; border-radius: 10px; font-weight: bold; border: 1px solid rgba(240, 185, 11, 0.3); }
        .balance-badge { background: #2b313a; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; color: #fff; }

        .mode-tabs { display: flex; background: var(--card-bg); border-bottom: 1px solid var(--border-color); }
        .mode-btn { flex: 1; padding: 10px; text-align: center; font-size: 13px; font-weight: 700; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; }
        .mode-btn.active { color: var(--accent-yellow); border-bottom-color: var(--accent-yellow); }

        .container { padding: 10px; }
        .chart-box { background: var(--card-bg); border-radius: 8px; padding: 4px; margin-bottom: 10px; height: 260px; border: 1px solid var(--border-color); }
        #tv_chart_container { width: 100%; height: 100%; }

        .trade-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
        .panel-box { background: var(--card-bg); border-radius: 8px; padding: 10px; border: 1px solid var(--border-color); }

        .ob-header { display: flex; justify-content: space-between; font-size: 10px; color: var(--text-muted); margin-bottom: 4px; }
        .ob-row { display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; margin: 2px 0; }
        .ob-ask { color: var(--red); }
        .ob-bid { color: var(--green); }
        .ob-price-large { font-size: 13px; font-weight: bold; text-align: center; margin: 6px 0; color: var(--green); }

        .input-group { margin-bottom: 8px; }
        .input-group label { display: block; font-size: 10px; color: var(--text-muted); margin-bottom: 3px; }
        .input-field { width: 100%; background: #121418; border: 1px solid var(--border-color); border-radius: 4px; color: #fff; padding: 6px 8px; font-size: 11px; font-weight: 600; outline: none; }
        
        .leverage-btn { background: #2b313a; color: var(--accent-yellow); border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; cursor: pointer; }

        .btn-action { width: 100%; padding: 8px; border: none; border-radius: 6px; font-weight: bold; font-size: 12px; cursor: pointer; margin-top: 4px; color: #fff; }
        .btn-buy { background-color: var(--green); }
        .btn-sell { background-color: var(--red); }
        .btn-yellow { background-color: var(--accent-yellow); color: #000; }
        .btn-dual { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 6px; }

        .card { background: var(--card-bg); border-radius: 8px; padding: 12px; margin-bottom: 10px; border: 1px solid var(--border-color); }
        .metric-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; font-size: 11px; margin: 6px 0; }
        .metric-label { color: var(--text-muted); }
        .metric-val { text-align: right; font-weight: 600; }

        .badge { font-size: 10px; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
        .bg-long { background: rgba(14, 203, 129, 0.2); color: var(--green); }
    </style>
</head>
<body>

    <div class="top-nav">
        <div>
            <span class="logo-title">BINANCE PRO</span>
            <span class="mode-badge">DEMO MODE</span>
        </div>
        <div class="balance-badge">Wallet: $10,000.00 USDT</div>
    </div>

    <div class="mode-tabs">
        <div class="mode-btn active" onclick="switchMainTab('spot', event)">Spot</div>
        <div class="mode-btn" onclick="switchMainTab('futures', event)">Futures</div>
        <div class="mode-btn" onclick="switchMainTab('bots', event)">AI Bots (10)</div>
    </div>

    <div class="container">
        <div class="chart-box">
            <div id="tv_chart_container"></div>
        </div>
        <div id="content-area"></div>
    </div>

    <script>
        function loadTradingViewChart() {
            if(typeof TradingView !== "undefined") {
                new TradingView.widget({
                    "autosize": true,
                    "symbol": "BINANCE:BTCUSDT",
                    "interval": "1",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#1e2329",
                    "enable_publishing": false,
                    "hide_top_toolbar": false,
                    "container_id": "tv_chart_container"
                });
            }
        }

        const botData = [
            { id: 1, name: "1. AI Spot Grid Strategy", type: "Spot Grid", desc: "Auto low-buy high-sell grid engine." },
            { id: 2, name: "2. AI Futures Grid (Long/Short)", type: "Futures Grid", desc: "Leveraged grid execution with stop-loss." },
            { id: 3, name: "3. AI Smart Money (SMC) Bot", type: "Order Block", desc: "Identifies institutional Order Block entries." },
            { id: 4, name: "4. AI ICT Silver Bullet Bot", type: "Fair Value Gap", desc: "Executes micro-timeframe FVG trades." },
            { id: 5, name: "5. AI DCA Investment Bot", type: "Automated DCA", desc: "Time-weighted average price accumulation." },
            { id: 6, name: "6. AI Arbitrage Delta Neutral", type: "Arbitrage", desc: "Risk-free funding rate arbitrage." },
            { id: 7, name: "7. AI Infinity Grid Engine", type: "Bull Grid", desc: "Uncapped upside grid designed for trends." },
            { id: 8, name: "8. AI Momentum Breakout Bot", type: "Trend Follow", desc: "Captures high volume key level breaks." },
            { id: 9, name: "9. AI Rebalancing Index Bot", type: "Balancer", desc: "Auto-adjusts crypto weights dynamically." },
            { id: 10, name: "10. AI Scalping High-Frequency", type: "Scalper 1m", desc: "Fast micro trades targeting small spreads." }
        ];

        function switchMainTab(tab, evt) {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            if(evt) evt.target.classList.add('active');
            const area = document.getElementById('content-area');

            if (tab === 'spot') {
                area.innerHTML = `
                    <div class="trade-grid">
                        <div class="panel-box">
                            <div class="ob-header"><span>Price</span><span>Qty</span></div>
                            <div id="asks-list">
                                <div class="ob-row ob-ask"><span>65,150.0</span><span>0.412</span></div>
                                <div class="ob-row ob-ask"><span>65,148.5</span><span>1.205</span></div>
                            </div>
                            <div class="ob-price-large">$65,142.80</div>
                            <div id="bids-list">
                                <div class="ob-row ob-bid"><span>65,140.0</span><span>0.850</span></div>
                                <div class="ob-row ob-bid"><span>65,138.2</span><span>2.110</span></div>
                            </div>
                        </div>

                        <div class="panel-box">
                            <div class="input-group">
                                <label>Price (USDT)</label>
                                <input type="text" class="input-field" value="65142.80">
                            </div>
                            <div class="input-group">
                                <label>Amount (BTC)</label>
                                <input type="text" class="input-field" placeholder="0.00">
                            </div>
                            <button class="btn-action btn-buy" onclick="alert('Spot Buy Placed!')">Buy BTC</button>
                            <button class="btn-action btn-sell" onclick="alert('Spot Sell Placed!')">Sell BTC</button>
                        </div>
                    </div>`;
            } else if (tab === 'futures') {
                area.innerHTML = `
                    <div class="trade-grid">
                        <div class="panel-box">
                            <div class="ob-header"><span>Price</span><span>Qty</span></div>
                            <div class="ob-row ob-ask"><span>65,152.0</span><span>0.810</span></div>
                            <div class="ob-price-large">$65,142.80</div>
                            <div class="ob-row ob-bid"><span>65,141.0</span><span>1.120</span></div>
                        </div>

                        <div class="panel-box">
                            <div style="display:flex; justify-content:space-between; margin-bottom: 6px;">
                                <button class="leverage-btn">Cross</button>
                                <button class="leverage-btn">20x ✎</button>
                            </div>
                            <div class="input-group">
                                <label>Margin (USDT)</label>
                                <input type="text" class="input-field" placeholder="100.00">
                            </div>
                            <div class="btn-dual">
                                <button class="btn-action btn-buy" onclick="alert('Long Position Opened!')">Long</button>
                                <button class="btn-action btn-sell" onclick="alert('Short Position Opened!')">Short</button>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-weight:bold; font-size:12px;">BTCUSDT Perp</span>
                            <span class="badge bg-long">LONG 20x</span>
                        </div>
                        <div class="metric-grid">
                            <span class="metric-label">Entry Price:</span><span class="metric-val">$64,800.00</span>
                            <span class="metric-label">Mark Price:</span><span class="metric-val">$65,142.80</span>
                            <span class="metric-label">Est. Liq Price:</span><span class="metric-val" style="color:var(--red);">$61,850.00</span>
                            <span class="metric-label">PnL (ROE%):</span><span class="metric-val" style="color:var(--green);">+$51.42 (+10.58%)</span>
                        </div>
                    </div>`;
            } else if (tab === 'bots') {
                let html = `
                    <div class="card" style="border-color: var(--accent-yellow);">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span style="font-weight:bold; color:var(--accent-yellow); font-size:12px;">ACTIVE: AI Futures Grid</span>
                            <span class="badge bg-long">RUNNING</span>
                        </div>
                        <div class="metric-grid">
                            <span class="metric-label">Grids Status:</span><span class="metric-val" style="color:var(--green);">14 Filled / 6 Pending</span>
                            <span class="metric-label">Liq Price:</span><span class="metric-val" style="color:var(--red);">$58,200.00</span>
                            <span class="metric-label">Grid Profit:</span><span class="metric-val" style="color:var(--green);">+$84.20 (+7.01%)</span>
                        </div>
                    </div>`;

                botData.forEach(bot => {
                    html += `
                        <div class="card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                <span style="font-weight:bold; font-size:12px; color:var(--accent-yellow);">${bot.name}</span>
                                <span class="badge" style="background:#2b313a; color:var(--text-muted);">${bot.type}</span>
                            </div>
                            <p style="font-size: 11px; color: var(--text-muted); margin-bottom: 6px;">${bot.desc}</p>
                            <button class="btn-action btn-yellow" onclick="alert('Configuring ${bot.name}...')">Launch Bot</button>
                        </div>`;
                });
                area.innerHTML = html;
            }
        }

        window.onload = function() {
            loadTradingViewChart();
            switchMainTab('spot', null);
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_index():
    return HTML_CONTENT

@app.get("/api/market/{symbol}")
def fallback_market_api(symbol: str):
    return {"symbol": symbol, "price": 65142.80, "status": "active"}
    
