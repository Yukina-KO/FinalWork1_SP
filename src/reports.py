import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def save_report(filename: Optional[str] = None) -> Callable[[Callable], Callable[..., pd.DataFrame]]:
    """
    Декоратор для сохранения результата функции-отчета в JSON-файл.
    :param filename: Имя выходного файла (опционально)
    :return: Обёртка, сохраняющая результат вызова функции в файл
    """

    def decorator(func: Callable) -> Callable[..., pd.DataFrame]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = func(*args, **kwargs)
            default_name = f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            out_file = filename or default_name
            try:
                result.to_json(out_file, orient="records", force_ascii=False, indent=2)
                logger.info(f"Отчет сохранен в {out_file}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")
            return result

        return wrapper

    return decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Формирует отчет по тратам за указанную категорию за последние три месяца.
    :param transactions: DataFrame с транзакциями
    :param category: Название категории
    :param date: Дата отсчета (по умолчанию текущая)
    :return: Отфильтрованный DataFrame по категории и дате
    """
    try:
        end_date = pd.to_datetime(date or datetime.now())
        start_date = end_date - pd.DateOffset(months=3)

        filtered = transactions[
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Категория"] == category)
        ]

        return filtered

    except Exception as e:
        logger.error(f"Ошибка в spending_by_category: {e}")
        return pd.DataFrame()


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает средние траты по дням недели за последние три месяца от указанной даты.
    :param transactions: DataFrame с транзакциями
    :param date: Дата отсчета (по умолчанию текущая)
    :return: DataFrame со средними тратами по дням недели
    """
    try:
        end_date = pd.to_datetime(date or datetime.now())
        start_date = end_date - pd.DateOffset(months=3)

        filtered = transactions[
            (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
        ]

        result = (
            filtered.groupby(filtered["Дата операции"].dt.day_name())["Сумма платежа"]
            .mean()
            .reset_index()
            .rename(columns={"Дата операции": "День недели", "Сумма платежа": "Средние траты"})
        )

        return result

    except Exception as e:
        logger.error(f"Ошибка в spending_by_weekday: {e}")
        return pd.DataFrame()
