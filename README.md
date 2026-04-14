# ValoriumGPT

Чат-приложение на базе Gemini AI. Бекенд на FastAPI, фронтенд — чистый HTML/JS.

## Стек

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, SQLite
- **AI:** Google Gemini (`gemini-3-flash-preview`)
- **Frontend:** HTML + JS (marked.js для рендера markdown)

## Структура

```
├── main.py            # FastAPI приложение, роуты
├── db.py              # Модели и работа с БД
├── gemini_client.py   # Клиент Gemini API
├── frontend/
│   └── index.html     # Фронтенд
└── pyproject.toml
```

## Запуск

**1. Установи зависимости**

```bash
uv sync
```

**2. Создай файл `config.py` с API ключом**

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    gemini_api_key: str

config_obj = Config()
```

И `.env` файл:

```
GEMINI_API_KEY=your_key_here
```

**3. Запусти сервер**

```bash
uvicorn main:app --reload
```

**4. Открой фронтенд**

Открой `frontend/index.html` через Live Server в VS Code.

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/requests` | История запросов текущего пользователя (по IP) |
| `POST` | `/requests` | Отправить промпт, получить ответ от Gemini |

**POST /requests — тело запроса:**

```json
{ "prompt": "Твой вопрос" }
```

**Ответ:**

```json
{ "answer": "Ответ от Gemini" }
```
