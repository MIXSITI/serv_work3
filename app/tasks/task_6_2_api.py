import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.schemas import Message, User, UserInDB
from app.tasks.task_6_1_6_2 import hash_password, verify_password

router = APIRouter(tags=["6.2 register + basic login"])
security = HTTPBasic(auto_error=False)
fake_users_db: dict[str, UserInDB] = {}


@router.post("/register", response_model=Message)
def register_6_2(body: User) -> Message:
    if body.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    fake_users_db[body.username] = UserInDB(
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    return Message(message="User added successfully")


@router.get("/login", response_model=Message)
def login_6_2(credentials: HTTPBasicCredentials | None = Depends(security)) -> Message:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    user = fake_users_db.get(credentials.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not secrets.compare_digest(user.username, credentials.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    return Message(message=f"Welcome, {user.username}!")
