import pytest
from httpx import AsyncClient

from resale_monitor.database import Database


@pytest.mark.anyio
async def test_readiness_reports_database_health(client: AsyncClient) -> None:
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "resale-monitor",
        "checks": {"database": "ok"},
    }


@pytest.mark.anyio
async def test_liveness_does_not_require_database(client: AsyncClient) -> None:
    response = await client.get("/api/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "resale-monitor"}


@pytest.mark.anyio
async def test_readiness_returns_503_when_database_is_unavailable(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Database, "is_ready", lambda _: False)

    response = await client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database is unavailable"}
