from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, Request
from starlette import status

from app.database import get_db
from app.rate_limit import limiter
from app.schemas import Message, Token, User, UserRegister
from app.tasks.task_6_1_6_2 import register_user
from app.tasks.task_6_4 import login_with_jwt

router = APIRouter(tags=["6.5 register JWT rate-limit"])


@router.post(
    "/register",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "User exists"}},
)
@limiter.limit("1/minute")
async def register(
    request: Request,
    body: UserRegister,
    db: sqlite3.Connection = Depends(get_db),
) -> Message:
    return await register_user(body, db)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_jwt(
    request: Request,
    body: User,
    db: sqlite3.Connection = Depends(get_db),
) -> Token:
    return await login_with_jwt(body, db)
