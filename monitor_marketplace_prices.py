import time
import datetime
import json
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SEARCH_QUERIES = {
    "копье": "копье",
    "дуршлаг": "дуршлаг",
    "красные носки": "красные носки",
    "леска для спиннинга": "леска спиннинг",
}

MARKETPLACES = [
    {"name": "Wildberries", "url": "https://www.wildberries.ru/"},
    {"name": "Ozon", "url": "https://www.ozon.ru/?__rr=1"},
    {"name": "Yandex.Market", "url": "https://market.yandex.ru/"},
]

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_lowest_price_item(driver, marketplace, query):
    driver.get(marketplace["url"])
    search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
    search_input.send_keys(query)
    search_input.submit()

    time.sleep(5)  # Wait for the search results to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    if marketplace["name"] == "Wildberries":
        cards = soup.find_all("div", class_="product-card__wrapper")
    elif marketplace["name"] == "Ozon":
        cards = soup.find_all("div", class_="tile tile--with-image")
    elif marketplace["name"] == "Yandex.Market":
        cards = soup.find_all("div", class_="n-snippet-card")

    lowest_price = float("inf")
    lowest_price_card = None
    for card in cards:
        if marketplace["name"] == "Wildberries":
            price = float(card.find("span", class_="price__main-value").text.replace(" ₽", "").replace(",", "."))
        elif marketplace["name"] == "Ozon":
            price = float(card.find("span", class_="g-price__current").text.replace(" ₽", "").replace(",", "."))
        elif marketplace["name"] == "Yandex.Market":
            price = float(card.find("span", class_="price__current").text.replace(" ₽", "").replace(",", "."))

        if price < lowest_price:
            lowest_price = price
            lowest_price_card = card

    return lowest_price_card

def extract_item_info(card, marketplace):
    if marketplace["name"] == "Wildberries":
        title = card.find("span", class_="product-card__name").text
        url = card.find("a", class_="product-card__link")["href"]
        image_url = card.find("img", class_="product-card__image")["src"]
        price = float(card.find("span", class_="price__main-value").text.replace(" ₽", "").replace(",", "."))
    elif marketplace["name"] == "Ozon":
        title = card.find("span", class_="title").text
        url = f"https://www.ozon.ru{card.find('a')['href']}"
        image_url = card.find("img")["src"]
        price = float(card.find("span", class_="g-price__current").text.replace(" ₽", "").replace(",", "."))
    elif marketplace["name"] == "Yandex.Market":
        title = card.find("a", class_="n-snippet-card__title").text
        url = card.find("a", class_="n-snippet-card__title")["href"]
        image_url = card.find("img", class_="n-snippet-card__image")["src"]
        price = float(card.find("span", class_="price__current").text.replace(" ₽", "").replace(",", "."))

    return {
        "title": title,
        "url": url,
        "image_url": image_url,
        "price": price,
        "marketplace": marketplace["name"],
        "date": datetime.datetime.now().isoformat(),
    }

def monitor_prices():
    driver = init_driver()
    data = []

    for query, search_query in SEARCH_QUERIES.items():
        for marketplace in MARKETPLACES:
            card = get_lowest_price_item(driver, marketplace, search_query)
            if card:
                item_info = extract_item_info(card, marketplace)
                data.append(item_info)
                print(f"Found {item_info['title']} on {item_info['marketplace']} for {item_info['price']}₽")

    driver.quit()

    df = pd.DataFrame(data)
    df.to_csv("marketplace_prices.csv", index=False, encoding="utf-8")

    with open("marketplace_prices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    monitor_prices()