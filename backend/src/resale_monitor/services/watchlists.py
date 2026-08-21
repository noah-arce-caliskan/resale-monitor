from sqlalchemy import select
from sqlalchemy.orm import Session

from resale_monitor.models import SearchScope, Watchlist
from resale_monitor.schemas.watchlists import (
    SearchScopeRead,
    WatchlistCreate,
    WatchlistRead,
)

METERS_PER_MILE = 1609


def create_watchlist(session: Session, command: WatchlistCreate) -> WatchlistRead:
    watchlist = Watchlist(
        name=command.name,
        center_place=command.center_place,
        radius_meters=command.radius_miles * METERS_PER_MILE,
        minimum_price_minor=command.minimum_price_minor,
        maximum_price_minor=command.maximum_price_minor,
        preferences_json={},
    )
    session.add(watchlist)
    session.flush()

    query = {"keywords": command.query, "category": "moped"}
    scopes = [
        SearchScope(
            watchlist_id=watchlist.id,
            provider="ebay",
            purpose="acquisition",
            query_json=query,
            geography_json={
                "center_place": command.center_place,
                "radius_miles": command.radius_miles,
            },
            cadence_seconds=3600,
        ),
        SearchScope(
            watchlist_id=watchlist.id,
            provider="ebay",
            purpose="reference",
            query_json=query,
            geography_json={"country": "US"},
            cadence_seconds=86400,
        ),
    ]
    session.add_all(scopes)
    session.flush()
    return _to_read(watchlist, scopes)


def list_watchlists(session: Session) -> list[WatchlistRead]:
    watchlists = session.scalars(select(Watchlist).order_by(Watchlist.created_at)).all()
    results: list[WatchlistRead] = []
    for watchlist in watchlists:
        scopes = session.scalars(
            select(SearchScope)
            .where(SearchScope.watchlist_id == watchlist.id)
            .order_by(SearchScope.purpose)
        ).all()
        results.append(_to_read(watchlist, list(scopes)))
    return results


def _to_read(watchlist: Watchlist, scopes: list[SearchScope]) -> WatchlistRead:
    purpose_order = {"acquisition": 0, "reference": 1}
    scopes.sort(key=lambda scope: purpose_order.get(scope.purpose, 99))
    return WatchlistRead(
        id=watchlist.id,
        name=watchlist.name,
        category=watchlist.category,
        status=watchlist.status,
        center_place=watchlist.center_place,
        radius_miles=round(watchlist.radius_meters / METERS_PER_MILE),
        minimum_price_minor=watchlist.minimum_price_minor,
        maximum_price_minor=watchlist.maximum_price_minor,
        currency=watchlist.currency,
        created_at=watchlist.created_at,
        scopes=[
            SearchScopeRead(
                id=scope.id,
                provider=scope.provider,
                purpose=scope.purpose,
                query=scope.query_json,
                geography=scope.geography_json,
                enabled=scope.enabled,
            )
            for scope in scopes
        ],
    )
