import os
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.engine import get_session, engine
from app.db.models import *
from app.api.routes.family_files import add_family, process_group_of_files
from app.api.schemas import Response, AdminCommand, FamilyFileRequest


router = APIRouter(prefix=f"{settings.API_V1_STR}/jobs", tags=["jobs"])


@router.post("/periodic", summary="run with interval", description="for auto tests", response_model=Response)
async def periodic(cmd: AdminCommand):
    session_generator = get_session()
    session = await anext(session_generator)

    print(f'placeholder code executed')

    return Response(message=f'periodic job finished', data=[]).as_dict()


@router.post("/read_from_storage", summary="update files from storage", description="for auto tests", response_model=Response)
async def read_from_storage(cmd: AdminCommand, session: AsyncSession = Depends(get_session)):
    files_query = await session.execute(select(FamilyFile))
    families = files_query.scalars().all()
    response = await process_group_of_files(id_list=[str(family.id) for family in families],
                                            mode='read',
                                            session=session)

    return Response(message=f'transmitted reading task to worker', data=response).as_dict()


