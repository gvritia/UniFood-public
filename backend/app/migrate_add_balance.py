"""
Скрипт для добавления колонки balance в таблицу users
Запуск: py -m app.migrate_add_balance
"""

from sqlalchemy import text
from app.db import engine


def migrate():
    with engine.connect() as conn:
        try:
            # Проверяем, существует ли уже колонка
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            if 'balance' in columns:
                print("✅ Колонка balance уже существует!")
                return

            # Добавляем колонку balance
            conn.execute(text("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0.0 NOT NULL"))
            conn.commit()
            print("✅ Колонка balance успешно добавлена!")

        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")
            conn.rollback()


if __name__ == "__main__":
    migrate()