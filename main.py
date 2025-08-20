from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

PRICES_API = "https://my-arbitrage.onrender.com/prices"  # или локально /prices

@app.get("/")
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Arbitrage Monitor</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; margin: 20px 0; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background: #eee; }
        .profit-pos { color: green; font-weight: bold; }
        .profit-neg { color: red; font-weight: bold; }
        .tables-row { display: flex; gap: 20px; flex-wrap: wrap; }
        .tables-row table { width: 48%; }
      </style>
    </head>
    <body>
      <h1>📊 Arbitrage Monitor</h1>
      <div class="tables-row">
        <table id="odos-mexc">
          <thead>
            <tr>
              <th>Токен</th>
              <th>ODOS цена</th>
              <th>MEXC цена</th>
              <th>Спред (%)</th>
              <th>Прибыль (USDT)</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>

        <table id="mexc-odos">
          <thead>
            <tr>
              <th>Токен</th>
              <th>MEXC цена</th>
              <th>ODOS цена</th>
              <th>Спред (%)</th>
              <th>Прибыль (USDT)</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>

      <script>
        const TOKENS = [
          "NAKA","SAND","NWS","ZRO","UPO","QUICK","APEPE","SUT","GNS","GEOD",
          "COCA","MLC","IXT","KASTA","SOIL","SWCH","UBU","FURI","PolyDoge",
          "CARR","DEOD","DTEC","EDX","MINX","WEFI","WSDM"
        ];

        function formatProfit(value) {
          if (value == null) return "-";
          const fixed = value.toFixed(4);
          if (value > 0) return `<span class="profit-pos">+${fixed}</span>`;
          if (value < 0) return `<span class="profit-neg">${fixed}</span>`;
          return fixed;
        }

        async function loadData() {
          const res = await fetch("/prices");
          const data = await res.json();

          const tbodyOdos = document.querySelector("#odos-mexc tbody");
          const tbodyMexc = document.querySelector("#mexc-odos tbody");
          tbodyOdos.innerHTML = "";
          tbodyMexc.innerHTML = "";

          for (const token of TOKENS) {
            const rowOdos = document.createElement("tr");
            rowOdos.innerHTML = `
              <td>${token}</td>
              <td>${data.odos?.[token] ? data.odos[token].toFixed(6) : "-"}</td>
              <td>${data.mexc?.[token] ? data.mexc[token].toFixed(6) : "-"}</td>
              <td>${data.spread?.[token] ? data.spread[token].toFixed(2) : "-"}%</td>
              <td>${formatProfit(data.profit?.[token])}</td>
            `;
            tbodyOdos.appendChild(rowOdos);

            const rowMexc = document.createElement("tr");
            rowMexc.innerHTML = `
              <td>${token}</td>
              <td>${data.mexc?.[token] ? data.mexc[token].toFixed(6) : "-"}</td>
              <td>${data.odos?.[token] ? data.odos[token].toFixed(6) : "-"}</td>
              <td>${data.spread?.[token] ? data.spread[token].toFixed(2) : "-"}%</td>
              <td>${formatProfit(data.profit?.[token])}</td>
            `;
            tbodyMexc.appendChild(rowMexc);
          }
        }

        loadData();
        setInterval(loadData, 10000); // обновление каждые 10 секунд
      </script>
    </body>
    </html>
    """)
