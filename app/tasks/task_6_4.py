"""
Задание 6.4 (ТЗ).

Аутентификация по JWT (библиотека PyJWT): выдача токена при POST /login (JSON),
точка GET /protected_resource с Bearer; скрытие /docs, /openapi.json, /redoc (404 в PROD
реализуется в main + задание 6.3); pydantic-settings для конфигурации.
"""
from __future__ import annotations

import secrets
import sqlite3

from fastapi import HTTPException, status

from app.config import Settings, get_settings
from app.schemas import Token, User
from app.tasks.task_6_1_6_2 import verify_password


def create_access_token(
    *,
    subject: str,
    role: str,
    settings: Settings | None = None,
) -> str:
    from datetime import UTC, datetime, timedelta

    import jwt

    s = settings or get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=s.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def decode_token(token: str, settings: Settings | None = None) -> dict:
    import jwt

    s = settings or get_settings()
    return jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])


async def login_with_jwt(body: User, db: sqlite3.Connection) -> Token:
    """POST /login: JSON username/password → JWT (задание 6.5 уточняет коды ответов)."""
    cur = db.cursor()
    cur.execute(
        "SELECT username, password, role FROM users WHERE username = ?",
        (body.username,),
    )
    row = cur.fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not secrets.compare_digest(row["username"], body.username):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not verify_password(body.password, row["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )
    token = create_access_token(subject=row["username"], role=row["role"])
    return Token(access_token=token, token_type="bearer")
