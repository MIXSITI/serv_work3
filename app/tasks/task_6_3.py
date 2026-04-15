"""
Задание 6.3 (ТЗ).

Режим MODE=DEV|PROD; в DEV — Basic для /docs и /openapi.json (DOCS_USER, DOCS_PASSWORD),
сравнение через secrets.compare_digest; ReDoc скрыт; в PROD документация отключена
(см. также middleware в main).
"""
import base64
import binascii
import secrets

from fastapi import HTTPException, Request, status

from app.config import get_settings


def _parse_basic_auth(authorization: str | None) -> tuple[str, str] | None:
    if not authorization or not authorization.lower().startswith("basic "):
        return None
    try:
        raw = base64.b64decode(authorization.split(" ", 1)[1].strip()).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, IndexError):
        return None
    if ":" not in raw:
        return None
    user, _, pwd = raw.partition(":")
    return user, pwd


async def verify_docs_basic(request: Request) -> None:
    """Зависимость: Basic-auth для документации только в DEV."""
    settings = get_settings()
    if settings.mode != "DEV":
        return
    path = request.url.path
    if path not in ("/docs", "/openapi.json") and not path.startswith("/docs"):
        return
    auth = request.headers.get("authorization")
    parsed = _parse_basic_auth(auth)
    if not parsed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    user, pwd = parsed
    if not (
        secrets.compare_digest(user, settings.docs_user)
        and secrets.compare_digest(pwd, settings.docs_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
