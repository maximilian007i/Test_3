import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
DB_URL = os.getenv("DB_URL")

EXCHANGES = [
    {"name": "Binance", "url": "https://api.binance.com/api/v3/ticker/price", "pairs": ["BTCUSDT", "BTCEUR", "BTCRUB"]},
    {"name": "CoinMarketCap", "url": "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest", "pairs": ["BTC", "ETH", "XMR", "SOL", "DOGE"]},
    # Add more exchanges as needed
]

PAIRS = {
    "BTCUSDT": "BTC/USDT",
    "BTCEUR": "BTC/EUR",
    "BTCRUB": "BTC/RUB",
    "BTC": "BTC/ETH",
    "ETH": "BTC/ETH",
    "XMR": "BTC/XMR",
    "SOL": "BTC/SOL",
    "DOGE": "BTC/DOGE",
}

THRESHOLD = 0.0003  # 0.03% threshold for price increase