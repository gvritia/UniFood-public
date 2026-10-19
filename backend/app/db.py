# инициализация SQLAlchemy и сессий
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

print(DATABASE_URL)
# точка входа в базу данных
# Тут возникает ошибка с SQLite если передать параметры pool_size
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=True, pool_size=5, max_overflow=10)

# класс для создания сессий базы данных
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# базовый класс для всех моделей SQLAlchemy
# все модели будут наследоваться от него
Base = declarative_base()

# Dependency для FastAPI
# Функция для получения сессии БД в запросах FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()