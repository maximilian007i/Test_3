import asyncio
import os
import smtplib
import schedule
import pandas as pd
from aiohttp import ClientSession
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.message import EmailMessage
from tortoise import Tortoise
from models import PriceHistory
from config import EXCHANGES, PAIRS, THRESHOLD, DB_URL, EMAIL_ADDRESS, EMAIL_PASSWORD
import time

load_dotenv()

async def get_exchange_data(exchange):
    async with ClientSession() as session:
        async with session.get(exchange["url"]) as response:
            data = await response.json()
            if exchange["name"] == "Binance":
                return {pair: float(data[pair]["price"]) for pair in exchange["pairs"]}
            elif exchange["name"] == "CoinMarketCap":
                return {f"{pair.upper()}/BTC": float(data["data"][pair]["quote"]["BTC"]["price"] * 10000) for pair in exchange["pairs"]}

async def check_price_increase(exchange_data, prev_data):
    current_pairs = set(exchange_data.keys())
    prev_pairs = set(prev_data.keys())

    for pair in current_pairs & prev_pairs:
        current_price = exchange_data[pair]
        prev_price = prev_data[pair]
        if current_price > prev_price * (1 + THRESHOLD):
            return pair, current_price, prev_price, (current_price - prev_price) / prev_price

    return None, None, None, None

async def send_email(title, price, max_price, min_price, date, difference, total_amount):
    msg = EmailMessage()
    msg.set_content(
        f"Title: {title}\n"
        f"Price: {price}\n"
        f"Max Price: {max_price}\n"
        f"Min Price: {min_price}\n"
        f"Date: {date}\n"
        f"Difference: {difference * 100:.2f}%\n"
        f"Total Amount: {total_amount}"
    )
    msg["Subject"] = f"Cryptocurrency Price Alert: {title}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

async def main():
    await Tortoise.init(db_url=DB_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()

    prev_data = {}
    while True:
        exchange_data = {}
        for exchange in EXCHANGES:
            data = await get_exchange_data(exchange)
            exchange_data.update(data)

        pair, current_price, prev_price, difference = await check_price_increase(exchange_data, prev_data)
        if pair:
            title = PAIRS[pair]
            date = datetime.now().isoformat()
            await PriceHistory.create(title=title, price=current_price, max_price=current_price, min_price=prev_price, difference=difference, total_amount=0)
            await send_email(title, current_price, current_price, prev_price, date, difference, 0)

        prev_data = exchange_data
        await asyncio.sleep(60)  # Check prices every minute

if __name__ == "__main__":
    schedule.every(60).seconds.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)