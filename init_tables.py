"""Разовый запуск: создать таблицы SQLite (дублирует init_db при старте приложения)."""
from app.database import init_db

if __name__ == "__main__":
    init_db()
    print("Таблицы созданы (если их ещё не было).")
