from sqlalchemy.orm import Session
from app.models.models_menu import Menu
from app.schemas.schemas_menu import MenuItemCreate, MenuItemUpdate


class CRUDMenu:

    def get_menu_item(self, db: Session, item_id: int) -> Menu | None:
        return db.query(Menu).filter(Menu.id == item_id).first()

    def get_menu_items(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            category: str | None = None,
            q: str | None = None
    ):
        query = db.query(Menu)

        if category:
            query = query.filter(Menu.category == category)

        if q:
            query = query.filter(Menu.food_name.ilike(f"%{q}%"))

        return query.offset(skip).limit(limit).all()

    def create_menu_item(self, db: Session, item: MenuItemCreate) -> Menu:
        db_item = Menu(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update_menu_item(
        self, db: Session, item_id: int, item_update: MenuItemUpdate
    ) -> Menu | None:
        db_item = self.get_menu_item(db, item_id)
        if not db_item:
            return None

        update_data = item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)
        return db_item

    def delete_menu_item(self, db: Session, item_id: int) -> Menu | None:
        db_item = self.get_menu_item(db, item_id)
        if not db_item:
            return None
        db.delete(db_item)
        db.commit()
        return db_item


menu_crud = CRUDMenu()