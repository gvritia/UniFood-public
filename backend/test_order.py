"""
Тест создания заказа
Запуск: py test_order.py
"""

import requests

BASE_URL = "http://localhost:8001"

# 1. Регистрируем пользователя
print("1. Регистрация пользователя...")
reg_data = {
    "email": "testorder@test.com",
    "name": "Test Order",
    "password": "123456",
    "is_admin": False
}
reg_resp = requests.post(f"{BASE_URL}/users/", json=reg_data)
print(f"   Статус: {reg_resp.status_code}")
if reg_resp.status_code != 201:
    print(f"   Ошибка: {reg_resp.text}")
    exit(1)
user = reg_resp.json()
user_id = user["id"]
print(f"   Пользователь создан: {user['email']} (ID: {user_id})")

# 2. Логинимся
print("\n2. Логин...")
login_data = {"username": "testorder@test.com", "password": "123456"}
login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
print(f"   Статус: {login_resp.status_code}")
if login_resp.status_code != 200:
    print(f"   Ошибка: {login_resp.text}")
    exit(1)
token = login_resp.json()["access_token"]
print(f"   Токен получен")

# 3. Пополняем баланс
print("\n3. Пополнение баланса...")
headers = {"Authorization": f"Bearer {token}"}
balance_resp = requests.post(f"{BASE_URL}/profile/balance", json={"amount": 5000}, headers=headers)
print(f"   Статус: {balance_resp.status_code}")
if balance_resp.status_code != 200:
    print(f"   Ошибка: {balance_resp.text}")
    exit(1)
balance = balance_resp.json()["balance"]
print(f"   Баланс: {balance} ₽")

# 4. Добавляем товар в корзину
print("\n4. Добавление товара в корзину...")
cart_data = {"menu_item_id": 1, "quantity": 2}
cart_resp = requests.post(f"{BASE_URL}/cart/", json=cart_data, headers=headers)
print(f"   Статус: {cart_resp.status_code}")
if cart_resp.status_code != 201:
    print(f"   Ошибка: {cart_resp.text}")
    exit(1)
print(f"   Товар добавлен")

# 5. Получаем корзину
print("\n5. Получение корзины...")
cart_get_resp = requests.get(f"{BASE_URL}/cart/", headers=headers)
print(f"   Статус: {cart_get_resp.status_code}")
if cart_get_resp.status_code != 200:
    print(f"   Ошибка: {cart_get_resp.text}")
    exit(1)
cart = cart_get_resp.json()
print(f"   Корзина: {len(cart.get('items', []))} товаров, сумма: {cart.get('total_price', 0)} ₽")

# 6. Создаем заказ
print("\n6. Создание заказа...")
order_resp = requests.post(f"{BASE_URL}/orders/", headers=headers)
print(f"   Статус: {order_resp.status_code}")
if order_resp.status_code != 201:
    print(f"   Ошибка: {order_resp.text}")
    exit(1)
order = order_resp.json()
print(f"   Заказ создан: {order}")

# 7. Получаем историю заказов
print("\n7. Получение истории заказов...")
orders_resp = requests.get(f"{BASE_URL}/orders/", headers=headers)
print(f"   Статус: {orders_resp.status_code}")
if orders_resp.status_code != 200:
    print(f"   Ошибка: {orders_resp.text}")
    exit(1)
orders = orders_resp.json()
print(f"   Найдено заказов: {len(orders)}")
for o in orders:
    print(f"   - Заказ #{o['id']} ({o['order_number']}): {o['total_price']} ₽, статус: {o['status']}")

# 8. Проверяем баланс после заказа
print("\n8. Проверка баланса после заказа...")
profile_resp = requests.get(f"{BASE_URL}/profile/me", headers=headers)
if profile_resp.status_code == 200:
    profile = profile_resp.json()
    print(f"   Баланс: {profile['balance']} ₽")

print("\n✅ Тест завершен успешно!")
