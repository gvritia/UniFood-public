from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class MenuItemBase(BaseModel):
    food_name: str
    price: float
    category: str
    image_url: Optional[str] = None
    ingredients: Optional[str] = None
    description: Optional[str] = None
    calories: Optional[int] = None


class MenuItemCreate(MenuItemBase):
    pass  # для создания — те же поля


class MenuItemUpdate(BaseModel):
    food_name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    ingredients: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    calories: Optional[int] = None


class MenuItemResponse(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)