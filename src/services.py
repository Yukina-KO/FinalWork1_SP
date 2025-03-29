import logging
import math
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def analyze_cashback_categories(data: pd.DataFrame, year: int, month: int) -> Any:
    try:
        filtered = data[(data["Дата операции"].dt.year == year) & (data["Дата операции"].dt.month == month)]

        # Удаляем пустые значения
        filtered = filtered.dropna(subset=["Категория", "Сумма платежа"])

        # Группировка по категориям и расчёт кешбэка
        result = (
            filtered.groupby("Категория")["Сумма платежа"]
            .sum()
            .apply(lambda x: round(x * 0.01, 2))  # 1% кешбэка
            .to_dict()
        )

        return result

    except Exception as e:
        logger.error(f"Ошибка в analyze_cashback_categories: {e}")
        return {}


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
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


def simple_search(data: pd.DataFrame, query: str) -> Any:
    try:
        query = query.lower()
        mask = data["Категория"].fillna("").str.lower().str.contains(query) | data["Описание"].fillna(
            ""
        ).str.lower().str.contains(query)

        results = data[mask].copy()

        # 💥 Преобразуем все Timestamp → str
        for col in results.columns:
            if pd.api.types.is_datetime64_any_dtype(results[col]):
                results[col] = results[col].dt.strftime("%Y-%m-%d")

        return results.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Ошибка в simple_search: {e}")
        return []


def phone_search(data: pd.DataFrame) -> Any:
    try:
        pattern = r"\+7\s\d{3}\s\d{3}-\d{2}-\d{2}"
        mask = data["Описание"].fillna("").apply(lambda text: bool(re.search(pattern, text)))
        results = data[mask].copy()

        # 🔥 Преобразуем все datetime-столбцы в строки
        for col in results.columns:
            if pd.api.types.is_datetime64_any_dtype(results[col]):
                results[col] = results[col].dt.strftime("%Y-%m-%d")

        return results.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Ошибка в phone_search: {e}")
        return []
