import asyncio

from app.db import SessionLocal
from app.crud.crud_user import user as crud_user
from app.schemas.schemas_user import UserCreate
from app.crud.crud_menu import menu_crud
from app.schemas.schemas_menu import MenuItemCreate
from app.crud.crud_cart import add_to_cart
from app.schemas.schemas_cart import CartItemCreate
from app.crud.crud_order import create_order_from_cart


async def smoke_test():
    db = SessionLocal()
    try:
        print("-> Creating test user (if missing)")
        test_email = "testuser@example.com"
        existing = crud_user.get_user_by_email(db, test_email)

        if not existing:
            user = crud_user.create_user(
                db,
                UserCreate(email=test_email, name="Test Student", password="123456"),
            )
            print(f"  User created: {user.email} (id={user.id})")
        else:
            user = existing
            print(f"  User already exists: {user.email} (id={user.id})")

        print("\n-> Ensuring at least 2 menu items exist")
        menu_items = menu_crud.get_menu_items(db, limit=2)
        if len(menu_items) < 2:
            seed_items = [
                MenuItemCreate(food_name="Burger", price=220, category="Burgers", image_url="..."),
                MenuItemCreate(food_name="Cola 0.5", price=89, category="Drinks", image_url="..."),
                MenuItemCreate(food_name="French fries", price=145, category="Snacks", image_url="..."),
            ]
            missing = 2 - len(menu_items)
            for item in seed_items[:missing]:
                menu_crud.create_menu_item(db, item)
            menu_items = menu_crud.get_menu_items(db, limit=2)

        if len(menu_items) < 2:
            raise RuntimeError("Smoke test requires at least 2 menu items")

        print("\n-> Adding items to cart")
        add_to_cart(db, user.id, CartItemCreate(menu_item_id=menu_items[0].id, quantity=2))
        add_to_cart(db, user.id, CartItemCreate(menu_item_id=menu_items[1].id, quantity=1))
        print("  Added to cart")

        print("\n-> Creating order")
        order = create_order_from_cart(db, user.id)
        print("  Order created")
        print(f"    Order number: {order.order_number}")
        print(f"    Total:        {order.total_price}")
        print(f"    Status:       {order.status}")
        print(f"    Items:        {len(order.items)}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(smoke_test())
