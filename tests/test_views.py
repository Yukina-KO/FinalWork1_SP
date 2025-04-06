import pytest
from pytest import MonkeyPatch

from src.views import generate_main_page_data, get_greeting, get_user_settings


@pytest.mark.parametrize(
    "hour,expected",
    [
        (6, "Доброе утро"),
        (13, "Добрый день"),
        (20, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_get_greeting(hour: int, expected: str) -> None:
    """
    Проверяет функцию get_greeting, возвращающую корректное приветствие в зависимости от времени суток.
    :param hour: Час в формате 0–23
    :param expected: Ожидаемое приветствие
    """
    assert get_greeting(hour) == expected


def test_user_settings() -> None:
    """
    Проверяет, что функция get_user_settings успешно загружает настройки из файла user_settings.json.
    """
    settings = get_user_settings("user_settings.json")
    assert "user_currencies" in settings


def test_generate_main_data() -> None:
    """
    Проверяет, что функция generate_main_page_data возвращает корректную структуру JSON-ответа.
    """
    result = generate_main_page_data("2021-12-20 10:00:00")
    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert isinstance(result["cards"], list)


def test_get_user_settings_missing(monkeypatch: MonkeyPatch) -> None:
    """
    Проверяет поведение get_user_settings при отсутствии указанного файла: должно возвращаться значение по умолчанию.
    :param monkeypatch: Объект monkeypatch для подмены поведения встроенной функции open
    """
    from src.views import get_user_settings

    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(FileNotFoundError()))
    settings = get_user_settings("nonexistent.json")
    assert settings == {"user_currencies": []}
