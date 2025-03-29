from datetime import datetime

import pandas as pd

from src.utils import filter_by_date_range, load_excel_data


def test_load_excel_data() -> None:
    df = load_excel_data("data/operations.xlsx")
    assert not df.empty
    assert "Дата операции" in df.columns
    assert "Дата платежа" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["Дата операции"])
    assert pd.api.types.is_datetime64_any_dtype(df["Дата платежа"])


def test_filter_by_date_range() -> None:
    df = load_excel_data("data/operations.xlsx")
    end_date = datetime(2021, 12, 20)
    filtered = filter_by_date_range(df, end_date)
    assert all(filtered["Дата операции"] >= datetime(2021, 12, 1))
    assert all(filtered["Дата операции"] <= end_date)
