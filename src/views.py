import datetime
import logging
from typing import Any

from src.utils import (filter_by_date_range, get_exchange_rates, get_greeting, get_stock_prices, get_user_settings,
                       load_excel_data)

logger = logging.getLogger(__name__)


def generate_main_page_data(date_str: str) -> dict[str, Any]:
    """
    Генерирует данные для главной страницы.
    :param date_str: Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS
    :return: Словарь с приветствием, списком карт, топ-транзакциями и курсами валют
    """
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
    exchange_rates = get_exchange_rates(settings.get("user_currencies", []))
    stock_prices = get_stock_prices()

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "exchange_rates": exchange_rates,
        "stock_prices": stock_prices,
    }
