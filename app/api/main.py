from fastapi import APIRouter

from app.api.routes import db_utils, jobs, family_files, categories

api_router = APIRouter()
api_router.include_router(db_utils.router)
api_router.include_router(jobs.router)
api_router.include_router(family_files.router)
api_router.include_router(categories.router)
