from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.schemas import Message, User


def _db_path() -> Path:
    return Path(get_settings().database_path).resolve()


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_users_table(conn: sqlite3.Connection, with_role: bool = True) -> None:
    if with_role:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'guest'
            )
            """
        )
        return
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """
    )


def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


get_db = get_db_connection

router = APIRouter(tags=["8.1 SQLite users"])


@router.post("/register", response_model=Message)
def register_user_8_1(
    body: User,
    db: sqlite3.Connection = Depends(get_db),
) -> Message:
    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (body.username, body.password),
    )
    db.commit()
    return Message(message="User registered successfully!")
