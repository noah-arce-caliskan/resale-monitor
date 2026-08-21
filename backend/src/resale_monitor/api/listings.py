from typing import cast

from fastapi import APIRouter, HTTPException, Request

from resale_monitor.database import Database
from resale_monitor.schemas.feed import ListingDetailRead
from resale_monitor.services.ingestion import listing_detail

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("/{listing_id}", response_model=ListingDetailRead)
def detail(listing_id: str, request: Request) -> ListingDetailRead:
    database = cast(Database, request.app.state.database)
    try:
        with database.session() as session:
            return listing_detail(session, listing_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
