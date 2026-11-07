from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import List
import uuid
from pathlib import Path

from ..db import get_db
from ..dependencies import get_current_admin
from ..schemas.schemas_user import UserResponse
from ..schemas.schemas_menu import (
    MenuItemCreate, MenuItemResponse, MenuItemUpdate
)
from ..crud.crud_menu import menu_crud
from ..services.menu_cache import menu_cache

router = APIRouter(prefix="/menu", tags=["menu"])

# Путь для хранения фото
UPLOAD_DIR = Path(__file__).parent.parent.parent / "static" / "images" / "menu"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def image_extension(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return ".webp"
    return None


@router.get("/", response_model=List[MenuItemResponse])
def get_menu(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: str | None = Query(None, max_length=50),
    q: str | None = Query(None, max_length=100, description="Поиск по названию блюда"),
    db: Session = Depends(get_db)
):
    key = (skip, limit, category, q)

    def load_menu():
        rows = menu_crud.get_menu_items(db, skip=skip, limit=limit, category=category, q=q)
        # Do not keep SQLAlchemy objects tied to a closed request session.
        return [MenuItemResponse.model_validate(row) for row in rows]

    items, hit = menu_cache.get_or_load(key, load_menu)
    response.headers["X-Menu-Cache"] = "HIT" if hit else "MISS"
    return items


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
    allowed = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Разрешены только JPEG, PNG, WebP")

    content = await file.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Размер изображения не должен превышать 5 МБ")
    ext = image_extension(content)
    if ext != allowed[file.content_type]:
        raise HTTPException(status_code=400, detail="Содержимое файла не соответствует формату изображения")

    # Расширение определяется содержимым, имя отправителя не используется.
    filename = f"{item_id}_{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    old_image_url = item.image_url
    image_url = f"/static/images/menu/{filename}"
    try:
        filepath.write_bytes(content)
        updated = menu_crud.update_menu_item(db, item_id, MenuItemUpdate(image_url=image_url))
    except Exception:
        filepath.unlink(missing_ok=True)
        raise

    if old_image_url:
        old_name = Path(old_image_url).name
        if old_image_url == f"/static/images/menu/{old_name}":
            try:
                (UPLOAD_DIR / old_name).unlink(missing_ok=True)
            except OSError:
                pass

    return updated
