from typing import Literal

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from resale_monitor.database import Database

router = APIRouter(prefix="/api/health", tags=["health"])


class LiveResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["resale-monitor"] = "resale-monitor"


class ReadinessChecks(BaseModel):
    database: Literal["ok"] = "ok"


class ReadinessResponse(LiveResponse):
    checks: ReadinessChecks


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


@router.get("/live", response_model=LiveResponse)
def liveness() -> LiveResponse:
    return LiveResponse()


@router.get("", response_model=ReadinessResponse)
def readiness(request: Request) -> ReadinessResponse:
    if not _database(request).is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        )

    return ReadinessResponse(checks=ReadinessChecks())
