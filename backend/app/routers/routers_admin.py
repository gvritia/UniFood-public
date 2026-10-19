from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
from datetime import date

from ..db import get_db
from ..dependencies import get_current_admin
from ..schemas.schemas_user import UserResponse
from ..schemas.schemas_order import OrderResponse, OrderStatusUpdate, OrderStatus
from ..crud.crud_order import update_order_status
from ..models.models_order import Order
from ..models.models_user import User
from sqlalchemy import func, desc, asc

router = APIRouter(prefix="/admin", tags=["admin"])


# ====================== СТАТИСТИКА ======================
@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
):
    """Общая статистика для админ-панели (красиво для защиты курсовой)"""
    total_users = db.query(func.count(User.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.total_price)).scalar() or 0.0

    # Выручка за сегодня
    today = date.today()
    today_revenue = db.query(func.sum(Order.total_price)).filter(
        func.date(Order.created_at) == today
    ).scalar() or 0.0

    # Количество заказов по статусам
    status_counts = db.query(
        Order.status,
        func.count(Order.id).label("count")
    ).group_by(Order.status).all()

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": round(float(total_revenue), 2),
        "today_revenue": round(float(today_revenue), 2),
        "orders_by_status": {status.value: count for status, count in status_counts}
    }


# ====================== ЗАКАЗЫ ======================
@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    sort_by: str = Query("created_at", description="created_at | total_price | status | order_number"),
    order: str = Query("desc", description="asc | desc"),
    status_filter: Optional[OrderStatus] = None,
    search: Optional[str] = Query(None, description="Поиск по номеру заказа или email пользователя"),
):
    """Просмотр всех заказов + поиск + сортировка"""
    query = db.query(Order)

    if status_filter:
        query = query.filter(Order.status == status_filter)

    if search:
        query = query.filter(
            Order.order_number.ilike(f"%{search}%")
        )

    # Сортировка
    if sort_by == "total_price":
        query = query.order_by(Order.total_price.desc() if order == "desc" else Order.total_price.asc())
    elif sort_by == "status":
        query = query.order_by(Order.status.desc() if order == "desc" else Order.status.asc())
    elif sort_by == "order_number":
        query = query.order_by(Order.order_number.desc() if order == "desc" else Order.order_number.asc())
    else:
        query = query.order_by(Order.created_at.desc() if order == "desc" else Order.created_at.asc())

    return query.offset(skip).limit(limit).all()


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def admin_change_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
):
    """Админ меняет статус любого заказа"""
    try:
        updated = update_order_status(db, order_id, status_update.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return updated


@router.get("/orders/{order_id}/download")
def download_order(
    order_id: int,
    format: str = Query("json", description="json или txt"),
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
):
    """Скачать заказ в JSON или в виде чека TXT"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if format == "json":
        return JSONResponse(
            content={
                "order_number": order.order_number,
                "created_at": order.created_at.isoformat(),
                "total_price": order.total_price,
                "status": order.status.value,
                "items": [
                    {
                        "name": item.menu_item.food_name if item.menu_item else "Товар удалён",
                        "quantity": item.quantity,
                        "price": item.price_at_order,
                        "subtotal": round(item.quantity * item.price_at_order, 2)
                    } for item in order.items
                ]
            },
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="order_{order.order_number}.json"'}
        )

    # TXT-чек
    txt_content = f"""ЧЕК № {order.order_number}
Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}
Статус: {order.status.value.upper()}

ПОЗИЦИИ:
"""
    for item in order.items:
        name = item.menu_item.food_name if item.menu_item else "Товар удалён"
        txt_content += f"{name} ×{item.quantity} = {item.quantity * item.price_at_order:.2f} ₽\n"

    txt_content += f"\nИТОГО: {order.total_price:.2f} ₽\n"
    txt_content += "Спасибо за заказ в UniFood! 👋\n"

    return StreamingResponse(
        io.StringIO(txt_content),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="check_{order.order_number}.txt"'}
    )


# ====================== ПОЛЬЗОВАТЕЛИ ======================
@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    sort_by: str = Query("created_at", description="created_at | name | email | balance"),
    order: str = Query("desc", description="asc | desc"),
    search: Optional[str] = Query(None, description="Поиск по имени или email"),
):
    """Просмотр всех пользователей + поиск + сортировка"""
    query = db.query(User)

    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    sort_column = {
        "name": User.name,
        "email": User.email,
        "balance": User.balance,
        "created_at": User.created_at,
    }.get(sort_by, User.created_at)

    direction = desc if order == "desc" else asc
    query = query.order_by(direction(sort_column))

    return query.offset(skip).limit(limit).all()