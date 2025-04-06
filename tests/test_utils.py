import json
from datetime import datetime
from pathlib import Path
from typing import Any, Generator
from unittest.mock import patch

import pandas as pd
import pytest
from pytest import MonkeyPatch

from src.utils import filter_by_date_range, format_search_results, get_exchange_rates, get_greeting, get_user_settings


@pytest.fixture
def sample_excel_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Создает временный Excel-файл с тестовыми данными."""
    df = pd.DataFrame(
        {
            "Дата операции": ["01.12.2021", "15.12.2021", "30.12.2021"],
            "Дата платежа": ["02.12.2021", "16.12.2021", "31.12.2021"],
            "Сумма": [100, 200, 300],
        }
    )
    file_path = tmp_path / "sample.xlsx"
    df.to_excel(file_path, index=False)
    yield file_path


def test_filter_by_date_range() -> None:
    """Проверяет фильтрацию транзакций по дате."""
    df = pd.DataFrame(
        {"Дата операции": pd.to_datetime(["2021-12-01", "2021-12-15", "2021-11-30"]), "Amount": [100, 200, 300]}
    )
    end_date = datetime(2021, 12, 20)
    filtered = filter_by_date_range(df, end_date)
    assert len(filtered) == 2


@pytest.mark.parametrize(
    "hour,expected", [(6, "Доброе утро"), (13, "Добрый день"), (20, "Добрый вечер"), (2, "Доброй ночи")]
)
def test_get_greeting(hour: int, expected: str) -> None:
    """Проверяет корректность возвращаемого приветствия в зависимости от часа."""
    assert get_greeting(hour) == expected


def test_get_user_settings_file_found(tmp_path: Path) -> None:
    """Проверяет успешную загрузку настроек пользователя из файла."""
    settings_file = tmp_path / "user_settings.json"
    settings_file.write_text(json.dumps({"user_currencies": ["USD", "EUR"]}), encoding="utf-8")
    result = get_user_settings(str(settings_file))
    assert result["user_currencies"] == ["USD", "EUR"]


def test_get_user_settings_file_missing() -> None:
    """Проверяет возврат значений по умолчанию при отсутствии файла."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        result = get_user_settings("non_existent.json")
        assert result == {"user_currencies": []}


@patch("src.utils.requests.get")
def test_get_exchange_rates_success(mock_get: Any) -> None:
    """Проверяет получение курсов валют при успешном ответе от API."""
    mock_get.return_value.json.return_value = {"quote": {"USD": 0.01, "EUR": 0.012}}
    result = get_exchange_rates(["USD", "EUR", "RUB"])
    assert isinstance(result, list)
    assert any(item["currency"] == "USD" for item in result)


@patch("src.utils.requests.get", side_effect=Exception("API error"))
def test_get_exchange_rates_error(monkeypatch: MonkeyPatch) -> None:
    """
    Проверяет, что при отсутствии API ключа возвращается пустой список.
    :param monkeypatch: фикстура для временной подмены окружения
    """
    monkeypatch.setenv("FINNHUB_API_KEY", "")
    from src.utils import get_exchange_rates

    result = get_exchange_rates(["USD"])
    assert result == []


@patch("src.utils.requests.get")
def test_get_exchange_rates_with_rub(monkeypatch: MonkeyPatch) -> None:
    """
    Проверяет, что RUB возвращается с курсом 1.00.
    :param monkeypatch: фикстура для временной подмены окружения
    """
    monkeypatch.setenv("FINNHUB_API_KEY", "fake_key")
    from src.utils import get_exchange_rates

    result = get_exchange_rates(["RUB", "USD"])
    rub = next((item for item in result if item["currency"] == "RUB"), {})
    assert rub.get("rate") == 1.00


@patch("src.utils.requests.get", side_effect=Exception("API error"))
def test_get_stock_prices_error(monkeypatch: MonkeyPatch) -> None:
    """
    Проверяет поведение при ошибке API: цены всех акций равны None.
    :param monkeypatch: фикстура для временной подмены переменных окружения
    """
    monkeypatch.setenv("FINNHUB_API_KEY", "fake_key")
    from src.utils import get_stock_prices

    result = get_stock_prices()
    assert all(item["price"] is None for item in result)


def test_format_search_results() -> None:
    """Проверяет форматирование результатов поиска и преобразование дат."""
    df = pd.DataFrame({"Дата": pd.to_datetime(["2021-12-01", "2021-12-02"]), "Описание": ["test1", "test2"]})
    mask = df["Описание"].str.contains("test")
    json_str = format_search_results(df, mask)
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert len(parsed) == 2


def test_filter_by_date_range_includes_start_and_end() -> None:
    """
    Проверяет, что filter_by_date_range включает транзакции
    на границах диапазона (включительно).
    """
    df = pd.DataFrame({"Дата операции": pd.to_datetime(["2021-12-01", "2021-12-15", "2021-12-31", "2022-01-01"])})
    end_date = datetime(2021, 12, 31)
    result = filter_by_date_range(df, end_date)
    assert len(result) == 3
    assert result["Дата операции"].min() == pd.Timestamp("2021-12-01")
    assert result["Дата операции"].max() == pd.Timestamp("2021-12-31")


def test_format_search_results_with_dates() -> None:
    """
    Проверяет, что format_search_results сериализует даты в строки
    и фильтрует по маске.
    """
    df = pd.DataFrame({"Дата операции": pd.to_datetime(["2021-12-01", "2021-12-02"]), "Сумма платежа": [100, 200]})
    mask = pd.Series([True, False])
    json_str = format_search_results(df, mask)
    assert "2021-12-01" in json_str
    assert "2021-12-02" not in json_str
    assert '"Сумма платежа": 100' in json_str
