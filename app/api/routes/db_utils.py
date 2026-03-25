import json
import os
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.engine import get_session, engine
from app.db.models import *
from app.api.routes.categories import add_category
from app.api.routes.family_files import add_family
from app.api.schemas import Response, AdminCommand, CategoryRequest, FamilyFileRequest
from service.file_utils import FileUtils

router = APIRouter(prefix=f"{settings.API_V1_STR}/utils", tags=["utils"])


@router.post("/init_db", summary="initiate db", description="for manual tests", response_model=Response)
async def init_db(cmd: AdminCommand):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    return Response(message='db initiated', data=[]).as_dict()


@router.post("/seed_db", summary="sees db", description="for manual tests", response_model=Response)
async def seed_db(cmd: AdminCommand, session: AsyncSession = Depends(get_session)):
    
    # delete all backup files
    FileUtils.clean_revit_backups(settings.SERVER_STORAGE_PATH)
    
    # seed categories
    with open(settings.CATEGORIES_JSON_PATH, 'r', encoding='utf-8') as f:
        categories_dict = json.load(f)

    for ost_name, cat_dict in categories_dict.items():
        category_request = CategoryRequest(
            name=ost_name,
            number=str(cat_dict['id']),
            label=str(cat_dict['label']),
        )
        await add_category(category_request, session)

    # seed families
    root_dir = os.getenv("SCAN_PATH", "/data/rvt_files")
    for root, dirs, files in os.walk(root_dir):
        
        relative_path = os.path.relpath(root, root_dir)

        for file in files:
            if not file.lower().endswith('.rfa'):
                continue
            
            full_path = os.path.join(root, file)
            stats = os.stat(full_path)
            
            display_path = os.path.join(relative_path, file)
            
            family_request = FamilyFileRequest(
                title=file.replace('.rfa',''),
                status='new',
                path=display_path,
                edited_at=datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                size=stats.st_size
            )

            await add_family(family_request, session)

    return Response(message=f'succesfully added files', data=[]).as_dict()

