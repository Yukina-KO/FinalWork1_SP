from pathlib import Path

import pandas as pd
import pytest
from pytest import MonkeyPatch

from src.reports import save_report, spending_by_category, spending_by_weekday
from src.utils import load_excel_data


@pytest.fixture
def sample_df() -> pd.DataFrame:
    df = load_excel_data("data/operations.xlsx")
    return df[df["Категория"].notna()].copy()


def test_spending_by_category_valid(sample_df: pd.DataFrame) -> None:
    result = spending_by_category(sample_df, category="Супермаркеты", date="2021-12-20")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_invalid(sample_df: pd.DataFrame) -> None:
    # Не существует такой категории
    result = spending_by_category(sample_df, category="Несуществующая", date="2021-12-20")
    assert result.empty


def test_spending_by_weekday_valid(sample_df: pd.DataFrame) -> None:
    result = spending_by_weekday(sample_df, date="2021-12-20")
    assert isinstance(result, pd.DataFrame)
    assert "Средние траты" in result.columns


def test_spending_by_weekday_no_date(sample_df: pd.DataFrame) -> None:
    result = spending_by_weekday(sample_df)
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_with_decorator(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    # Указываем явный путь сохранения отчета
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
    # Тестируем save_report с параметром
    output_file = tmp_path / "my_weekday_report.json"

    @save_report(str(output_file))
    def test_func() -> pd.DataFrame:
        return spending_by_weekday(sample_df, date="2021-12-20")

    assert output_file.exists()
    df = pd.read_json(output_file)
    assert not df.empty


def test_spending_by_category_invalid_data() -> None:
    # Передаём невалидные данные
    bad_df = pd.DataFrame()
    result = spending_by_category(bad_df, "Супермаркеты", date="2021-12-20")
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_spending_by_weekday_invalid_data() -> None:
    # Пустой DataFrame должен вернуть пустой результат
    bad_df = pd.DataFrame()
    result = spending_by_weekday(bad_df, date="2021-12-20")
    assert result.empty


def test_save_report_error(monkeypatch: MonkeyPatch, sample_df: pd.DataFrame) -> None:
    # Провоцируем ошибку сохранения
    @save_report("/invalid_path/report.json")
    def test_func() -> pd.DataFrame:
        return spending_by_category(sample_df, "Супермаркеты", date="2021-12-20")

    result = test_func()
    assert isinstance(result, pd.DataFrame)
