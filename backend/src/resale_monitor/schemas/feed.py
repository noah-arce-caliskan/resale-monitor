from datetime import datetime

from pydantic import BaseModel


class SourceHealthRead(BaseModel):
    purpose: str
    status: str
    records_seen: int
    new_listings: int
    changed_listings: int
    error_code: str | None
    error_detail: str | None
    finished_at: datetime | None


class FeedItemRead(BaseModel):
    listing_id: str
    title: str
    asking_price_minor: int
    image_url: str | None
    opportunity_label: str
    confidence_bp: int
    fair_value_low_minor: int | None
    conservative_advantage_minor: int | None


class ReferenceRead(BaseModel):
    listing_id: str
    title: str
    price_minor: int
    location_text: str | None
    evidence_type: str


class WatchlistDetailRead(BaseModel):
    reference_count: int
    source_health: list[SourceHealthRead]
    feed: list[FeedItemRead]
    references: list[ReferenceRead]


class ObservationRead(BaseModel):
    observed_at: datetime
    retrieval_outcome: str
    asking_price_minor: int | None
    provider_status: str


class ComparableRead(BaseModel):
    market_evidence_id: str
    title: str
    price_minor: int
    evidence_type: str
    provider: str
    final_weight_bp: int
    reason_codes: list[str]


class CostRead(BaseModel):
    kind: str
    low_minor: int
    high_minor: int
    rationale: str


class ListingDetailRead(BaseModel):
    listing_id: str
    title: str
    source_url: str
    provider_status: str
    image_urls: list[str]
    attributes: dict[str, str | int | None]
    opportunity_label: str
    confidence_bp: int
    fair_value_low_minor: int | None
    fair_value_midpoint_minor: int | None
    fair_value_high_minor: int | None
    total_cost_low_minor: int | None
    total_cost_high_minor: int | None
    conservative_advantage_minor: int | None
    observations: list[ObservationRead]
    comparables: list[ComparableRead]
    costs: list[CostRead]
