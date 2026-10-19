# точка входа FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import engine, Base
from pathlib import Path
from app.routers import routers_user
from app.api.auth import router as api_router
from app.routers import routers_menu
from app.routers import routers_cart
from app.routers import routers_order
from app.routers import routers_profile  # Новый роутер профиля
from app.routers import routers_admin  # Роутер админки
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем все таблицы в базе данных
# В продакшене лучше использовать Alembic для миграций
Base.metadata.create_all(bind=engine)

# Создаем экземпляр FastAPI
app = FastAPI(
    title="UniFood API",
    description="MVP онлайн-заказ еды в столовой вуза",
    version="1.0"
)

# CORS для фронтенда (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:5173","http://localhost:5174",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ловим все необработанные исключения
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Мы уже разбираемся."}
    )

# Ловим ошибки валидации (400 Bad Request)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error at {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            logger.info(f"{request.method} {request.url.path} → {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error processing {request.method} {request.url}: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )

# Добавляем middleware
app.add_middleware(LoggingMiddleware)
# Подключаем роутеры
app.include_router(routers_user.router)
app.include_router(api_router)
app.include_router(routers_menu.router)
app.include_router(routers_cart.router)
app.include_router(routers_order.router)
app.include_router(routers_profile.router)  # Подключаем роутер профиля
app.include_router(routers_admin.router)  # Подключаем роутер админки

# Раздача статики (фото блюд)
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def root():
    return {"message": "Добро пожаловать в API управления пользователями"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}