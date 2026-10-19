from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
# загружает .env
load_dotenv(dotenv_path=ENV_PATH)
# load_dotenv(encoding='utf-8')
# запасной вариант

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
print(DATABASE_URL)
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
except (TypeError, ValueError):
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    print("Предупреждение: Используется значение по умолчанию для ACCESS_TOKEN_EXPIRE_MINUTES = 30")