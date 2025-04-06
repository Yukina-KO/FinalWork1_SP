# 🧾 Анализ транзакций из Excel-файла

## 📌 Описание

Проект представляет собой консольное приложение на Python, предназначенное для анализа финансовых транзакций из файла Excel. Приложение формирует отчёты, генерирует JSON-данные для веб-страниц, предоставляет сервисы анализа и сохраняет результаты в отдельные файлы.

---

## 📁 Структура проекта

```
.
├── data
│   └── operations.xlsx             # Excel-файл с транзакциями
├── src
│   ├── views.py                    # Генерация данных для веб-страниц
│   ├── utils.py                    # Утилиты: загрузка и фильтрация данных
│   ├── services.py                 # Сервисы: поиск, кешбэк, инвесткопилка
│   └── reports.py                  # Отчёты и декораторы для сохранения в файлы
├── tests
│   ├── test_utils.py               # Тесты модуля utils
│   ├── test_views.py               # Тесты модуля views
│   ├── test_services.py            # Тесты модуля services
│   └── test_reports.py             # Тесты модуля reports
├── main.py                         # Точка входа для проверки функциональности
├── .env                            # Файл переменных окружения (ключи API)
├── pyproject.toml                  # Конфигурация проекта (Poetry)
├── poetry.lock                     # Зависимости проекта
├── user_settings.json              # Настройки пользователя (валюты, акции)
└── README.md                       # Описание проекта
```

---

## ⚙️ Настройка файла `.env`

Для работы проекта необходим файл `.env`, расположенный в корне проекта, с переменными:

```env
FINNHUB_API_KEY=your_currency_api_key
```
https://finnhub.io/ - ссылка на API
---

## 🧠 Функциональность модулей

### 🔸 `main.py`
Точка входа для проверки работы функций:
- Данные главной страницы
- Анализ кешбэка
- Инвесткопилка
- Простой поиск
- Поиск телефонных номеров
- Генерация отчётов

### 🔸 `views.py`
Генерация JSON-данных для веб-интерфейса:
- `generate_main_page_data(date_str)`
- `get_greeting(hour)`
- `get_user_settings(filepath)`
- `get_currency_rates(currencies)`

### 🔸 `utils.py`
Работа с Excel-файлами и фильтрация данных:
- `load_excel_data(filepath)`
- `filter_by_date_range(df, end_date)`

### 🔸 `services.py`
Дополнительные сервисы обработки данных:
- `analyze_cashback_categories(data, year, month)` — расчёт выгодности категорий кешбэка
- `investment_bank(month, transactions, limit)` — расчёт суммы накоплений
- `simple_search(data, query)` — простой поиск транзакций
- `phone_search(data)` — поиск транзакций с телефонами

### 🔸 `reports.py`
Генерация и сохранение отчётов в JSON-файлы с помощью декораторов:
- Декоратор: `@save_report(filename: Optional[str])`
- `spending_by_category(transactions, category, date)` — отчёт по тратам по категориям
- `spending_by_weekday(transactions, date)` — отчёт по средним тратам по дням недели

---

## ✅ Тестирование

Модули протестированы с покрытием не менее 90%. Используется библиотека `pytest`:
- `test_utils.py` — тестирование загрузки и фильтрации данных
- `test_views.py` — тестирование генерации JSON, настройки и API валют
- `test_services.py` — тестирование сервисов анализа и поиска
- `test_reports.py` — тестирование отчётов и сохранения файлов через декоратор

---

## 📦 Установка и запуск

```bash
git clone https://github.com/yourname/transaction-analyzer.git
cd transaction-analyzer
poetry install
```

Запуск приложения:

```bash
poetry run python src/main.py
```

Запуск тестов:

```bash
poetry run pytest --cov=src tests/
```