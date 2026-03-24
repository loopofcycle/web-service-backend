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

# logging.basicConfig(
#     level=logging.INFO,
#     format="{levelname}:{asctime}:{message}",
#     style="{",
#     datefmt="%Y-%m-%d %H:%M")

scheduler = AsyncIOScheduler(timezone=utc)


@scheduler.scheduled_job(trigger='interval', max_instances=1, minutes=60)
async def periodic_job():
    await periodic(AdminCommand(user='igor', password='eliseev'))
    logging.info(f'{__name__}: cron_job: finished')


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


description = """
this API provide high level management of revit files. 🚀

## Get revit files from PDM and extract data from it

You can:

* **browse available revit files** .
* **export, print and sync data from those files** .

"""
app = FastAPI(
    title='Template for FastAPI backend',
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
    lifespan=lifespan
)
app.include_router(api_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
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
