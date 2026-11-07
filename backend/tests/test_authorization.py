"""HTTP checks for role and resource ownership rules on an isolated database."""

import os
import logging
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "postgresql+psycopg2://test:test@localhost/test"
os.environ["SECRET_KEY"] = "test-only-signing-key-long-enough"

from app.db import Base, get_db  # noqa: E402

with patch.object(Base.metadata, "create_all"):
    from app.main import app  # noqa: E402

from app.api.auth import create_access_token  # noqa: E402
from app.models.models_cart import CartItem  # noqa: E402
from app.models.models_menu import Menu  # noqa: E402
from app.models.models_order import Order, OrderStatus  # noqa: E402
from app.models.models_user import User  # noqa: E402
from app.routers import routers_menu  # noqa: E402

logging.getLogger("app.main").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine)

        def test_db():
            with self.sessions() as db:
                yield db

        app.dependency_overrides[get_db] = test_db
        self.client = TestClient(app)
        self.db = self.sessions()
        self.admin = User(email="admin@example.com", name="Admin", hashed_password="unused", is_admin=True)
        self.alice = User(email="alice@example.com", name="Alice", hashed_password="unused", is_admin=False)
        self.bob = User(email="bob@example.com", name="Bob", hashed_password="unused", is_admin=False)
        self.db.add_all([self.admin, self.alice, self.bob])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    @staticmethod
    def auth(user):
        return {"Authorization": f"Bearer {create_access_token({'sub': user.email})}"}

    def test_registration_cannot_assign_admin_role(self):
        data = {"email": "new@example.com", "name": "New", "password": "StrongPass1!"}
        denied = self.client.post("/users/", json={**data, "is_admin": True})
        self.assertEqual(denied.status_code, 422)

        created = self.client.post("/users/", json=data)
        self.assertEqual(created.status_code, 201)
        self.assertFalse(created.json()["is_admin"])

        login = self.client.post(
            "/auth/login",
            data={"username": data["email"], "password": data["password"]},
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["user"]["id"], created.json()["id"])
        token = login.json()["access_token"]
        self.assertEqual(
            self.client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code,
            200,
        )
        self.assertEqual(
            self.client.get("/auth/me", headers={"Authorization": "Bearer invalid"}).status_code,
            401,
        )

    def test_user_management_requires_admin(self):
        path = f"/users/{self.bob.id}"
        self.assertEqual(self.client.get("/users/").status_code, 401)
        self.assertEqual(self.client.get("/users/", headers=self.auth(self.alice)).status_code, 403)
        self.assertEqual(self.client.get(path, headers=self.auth(self.alice)).status_code, 403)
        self.assertEqual(self.client.put(path, json={"is_admin": True}, headers=self.auth(self.alice)).status_code, 403)
        self.assertEqual(self.client.delete(path, headers=self.auth(self.alice)).status_code, 403)
        self.assertEqual(self.client.get("/users/", headers=self.auth(self.admin)).status_code, 200)
        self.assertEqual(self.client.put(path, json={"is_admin": True}, headers=self.auth(self.admin)).status_code, 200)

    def test_profile_cannot_change_role(self):
        headers = self.auth(self.alice)
        self.assertEqual(
            self.client.put("/profile/me", json={"is_admin": True}, headers=headers).status_code,
            422,
        )
        response = self.client.get("/profile/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_admin"])
        self.assertEqual(
            self.client.put("/profile/me", json={"name": "Alice Updated"}, headers=headers).status_code,
            200,
        )

    def test_cart_item_belongs_to_current_user(self):
        menu = Menu(food_name="Test meal", price=100, category="Test")
        self.db.add(menu)
        self.db.flush()
        item = CartItem(user_id=self.bob.id, menu_item_id=menu.id, quantity=1)
        self.db.add(item)
        self.db.commit()

        item_id = item.id
        path = f"/cart/{item_id}"
        self.assertEqual(self.client.delete(path, headers=self.auth(self.alice)).status_code, 404)
        self.assertEqual(
            self.client.patch(path, json={"quantity": 2}, headers=self.auth(self.alice)).status_code,
            404,
        )
        self.assertIsNotNone(self.db.get(CartItem, item_id))
        self.assertEqual(self.client.delete(path, headers=self.auth(self.bob)).status_code, 204)
        self.db.expire_all()
        self.assertIsNone(self.db.get(CartItem, item_id))

        second_item = CartItem(user_id=self.bob.id, menu_item_id=menu.id, quantity=1)
        self.db.add(second_item)
        self.db.commit()
        second_id = second_item.id
        self.assertEqual(
            self.client.patch(
                f"/cart/{second_id}", json={"quantity": 0}, headers=self.auth(self.bob)
            ).status_code,
            204,
        )
        self.db.expire_all()
        self.assertIsNone(self.db.get(CartItem, second_id))

    def test_only_admin_sets_working_order_status(self):
        order = Order(user_id=self.alice.id, total_price=100, status=OrderStatus.NEW, order_number="TEST-1")
        self.db.add(order)
        self.db.commit()
        path = f"/orders/{order.id}/status"
        self.assertEqual(
            self.client.patch(path, json={"status": "ready"}, headers=self.auth(self.alice)).status_code,
            403,
        )
        self.assertEqual(
            self.client.patch(path, json={"status": "cancelled"}, headers=self.auth(self.bob)).status_code,
            404,
        )
        self.assertEqual(
            self.client.patch(
                f"/admin/orders/{order.id}/status",
                json={"status": "ready"},
                headers=self.auth(self.admin),
            ).status_code,
            200,
        )

    def test_last_admin_cannot_be_removed(self):
        path = f"/users/{self.admin.id}"
        headers = self.auth(self.admin)
        self.assertEqual(self.client.put(path, json={"is_admin": False}, headers=headers).status_code, 400)
        self.assertEqual(self.client.delete(path, headers=headers).status_code, 400)

    def test_invalid_numbers_are_rejected(self):
        self.assertEqual(
            self.client.post(
                "/menu/",
                json={"food_name": "Test", "price": -1, "category": "Test"},
                headers=self.auth(self.admin),
            ).status_code,
            422,
        )
        self.assertEqual(
            self.client.post(
                "/cart/",
                json={"menu_item_id": 1, "quantity": -2},
                headers=self.auth(self.alice),
            ).status_code,
            422,
        )
        self.assertEqual(
            self.client.post(
                "/profile/balance",
                json={"amount": -10},
                headers=self.auth(self.alice),
            ).status_code,
            422,
        )
        self.assertEqual(
            self.client.put(
                "/profile/me", json={"name": None}, headers=self.auth(self.alice)
            ).status_code,
            422,
        )
        self.assertEqual(
            self.client.put(
                f"/users/{self.bob.id}",
                json={"is_admin": None},
                headers=self.auth(self.admin),
            ).status_code,
            422,
        )
        menu = Menu(food_name="Test meal", price=100, category="Test")
        self.db.add(menu)
        self.db.commit()
        self.assertEqual(
            self.client.put(
                f"/menu/{menu.id}", json={"price": None}, headers=self.auth(self.admin)
            ).status_code,
            422,
        )

    def test_validation_response_does_not_echo_input(self):
        password = "StrongPass1!"
        response = self.client.post(
            "/users/",
            json={"email": "bad-email", "name": "Test", "password": password},
        )
        self.assertEqual(response.status_code, 422)
        self.assertNotIn(password, response.text)
        self.assertTrue(all("input" not in item for item in response.json()["detail"]))

    def test_bcrypt_password_limit_is_enforced(self):
        response = self.client.post(
            "/users/",
            json={"email": "long@example.com", "name": "Test", "password": "StrongPass1!" + "x" * 70},
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_rejects_oversize_and_spoofed_image(self):
        menu = Menu(food_name="Test meal", price=100, category="Test")
        self.db.add(menu)
        self.db.commit()
        path = f"/menu/{menu.id}/image"
        headers = self.auth(self.admin)
        with TemporaryDirectory() as directory, patch.object(routers_menu, "UPLOAD_DIR", Path(directory)):
            spoofed = self.client.post(
                path,
                files={"file": ("evil.png", b"not a PNG", "image/png")},
                headers=headers,
            )
            self.assertEqual(spoofed.status_code, 400)
            oversized = self.client.post(
                path,
                files={"file": ("large.png", b"x" * (routers_menu.MAX_IMAGE_BYTES + 1), "image/png")},
                headers=headers,
            )
            self.assertEqual(oversized.status_code, 413)

            png = b"\x89PNG\r\n\x1a\n" + b"test-image"
            uploaded = self.client.post(
                path,
                files={"file": ("../../unsafe.jpg", png, "image/png")},
                headers=headers,
            )
            self.assertEqual(uploaded.status_code, 200)
            image_url = uploaded.json()["image_url"]
            self.assertTrue(image_url.startswith(f"/static/images/menu/{menu.id}_"))
            self.assertTrue(image_url.endswith(".png"))
            saved = Path(directory) / Path(image_url).name
            self.assertTrue(saved.exists())
            self.assertEqual(saved.read_bytes(), png)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
