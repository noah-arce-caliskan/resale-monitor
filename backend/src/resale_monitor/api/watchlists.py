from dataclasses import asdict
from typing import cast

from fastapi import APIRouter, HTTPException, Request, status

from resale_monitor.database import Database
from resale_monitor.schemas.watchlists import WatchlistCreate, WatchlistRead
from resale_monitor.services.ingestion import run_watchlist, watchlist_detail
from resale_monitor.services.watchlists import create_watchlist, list_watchlists

router = APIRouter(prefix="/api/watchlists", tags=["watchlists"])


def _database(request: Request) -> Database:
    return cast(Database, request.app.state.database)


@router.post("", response_model=WatchlistRead, status_code=status.HTTP_201_CREATED)
def create(command: WatchlistCreate, request: Request) -> WatchlistRead:
    with _database(request).session() as session:
        return create_watchlist(session, command)


@router.get("", response_model=list[WatchlistRead])
def list_all(request: Request) -> list[WatchlistRead]:
    with _database(request).session() as session:
        return list_watchlists(session)


@router.post("/{watchlist_id}/runs")
async def run(watchlist_id: str, request: Request) -> dict[str, int]:
    try:
        with _database(request).session() as session:
            summary = await run_watchlist(
                session, watchlist_id, request.app.state.listing_provider
            )
            return asdict(summary)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{watchlist_id}")
def detail(watchlist_id: str, request: Request) -> dict[str, object]:
    with _database(request).session() as session:
        return watchlist_detail(session, watchlist_id)
