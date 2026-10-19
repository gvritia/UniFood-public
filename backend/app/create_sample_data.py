"""
Скрипт для создания тестовых данных (меню + администратор)
Запуск: python -m app.create_sample_data
"""

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.crud.crud_menu import menu_crud
from app.crud.crud_user import user as crud_user
from app.schemas.schemas_menu import MenuItemCreate
from app.schemas.schemas_user import UserCreate

# Создаем таблицы (если ещё не созданы)
Base.metadata.create_all(bind=engine)

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


def create_sample_data():
    db: Session = SessionLocal()
    try:
        # === Создаём меню ===
        existing_menu = menu_crud.get_menu_items(db, limit=1)
        if not existing_menu:
            print("Создаём тестовое меню...")
            for item in sample_menu_items:
                menu_crud.create_menu_item(db, item)
                print(f"✓ Добавлено: {item.food_name}")
            print("✅ Меню успешно создано!\n")
        else:
            print("Меню уже существует, пропускаем.\n")

        # === Создаём администратора ===
        admin_email = "admin@unifood.ru"
        admin_exists = crud_user.get_user_by_email(db, admin_email)

        if not admin_exists:
            admin_data = UserCreate(
                email=admin_email,
                name="admin",
                password="admin123",
                is_admin=True
            )
            crud_user.create_user(db, admin_data)
            print(f"✅ Администратор создан!")
            print(f"   Email: {admin_email}")
            print(f"   Пароль: admin123\n")
        else:
            print(f"Администратор {admin_email} уже существует.\n")

        print("🎉 Все тестовые данные готовы к использованию!")

    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()