from fastapi import APIRouter, Request, status

from resale_monitor.database import Database
from resale_monitor.schemas.watchlists import WatchlistCreate, WatchlistRead
from resale_monitor.services.watchlists import create_watchlist, list_watchlists

router = APIRouter(prefix="/api/watchlists", tags=["watchlists"])


def _database(request: Request) -> Database:
    return request.app.state.database


@router.post("", response_model=WatchlistRead, status_code=status.HTTP_201_CREATED)
def create(command: WatchlistCreate, request: Request) -> WatchlistRead:
    with _database(request).session() as session:
        return create_watchlist(session, command)


@router.get("", response_model=list[WatchlistRead])
def list_all(request: Request) -> list[WatchlistRead]:
    with _database(request).session() as session:
        return list_watchlists(session)
