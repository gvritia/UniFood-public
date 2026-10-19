import sqlite3
import os

def migrate():
    db_path = 'unifood.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Пытаемся добавить колонку description
        cursor.execute('ALTER TABLE menu ADD COLUMN description TEXT;')
        conn.commit()
        print("Column 'description' added successfully to 'menu' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'description' already exists.")
        else:
            print(f"Operational Error: {e}")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
