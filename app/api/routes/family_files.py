from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict
from starlette.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.core.config import settings
from app.core.security import resolve_under_storage
from app.db.engine import get_session
from app.db.models import *

from app.api.schemas import Response, FamilyFileRequest
from celery.app import Celery
from celery import group
import os

router = APIRouter(prefix=f"{settings.API_V1_STR}/families", tags=["families"])


@router.post("/add", summary="add family to db", description="service utils", response_model=Response)
async def add_family(request_info: FamilyFileRequest, session: AsyncSession = Depends(get_session)):
    family_file = FamilyFile(
        id=uuid.uuid4(),
        version_id=uuid.uuid4(),
        title=request_info.title,
        path=request_info.path,
        status=request_info.status,
        size=request_info.size,
    )
    session.add(family_file)
    await session.commit()

    return Response(message='family added to db', data=family_file.as_dict()).as_dict()


@router.get("/list", summary="read family from db", description="service utils")
async def get_families(session: AsyncSession = Depends(get_session)):
    files_query = await session.execute(select(FamilyFile))
    families = files_query.scalars().all()
    # result = [f.as_dict() for f in families]

    categories_query = await session.execute(select(Category))
    categories = categories_query.scalars().all()
    category_by_id = {c.id: c.label for c in categories}
    category_by_id[None] = 'common'

    base = settings.PUBLIC_API_BASE_URL.rstrip('/')
    data = []
    for f in families:
        data.append({
            'id': f.id,
            'title': f.title,
            'name': f.title.replace('_', ' '),
            'category': category_by_id.get(f.category_id, 'common'),
            'file_name': f.title + '.rfa',
            'path': f.path,
            'file_link': f'{base}{settings.API_V1_STR}/families/download?file_id={f.id}',
            'image_link': f'{base}{settings.API_V1_STR}/families/preview_pic?file_id={f.id}',
            'revit_version': '2024',
        })
    return data


@router.get("/get", summary="get list of all families", description="service utils", response_model=Response)
async def get_family(file_id: Optional[str] = None, path: Optional[str] = None, session: AsyncSession = Depends(get_session)):
    if not file_id and not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="provide at least one argument")

    family_file = None
    if file_id:
        file_query = await session.execute(select(FamilyFile).where(FamilyFile.id == file_id))
        family_file = file_query.scalars().first()
    elif path:
        file_query = await session.execute(select(FamilyFile).where(FamilyFile.path == path))
        family_file = file_query.scalars().first()

    if not family_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    type_query = await session.execute(select(FamilyType)
                                        .where(FamilyType.file_id == family_file.id))
    family_types = type_query.scalars().all()

    types_data = {}
    for f_type in family_types:
        spec_params_query = await session.execute(
            select(SpecParamSet).where(SpecParamSet.type_id == f_type.id)
        )
        spec_params = spec_params_query.scalars().first()

        sp_dict = {}
        if spec_params is not None:
            for c in spec_params.__table__.columns:
                sp_dict[c.name] = getattr(spec_params, c.key)

        types_data[f_type.name] = {
            "name": f_type.name,
            "parameters": sp_dict
        }

    result = family_file.as_dict()
    result['types_data'] = types_data

    return Response(message='family data', data=result).as_dict()


@router.get("/preview_pic", summary="download family preview picture", description="service utils")
async def download_preview(file_id: str, session: AsyncSession = Depends(get_session)):
    file_query = await session.execute(select(FamilyFile).where(FamilyFile.id == file_id))
    family_file = file_query.scalars().first()
    if not family_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")
    
    picture_rel = family_file.path.replace('.rfa', '.jpg').replace('.RFA', '.jpg')
    picture_path = resolve_under_storage(picture_rel)
    if not picture_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    return FileResponse(path=str(picture_path),
                        media_type='application/octet-stream',
                        filename=family_file.title + '.jpg')


@router.get("/download", summary="download family file", description="service utils")
async def download_family(file_id: str, session: AsyncSession = Depends(get_session)):
    file_query = await session.execute(select(FamilyFile).where(FamilyFile.id == file_id))
    family_file = file_query.scalars().first()
    if not family_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    file_path = resolve_under_storage(family_file.path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    return FileResponse(path=str(file_path),
                        media_type='application/octet-stream',
                        filename=family_file.title + '.rfa')

@router.post("/update", summary="update family info in db", description="for service", response_model=Response)
async def update_family(request_info: FamilyFileRequest, session: AsyncSession = Depends(get_session)):
    if not request_info.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id is required")

    file_query = await session.execute(select(FamilyFile).where(FamilyFile.id == request_info.id))
    family_file = file_query.scalars().first()
    if not family_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    payload = request_info.model_dump(exclude_unset=True)
    payload.pop('id', None)
    category_name = payload.pop('category', None)

    if category_name is not None:
        category_query = await session.execute(
            select(Category).where(Category.name == category_name)
        )
        category = category_query.scalars().first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"category '{category_name}' not found",
            )
        family_file.category_id = category.id

    for field_name, value in payload.items():
        if hasattr(family_file, field_name):
            setattr(family_file, field_name, value)

    await session.commit()
    await session.refresh(family_file)
    return Response(message='file updated', data=family_file.as_dict()).as_dict()


@router.post("/batch_io", summary="update files from storage", description="for auto tests", response_model=Response)
async def process_group_of_files(id_list: List[str], mode: str, session: AsyncSession = Depends(get_session)):
    for family_id in id_list:
        file_query = await session.execute(select(FamilyFile).where(FamilyFile.id == family_id))
        family_file = file_query.scalars().first()
        if not family_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"family id={family_id} not found")

    BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis_service:6379/0")
    celery_app = Celery(settings.CELERY_WORKER_NAME, broker=BROKER_URL)

    job_signatures = [
        celery_app.signature("process_family", args=[family_id, mode]) 
        for family_id in id_list
    ]
    
    job_group = group(job_signatures)
    result = job_group.apply_async()
    
    return Response(message=f'{len(id_list)} tasks transmited to worker', data={'result_id': result.id}).as_dict()


@router.post("/create_types", summary="revit plugin bound", description="for service", response_model=Response)
async def create_types(types: Dict[str, str], session: AsyncSession = Depends(get_session)):
    for type_name, family_id in types.items():
        file_query = await session.execute(select(FamilyFile).where(FamilyFile.id == family_id))
        family_file = file_query.scalars().first()
        if not family_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="file not found")
        
        type_query = await session.execute(select(FamilyType)
                                           .where(FamilyType.name == type_name,
                                                  FamilyType.file_id == family_id))
        family_type = type_query.scalars().first()
        if family_type:
            # print(f'type {type_name} already exist')
            continue
        
        family_type = FamilyType(
            id=uuid.uuid4(),
            name=type_name,
            file_id=family_id
        )
        session.add(family_type)

    await session.commit()
    return Response(message=f'{len(types)} added to a family {family_file.id}', data=types).as_dict()


@router.post("/update_type_parameters", summary="revit plugin bound", description="for service", response_model=Response)
async def update_type_parameters(data: Dict[str, str], session: AsyncSession = Depends(get_session)):
    # print(f'received')
    # print(data)
    file_id = data['file_id']
    file_query = await session.execute(select(FamilyFile).where(FamilyFile.id == file_id))
    family_file = file_query.scalars().first()
    if not family_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    type_name = data['type_name']
    type_query = await session.execute(select(FamilyType)
                                        .where(FamilyType.name == type_name,
                                                FamilyType.file_id == family_file.id))
    family_type = type_query.scalars().first()
    if not family_type:
        family_type = FamilyType(
            id=uuid.uuid4(),
            name=type_name,
            file_id=family_file.id
        )
        session.add(family_type)

    await session.execute(delete(SpecParamSet).where(SpecParamSet.type_id == family_type.id))
    await session.commit()

    spec_params_set = SpecParamSet(
        id=uuid.uuid4(),
        type_id=family_type.id
    )
    
    for c in SpecParamSet.__table__.columns:
        if c.name not in data:
            continue
        
        if str(c.type) == 'INTEGER':
            value = int(float(data[c.name]))
        else:
            value = data[c.name]

        setattr(spec_params_set, c.key, value)

    session.add(spec_params_set)
    await session.commit()

    return Response(message='file updated', data=family_type.as_dict()).as_dict()
