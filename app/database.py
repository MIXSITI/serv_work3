"""Инициализация БД: задание 8.1 (users) + задание 8.2 (todos)."""
from app.config import get_settings
from app.tasks.task_8_1 import get_connection, get_db_connection, init_users_table
from app.tasks.task_8_2 import init_todos_table

get_db = get_db_connection


def init_db() -> None:
    task = get_settings().app_task
    with get_connection() as conn:
        init_users_table(conn, with_role=task != "8.1")
        if task == "8.2":
            init_todos_table(conn)
        conn.commit()
