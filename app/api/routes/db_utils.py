import json
from fastapi import APIRouter, Depends

from app.core.config import settings
from app.db.engine import get_session, engine
from app.db.models import *
from app.api.routes.categories import add_category
from app.api.schemas import Response, AdminCommand, CategoryRequest

router = APIRouter(prefix=f"{settings.API_V1_STR}/utils", tags=["utils"])


@router.post("/init_db", summary="initiate db", description="for manual tests", response_model=Response)
async def init_db(cmd: AdminCommand):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    return Response(message='db initiated', data=[]).as_dict()

@router.post("/seed_db", summary="sees db", description="for manual tests", response_model=Response)
async def seed_db(cmd: AdminCommand):
    session_generator = get_session()
    session = await anext(session_generator)

    with open(settings.CATEGORIES_JSON_PATH, 'r', encoding='utf-8') as f:
        categories_dict = json.load(f)

    for ost_name, cat_dict in categories_dict.items():
        category_request = CategoryRequest(
            name=ost_name,
            number=str(cat_dict['id']),
            label=str(cat_dict['label']),
        )
        await add_category(category_request, session)

    return Response(message='db seeded', data=[]).as_dict()
