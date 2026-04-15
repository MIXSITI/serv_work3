"""
Задания 6.1 и 6.2 (ТЗ).

6.1 — защищённая базовой аутентификацией точка GET /login (маршрут: task_6_1_6_2_api).
6.2 — модели UserBase, User, UserInDB в app.schemas; PassLib CryptContext (bcrypt);
зависимость auth_user; логика POST /register (маршрут с лимитом: task_6_5);
сравнение через secrets.compare_digest.
"""
from __future__ import annotations

import secrets
import sqlite3
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from app.schemas import Message, UserInDB, UserRegister

# --- 6.2: PassLib CryptContext, алгоритм bcrypt ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

http_basic = HTTPBasic(auto_error=False)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def user_row_to_in_db(row: sqlite3.Row) -> UserInDB:
    return UserInDB(username=row["username"], hashed_password=row["password"], role=row["role"])


def auth_user(
    db: sqlite3.Connection,
    username: str,
    password: str,
) -> UserInDB | None:
    """Проверка учётных данных (как в ТЗ: поиск пользователя и verify)."""
    cur = db.cursor()
    cur.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if row is None:
        return None
    if not secrets.compare_digest(row["username"], username):
        return None
    if not verify_password(password, row["password"]):
        return None
    return user_row_to_in_db(row)


async def login_basic(
    credentials: HTTPBasicCredentials | None,
    db: sqlite3.Connection,
) -> Message:
    """GET /login: HTTP Basic, ответ Welcome, <username>!"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    user = auth_user(db, credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    return Message(message=f"Welcome, {user.username}!")


async def register_user(
    body: UserRegister,
    db: sqlite3.Connection,
) -> Message:
    """POST /register: JSON User, хеш пароля, сохранение UserInDB в БД."""
    cur = db.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (body.username,))
    if cur.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    hashed = hash_password(body.password)
    in_db = UserInDB(username=body.username, hashed_password=hashed, role=body.role)
    cur.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (in_db.username, in_db.hashed_password, in_db.role),
    )
    db.commit()
    return Message(message="New user created")


__all__ = [
    "UserInDB",
    "UserRegister",
    "pwd_context",
    "auth_user",
    "verify_password",
    "hash_password",
    "http_basic",
    "login_basic",
    "register_user",
]
