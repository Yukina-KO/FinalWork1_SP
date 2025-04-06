import json

from src.reports import spending_by_category, spending_by_weekday
from src.services import analyze_cashback_categories, investment_bank, phone_search, simple_search
from src.utils import load_excel_data
from src.views import generate_main_page_data

if __name__ == "__main__":
    # Пример даты
    input_date = "2021-12-20 10:00:00"

    # === Главная страница ===
    main_result = generate_main_page_data(input_date)
    print("\n Главная страница:")
    print(json.dumps(main_result, ensure_ascii=False, indent=2))

    # Загружаем датафрейм для сервисов и отчетов
    df = load_excel_data("data/operations.xlsx")

    # === Сервис 1: Повышенный кешбэк ===
    cashback_result = analyze_cashback_categories(
        df.to_dict(orient="records"),
        year=2021,
        month=12
    )
    print("\n Повышенный кешбэк:")
    print(json.dumps(json.loads(cashback_result), ensure_ascii=False, indent=2))

    # === Сервис 2: Инвесткопилка ===
    transactions = (
        df[(df["Дата операции"].dt.strftime("%Y-%m") == "2021-12") & (df["Сумма операции"] > 0)][
            ["Дата " "операции", "Сумма операции"]
        ]
        .dropna()
        .to_dict(orient="records")
    )
    invest_result = investment_bank("2021-12", transactions, limit=50)
    print("\n Инвесткопилка (шаг 50):")
    print(invest_result)

    # === Сервис 3: Простой поиск ===
    search_result = simple_search(df.to_dict(orient="records"), "Магнит")
    print("\n Поиск 'Магнит':")
    print(json.dumps(json.loads(search_result), ensure_ascii=False, indent=2))

    # === Сервис 4: Поиск по телефонам ===
    phone_result = phone_search(df.to_dict(orient="records"))
    print("\n Телефоны:")
    print(json.dumps(phone_result, ensure_ascii=False, indent=2))

    # === Отчет 1: Траты по категории ===
    category_report = spending_by_category(df, category="Супермаркеты", date="2021-12-20")
    print("\n Отчет: Траты по категории 'Супермаркеты' (последние 3 месяца):")
    print(category_report)

    # === Отчет 2: Траты по дням недели ===
    weekday_report = spending_by_weekday(df, date="2021-12-20")
    print("\n Отчет: Средние траты по дням недели (последние 3 месяца):")
    print(weekday_report)
