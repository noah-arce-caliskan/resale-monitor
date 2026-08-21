import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_create_hartford_moped_watchlist_builds_two_scopes(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/watchlists",
        json={
            "name": "Mopeds near Hartford",
            "query": "moped scooter",
            "center_place": "Hartford, CT",
            "radius_miles": 50,
            "maximum_price_minor": 300_000,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["category"] == "moped"
    assert payload["status"] == "active"
    assert [(scope["provider"], scope["purpose"]) for scope in payload["scopes"]] == [
        ("ebay", "acquisition"),
        ("ebay", "reference"),
    ]
    assert payload["scopes"][0]["geography"]["radius_miles"] == 50
    assert payload["scopes"][1]["geography"] == {"country": "US"}

    listed = await client.get("/api/watchlists")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [payload["id"]]


async def test_create_watchlist_rejects_invalid_price_range(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/watchlists",
        json={
            "name": "Impossible range",
            "query": "moped",
            "center_place": "Hartford, CT",
            "radius_miles": 25,
            "minimum_price_minor": 200_000,
            "maximum_price_minor": 100_000,
        },
    )

    assert response.status_code == 422
