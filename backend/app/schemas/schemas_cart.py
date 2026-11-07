from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

from .schemas_menu import MenuItemResponse


class CartItemBase(BaseModel):
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=99)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, ge=0, le=99)


class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    menu_item: Optional[MenuItemResponse] = None      # вложенный товар с ценой, названием и т.д.
    created_at: Optional[datetime] = None  # если добавишь поле в модель

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_price: float

    model_config = ConfigDict(from_attributes=True)
