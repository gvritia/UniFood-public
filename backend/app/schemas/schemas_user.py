from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
from datetime import datetime
from typing import Optional
# Pydantic схемы используются для валидации данных
# и определения структуры запросов/ответов API

# Базовая схема пользователя (общие поля)
class UserBase(BaseModel):
    email: EmailStr  # Валидация email
    name: str = Field(min_length=1, max_length=100)


# Схема для создания пользователя (наследуется от UserBase)
class UserCreate(UserBase):
    password: str  # Пароль (не хешированный)
    is_admin: bool = False

    # Конфигурация для Pydantic v2
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "password": "secretpassword"
            }
        }
    }


class UserRegistration(UserBase):
    password: str

    model_config = ConfigDict(extra="forbid")


# Схема для обновления пользователя (все поля опциональны)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

    @model_validator(mode="after")
    def provided_fields_cannot_be_null(self):
        for field in ("email", "name", "password", "is_admin"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def provided_fields_cannot_be_null(self):
        for field in ("email", "name", "password"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


# Схема для ответа (то, что возвращаем клиенту)
class UserResponse(UserBase):
    id: int
    is_admin: bool
    balance: float
    created_at: datetime

    # Включаем поддержку ORM (преобразование SQLAlchemy модели в Pydantic)
    model_config = ConfigDict(from_attributes=True)


# Схема для обновления баланса
class BalanceUpdate(BaseModel):
    amount: float = Field(gt=0, le=100000, allow_inf_nan=False)


class BalanceResponse(BaseModel):
    balance: float


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
