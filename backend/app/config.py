import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import URL, make_url

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

raw_database_url = os.getenv("DATABASE_URL")
if raw_database_url:
    DATABASE_URL = make_url(raw_database_url)
else:
    database_password = os.getenv("POSTGRES_PASSWORD")
    if not database_password:
        raise RuntimeError("Set DATABASE_URL or POSTGRES_PASSWORD")
    DATABASE_URL = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER", "unifood"),
        password=database_password,
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "unifood"),
    )

if DATABASE_URL.get_backend_name() != "postgresql":
    raise RuntimeError("DATABASE_URL must be a PostgreSQL connection URL")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
