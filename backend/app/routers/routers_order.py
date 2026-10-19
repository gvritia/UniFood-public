from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timezone

from ..db import get_db
from ..api.auth import get_current_user
from ..schemas.schemas_user import UserResponse
from ..schemas.schemas_order import OrderResponse, OrderStatusUpdate
from ..schemas.schemas_cart import CartItemCreate
from ..crud.crud_order import create_order_from_cart, get_user_orders, get_order, update_order_status
from ..crud.crud_cart import add_to_cart, clear_cart
from ..crud.crud_menu import menu_crud
from ..services.payment_stub import payment_stub
from ..services.iiko_stub import iiko_stub
from ..services.order_tasks import change_order_status_after_delay
from ..models.models_order import Order, OrderItem, OrderStatus
from app.exceptions import CartEmptyException, InsufficientBalanceException


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    background_tasks: BackgroundTasks,          # ← добавлено
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать заказ из текущей корзины"""
    try:
        order = create_order_from_cart(db, current_user.id)

        # Автоматическая смена статуса в фоне
        background_tasks.add_task(change_order_status_after_delay, order.id, delay_seconds=40)

        return order
    except (CartEmptyException, InsufficientBalanceException) as e:
        raise e
    except Exception as e:
        import traceback
        print(f"ERROR creating order: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Ошибка при создании заказа: {str(e)}")


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
        updated = update_order_status(db, order_id, status_update.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if updated.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return updated


@router.post("/guest", response_model=OrderResponse)
def create_guest_order(
    order_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Создание заказа для гостя (без авторизации)"""
    if "items" not in order_data or "total" not in order_data:
        raise HTTPException(status_code=400, detail="Требуются поля 'items' и 'total'")

    items = order_data["items"]
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="Поле 'items' должно быть непустым списком")

    total = 0.0
    items_data = []

    for it in items:
        if "menu_item_id" not in it or "quantity" not in it:
            raise HTTPException(status_code=400, detail="Каждый item должен содержать menu_item_id и quantity")

        menu_item = menu_crud.get_menu_item(db, it["menu_item_id"])
        if not menu_item:
            raise HTTPException(status_code=400, detail=f"Товар с id {it['menu_item_id']} не найден")

        item_total = menu_item.price * it["quantity"]
        total += item_total

        items_data.append({
            "menu_item_id": it["menu_item_id"],
            "name": menu_item.food_name,
            "quantity": it["quantity"],
            "price": menu_item.price
        })

    if abs(total - float(order_data["total"])) > 0.01:
        raise HTTPException(status_code=400, detail="Сумма не совпадает с расчётом на сервере")

    # Имитация оплаты и отправки в iiko
    payment_stub.process_payment({"total": total})

    stub_data = {
        "user_id": None,
        "total": total,
        "items": items_data,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    order_number = iiko_stub.send_order(stub_data)

    new_order = Order(
        user_id=None,
        total_price=total,
        status=OrderStatus.NEW,
        order_number=order_number
    )
    
    # Добавляем позиции через коллекцию, чтобы SQLAlchemy сам всё разрулил
    for it in items:
        menu_item = menu_crud.get_menu_item(db, it["menu_item_id"])
        new_order.items.append(OrderItem(
            menu_item_id=it["menu_item_id"],
            quantity=it["quantity"],
            price_at_order=menu_item.price
        ))

    db.add(new_order)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

    # Очищаем текущую корзину и добавляем товары из прошлого заказа
    clear_cart(db, current_user.id)

    for item in order.items:
        add_to_cart(db, current_user.id, CartItemCreate(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        ))

    # Создаём новый заказ
    new_order = create_order_from_cart(db, current_user.id)

    # Запускаем автоматическую смену статуса
    background_tasks.add_task(change_order_status_after_delay, new_order.id, delay_seconds=40)

    return new_order