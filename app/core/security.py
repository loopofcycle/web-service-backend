from pathlib import Path

from fastapi import HTTPException, status

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
