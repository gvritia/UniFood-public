# REST API UniFood

Документ к пункту 20 практического занятия. API реализован на FastAPI; актуальная машинная схема доступна по `/openapi.json`, интерактивный просмотр — по `/docs` и `/redoc`.

## Адреса и соглашения

- Прямой адрес backend в Docker Compose: `http://localhost:8001`. Пути ниже указаны относительно него. Через frontend те же запросы доступны с префиксом `/api`, например `http://localhost:8080/api/menu/`.
- Запросы и ответы используют JSON, кроме `/auth/login` (форма) и загрузки изображения (multipart). Идентификаторы — целые числа. Денежные суммы в текущем API — числа с двумя знаками после округления бизнес-логикой.
- Защищённые методы требуют заголовок `Authorization: Bearer <access_token>`. Для методов администратора дополнительно нужна роль `is_admin`.
- У маршрутов со слешем на конце (`/menu/`, `/orders/` и другие) следует сохранять слеш: FastAPI может перенаправить запрос без него.
- Ошибки FastAPI имеют вид `{"detail": "сообщение"}`; ошибки проверки входных данных возвращают `422` и массив деталей. `401` означает отсутствующий или недействительный токен, `403` — недостаточно прав, `404` — отсутствие ресурса, `400` — нарушение бизнес-правил.

## Регистрация и вход

| Метод и путь | Доступ | Запрос | Успешный ответ |
| --- | --- | --- | --- |
| `POST /users/` | Публичный | `UserCreate` | `201 UserResponse` |
| `POST /auth/login` | Публичный | Форма `username` (email), `password` | `200 TokenResponse` |
| `GET /auth/me` | Пользователь | — | `200 UserResponse` |

Пароль при регистрации должен содержать минимум 8 символов, заглавную и строчную букву, цифру и спецсимвол. В ответе `UserResponse` нет пароля и его хеша.

```bash
curl.exe -X POST http://localhost:8001/users/ -H "Content-Type: application/json" -d '{"email":"student@example.com","name":"Студент","password":"StrongPass1!"}'
curl.exe -X POST http://localhost:8001/auth/login -d "username=student@example.com" -d "password=StrongPass1!"
```

Ответ входа содержит `access_token`, `token_type: "bearer"` и объект `user`. В следующих примерах `<JWT>` означает значение `access_token`.

## Меню

| Метод и путь | Доступ | Запрос | Успешный ответ |
| --- | --- | --- | --- |
| `GET /menu/` | Публичный | `skip`, `limit`, `category`, `q` в строке запроса | `200 MenuItemResponse[]` |
| `GET /menu/{item_id}` | Публичный | ID в пути | `200 MenuItemResponse` |
| `POST /menu/` | Администратор | `MenuItemCreate` | `201 MenuItemResponse` |
| `PUT /menu/{item_id}` | Администратор | `MenuItemUpdate` | `200 MenuItemResponse` |
| `DELETE /menu/{item_id}` | Администратор | ID в пути | `204`, без тела |
| `POST /menu/{item_id}/image` | Администратор | Multipart-поле `file` с JPEG, PNG или WebP | `200 MenuItemResponse` |

`MenuItemCreate` содержит `food_name`, `price`, `category` и необязательные `ingredients`, `description`, `image_url`, `calories`. `MenuItemResponse` добавляет `id`, `created_at`, `updated_at`. `q` ищет по названию блюда; `category` фильтрует по категории.

```bash
curl.exe "http://localhost:8001/menu/?category=Напитки&q=чай&skip=0&limit=20"
curl.exe -X POST http://localhost:8001/menu/ -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" -d '{"food_name":"Чай","price":80,"category":"Напитки"}'
```

## Корзина

Все методы раздела требуют входа. `CartResponse` содержит массив `items` и пересчитанный на сервере `total_price`.

| Метод и путь | Запрос | Успешный ответ |
| --- | --- | --- |
| `GET /cart/` | — | `200 CartResponse` |
| `POST /cart/` | `{"menu_item_id": 1, "quantity": 2}` | `201 CartItemResponse` |
| `PATCH /cart/{cart_item_id}` | `{"quantity": 3}` | `200 CartItemResponse` |
| `DELETE /cart/{cart_item_id}` | — | `204`, без тела |
| `DELETE /cart/` | — | `204`, без тела |

`POST /cart/` увеличивает количество, если блюдо уже находится в корзине. `PATCH` с количеством не больше нуля удаляет позицию; текущая реализация возвращает `200` с `detail` об удалении, а не `CartItemResponse`.

## Заказы

`OrderResponse` содержит `id`, `order_number`, `status`, `total_price`, `created_at`, `updated_at`, `user_id`, `user` и массив `items`. Каждая позиция хранит `quantity` и `price_at_order`, поэтому история сохраняет цену на момент покупки. Статусы: `new`, `preparing`, `ready`, `completed`, `cancelled`.

| Метод и путь | Доступ | Запрос | Успешный ответ |
| --- | --- | --- | --- |
| `POST /orders/` | Пользователь | Пустое тело; заказ создаётся из текущей корзины | `201 OrderResponse` |
| `GET /orders/` | Пользователь | — | `200 OrderResponse[]` |
| `GET /orders/{order_id}` | Владелец | ID в пути | `200 OrderResponse` |
| `PATCH /orders/{order_id}/status` | Владелец | `{"status":"ready"}` | `200 OrderResponse` |
| `POST /orders/{order_id}/repeat` | Владелец | ID в пути | `201 OrderResponse` |
| `POST /orders/guest` | Публичный | `{"items":[{"menu_item_id":1,"quantity":2}],"total":160}` | `200 OrderResponse` |

При оформлении заказа из корзины backend проверяет товары, рассчитывает сумму, проверяет демонстрационный баланс и фиксирует заказ. Гостевой заказ проверяет сумму относительно текущих цен и использует демонстрационную оплату. `POST /orders/{order_id}/repeat` создаёт новый заказ по составу старого, если блюда ещё доступны.

```bash
curl.exe -X POST http://localhost:8001/cart/ -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" -d '{"menu_item_id":1,"quantity":2}'
curl.exe -X POST http://localhost:8001/orders/ -H "Authorization: Bearer <JWT>"
curl.exe http://localhost:8001/orders/ -H "Authorization: Bearer <JWT>"
```

## Профиль

Все методы требуют входа. `POST /profile/balance` меняет демонстрационный баланс; это не реальный платёж.

| Метод и путь | Запрос | Успешный ответ |
| --- | --- | --- |
| `GET /profile/me` | — | `200 UserResponse` |
| `PUT /profile/me` | `UserUpdate` | `200 UserResponse` |
| `GET /profile/balance` | — | `200 BalanceResponse`, например `{"balance":500}` |
| `POST /profile/balance` | `{"amount":500}` (положительное число) | `200 UserResponse` |

## Администрирование и пользователи

| Метод и путь | Доступ | Запрос | Успешный ответ |
| --- | --- | --- | --- |
| `GET /admin/stats` | Администратор | — | `200 AdminStatsResponse` |
| `GET /admin/orders` | Администратор | `skip`, `limit`, `sort_by`, `order`, `status_filter`, `search` | `200 OrderResponse[]` |
| `PATCH /admin/orders/{order_id}/status` | Администратор | `{"status":"ready"}` | `200 OrderResponse` |
| `GET /admin/orders/{order_id}/download` | Администратор | `format=json` или `format=txt` | `200`, файл JSON или TXT |
| `GET /admin/users` | Администратор | `skip`, `limit`, `sort_by`, `order`, `search` | `200 UserResponse[]` |
| `GET /users/` | Сейчас публичный | `skip`, `limit` | `200 UserResponse[]` |
| `GET /users/{user_id}` | Сейчас публичный | ID в пути | `200 UserResponse` |
| `PUT /users/{user_id}` | Сейчас публичный | `UserUpdate` | `200 UserResponse` |
| `DELETE /users/{user_id}` | Сейчас публичный | ID в пути | `200 UserResponse` |

`AdminStatsResponse` содержит числа пользователей и заказов, общую и сегодняшнюю выручку, а также `orders_by_status`. Маршруты `/users/` для чтения и изменения пользователей в текущей версии открыты без проверки роли; `UserCreate` сейчас принимает `is_admin`. Это ограничение текущей реализации, которое необходимо устранить в пункте об аутентификации и авторизации до открытого развёртывания. Удаление отдельной позиции корзины пока не проверяет её владельца; это также требует исправления.

## Служебные маршруты

`GET /health` возвращает `{"status":"healthy"}`. `GET /` возвращает приветствие backend. Статические изображения меню доступны по `/static/images/menu/{filename}`.
