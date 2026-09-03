import logging
import typer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc


from app.api.main import api_router
from app.core.config import settings
from app.api.routes.jobs import periodic
from app.api.schemas import AdminCommand

scheduler = AsyncIOScheduler(timezone=utc)


@scheduler.scheduled_job(trigger='interval', max_instances=1, minutes=60)
async def periodic_job():
    if not settings.ADMIN_USER or not settings.ADMIN_PASSWORD:
        logging.warning('%s: cron_job skipped: admin credentials not configured', __name__)
        return
    await periodic(AdminCommand(user=settings.ADMIN_USER, password=settings.ADMIN_PASSWORD))
    logging.info('%s: cron_job: finished', __name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


description = """
this API provide high level management of .rfa files. 🚀

## Upload .rfa files, manage shared parameters

You can:

* **browse available .rfa files** .
* **read, write and sync parameters with db** .

"""
app = FastAPI(
    title='Revit family manager',
    description=description,
    summary="FastAPI based backend",
    version="0.0.1",
    contact={
        "name": "Igor Eliseev",
        "email": "loopofcycle@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    # lifespan=lifespan
)
app.include_router(api_router)


_cors_origins = settings.cors_origin_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cli = typer.Typer()


@cli.command()
def db_init_models():
    print("Done")


if __name__ == "__main__":
    cli()
