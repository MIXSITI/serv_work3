from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.tasks.task_6_4 import decode_token

security_bearer = HTTPBearer(auto_error=False)


def get_current_settings() -> Settings:
    return get_settings()


class RoleChecker:
    def __init__(self, allowed: set[str]) -> None:
        self.allowed = allowed

    def __call__(
        self,
        credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
        settings: Settings = Depends(get_current_settings),
    ) -> dict:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        try:
            payload = decode_token(credentials.credentials, settings)
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from None
        username = payload.get("sub")
        role = str(payload.get("role", "guest"))
        if username is None or role not in self.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return {"username": str(username), "role": role}


RequireAdmin = Annotated[dict, Depends(RoleChecker({"admin"}))]
RequireAdminOrUser = Annotated[dict, Depends(RoleChecker({"admin", "user"}))]
RequireAnyRole = Annotated[dict, Depends(RoleChecker({"admin", "user", "guest"}))]


rbac_router = APIRouter(prefix="/rbac", tags=["7.1 RBAC"])


@rbac_router.get("/admin")
def rbac_admin_only(user: RequireAdmin) -> dict:
    return {"role": user["role"], "scope": "admin-only: full CRUD on todos"}


@rbac_router.get("/user")
def rbac_user_area(user: RequireAdminOrUser) -> dict:
    return {"role": user["role"], "scope": "user: read and update todos"}


@rbac_router.get("/guest")
def rbac_guest_area(user: RequireAnyRole) -> dict:
    return {"role": user["role"], "scope": "guest: read-only todos"}
