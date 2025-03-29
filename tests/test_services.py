import pandas as pd

from src.services import analyze_cashback_categories, investment_bank, phone_search, simple_search
from src.utils import load_excel_data


def test_analyze_cashback_categories() -> None:
    df = load_excel_data("data/operations.xlsx")
    result = analyze_cashback_categories(df, 2021, 12)
    assert isinstance(result, dict)


def test_investment_bank() -> None:
    df = load_excel_data("data/operations.xlsx")
    txs = df[["Дата операции", "Сумма операции"]].dropna().to_dict("records")
    result = investment_bank("2021-12", txs, limit=50)
    assert isinstance(result, float)


def test_simple_search() -> None:
    df = load_excel_data("data/operations.xlsx")
    result = simple_search(df, "магнит")
    assert isinstance(result, list)


def test_phone_search() -> None:
    df = load_excel_data("data/operations.xlsx")
    result = phone_search(df)
    assert isinstance(result, list)


def test_simple_search_not_found() -> None:
    df = pd.DataFrame({"Категория": ["Супермаркеты", "Кафе"], "Описание": ["Лента", "Шоколадница"]})
    result = simple_search(df, "Телевизор")
    assert result == []


def test_phone_search_no_matches() -> None:
    # Без номеров
    df = pd.DataFrame({"Описание": ["Тест без номера", "Еще одна строка"]})
    result = phone_search(df)
    assert result == []


def test_investment_bank_invalid_data() -> None:
    # Передаём плохие транзакции
    bad_data = [{"Дата операции": None, "Сумма операции": -100}]
    result = investment_bank("2021-12", bad_data, 50)
    assert result == 0.0


def test_analyze_cashback_categories_with_invalid_data() -> None:
    bad_df = pd.DataFrame()  # пустой датафрейм
    result = analyze_cashback_categories(bad_df, 2021, 12)
    assert isinstance(result, dict)
    assert result == {}


def test_investment_bank_with_invalid_data() -> None:
    bad_transactions = [{"Дата операции": None, "Сумма операции": -100}]
    result = investment_bank("2021-12", bad_transactions, limit=50)
    assert result == 0.0


def test_simple_search_with_missing_columns() -> None:
    df = pd.DataFrame({"Другое поле": ["тест"]})
    result = simple_search(df, "тест")
    assert result == []


def test_phone_search_with_invalid_column() -> None:
    df = pd.DataFrame({"Другое поле": ["+7 921 123-45-67"]})
    result = phone_search(df)
    assert result == []


def test_phone_search_with_empty_data() -> None:
    df = pd.DataFrame({"Описание": [None, "", "No phone here"]})
    result = phone_search(df)
    assert result == []
