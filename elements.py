from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from app.core.config import settings
from app.db.engine import get_session
from app.db.models import *
from app.api.schemas import Response


router = APIRouter(prefix=settings.API_V1_STR + "/bim_elements", tags=["bim"])


@router.get("/{title}/{table}", summary="elements from file", description="for BIMDATA", response_model=Response)
async def read_elements_data(title: str, table: str, session: AsyncSession = Depends(get_session)):
    file_obj = await session.execute(select(RevitFile).where(RevitFile.title == title))
    rvt_file = file_obj.scalars().first()
    if not rvt_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    project_obj = await session.execute(select(Project).where(rvt_file.project_id == Project.id))
    project = project_obj.scalars().first()

    db_url = URL.create("mssql+pyodbc",
                        host=settings.DB_HOST,
                        database=project.db_name,
                        query={"driver": "ODBC Driver 18 for SQL Server",
                               "Trusted_Connection": "yes",
                               "TrustServerCertificate": "yes"})
    db_engine = create_engine(db_url)

    query = f"SELECT * FROM [dbo].[{table}] WHERE [title] = '{rvt_file.title}'"

    with db_engine.connect() as connection:
        result = connection.execute(text(query))
        mapped_results = result.mappings().all()

    db_engine.dispose()

    elements = [dict(row) for row in mapped_results]
    return Response(message='rooms', data=elements).as_dict()


@router.get("/{title}/rooms", summary="rooms from file", description="for BIMDATA", response_model=Response)
async def read_rooms_data(title: str, session: AsyncSession = Depends(get_session)):
    resp = await read_elements_data(title, "Rooms")
    return Response(message='rooms', data=resp['data']).as_dict()


@router.get("/{title}/parking", summary="parking data from file", description="for BIMDATA", response_model=Response)
async def read_parking_data(title: str, session: AsyncSession = Depends(get_session)):
    resp = await read_elements_data(title, "Parking")
    return Response(message='parking', data=resp['data']).as_dict()


@router.get("/{title}/masterplan", summary="masterplan data", description="for BIMDATA", response_model=Response)
async def read_masterplan_data(title: str, session: AsyncSession = Depends(get_session)):
    resp = await read_elements_data(title, "Masterplan")
    return Response(message='masterplan', data=resp['data']).as_dict()
