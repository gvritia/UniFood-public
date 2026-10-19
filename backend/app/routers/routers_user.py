from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import re
from app.crud import crud_user
from app.schemas import schemas_user
from app.db import get_db

# Создаем роутер с префиксом /users
router = APIRouter(
    prefix="/users",
    tags=["users"],  # Для автоматической документации
)


def validate_password_strength(password: str) -> None:
    """Проверка сложности пароля"""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать минимум 8 символов"
        )
    if not re.search(r'[A-ZА-ЯЁ]', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать хотя бы одну заглавную букву"
        )
    if not re.search(r'[a-zа-яё]', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать хотя бы одну строчную букву"
        )
    if not re.search(r'\d', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать хотя бы одну цифру"
        )
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать хотя бы один специальный символ (!@#$%^&*...)"
        )


@router.post("/", response_model=schemas_user.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas_user.UserCreate, db: Session = Depends(get_db)):
    """
    Создать нового пользователя.

    - **email**: уникальный email пользователя
    - **name**: имя пользователя
    - **password**: пароль (мин. 8 символов, заглавные, строчные, цифры, спецсимволы)
    """
    # Проверяем сложность пароля
    validate_password_strength(user.password)

    # Проверяем, не существует ли пользователь с таким email
    db_user = crud_user.user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Создаем пользователя
    return crud_user.user.create_user(db=db, user=user)



@router.get("/", response_model=List[schemas_user.UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Получить список всех пользователей.

    - **skip**: количество пропущенных записей (для пагинации)
    - **limit**: максимальное количество записей
    """
    users = crud_user.user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas_user.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о конкретном пользователе по ID.
    """
    db_user = crud_user.user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.put("/{user_id}", response_model=schemas_user.UserResponse)
def update_user(user_id: int, user_update: schemas_user.UserUpdate, db: Session = Depends(get_db)):
    """
    Обновить данные пользователя.

    Можно обновить одно или несколько полей.
    """
    # Задача 12: Админ не может лишить себя прав
    if user_update.is_admin is False:
        current_user = crud_user.user.get_user(db, user_id)
        if current_user and current_user.is_admin:
            # Проверяем, есть ли другие админы
            all_users = crud_user.user.get_users(db, skip=0, limit=10000)
            admin_count = sum(1 for u in all_users if u.is_admin)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Нельзя снять права администратора — это последний админ в системе"
                )

    # Если обновляется пароль — проверяем его сложность
    if user_update.password is not None:
        validate_password_strength(user_update.password)

    db_user = crud_user.user.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.delete("/{user_id}", response_model=schemas_user.UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Удалить пользователя.
    """
    db_user = crud_user.user.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user