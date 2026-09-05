from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Serve Static Folder
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

# Fallback endpoint for legacy requests
@app.get("/api/market/{symbol}")
def fallback_market_api(symbol: str):
    return {"symbol": symbol, "price": 65142.80, "status": "active"}
    
