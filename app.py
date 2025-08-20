from fastapi import FastAPI
import requests
import os

app = FastAPI()

MEXC_URL = "https://api.mexc.com/api/v3/ticker/price?symbol=COCAUSDT"

@app.get("/")
def read_root():
    return {"message": "Arbitrage API running"}

@app.get("/price")
def get_price():
    try:
        res = requests.get(MEXC_URL, timeout=5)
        res.raise_for_status()
        data = res.json()
        return {"symbol": "COCA", "price": float(data["price"])}
    except Exception as e:
        return {"error": str(e)}
