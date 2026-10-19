import random
import string
from datetime import datetime


class IikoStub:
    @staticmethod
    def send_order(order_data: dict) -> str:
        """
        Имитация отправки заказа в iiko.
        Возвращает уникальный номер заказа.
        """
        # Генерируем фейковый номер (4 случайные цифры: например, #4829)
        random_part = random.randint(1000, 9999)
        order_number = f"#{random_part}"

        # Здесь можно добавить print или лог, чтобы видеть, что "отправили"
        print(f"[IIKO STUB] Заказ отправлен: {order_number}, данные: {order_data}")

        return order_number


iiko_stub = IikoStub()