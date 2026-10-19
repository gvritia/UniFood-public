from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import crud_user
from app.schemas import schemas_user
from app.db import get_db
from ..api.auth import get_current_user
from ..schemas.schemas_user import UserResponse, BalanceUpdate
from .routers_user import validate_password_strength

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: UserResponse = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
        user_update: schemas_user.UserUpdate,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обновить информацию о текущем пользователе"""
    # Если обновляется пароль — проверяем его сложность
    if user_update.password is not None:
        validate_password_strength(user_update.password)

    # Проверяем, что email не занят другим пользователем
    if user_update.email and user_update.email != current_user.email:
        existing_user = crud_user.user.get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже занят"
            )

    updated_user = crud_user.user.update_user(db, user_id=current_user.id, user_update=user_update)
    return updated_user


@router.post("/balance", response_model=UserResponse)
def add_balance(
        balance_data: BalanceUpdate,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Пополнить баланс (amount должен быть положительным)"""
    if balance_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сумма должна быть положительной"
        )

    updated_user = crud_user.user.update_balance(db, current_user.id, balance_data.amount)
    return updated_user


@router.get("/balance", response_model=dict)
def get_balance(
        current_user: UserResponse = Depends(get_current_user)
):
    """Получить текущий баланс"""
    return {"balance": current_user.balance}