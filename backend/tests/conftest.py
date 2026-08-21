from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from resale_monitor.config import Settings
from resale_monitor.main import create_app
from resale_monitor.models import metadata


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'test.sqlite3'}"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def app(database_url: str) -> FastAPI:
    app = create_app(Settings(database_url=database_url))
    metadata.create_all(app.state.database.engine)
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)

    async with (
        app.router.lifespan_context(app),
        AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client,
    ):
        yield test_client
