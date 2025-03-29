import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from src.utils import filter_by_date_range, load_excel_data

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
load_dotenv()
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
CURRENCY_API_URL = os.getenv("CURRENCY_API_URL")


def get_greeting(hour: int) -> str:
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_user_settings(filepath: str = "../user_settings.json") -> Any:
    try:
        with open(Path(filepath), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Файл user_settings.json не найден.")
        return {"user_currencies": []}


def get_currency_rates(currencies: list[str]) -> list[dict[str, object]]:
    results = []

    if not CURRENCY_API_URL or not CURRENCY_API_KEY:
        logger.error("CURRENCY_API_URL или CURRENCY_API_KEY не установлены.")
        return []

    for currency in currencies:
        if currency == "RUB":
            results.append({"currency": "RUB", "rate": 1.00})
            continue
        try:
            response = requests.get(
                CURRENCY_API_URL, params={"apikey": CURRENCY_API_KEY, "base_currency": currency, "currencies": "RUB"}
            )
            data = response.json()
            rate = data["data"]["RUB"]["value"]
            results.append({"currency": currency, "rate": round(rate, 2)})
        except Exception as e:
            logger.error(f"Ошибка при получении курса валюты {currency}: {e}")
            results.append({"currency": currency, "rate": None})
    return results


def generate_main_page_data(date_str: str) -> dict:
    input_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    df = load_excel_data("data/operations.xlsx")
    df_filtered = filter_by_date_range(df, input_date)

    greeting = get_greeting(input_date.hour)

    cards = []
    grouped = df_filtered.groupby("Номер карты")
    for card, group in grouped:
        total_spent = group["Сумма платежа"].sum()
        cashback = round(total_spent / 100, 2)
        cards.append({"last_digits": card[-4:], "total_spent": round(total_spent, 2), "cashback": cashback})

    top_transactions_df = df_filtered.nlargest(5, "Сумма платежа")
    top_transactions = []
    for _, row in top_transactions_df.iterrows():
        top_transactions.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": round(row["Сумма платежа"], 2),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    settings = get_user_settings()
    currency_rates = get_currency_rates(settings.get("user_currencies", []))

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
    }
