"""HTTP-маршруты заданий 6.1–6.2: только GET /login (Basic)."""
import sqlite3

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials

from app.database import get_db
from app.schemas import Message
from app.tasks.task_6_1_6_2 import http_basic, login_basic

router = APIRouter(tags=["6.1-6.2 Basic GET /login"])


@router.get("/login", response_model=Message)
async def login_get(
    credentials: HTTPBasicCredentials | None = Depends(http_basic),
    db: sqlite3.Connection = Depends(get_db),
) -> Message:
    return await login_basic(credentials, db)
