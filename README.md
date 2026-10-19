# 🍽️ UniFood - Система онлайн-заказа еды

## Описание
Онлайн-заказ еды в столовой вуза. Быстро, удобно и вкусно!

## 📁 Структура проекта

```
UniFood/
├── backend/              # FastAPI бэкенд
│   ├── app/
│   │   ├── api/         # API эндпоинты (auth)
│   │   ├── crud/        # CRUD операции
│   │   ├── models/      # SQLAlchemy модели
│   │   ├── routers/     # API роутеры
│   │   ├── schemas/     # Pydantic схемы
│   │   ├── services/    # Сервисы (payment, iiko stubs)
│   │   ├── config.py    # Конфигурация
│   │   ├── db.py        # Настройки БД
│   │   └── main.py      # Точка входа
│   ├── .env             # Переменные окружения
│   └── requirements.txt # Зависимости Python
│
└── frontend/
    └── unifood-frontend/    # React фронтенд
        ├── src/
        │   ├── api/         # API клиенты
        │   ├── components/  # UI компоненты
        │   ├── contexts/    # React Context
        │   ├── pages/       # Страницы
        │   └── App.jsx      # Главный компонент
        ├── .env             # Переменные окружения
        └── package.json     # Зависимости Node.js
```

## 🚀 Запуск проекта

### 1. Запуск бэкенда

```bash
cd c:\Users\muham\UniFood\backend

# Установка зависимостей (если еще не установлены)
py -m pip install -r requirements.txt

# Запуск сервера на порту 8001
py -m uvicorn app.main:app --reload --port 8001
```

**API документация**: http://localhost:8001/docs

### 2. Запуск фронтенда

```bash
cd c:\Users\muham\UniFood\frontend\unifood-frontend

# Установка зависимостей (если еще не установлены)
npm install

# Запуск dev-сервера
npm run dev
```

**Фронтенд**: http://localhost:5173 (или 5174)

## 🔧 Конфигурация

### Бэкенд (.env)
```env
DATABASE_URL=sqlite:///./unifood.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Фронтенд (.env)
```env
VITE_API_URL=http://localhost:8001
```

## 📱 Страницы фронтенда

| Страница | Маршрут | Описание |
|----------|---------|----------|
| Главная | `/` | Приветственная страница |
| Меню | `/menu` | Каталог блюд с фильтрами |
| Корзина | `/cart` | Управление корзиной (требуется вход) |
| Заказы | `/orders` | История заказов (требуется вход) |
| Вход | `/auth/login` | Авторизация |
| Регистрация | `/auth/register` | Регистрация нового пользователя |

## 🛠️ Технологии

### Бэкенд
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM
- **Pydantic** - валидация данных
- **JWT (python-jose)** - аутентификация
- **Passlib** - хеширование паролей
- **SQLite** - база данных (для разработки)

### Фронтенд
- **React 19** - UI библиотека
- **React Router** - маршрутизация
- **Material-UI (MUI)** - компоненты
- **Axios** - HTTP клиент
- **Vite** - сборщик

## 📦 Тестовые данные

Для заполнения меню тестовыми блюдами:

```bash
cd c:\Users\muham\UniFood\backend
py -m app.create_sample_data
```

Будут созданы:
- Пицца Маргарита, Пицца Пепперони
- Бургер Классический, Бургер Чизбургер
- Цезарь с курицей, Греческий салат
- Кола, Лимонад
- Чизкейк
- Паста Карбонара

## 🔑 Регистрация и вход

1. Откройте http://localhost:5173/auth/register
2. Введите имя, email и пароль
3. После регистрации войдите на странице /auth/login
4. Теперь доступен заказ блюд из меню!

## 📝 API Endpoints

### Авторизация
- `POST /auth/login` - Вход (email + password)
- `GET /auth/me` - Получение текущего пользователя

### Пользователи
- `POST /users/` - Регистрация
- `GET /users/` - Список пользователей (admin)
- `GET /users/{id}` - Информация о пользователе
- `PUT /users/{id}` - Обновление данных
- `DELETE /users/{id}` - Удаление

### Меню
- `GET /menu/` - Получить меню (с фильтрами)
- `GET /menu/{id}` - Получить блюдо
- `POST /menu/` - Добавить блюдо (admin)
- `PUT /menu/{id}` - Обновить блюдо (admin)
- `DELETE /menu/{id}` - Удалить блюдо (admin)

### Корзина
- `GET /cart/` - Получить корзину
- `POST /cart/` - Добавить в корзину
- `PATCH /cart/{id}` - Обновить количество
- `DELETE /cart/{id}` - Удалить позицию
- `DELETE /cart/` - Очистить корзину

### Заказы
- `POST /orders/` - Создать заказ
- `GET /orders/` - История заказов
- `GET /orders/{id}` - Детали заказа
- `PATCH /orders/{id}/status` - Изменить статус

## 👥 Авторы
UniFood Team - 2026
