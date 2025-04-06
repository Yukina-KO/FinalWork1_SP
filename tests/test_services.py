import json
from datetime import datetime
from typing import Dict, List

import pytest

from src.services import analyze_cashback_categories, investment_bank, phone_search, simple_search


@pytest.fixture
def sample_data() -> list[dict]:
    """Возвращает пример транзакций для тестов."""
    return [
        {
            "Дата операции": "2021-12-15",
            "Категория": "Супермаркеты",
            "Сумма платежа": 1000.0,
            "Описание": "Пятёрочка",
            "Сумма операции": 999.99,
        },
        {
            "Дата операции": "2021-12-16",
            "Категория": "Переводы",
            "Сумма платежа": 2000.0,
            "Описание": "Перевод клиенту",
            "Сумма операции": 1900.0,
        },
        {
            "Дата операции": "2021-12-17",
            "Категория": "Продукты",
            "Сумма платежа": 500.0,
            "Описание": "Магнит +7 999 999-99-99",
            "Сумма операции": 475.0,
        },
    ]


def test_analyze_cashback_categories(sample_data: List[Dict]) -> None:
    """
    Проверяет вычисление кешбэка по категориям.
    :param sample_data: Тестовые транзакции
    """
    result = analyze_cashback_categories(sample_data, 2021, 12)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)
    assert "Супермаркеты" in parsed
    assert parsed["Супермаркеты"] == 10.0


def test_analyze_cashback_categories_with_invalid_data() -> None:
    """Проверяет возврат пустого словаря при некорректных данных."""
    result = analyze_cashback_categories([{"неправильные": "данные"}], 2021, 12)
    assert result == "{}"


def test_investment_bank_success(sample_data: List[Dict]) -> None:
    """
    Проверяет правильность расчета суммы для инвесткопилки.
    :param sample_data: Тестовые транзакции
    """
    result = investment_bank("2021-12", sample_data, limit=100)
    assert isinstance(result, float)
    assert result > 0


def test_investment_bank_empty() -> None:
    """Проверяет результат при пустом списке транзакций."""
    result = investment_bank("2021-12", [], limit=100)
    assert result == 0.0


def test_simple_search_match(sample_data: List[Dict]) -> None:
    """
    Проверяет, что простой поиск находит совпадения по описанию.
    :param sample_data: Тестовые транзакции
    """
    result = simple_search(sample_data, "пятёрочка")
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert any("Пятёрочка" in item["Описание"] for item in parsed)


def test_simple_search_no_match(sample_data: List[Dict]) -> None:
    """
    Проверяет, что поиск возвращает пустой список при отсутствии совпадений.
    :param sample_data: Тестовые транзакции
    """
    result = simple_search(sample_data, "несуществующее слово")
    assert json.loads(result) == []


def test_phone_search_found(sample_data: List[Dict]) -> None:
    """
    Проверяет, что phone_search находит номера телефонов в описаниях.
    :param sample_data: Тестовые транзакции
    """
    result = phone_search(sample_data)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert any("+7" in item["Описание"] for item in parsed)


def test_phone_search_no_phones() -> None:
    """Проверяет, что при отсутствии телефонов возвращается пустой список."""
    data = [{"Дата операции": "2021-12-01", "Описание": "Без телефона", "Сумма платежа": 100.0}]
    result = phone_search(data)
    assert json.loads(result) == []


def test_investment_bank_zero_amount() -> None:
    """Проверяет, что транзакции с нулевой суммой не учитываются."""
    data = [{"Дата операции": "2021-12-01", "Сумма операции": 0}]
    result = investment_bank("2021-12", data, limit=100)
    assert result == 0.0


def test_investment_bank_with_datetime_date() -> None:
    """Проверяет работу функции с объектами datetime."""
    data = [{"Дата операции": datetime(2021, 12, 5), "Сумма операции": 99}]
    result = investment_bank("2021-12", data, limit=100)
    assert result == 1.0


def test_simple_search_with_none_fields() -> None:
    """Проверяет обработку None в Категория и Описание."""
    data = [{"Категория": None, "Описание": None}]
    result = simple_search(data, "что-то")
    assert json.loads(result) == []


def test_phone_search_with_none_description() -> None:
    """Проверяет обработку None в поле Описание."""
    data = [{"Описание": None}]
    result = phone_search(data)
    assert json.loads(result) == []
