from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
# Pydantic схемы используются для валидации данных
# и определения структуры запросов/ответов API

# Базовая схема пользователя (общие поля)
class UserBase(BaseModel):
    email: EmailStr  # Валидация email
    name: str


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


# Схема для обновления пользователя (все поля опциональны)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


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
    amount: float  # Сумма для пополнения (положительная) или списания (отрицательная)