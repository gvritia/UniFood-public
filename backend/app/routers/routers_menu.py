from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path

from ..db import get_db
from ..dependencies import get_current_admin
from ..schemas.schemas_user import UserResponse
from ..schemas.schemas_menu import (
    MenuItemCreate, MenuItemResponse, MenuItemUpdate
)
from ..crud.crud_menu import menu_crud

router = APIRouter(prefix="/menu", tags=["menu"])

# Путь для хранения фото
UPLOAD_DIR = Path(__file__).parent.parent.parent / "static" / "images" / "menu"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=List[MenuItemResponse])
def get_menu(
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    q: str | None = Query(None, description="Поиск по названию блюда"),
    db: Session = Depends(get_db)
):
    return menu_crud.get_menu_items(db, skip=skip, limit=limit, category=category, q=q)


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = menu_crud.get_menu_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return item


@router.post("/", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
):
    """Создать новое блюдо (только админ)"""
    return menu_crud.create_menu_item(db, item)


@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_update: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
):
    """Обновить блюдо (только админ)"""
    updated = menu_crud.update_menu_item(db, item_id, item_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return updated


@router.delete("/{item_id}", status_code=204)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
):
    """Удалить блюдо (только админ)"""
    deleted = menu_crud.delete_menu_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return None


@router.post("/{item_id}/image", response_model=MenuItemResponse)
async def upload_menu_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: UserResponse = Depends(get_current_admin),
):
    """Загрузить фото для блюда (только админ). Файл сохраняется на сервере."""
    # Проверяем что блюдо существует
    item = menu_crud.get_menu_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    # Проверяем формат файла
    allowed = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Разрешены только JPEG, PNG, WebP")

    # Генерируем уникальное имя файла
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{item_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = UPLOAD_DIR / filename

    # Сохраняем файл
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Удаляем старое фото если оно локальное
    if item.image_url and item.image_url.startswith("/static/"):
        old_path = Path(__file__).parent.parent.parent / "static" / item.image_url.lstrip("/static/")
        if old_path.exists():
            try:
                old_path.unlink()
            except OSError:
                pass

    # Обновляем URL изображения
    image_url = f"/static/images/menu/{filename}"
    menu_crud.update_menu_item(db, item_id, MenuItemUpdate(image_url=image_url))

    return menu_crud.get_menu_item(db, item_id)