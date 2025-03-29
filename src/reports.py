import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def save_report(filename: Optional[str] = None) -> Callable[[Callable], Callable]:
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
    try:
        end_date = pd.to_datetime(date or datetime.now())
        start_date = end_date - pd.DateOffset(months=3)

        filtered = transactions[
            (transactions["Дата операция"] >= start_date)
            & (transactions["Дата операция"] <= end_date)
            & (transactions["Категория"] == category)
        ]

        return filtered

    except Exception as e:
        logger.error(f"Ошибка в spending_by_category: {e}")
        return pd.DataFrame()


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    try:
        end_date = pd.to_datetime(date or datetime.now())
        start_date = end_date - pd.DateOffset(months=3)

        filtered = transactions[
            (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
        ]

        # Группировка по дню недели
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
