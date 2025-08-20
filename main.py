from fastapi import FastAPI
import httpx
import json
import os

app = FastAPI()

CHAIN_ID = 137
USDT = "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"
ODOS_FEE = 0.002
MEXC_FEE = 0.001

# Загружаем токены
with open("tokens.json", "r") as f:
    TOKENS = json.load(f)

@app.get("/prices")
async def get_prices():
    odos_prices = {}
    mexc_prices = {}
    spread = {}
    profit = {}

    async with httpx.AsyncClient() as client:
        for token in TOKENS:
            tokens_bought = None

            # ODOS (покупка на 50 USDT)
            try:
                effective_usdt = 50 * (1 - ODOS_FEE)
                res = await client.post(
                    "https://api.odos.xyz/sor/quote/v2",
                    json={
                        "chainId": CHAIN_ID,
                        "inputTokens": [{"tokenAddress": USDT, "amount": str(int(effective_usdt * 1e6))}],
                        "outputTokens": [{"tokenAddress": token["address"]}],
                        "slippageLimitPercent": 1
                    }
                )
                data = res.json()
                out = data.get("outAmounts", [None])[0]
                if out:
                    tokens_bought = int(out) / 1e18
                    odos_prices[token["symbol"]] = effective_usdt / tokens_bought
                else:
                    odos_prices[token["symbol"]] = None
            except:
                odos_prices[token["symbol"]] = None

            # MEXC (продажа этих токенов)
            try:
                res = await client.get(f"https://api.mexc.com/api/v3/depth?symbol={token['symbol']}USDT&limit=50")
                data = res.json()
                asks = data.get("asks", [])

                if asks and tokens_bought:
                    remaining_tokens = tokens_bought
                    total_usdt = 0
                    for price_str, qty_str in asks:
                        price = float(price_str)
                        qty = float(qty_str)
                        if remaining_tokens >= qty:
                            total_usdt += price * qty
                            remaining_tokens -= qty
                        else:
                            total_usdt += price * remaining_tokens
                            break

                    usdt_after_fee = total_usdt * (1 - MEXC_FEE)
                    mexc_prices[token["symbol"]] = total_usdt / tokens_bought
                    profit[token["symbol"]] = usdt_after_fee - 50
                else:
                    mexc_prices[token["symbol"]] = None
                    profit[token["symbol"]] = None
            except:
                mexc_prices[token["symbol"]] = None
                profit[token["symbol"]] = None

            # Спред
            if odos_prices[token["symbol"]] and mexc_prices[token["symbol"]]:
                spread[token["symbol"]] = (
                    (odos_prices[token["symbol"]] - mexc_prices[token["symbol"]])
                    / mexc_prices[token["symbol"]] * 100
                )
            else:
                spread[token["symbol"]] = None

    return {"odos": odos_prices, "mexc": mexc_prices, "spread": spread, "profit": profit}
