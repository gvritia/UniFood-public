# Добавляем BackgroundTasks для автоматической смены статуса
import asyncio
from sqlalchemy.orm import Session
from app.models.models_order import Order, OrderStatus
from app.db import SessionLocal


async def change_order_status_after_delay(order_id: int, delay_seconds: int = 45):
    """Автоматически меняет статус заказа: NEW → PREPARING → READY"""
    await asyncio.sleep(delay_seconds)

    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return

        if order.status == OrderStatus.NEW:
            order.status = OrderStatus.PREPARING
            db.commit()
            print(f"[BACKGROUND] Заказ {order.order_number} → PREPARING")

            # Ещё одна задержка до READY
            await asyncio.sleep(35)
            order = db.query(Order).filter(Order.id == order_id).first()
            if order and order.status == OrderStatus.PREPARING:
                order.status = OrderStatus.READY
                db.commit()
                print(f"[BACKGROUND] Заказ {order.order_number} → READY")

    finally:
        db.close()