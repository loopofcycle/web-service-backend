import secrets
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings


def require_admin_configured() -> None:
    if not settings.ADMIN_USER or not settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin credentials are not configured on the server",
        )


def resolve_under_storage(relative_path: str, storage_root: str | None = None) -> Path:
    """Resolve a DB-stored relative path and reject path traversal."""
    root = Path(storage_root or settings.MOUNTED_STORAGE_PATH).resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path",
        ) from exc
    return candidate


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value:
        return None
    return value.strip()


async def require_service_auth(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """Require API_SERVICE_TOKEN via Authorization: Bearer or X-API-Key."""
    expected = settings.API_SERVICE_TOKEN
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_SERVICE_TOKEN is not configured on the server",
        )

    provided = x_api_key or _extract_bearer(authorization)
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


ServiceAuth = Annotated[None, Depends(require_service_auth)]
