import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.engine import get_session, engine
from app.db.models import *

from app.api.schemas import Response, CategoryRequest

router = APIRouter(prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])


@router.post("/add", summary="add category to db", description="service utils", response_model=Response)
async def add_category(request_info: CategoryRequest, session: AsyncSession = Depends(get_session)):
    family_file = Category(
        id=uuid.uuid4(),
        name=request_info.name,
        number=request_info.number,
        label=request_info.label,
        # updated_at=datetime.fromisoformat(request_info.edited_at)
    )
    session.add(family_file)
    await session.commit()

    return Response(message='family added to db', data=family_file.as_dict()).as_dict()