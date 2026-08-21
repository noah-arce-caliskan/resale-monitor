from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    query: str = Field(min_length=1, max_length=200)
    center_place: str = Field(min_length=1, max_length=200)
    radius_miles: int = Field(gt=0, le=500)
    minimum_price_minor: int | None = Field(default=None, ge=0)
    maximum_price_minor: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_price_range(self) -> "WatchlistCreate":
        if (
            self.minimum_price_minor is not None
            and self.maximum_price_minor is not None
            and self.maximum_price_minor < self.minimum_price_minor
        ):
            raise ValueError("maximum price must not be below minimum price")
        return self


class SearchScopeRead(BaseModel):
    id: str
    provider: str
    purpose: str
    query: dict[str, Any]
    geography: dict[str, Any]
    enabled: bool


class WatchlistRead(BaseModel):
    id: str
    name: str
    category: str
    status: str
    center_place: str
    radius_miles: int
    minimum_price_minor: int | None
    maximum_price_minor: int | None
    currency: str
    created_at: datetime
    scopes: list[SearchScopeRead]
