import asyncio
from app.models.models_order import Order, OrderStatus
from app.db import SessionLocal


async def change_order_status_after_delay(order_id: int, delay_seconds: int = 45):
    """Автоматически меняет статус заказа: NEW → PREPARING → READY"""
    await asyncio.sleep(delay_seconds)

    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.status != OrderStatus.NEW:
            return
        order.status = OrderStatus.PREPARING
        db.commit()

    await asyncio.sleep(35)
    with SessionLocal() as db:
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order and order.status == OrderStatus.PREPARING:
                order.status = OrderStatus.READY
                db.commit()
        except Exception:
            db.rollback()
            raise
