from sqlalchemy import Column, Integer, String, Float, DateTime # Boolean
from datetime import datetime
from ..db import Base

# Модель SQLAlchemy - это описание таблицы в базе данных
class Menu(Base):
    # Имя таблицы в базе данных
    __tablename__ = "menu"

    # Колонки таблицы
    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    ingredients = Column(String(500), nullable=True)
    description = Column(String(1000), nullable=True)
    image_url = Column(String(300), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow())
    calories = Column(Integer, nullable=True)

    def __repr__(self):
        """Строковое представление объекта"""
        return f"MenuItem(id={self.id}, name='{self.food_name}', price={self.price}, category='{self.category}')"

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "food_name": self.food_name,
            "price": self.price,
            "category": self.category,
            "ingredients": self.ingredients,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "calories": self.calories
        }