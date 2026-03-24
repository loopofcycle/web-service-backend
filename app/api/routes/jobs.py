import os
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.engine import get_session, engine
from app.db.models import *
from app.api.routes.family_files import add_family
from app.api.schemas import Response, AdminCommand, FamilyFileRequest


router = APIRouter(prefix=f"{settings.API_V1_STR}/jobs", tags=["jobs"])


@router.post("/periodic", summary="run with interval", description="for auto tests", response_model=Response)
async def periodic(cmd: AdminCommand):
    session_generator = get_session()
    session = await anext(session_generator)
    await sync_storage(cmd=cmd, session=session)

    return Response(message=f'periodic job finished', data=[]).as_dict()


@router.post("/sync_storage", summary="update files from storage", description="for auto tests", response_model=Response)
async def sync_storage(cmd: AdminCommand, session: AsyncSession = Depends(get_session)):
    root_dir = os.getenv("SCAN_PATH", "/data/rvt_files")
    # root_dir = settings.MOUNTED_STORAGE_PATH
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

