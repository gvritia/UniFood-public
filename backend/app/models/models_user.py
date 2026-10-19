from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

# Модель SQLAlchemy - это описание таблицы в базе данных
class User(Base):
    # Имя таблицы в базе данных
    __tablename__ = "users"

    # Колонки таблицы
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)  # Баланс пользователя
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Связи с другими моделями
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")  # Связь с заказами

    def __repr__(self):
        return f"<User {self.email}>"