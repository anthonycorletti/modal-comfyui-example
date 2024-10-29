import os
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Dict, TypedDict

import structlog
from fastapi import FastAPI
from fastapi.routing import APIRoute

from app import __version__
from app.kit.postgres import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from app.logging import configure_logging
from app.router import router
from app.settings import settings

log = structlog.get_logger()

os.environ["TZ"] = "UTC"


def generate_unique_openapi_id(route: APIRoute) -> str:
    return f"{route.tags[0]}:{route.name}"


class State(TypedDict):
    asyncengine: AsyncEngine
    asyncsessionmaker: async_sessionmaker[AsyncSession]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[Dict]:
    log.info("starting up app services...")
    subprocess.run("comfy launch --background", shell=True, check=True)
    log.info("started comfy ui")
    # asyncengine = create_async_engine("app")
    # log.info("created async engine")
    # asyncsessionmaker = create_async_sessionmaker(asyncengine)
    # log.info("created async sessionmaker")
    log.info("app starting...")
    # yield {"asyncengine": asyncengine, "asyncsessionmaker": asyncsessionmaker}
    yield {}
    log.info("app stopping...")
    # await asyncengine.dispose()
    # log.info("disposed async engine")
    subprocess.run("comfy stop", shell=True, check=True)
    log.info("stopped comfy ui")
    log.info("app stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title="modal-comfyui-example",
        generate_unique_id_function=generate_unique_openapi_id,
        version=__version__,
        lifespan=lifespan,
    )

    app.include_router(router)

    if not Path(settings.COMFYUI_OUTPUT_DIR).exists():
        Path(settings.COMFYUI_OUTPUT_DIR).mkdir(parents=True)

    return app


configure_logging()
app = create_app()
