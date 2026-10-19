from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from ..api.auth import get_current_user
from ..schemas.schemas_user import UserResponse
from ..schemas.schemas_cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse
)
from ..crud.crud_cart import (
    get_cart_items,
    get_cart_item,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart
)

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartResponse)
def get_my_cart(
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получить корзину текущего пользователя"""
    items = get_cart_items(db, current_user.id)

    total = sum(
        item.quantity * item.menu_item.price
        for item in items
        if item.menu_item  # на всякий случай защита
    )

    return {
        "items": items,
        "total_price": round(total, 2)
    }


@router.post("/", response_model=CartItemResponse, status_code=201)
def add_item_to_cart(
        item: CartItemCreate,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Добавить товар в корзину (или увеличить количество)"""
    # Можно добавить проверку, существует ли menu_item_id вообще,
    # но для MVP опустим — будет ошибка на уровне FK

    created = add_to_cart(db, current_user.id, item)
    return created


@router.patch("/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item_quantity(
        cart_item_id: int,
        update_data: CartItemUpdate,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Изменить количество позиции в корзине"""
    # Проверяем, что позиция принадлежит текущему пользователю
    from ..models.models_cart import CartItem
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == current_user.id).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Позиция не найдена или не принадлежит вам"
        )

    if update_data.quantity is not None:
        if update_data.quantity <= 0:
            # Если количество стало ≤0 — удаляем позицию
            remove_from_cart(db, cart_item_id)
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Позиция удалена (количество ≤ 0)"
            )

    updated = update_cart_item(db, cart_item_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Позиция не найдена")

    return updated


@router.delete("/{cart_item_id}", status_code=204)
def delete_cart_item(
        cart_item_id: int,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Удалить позицию из корзины"""
    # Для безопасности можно проверить принадлежность, но для MVP достаточно
    remove_from_cart(db, cart_item_id)
    return None


@router.delete("/", status_code=204)
def clear_my_cart(
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Очистить всю корзину"""
    clear_cart(db, current_user.id)
    return None