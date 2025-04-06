import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")


def load_excel_data(filepath: str) -> pd.DataFrame:
    """
    Загружает данные из Excel-файла.
    Преобразует путь к файлу в абсолютный от корня проекта,
    загружает данные в DataFrame и приводит даты к формату datetime.
    :param filepath: Относительный путь к файлу Excel (например, "data/operations.xlsx")
    :return: DataFrame с транзакциями
    """
    project_root = Path(__file__).resolve().parents[1]
    full_path = project_root / filepath
    df = pd.read_excel(full_path)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
    return df


def filter_by_date_range(df: pd.DataFrame, end_date: datetime) -> pd.DataFrame:
    """
    Фильтрует транзакции по дате операции от начала месяца до заданной даты (включительно).
    :param df: Исходный DataFrame с транзакциями
    :param end_date: Конечная дата диапазона
    :return: Отфильтрованный DataFrame
    """
    start_date = end_date.replace(day=1)
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    return df.loc[mask]


def get_greeting(hour: int) -> str:
    """
    Возвращает приветствие в зависимости от часа суток.
    :param hour: Час от 0 до 23
    :return: Строка с приветствием
    """
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_user_settings(filepath: str = "user_settings.json") -> Any:
    """
    Загружает пользовательские настройки из JSON-файла.
    :param filepath: Путь к JSON-файлу с настройками
    :return: Словарь с настройками или словарь по умолчанию
    """
    try:
        with open(Path(filepath), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Файл user_settings.json не найден.")
        return {"user_currencies": []}


def get_exchange_rates(currencies: list[str]) -> list[dict[str, object]]:
    """
    Получает курсы валют по отношению к RUB через API finnhub.io.
    :param currencies: Список кодов валют (например, ["USD", "EUR"])
    :return: Список словарей с валютами и курсами
    """
    if not FINNHUB_API_KEY:
        logger.error("FINNHUB_API_KEY не найден в .env")
        return []

    try:
        response = requests.get(
            "https://finnhub.io/api/v1/forex/rates", params={"base": "RUB", "token": FINNHUB_API_KEY}, timeout=5
        )
        data = response.json()
        rub_rates = data.get("quote", {})

        results = []
        for currency in currencies:
            if currency == "RUB":
                results.append({"currency": "RUB", "rate": 1.00})
            else:
                rate = rub_rates.get(currency)
                results.append({"currency": currency, "rate": round(1 / rate, 2) if rate else None})
        return results
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return []


def get_stock_prices() -> list[dict[str, float | None]]:
    """
    Получает цены акций из S&P500 через API finnhub.io.
    :return: Список словарей с тикерами и ценами акций
    """
    if not FINNHUB_API_KEY:
        logger.error("FINNHUB_API_KEY не найден в .env")
        return []

    tickers = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    prices = []

    for symbol in tickers:
        try:
            response = requests.get(
                "https://finnhub.io/api/v1/quote", params={"symbol": symbol, "token": FINNHUB_API_KEY}, timeout=5
            )
            data = response.json()
            current_price = round(data.get("c", 0), 2)
            prices.append({"stock": symbol, "price": current_price})
        except Exception as e:
            logger.error(f"Ошибка при получении цены акции {symbol}: {e}")
            prices.append({"stock": symbol, "price": None})

    return prices


def format_search_results(df: pd.DataFrame, mask: pd.Series) -> str:
    """
    Преобразует отфильтрованный DataFrame в JSON-строку с преобразованием дат в строки.
    :param df: Исходный DataFrame
    :param mask: Булева маска фильтрации
    :return: JSON-строка с результатами
    """
    results = df[mask].copy()
    for col in results.columns:
        if pd.api.types.is_datetime64_any_dtype(results[col]):
            results[col] = results[col].dt.strftime("%Y-%m-%d")
    return json.dumps(results.to_dict(orient="records"), ensure_ascii=False)
