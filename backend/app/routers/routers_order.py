from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from ..api.auth import get_current_user
from ..schemas.schemas_user import UserResponse
from ..schemas.schemas_order import GuestOrderCreate, OrderResponse, OrderStatusUpdate
from ..crud.crud_order import create_order_from_cart, get_user_orders, get_order, update_order_status
from ..crud.crud_menu import menu_crud
from ..services.payment_stub import payment_stub
from ..services.order_number import new_order_number
from ..services.order_tasks import change_order_status_after_delay
from ..models.models_order import Order, OrderItem, OrderStatus
from ..models.models_cart import CartItem


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать заказ из текущей корзины"""
    try:
        order = create_order_from_cart(db, current_user.id)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    background_tasks.add_task(change_order_status_after_delay, order.id, delay_seconds=40)
    return order


@router.get("/", response_model=List[OrderResponse])
def get_my_orders(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить историю заказов текущего пользователя"""
    return get_user_orders(db, current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_my_order(
    order_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден или не принадлежит вам")
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def change_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Изменить статус заказа (для демонстрации)"""
    try:
        updated = update_order_status(db, order_id, status_update.status, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return updated


@router.post("/guest", response_model=OrderResponse)
def create_guest_order(
    order_data: GuestOrderCreate,
    db: Session = Depends(get_db)
):
    """Создание заказа для гостя (без авторизации)"""
    total = 0.0

    new_order = Order(
        user_id=None,
        status=OrderStatus.NEW,
        order_number=new_order_number(),
    )

    for item in order_data.items:
        menu_item = menu_crud.get_menu_item(db, item.menu_item_id)
        if not menu_item:
            raise HTTPException(status_code=400, detail=f"Товар с id {item.menu_item_id} не найден")

        total += menu_item.price * item.quantity
        new_order.items.append(OrderItem(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price_at_order=menu_item.price,
        ))

    total = round(total, 2)
    if abs(total - order_data.total) > 0.01:
        raise HTTPException(status_code=400, detail="Сумма не совпадает с расчётом на сервере")

    # Демонстрационная оплата; реальный платёжный провайдер не подключён.
    payment_stub.process_payment({"total": total})
    new_order.total_price = total

    db.add(new_order)
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(new_order)
    return new_order


@router.post("/{order_id}/repeat", response_model=OrderResponse, status_code=201)
def repeat_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Повторить предыдущий заказ"""
    order = get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if not order.items:
        raise HTTPException(status_code=400, detail="В заказе нет товаров")

    if any(item.menu_item is None or item.menu_item_id is None for item in order.items):
        raise HTTPException(status_code=400, detail="Один из товаров прошлого заказа больше недоступен")

    try:
        db.query(CartItem).filter(CartItem.user_id == current_user.id).delete(synchronize_session=False)
        db.add_all(
            CartItem(user_id=current_user.id, menu_item_id=item.menu_item_id, quantity=item.quantity)
            for item in order.items
        )
        db.flush()
        new_order = create_order_from_cart(db, current_user.id)
    except Exception:
        db.rollback()
        raise

    # Запускаем автоматическую смену статуса
    background_tasks.add_task(change_order_status_after_delay, new_order.id, delay_seconds=40)

    return new_order
