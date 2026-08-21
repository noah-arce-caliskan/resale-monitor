from dataclasses import replace

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from resale_monitor.providers.ebay import FixtureEbayClient, ProviderRateLimitError
from resale_monitor.services.ingestion import record_retrieval_outcome

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


async def test_fixture_run_builds_ranked_feed_and_is_idempotent(
    client: AsyncClient,
) -> None:
    created = await client.post(
        "/api/watchlists",
        json={
            "name": "Mopeds near Hartford",
            "query": "moped scooter",
            "center_place": "Hartford, CT",
            "radius_miles": 50,
        },
    )
    watchlist_id = created.json()["id"]

    first = await client.post(f"/api/watchlists/{watchlist_id}/runs")
    second = await client.post(f"/api/watchlists/{watchlist_id}/runs")
    detail = await client.get(f"/api/watchlists/{watchlist_id}")

    assert first.status_code == 200
    assert first.json() == {
        "records_seen": 7,
        "new_listings": 7,
        "changed_listings": 0,
    }
    assert second.json() == {
        "records_seen": 7,
        "new_listings": 0,
        "changed_listings": 0,
    }
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["reference_count"] == 5
    assert len(payload["references"]) == 5
    assert [item["status"] for item in payload["source_health"]] == [
        "succeeded",
        "succeeded",
    ]
    assert len(payload["feed"]) == 2
    assert payload["feed"][0]["opportunity_label"] in {"promising", "watch"}
    assert payload["feed"][0]["image_url"] == "/demo-moped.svg"

    listing = await client.get(f"/api/listings/{payload['feed'][0]['listing_id']}")
    assert listing.status_code == 200
    evidence = listing.json()
    assert evidence["attributes"]["make"] == "Honda"
    assert len(evidence["comparables"]) == 5
    assert evidence["comparables"][0]["evidence_type"] == "active_asking"
    assert evidence["costs"][0]["kind"] == "risk_reserve"
    assert len(evidence["observations"]) == 1


async def test_changed_listing_appends_observation_history(
    app: FastAPI, client: AsyncClient
) -> None:
    class ChangingProvider(FixtureEbayClient):
        acquisition_round = 0
        reference_round = 0

        async def search(self, *, query: str, purpose: str, radius_miles: int):
            listings = await super().search(
                query=query, purpose=purpose, radius_miles=radius_miles
            )
            if purpose == "acquisition":
                self.acquisition_round += 1
                if self.acquisition_round == 2:
                    changed = replace(
                        listings[0],
                        asking_price_minor=850_00,
                        payload={
                            "fixture": True,
                            "purpose": purpose,
                            "price_minor": 850_00,
                        },
                    )
                    return [changed, *listings[1:]]
            if purpose == "reference":
                self.reference_round += 1
                if self.reference_round == 2:
                    return [
                        replace(item, image_url=f"/changed-{index}.svg")
                        for index, item in enumerate(listings)
                    ]
            return listings

    app.state.listing_provider = ChangingProvider()
    created = await client.post(
        "/api/watchlists",
        json={
            "name": "History",
            "query": "moped",
            "center_place": "Hartford, CT",
            "radius_miles": 50,
        },
    )
    watchlist_id = created.json()["id"]
    await client.post(f"/api/watchlists/{watchlist_id}/runs")
    changed = await client.post(f"/api/watchlists/{watchlist_id}/runs")
    detail = (await client.get(f"/api/watchlists/{watchlist_id}")).json()
    listing = (
        await client.get(f"/api/listings/{detail['feed'][0]['listing_id']}")
    ).json()

    assert changed.json()["changed_listings"] == 6
    assert [item["asking_price_minor"] for item in listing["observations"]] == [
        850_00,
        900_00,
    ]
    assert len(listing["comparables"]) == 5


async def test_reference_price_change_revalues_unchanged_acquisition(
    app: FastAPI, client: AsyncClient
) -> None:
    class RepricedReferenceProvider(FixtureEbayClient):
        reference_round = 0

        async def search(self, *, query: str, purpose: str, radius_miles: int):
            listings = await super().search(
                query=query, purpose=purpose, radius_miles=radius_miles
            )
            if purpose == "reference":
                self.reference_round += 1
                if self.reference_round == 2:
                    return [
                        replace(
                            listings[0],
                            asking_price_minor=2500_00,
                            payload={
                                "fixture": True,
                                "purpose": purpose,
                                "price_minor": 2500_00,
                            },
                        ),
                        *listings[1:],
                    ]
            return listings

    app.state.listing_provider = RepricedReferenceProvider()
    created = await client.post(
        "/api/watchlists",
        json={
            "name": "Repricing",
            "query": "moped",
            "center_place": "Hartford, CT",
            "radius_miles": 50,
        },
    )
    watchlist_id = created.json()["id"]
    await client.post(f"/api/watchlists/{watchlist_id}/runs")
    first_feed = (await client.get(f"/api/watchlists/{watchlist_id}")).json()["feed"]
    first = (await client.get(f"/api/listings/{first_feed[0]['listing_id']}")).json()

    changed = await client.post(f"/api/watchlists/{watchlist_id}/runs")
    second = (await client.get(f"/api/listings/{first_feed[0]['listing_id']}")).json()

    assert changed.json()["changed_listings"] == 1
    assert len(second["observations"]) == 1
    assert len(second["comparables"]) == 5
    assert 2500_00 in [item["price_minor"] for item in second["comparables"]]
    assert 1500_00 not in [item["price_minor"] for item in second["comparables"]]
    assert second["fair_value_midpoint_minor"] != first["fair_value_midpoint_minor"]


async def test_rate_limit_is_persisted_as_source_health(
    app: FastAPI, client: AsyncClient
) -> None:
    class LimitedProvider:
        async def search(self, *, query: str, purpose: str, radius_miles: int):
            del query, purpose, radius_miles
            raise ProviderRateLimitError(120)

    app.state.listing_provider = LimitedProvider()
    created = await client.post(
        "/api/watchlists",
        json={
            "name": "Limited",
            "query": "moped",
            "center_place": "Hartford, CT",
            "radius_miles": 50,
        },
    )
    watchlist_id = created.json()["id"]
    result = await client.post(f"/api/watchlists/{watchlist_id}/runs")
    detail = (await client.get(f"/api/watchlists/{watchlist_id}")).json()

    assert result.json()["records_seen"] == 0
    assert [item["status"] for item in detail["source_health"]] == [
        "rate_limited",
        "rate_limited",
    ]
    assert all(
        item["error_detail"] == "Retry after 120 seconds."
        for item in detail["source_health"]
    )


async def test_missing_listing_remains_unknown_and_can_recover(
    app: FastAPI, client: AsyncClient
) -> None:
    created = await client.post(
        "/api/watchlists",
        json={
            "name": "Lifecycle",
            "query": "moped",
            "center_place": "Hartford, CT",
            "radius_miles": 50,
        },
    )
    watchlist_id = created.json()["id"]
    await client.post(f"/api/watchlists/{watchlist_id}/runs")
    listing_id = (await client.get(f"/api/watchlists/{watchlist_id}")).json()["feed"][
        0
    ]["listing_id"]

    with app.state.database.session() as session:
        record_retrieval_outcome(session, listing_id, "missing")
    missing = (await client.get(f"/api/listings/{listing_id}")).json()
    assert missing["provider_status"] == "unavailable_unknown"
    assert missing["observations"][0]["retrieval_outcome"] == "missing"
    assert all(item["provider_status"] != "sold" for item in missing["observations"])

    with app.state.database.session() as session:
        record_retrieval_outcome(session, listing_id, "missing")
    still_missing = (await client.get(f"/api/listings/{listing_id}")).json()
    assert still_missing["provider_status"] == "unavailable_unknown"

    with app.state.database.session() as session:
        record_retrieval_outcome(session, listing_id, "available")
    recovered = (await client.get(f"/api/listings/{listing_id}")).json()
    assert recovered["provider_status"] == "available"
    assert [item["retrieval_outcome"] for item in recovered["observations"][:3]] == [
        "available",
        "missing",
        "missing",
    ]
