from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from ..db import Base


class OrderStatus(str, PyEnum):
    NEW = "new"               # только что создан после оплаты
    PREPARING = "preparing"   # в процессе приготовления (можно вручную менять)
    READY = "ready"           # готов к выдаче
    COMPLETED = "completed"   # выдан / завершён
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW, nullable=False)
    order_number = Column(String(20), unique=True, nullable=False)  # от stub iiko
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    user = relationship("User", back_populates="orders")  # Связь с пользователем


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Float, nullable=False)   # цена на момент заказа (фиксация)

    # Связи
    order = relationship("Order", back_populates="items")
    menu_item = relationship("Menu")  # Добавляем связь с меню