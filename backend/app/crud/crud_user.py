from sqlalchemy.orm import Session
from app.models import models_user
from app.schemas import schemas_user
from passlib.context import CryptContext

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# CRUD = Create, Read, Update, Delete
# Этот класс содержит все операции с пользователями в БД
class CRUDUser:

    def __init__(self):
        # Метод для хеширования пароля
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        """Хеширует пароль"""
        return self.pwd_context.hash(password)

    def get_user(self, db: Session, user_id: int):
        """Получить пользователя по ID"""
        return db.query(models_user.User).filter(models_user.User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str):
        """Получить пользователя по email"""
        return db.query(models_user.User).filter(models_user.User.email == email).first()

    def get_users(self, db: Session, skip: int = 0, limit: int = 100):
        """Получить список пользователей с пагинацией"""
        return db.query(models_user.User).offset(skip).limit(limit).all()

    def create_user(self, db: Session, user: schemas_user.UserCreate):
        """Создать нового пользователя"""
        # Хешируем пароль перед сохранением
        hashed_password = self.get_password_hash(user.password)

        # Создаем объект модели SQLAlchemy
        db_user = models_user.User(
            email=user.email,
            name=user.name,
            hashed_password=hashed_password,
            is_admin=user.is_admin
        )

        # Добавляем в сессию
        db.add(db_user)
        # Сохраняем в БД (commit)
        db.commit()
        # Обновляем объект из БД (получаем id и другие поля)
        db.refresh(db_user)

        return db_user

    def update_user(self, db: Session, user_id: int, user_update: schemas_user.UserUpdate):
        """Обновить данные пользователя"""
        # Получаем пользователя
        db_user = self.get_user(db, user_id)
        if not db_user:
            return None

        # Обновляем только переданные поля
        update_data = user_update.model_dump(exclude_unset=True)

        # Если обновляем пароль - хешируем его
        if "password" in update_data:
            update_data["hashed_password"] = self.get_password_hash(update_data.pop("password"))

        # Применяем обновления
        for field, value in update_data.items():
            setattr(db_user, field, value)

        # Сохраняем изменения
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete_user(self, db: Session, user_id: int):
        """Удалить пользователя"""
        db_user = self.get_user(db, user_id)
        if not db_user:
            return None

        db.delete(db_user)
        db.commit()
        return db_user

    def update_balance(self, db: Session, user_id: int, amount: float):
        """Обновить баланс пользователя (пополнение или списание)"""
        db_user = self.get_user(db, user_id)
        if not db_user:
            return None

        # Защита от None (на всякий случай)
        if db_user.balance is None:
            db_user.balance = 0.0
            
        db_user.balance += amount
        db.commit()
        db.refresh(db_user)
        return db_user


# Создаем экземпляр CRUD для использования в других модулях
user = CRUDUser()