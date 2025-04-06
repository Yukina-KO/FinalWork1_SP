from pathlib import Path

import pandas as pd
import pytest
from pytest import MonkeyPatch

from src.reports import save_report, spending_by_category, spending_by_weekday
from src.utils import load_excel_data


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """
    Загружает тестовый DataFrame из файла операций, отфильтровывая строки с ненулевыми категориями.
    :return: DataFrame с транзакциями, содержащими категории
    """
    df = load_excel_data("data/operations.xlsx")
    return df[df["Категория"].notna()].copy()


def test_spending_by_category_valid(sample_df: pd.DataFrame) -> None:
    """
    Проверяет корректную работу отчета по категории, если категория существует.
    :param sample_df: Тестовый DataFrame
    """
    result = spending_by_category(sample_df, category="Супермаркеты", date="2021-12-20")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_invalid(sample_df: pd.DataFrame) -> None:
    """
    Проверяет, что функция возвращает пустой DataFrame при передаче несуществующей категории.
    :param sample_df: Тестовый DataFrame
    """
    result = spending_by_category(sample_df, category="Несуществующая", date="2021-12-20")
    assert result.empty


def test_spending_by_weekday_valid(sample_df: pd.DataFrame) -> None:
    """
    Проверяет, что отчет по дням недели возвращает DataFrame с колонкой "Средние траты".
    :param sample_df: Тестовый DataFrame
    """
    result = spending_by_weekday(sample_df, date="2021-12-20")
    assert isinstance(result, pd.DataFrame)
    assert "Средние траты" in result.columns


def test_spending_by_weekday_no_date(sample_df: pd.DataFrame) -> None:
    """
    Проверяет, что функция работает без указания даты (используется текущая).
    :param sample_df: Тестовый DataFrame
    """
    result = spending_by_weekday(sample_df)
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_with_decorator(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    """
    Проверяет сохранение отчета по категории в файл при использовании декоратора save_report.
    :param tmp_path: Временная директория, предоставляемая pytest
    :param sample_df: Тестовый DataFrame
    """
    output_file = tmp_path / "custom_category_report.json"

    @save_report(str(output_file))
    def test_func() -> pd.DataFrame:
        return spending_by_category(sample_df, "Супермаркеты", date="2021-12-20")

    result = test_func()

    assert output_file.exists(), "Файл отчета не был создан"
    assert result is not None
    df = pd.read_json(output_file)
    assert not df.empty


def test_spending_by_weekday_with_filename(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    """
    Проверяет сохранение weekday-отчета в файл с помощью save_report.
    :param tmp_path: Временная директория
    :param sample_df: Тестовый DataFrame
    """

    output_file = tmp_path / "my_weekday_report.json"

    @save_report(str(output_file))
    def test_func() -> pd.DataFrame:
        return spending_by_weekday(sample_df, date="2021-12-20")

    result = test_func()

    assert output_file.exists(), "Файл не создан"
    df = pd.read_json(output_file)
    assert not df.empty
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_invalid_data() -> None:
    """
    Проверяет, что функция возвращает пустой DataFrame при передаче пустого входного DataFrame.
    """
    bad_df = pd.DataFrame()
    result = spending_by_category(bad_df, "Супермаркеты", date="2021-12-20")
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_spending_by_weekday_invalid_data() -> None:
    """
    Проверяет, что функция по дням недели возвращает пустой DataFrame при пустом входе.
    """
    bad_df = pd.DataFrame()
    result = spending_by_weekday(bad_df, date="2021-12-20")
    assert result.empty


def test_save_report_error(monkeypatch: MonkeyPatch, sample_df: pd.DataFrame) -> None:
    """
    Проверяет, что save_report не выбрасывает исключение при ошибке сохранения и возвращает результат.
    :param monkeypatch: Объект для подмены поведения функций (не используется)
    :param sample_df: Тестовый DataFrame
    """

    @save_report("/invalid_path/report.json")
    def test_func() -> pd.DataFrame:
        return spending_by_category(sample_df, "Супермаркеты", date="2021-12-20")

    result = test_func()
    assert isinstance(result, pd.DataFrame)
