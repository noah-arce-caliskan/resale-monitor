from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from resale_monitor.config import Settings
from resale_monitor.main import create_app


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'test.sqlite3'}"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client(database_url: str) -> AsyncIterator[AsyncClient]:
    app = create_app(Settings(database_url=database_url))
    transport = ASGITransport(app=app)

    async with (
        app.router.lifespan_context(app),
        AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client,
    ):
        yield test_client
