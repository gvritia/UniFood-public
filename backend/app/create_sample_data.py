"""Idempotent local demo data for both supported roles and the main workflows.

Run with ``python -m app.create_sample_data`` inside the backend container.
The published credentials are only suitable for a local demonstration.
"""

import argparse
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.crud.crud_user import user as crud_user
from app.db import Base, SessionLocal, engine
from app.models.models_cart import CartItem
from app.models.models_menu import Menu
from app.models.models_order import Order, OrderItem, OrderStatus
from app.models.models_user import User
from app.schemas.schemas_menu import MenuItemCreate
from app.services.menu_cache import menu_cache


DEMO_PASSWORD = "DemoPass2026!"
DEMO_ACCOUNTS = (
    ("demo.admin@unifood.ru", "Администратор", True, 0.0),
    ("demo.student@unifood.ru", "Студент Анна", False, 1800.0),
    ("demo.student2@unifood.ru", "Студент Борис", False, 900.0),
)

DEMO_ORDERS = (
    ("DEMO-NEW-001", "demo.student@unifood.ru", OrderStatus.NEW,
     (("Пицца Маргарита", 1), ("Кола", 1))),
    ("DEMO-PREP-002", "demo.student@unifood.ru", OrderStatus.PREPARING,
     (("Бургер Классический", 2),)),
    ("DEMO-READY-003", "demo.student2@unifood.ru", OrderStatus.READY,
     (("Паста Карбонара", 1), ("Лимонад", 1))),
    ("DEMO-DONE-004", "demo.student@unifood.ru", OrderStatus.COMPLETED,
     (("Цезарь с курицей", 1), ("Чизкейк", 1))),
    ("DEMO-CANCEL-005", "demo.student2@unifood.ru", OrderStatus.CANCELLED,
     (("Пицца Пепперони", 1),)),
)

# ==================== ТЕСТОВЫЕ БЛЮДА ====================
sample_menu_items = [
    MenuItemCreate(food_name="Пицца Маргарита", price=350.0, category="Пицца", ingredients="Тесто, томатный соус, моцарелла, базилик",
                   image_url="https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400", calories=250),
    MenuItemCreate(food_name="Пицца Пепперони", price=450.0, category="Пицца", ingredients="Тесто, томатный соус, моцарелла, пепперони",
                   image_url="https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400", calories=300),
    MenuItemCreate(food_name="Бургер Классический", price=290.0, category="Бургеры", ingredients="Булочка, говяжья котлета, салат, помидор, соус",
                   image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400", calories=450),
    MenuItemCreate(food_name="Бургер Чизбургер", price=350.0, category="Бургеры", ingredients="Булочка, 2 говяжьи котлеты, сыр чеддер, соус, маринованные огурцы",
                   image_url="https://images.unsplash.com/photo-1550547660-d9450f859349?w=400", calories=500),
    MenuItemCreate(food_name="Цезарь с курицей", price=320.0, category="Салаты", ingredients="Салат айсберг, куриное филе, сухарики, пармезан, соус цезарь",
                   image_url="https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400", calories=180),
    MenuItemCreate(food_name="Греческий салат", price=280.0, category="Салаты", ingredients="Огурцы, помидоры, перец болгарский, маслины, сыр фета, оливковое масло",
                   image_url="https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400", calories=150),
    MenuItemCreate(food_name="Кола", price=100.0, category="Напитки", ingredients="Газированный напиток Cola 0.5л",
                   image_url="https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400", calories=140),
    MenuItemCreate(food_name="Лимонад", price=120.0, category="Напитки", ingredients="Освежающий лимонад Домашний 0.4л",
                   image_url="https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=400", calories=120),
    MenuItemCreate(food_name="Чизкейк", price=180.0, category="Десерты", ingredients="Классический чизкейк Нью-Йорк",
                   image_url="https://images.unsplash.com/photo-1533134242116-79c5e60818a7?w=400", calories=350),
    MenuItemCreate(food_name="Паста Карбонара", price=380.0, category="Горячее", ingredients="Спагетти, бекон, сливки, яичный желток, пармезан",
                   image_url="https://images.unsplash.com/photo-1612874742237-6526221588e3?w=400", calories=520),
]


def seed_demo_data(db: Session, *, reset_demo_passwords: bool = False) -> dict[str, int]:
    """Add missing demo records without deleting or replacing application data."""
    counts = {"menu": 0, "users": 0, "cart_items": 0, "orders": 0}
    try:
        names = [item.food_name for item in sample_menu_items]
        menu_by_name = {
            item.food_name: item
            for item in db.query(Menu).filter(Menu.food_name.in_(names)).all()
        }
        for item in sample_menu_items:
            if item.food_name not in menu_by_name:
                row = Menu(**item.model_dump())
                db.add(row)
                menu_by_name[item.food_name] = row
                counts["menu"] += 1
        db.flush()

        emails = [account[0] for account in DEMO_ACCOUNTS]
        users_by_email = {
            account.email: account
            for account in db.query(User).filter(User.email.in_(emails)).all()
        }
        new_emails = set()
        for email, name, is_admin, balance in DEMO_ACCOUNTS:
            account = users_by_email.get(email)
            if account is None:
                account = User(
                    email=email, name=name, is_admin=is_admin,
                    hashed_password=crud_user.get_password_hash(DEMO_PASSWORD),
                    balance=balance,
                )
                db.add(account)
                users_by_email[email] = account
                new_emails.add(email)
                counts["users"] += 1
            elif account.is_admin != is_admin:
                raise ValueError(f"Demo account {email} has an unexpected role")
            elif reset_demo_passwords:
                account.hashed_password = crud_user.get_password_hash(DEMO_PASSWORD)
        db.flush()

        # A ready cart demonstrates quantity changes and checkout without
        # altering a student's cart on subsequent runs.
        if "demo.student@unifood.ru" in new_emails:
            student_id = users_by_email["demo.student@unifood.ru"].id
            for name, quantity in (("Пицца Маргарита", 1), ("Лимонад", 2)):
                db.add(CartItem(
                    user_id=student_id,
                    menu_item_id=menu_by_name[name].id,
                    quantity=quantity,
                ))
                counts["cart_items"] += 1

        numbers = [spec[0] for spec in DEMO_ORDERS]
        existing_numbers = {
            number for (number,) in db.query(Order.order_number)
            .filter(Order.order_number.in_(numbers)).all()
        }
        now = datetime.now(timezone.utc)
        for index, (number, email, status, lines) in enumerate(DEMO_ORDERS):
            if number in existing_numbers:
                continue
            items = [
                OrderItem(
                    menu_item_id=menu_by_name[name].id,
                    quantity=quantity,
                    price_at_order=menu_by_name[name].price,
                )
                for name, quantity in lines
            ]
            total = round(sum(item.quantity * item.price_at_order for item in items), 2)
            db.add(Order(
                user_id=users_by_email[email].id,
                order_number=number,
                status=status,
                total_price=total,
                created_at=now - timedelta(hours=index + 1),
                items=items,
            ))
            counts["orders"] += 1

        db.commit()
    except Exception:
        db.rollback()
        raise

    menu_cache.invalidate()
    return counts


def create_sample_data(*, reset_demo_passwords: bool = False) -> dict[str, int]:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        counts = seed_demo_data(db, reset_demo_passwords=reset_demo_passwords)
    print(f"Добавлено: {counts['menu']} блюд, {counts['users']} пользователей, "
          f"{counts['cart_items']} позиций корзины, {counts['orders']} заказов.")
    print("Демонстрационные логины и пароль указаны в README.md.")
    print("Если меню кэшировалось до запуска скрипта, обновите страницу через 30 секунд.")
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create local UniFood demo records")
    parser.add_argument(
        "--reset-demo-passwords", action="store_true",
        help="restore the README password only for the three named demo accounts",
    )
    args = parser.parse_args()
    create_sample_data(reset_demo_passwords=args.reset_demo_passwords)
