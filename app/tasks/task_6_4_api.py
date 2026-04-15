import secrets

from fastapi import APIRouter, HTTPException, status

from app.schemas import Token, User
from app.tasks.task_6_4 import create_access_token

router = APIRouter(tags=["6.4 JWT login"])


def authenticate_user(username: str, password: str) -> bool:
    return secrets.compare_digest(username, "john_doe") and secrets.compare_digest(
        password,
        "securepassword123",
    )


@router.post("/login", response_model=Token)
def login_6_4(body: User) -> Token:
    if not authenticate_user(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(subject=body.username, role="user")
    return Token(access_token=token, token_type="bearer")
