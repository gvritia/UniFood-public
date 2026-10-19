from fastapi import HTTPException, status

class UniFoodException(HTTPException):
    """Базовое исключение для нашего приложения"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class CartEmptyException(UniFoodException):
    def __init__(self):
        super().__init__(
            detail="Корзина пуста. Добавьте товары перед оформлением заказа.",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class InsufficientBalanceException(UniFoodException):
    def __init__(self, balance: float, required: float):
        super().__init__(
            detail=f"Недостаточно средств на балансе. Текущий баланс: {balance:.2f} ₽, требуется: {required:.2f} ₽",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class OrderNotFoundException(UniFoodException):
    def __init__(self):
        super().__init__(
            detail="Заказ не найден или у вас нет доступа к нему.",
            status_code=status.HTTP_404_NOT_FOUND
        )