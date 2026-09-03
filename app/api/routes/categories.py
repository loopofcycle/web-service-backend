import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import require_service_auth
from app.db.engine import get_session
from app.db.models import Category
from app.api.schemas import Response, CategoryRequest

router = APIRouter(prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])


@router.post("/add", summary="add category to db", description="service utils", response_model=Response)
async def add_category(
    request_info: CategoryRequest,
    session: AsyncSession = Depends(get_session),
    _auth: None = Depends(require_service_auth),
):
    category = Category(
        id=uuid.uuid4(),
        name=request_info.name,
        number=request_info.number,
        label=request_info.label,
    )
    session.add(category)
    await session.commit()

    return Response(message='category added to db', data=category.as_dict()).as_dict()
