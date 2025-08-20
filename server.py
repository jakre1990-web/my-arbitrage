from fastapi import FastAPI
import requests

app = FastAPI()

MEXC_API = "https://www.mexc.com/api/v2/market/ticker?symbol=COCA_USDT"

@app.get("/")
def get_coca_price():
    try:
        response = requests.get(MEXC_API, timeout=5)
        data = response.json()
        # MEXC возвращает массив с тикерами, берём первый
        price = float(data['data'][0]['last'])
        return {"token": "COCA", "price": price}
    except Exception as e:
        return {"error": str(e)}
