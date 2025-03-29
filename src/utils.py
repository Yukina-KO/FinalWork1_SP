from datetime import datetime
from pathlib import Path

import pandas as pd


def load_excel_data(filepath: str) -> pd.DataFrame:
    """
    Загружает данные из Excel, используя абсолютный путь от корня проекта.
    """
    project_root = Path(__file__).resolve().parents[1]
    full_path = project_root / filepath
    df = pd.read_excel(full_path)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
    return df


def filter_by_date_range(df: pd.DataFrame, end_date: datetime) -> pd.DataFrame:
    """
    Возвращает данные с начала месяца по указанную дату (включительно).
    :param df: исходный DataFrame
    :param end_date: дата окончания диапазона
    :return: отфильтрованный DataFrame
    """
    start_date = end_date.replace(day=1)
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    return df.loc[mask]
