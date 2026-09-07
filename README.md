# CRM FastAPI Vue

CRM-система (FastAPI async + Vue 3) — переписана с Django по ТЗ Skillbox.

## Быстрый старт

### Backend
```bash
cd crm_fastapi_vue/backend
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# Docs: http://127.0.0.1:8000/docs
```

### Frontend
```bash
cd crm_fastapi_vue/frontend
npm install
npm run dev
# http://localhost:5173
# логин: admin / admin123
```

Подробнее — см. `instructions.docx` в корне проекта и в `crm_fastapi_vue/`.

## Структура
```
crm_fastapi_vue/
├── backend/   # FastAPI async, SQLAlchemy, JWT, SQLite/PostgreSQL
└── frontend/  # Vue 3 + Vite + Pinia + Axios + Bootstrap
```

## Демо-аккаунты
- admin / admin123 (админ, всё)
- operator1 / operator123 (лиды)
- marketer1 / marketer123 (услуги, реклама)
- manager1 / manager123 (контракты, клиенты)

## API
- `POST /api/auth/login` — JWT
- CRUD: `/api/products`, `/api/ads`, `/api/leads`, `/api/contracts`, `/api/customers`, `/api/users`
- Статистика: `/api/ads/statistic`, `/api/stats/dashboard`
- Swagger: http://127.0.0.1:8000/docs

## Особенности
- Async SQLAlchemy, зависимости RBAC
- SQLite по умолчанию (файл `backend/crm.db`), PostgreSQL опционально
- Загрузка файлов контрактов в `backend/media/contracts/`
- SPA с прокси Vite `/api` → `http://localhost:8000`

## Проверка без запуска сервера
```bash
cd backend
python -c "import sys; sys.path.insert(0,'.'); from app.main import app; print(app.title)"
```
