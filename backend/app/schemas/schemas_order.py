from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

from .schemas_menu import MenuItemResponse
from .schemas_user import UserResponse


class OrderStatus(str, Enum):
    NEW = "new"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    price_at_order: float


class OrderItemResponse(OrderItemBase):
    id: int
    menu_item: Optional[MenuItemResponse] = None

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    total_price: float
    status: OrderStatus
    order_number: str


class OrderResponse(OrderBase):
    id: int
    user_id: Optional[int] = None
    user: Optional[UserResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class GuestOrderItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)


class GuestOrderCreate(BaseModel):
    items: List[GuestOrderItem] = Field(min_length=1)
    total: float = Field(ge=0)
