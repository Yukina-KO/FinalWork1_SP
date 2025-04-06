import json
import logging
import math
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from src.utils import format_search_results

logger = logging.getLogger(__name__)


def analyze_cashback_categories(data: list[dict[str, Any]], year: int, month: int) -> str:
    """
    Анализирует категории расходов за указанный месяц и возвращает кешбэк 1% по каждой категории в виде JSON-строки.
    :param data: Список транзакций в виде словарей
    :param year: Год анализа
    :param month: Месяц анализа
    :return: JSON-строка вида '{"Категория": сумма_кешбэка, ...}'
    """
    try:
        df = pd.DataFrame(data)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%Y-%m-%d")

        filtered = df[
            (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month) & (df["Сумма платежа"] > 0)
        ].dropna(subset=["Категория", "Сумма платежа"])

        result = filtered.groupby("Категория")["Сумма платежа"].sum().apply(lambda x: round(x * 0.01, 2)).to_dict()

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Ошибка в analyze_cashback_categories: {e}")
        return json.dumps({})


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Вычисляет сумму округлений до заданного лимита для пополнения инвесткопилки.
    :param month: Месяц в формате "YYYY-MM"
    :param transactions: Список транзакций (словарей)
    :param limit: Лимит округления (например, 50)
    :return: Общая сумма округлений
    """
    try:
        total_saved = 0
        for tx in transactions:
            date = tx.get("Дата операции")
            if isinstance(date, str):
                tx_month = date[:7]
            elif isinstance(date, datetime):
                tx_month = date.strftime("%Y-%m")
            else:
                continue

            if tx_month == month:
                amount = tx["Сумма операции"]
                if amount > 0:
                    rounded = math.ceil(amount / limit) * limit
                    delta = round(rounded - amount, 2)
                    total_saved += delta

        return round(total_saved, 2)

    except Exception as e:
        logger.error(f"Ошибка в investment_bank: {e}")
        return 0.0


def simple_search(data: list[dict[str, Any]], query: str) -> str:
    """
    Выполняет простой поиск по категориям и описаниям транзакций.
    Возвращает результат в виде JSON-строки.
    :param data: Список транзакций в виде словарей
    :param query: Поисковый запрос
    :return: JSON-строка с результатами поиска
    """
    try:
        df = pd.DataFrame(data)
        query = query.lower()
        mask = df["Категория"].fillna("").str.lower().str.contains(query) | df["Описание"].fillna(
            ""
        ).str.lower().str.contains(query)
        return format_search_results(df, mask)

    except Exception as e:
        logger.error(f"Ошибка в simple_search: {e}")
        return json.dumps([])


def phone_search(data: list[dict[str, Any]]) -> str:
    """
    Ищет телефоны в формате +7 XXX XXX-XX-XX в описаниях транзакций.
    Возвращает результат в виде JSON-строки.
    :param data: Список транзакций в виде словарей
    :return: JSON-строка с найденными транзакциями
    """
    try:
        df = pd.DataFrame(data)
        pattern = r"\+7\s\d{3}\s\d{3}-\d{2}-\d{2}"
        mask = df["Описание"].fillna("").apply(lambda text: bool(re.search(pattern, text)))
        return format_search_results(df, mask)

    except Exception as e:
        logger.error(f"Ошибка в phone_search: {e}")
        return json.dumps([])
