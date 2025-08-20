from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()

# Папка с фронтендом
app.mount("/", StaticFiles(directory="public", html=True), name="static")

MEXC_URL_TEMPLATE = "https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"

@app.get("/api/price")
def get_price(symbol: str = "COCA"):
    try:
        res = requests.get(MEXC_URL_TEMPLATE.format(symbol=symbol.upper()), timeout=5)
        res.raise_for_status()
        data = res.json()
        return {"symbol": symbol.upper(), "price": float(data["price"])}
    except Exception as e:
        return {"error": str(e)}
