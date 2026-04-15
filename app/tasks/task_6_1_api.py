import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.schemas import Message

router = APIRouter(tags=["6.1 Basic login"])
security = HTTPBasic(auto_error=False)


@router.get("/login", response_model=Message)
def login_6_1(credentials: HTTPBasicCredentials | None = Depends(security)) -> Message:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    ok_user = secrets.compare_digest(credentials.username, "admin")
    ok_password = secrets.compare_digest(credentials.password, "qwerty")
    if not (ok_user and ok_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    return Message(message="You got my secret, welcome")
