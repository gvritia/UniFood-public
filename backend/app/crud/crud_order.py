from sqlalchemy.orm import Session, selectinload
from app.models.models_order import Order, OrderItem, OrderStatus
from app.models.models_cart import CartItem
from app.models.models_user import User
from app.services.order_number import new_order_number
from app.exceptions import CartEmptyException, InsufficientBalanceException


ORDER_RESPONSE_OPTIONS = (
    selectinload(Order.items).selectinload(OrderItem.menu_item),
    selectinload(Order.user),
)


def load_order_for_response(db: Session, order_id: int) -> Order:
    """Load the full response graph in a bounded number of queries."""
    return (
        db.query(Order)
        .options(*ORDER_RESPONSE_OPTIONS)
        .populate_existing()
        .filter(Order.id == order_id)
        .one()
    )


def create_order_from_cart(db: Session, user_id: int) -> Order:
    """Создать заказ из корзины авторизованного пользователя"""
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        raise ValueError("Пользователь не найден")

    # Получаем корзину. Используем .all(), чтобы сразу выгрузить всё в память.
    # selectinload гарантирует, что данные о блюдах будут загружены одним махом.
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .options(selectinload(CartItem.menu_item))
        .all()
    )

    if not cart_items:
        raise CartEmptyException()

    if any(ci.quantity <= 0 or ci.menu_item is None for ci in cart_items):
        raise ValueError("Корзина содержит недоступные или некорректные позиции")

    total_price = sum(ci.quantity * (ci.menu_item.price if ci.menu_item else 0) for ci in cart_items)
    total_price = round(total_price, 2)

    # Округляем до 2 знаков, чтобы избежать проблем с float
    if round(user.balance, 2) < total_price:
        raise InsufficientBalanceException(balance=round(user.balance, 2), required=total_price)

    # Уменьшаем баланс (округляем до 2 знаков)
    user.balance = round(user.balance - total_price, 2)

    # Создаём заказ
    new_order = Order(
        user_id=user_id,
        total_price=total_price,
        status=OrderStatus.NEW,
        order_number=new_order_number()
    )
    
    # Добавляем позиции заказа, НЕ используя flush() раньше времени
    for ci in cart_items:
        new_order.items.append(OrderItem(
            menu_item_id=ci.menu_item_id,
            quantity=ci.quantity,
            price_at_order=ci.menu_item.price if ci.menu_item else 0.0
        ))
    
    db.add(new_order)

    # Очистка корзины ПЕРЕД коммитом. 
    # Не синхронизируем уже загруженные объекты: после коммита сессия обновится.
    db.query(CartItem).filter(CartItem.user_id == user_id).delete(synchronize_session=False)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return load_order_for_response(db, new_order.id)


def get_user_orders(db: Session, user_id: int):
    """История заказов пользователя"""
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .options(*ORDER_RESPONSE_OPTIONS)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order(db: Session, order_id: int, user_id: int) -> Order | None:
    """Получить один заказ с полными данными"""
    return (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == user_id)
        .options(*ORDER_RESPONSE_OPTIONS)
        .first()
    )


def update_order_status(db: Session, order_id: int, new_status: OrderStatus, user_id: int | None = None) -> Order | None:
    """Изменить статус заказа с возвратом денег при отмене и блокировкой после 'выдан'"""
    query = db.query(Order).filter(Order.id == order_id)
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    order = query.with_for_update().first()
    if not order:
        return None

    # Задача 11: После статуса "completed" (выдан) или "cancelled" (отменён) нельзя изменить статус
    if order.status == OrderStatus.COMPLETED:
        raise ValueError("Нельзя изменить статус заказа после того, как он был выдан")
    if order.status == OrderStatus.CANCELLED:
        raise ValueError("Нельзя изменить статус отменённого заказа")

    # Задача 9: Возврат денег на баланс при отмене заказа
    if new_status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        # Заказ переходит в "отменён" — возвращаем деньги
        if order.user_id is not None:
            user = db.query(User).filter(User.id == order.user_id).with_for_update().first()
            if user:
                user.balance = round(user.balance + order.total_price, 2)

    order.status = new_status
    db.commit()
    return load_order_for_response(db, order.id)
