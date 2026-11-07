from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from typing import Optional


class MenuItemBase(BaseModel):
    food_name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, le=100000, allow_inf_nan=False)
    category: str = Field(min_length=1, max_length=50)
    image_url: Optional[str] = Field(default=None, max_length=300)
    ingredients: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=1000)
    calories: Optional[int] = Field(default=None, ge=0)


class MenuItemCreate(MenuItemBase):
    pass  # для создания — те же поля


class MenuItemUpdate(BaseModel):
    food_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[float] = Field(default=None, gt=0, le=100000, allow_inf_nan=False)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    ingredients: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=1000)
    image_url: Optional[str] = Field(default=None, max_length=300)
    calories: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def required_columns_cannot_be_cleared(self):
        for field in ("food_name", "price", "category"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class MenuItemResponse(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
