from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..db import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    # Связи для удобства
    user = relationship("User", back_populates="cart_items")
    menu_item = relationship("Menu")

    # Запрещаем дубли одной позиции у одного пользователя
    __table_args__ = (
        UniqueConstraint("user_id", "menu_item_id", name="unique_user_menu_item"),
    )