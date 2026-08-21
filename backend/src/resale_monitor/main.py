from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from resale_monitor import __version__
from resale_monitor.api.health import router as health_router
from resale_monitor.config import Settings
from resale_monitor.database import create_database


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()
    database = create_database(app_settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        database.dispose()

    app = FastAPI(
        title="Resale Monitor API",
        version=__version__,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.state.database = database
    app.include_router(health_router)
    return app


app = create_app()
