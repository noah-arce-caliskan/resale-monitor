from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    MetaData,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    metadata = MetaData()


metadata = Base.metadata


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(40), default="moped")
    status: Mapped[str] = mapped_column(String(20), default="active")
    center_place: Mapped[str] = mapped_column(String(200))
    radius_meters: Mapped[int]
    minimum_price_minor: Mapped[int | None]
    maximum_price_minor: Mapped[int | None]
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    preferences_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    last_successful_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )


class SearchScope(Base):
    __tablename__ = "search_scopes"
    __table_args__ = (
        UniqueConstraint("watchlist_id", "provider", "purpose"),
        Index("ix_search_scopes_due", "enabled", "next_run_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    watchlist_id: Mapped[str] = mapped_column(ForeignKey("watchlists.id"))
    provider: Mapped[str] = mapped_column(String(40))
    purpose: Mapped[str] = mapped_column(String(30))
    query_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    geography_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    provider_filters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    cadence_seconds: Mapped[int]
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    authorization_mode: Mapped[str] = mapped_column(String(30), default="official_api")
    adapter_version: Mapped[str] = mapped_column(String(30), default="ebay-v1")
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_succeeded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class SourceRun(Base):
    __tablename__ = "source_runs"
    __table_args__ = (Index("ix_source_runs_lease", "status", "lease_expires_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    search_scope_id: Mapped[str | None] = mapped_column(ForeignKey("search_scopes.id"))
    provider: Mapped[str] = mapped_column(String(40))
    purpose: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="queued")
    adapter_version: Mapped[str] = mapped_column(String(30))
    request_fingerprint: Mapped[str] = mapped_column(String(64))
    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_seen: Mapped[int] = mapped_column(default=0)
    new_listings: Mapped[int] = mapped_column(default=0)
    changed_listings: Mapped[int] = mapped_column(default=0)
    rejected_records: Mapped[int] = mapped_column(default=0)
    error_code: Mapped[str | None] = mapped_column(String(80))
    error_detail: Mapped[str | None] = mapped_column(Text)


class SourceRecord(Base):
    __tablename__ = "source_records"
    __table_args__ = (UniqueConstraint("source_run_id", "content_hash"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source_run_id: Mapped[str] = mapped_column(ForeignKey("source_runs.id"))
    provider: Mapped[str] = mapped_column(String(40))
    provider_record_id: Mapped[str | None] = mapped_column(String(200))
    source_url: Mapped[str] = mapped_column(Text)
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    content_hash: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    category: Mapped[str] = mapped_column(String(40), default="moped")
    current_status: Mapped[str] = mapped_column(String(30), default="available")
    status_confidence_bp: Mapped[int] = mapped_column(default=10000)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class ListingSource(Base):
    __tablename__ = "listing_sources"
    __table_args__ = (UniqueConstraint("provider", "provider_listing_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.id"))
    provider: Mapped[str] = mapped_column(String(40))
    provider_listing_id: Mapped[str] = mapped_column(String(200))
    canonical_url: Mapped[str] = mapped_column(Text)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    last_checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    first_missing_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_provider_status: Mapped[str] = mapped_column(
        String(30), default="available"
    )
    content_fingerprint: Mapped[str] = mapped_column(String(64))


class ListingObservation(Base):
    __tablename__ = "listing_observations"
    __table_args__ = (
        Index("ix_listing_observations_timeline", "listing_id", "observed_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.id"))
    listing_source_id: Mapped[str] = mapped_column(ForeignKey("listing_sources.id"))
    source_record_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_records.id")
    )
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    retrieval_outcome: Mapped[str] = mapped_column(String(30), default="available")
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    location_text: Mapped[str | None] = mapped_column(String(200))
    asking_price_minor: Mapped[int | None]
    shipping_price_minor: Mapped[int | None]
    currency: Mapped[str | None] = mapped_column(String(3))
    provider_status: Mapped[str] = mapped_column(String(30), default="available")
    content_hash: Mapped[str] = mapped_column(String(64), index=True)


class ImageAsset(Base):
    __tablename__ = "image_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    sha256: Mapped[str | None] = mapped_column(String(64), unique=True)
    original_url: Mapped[str] = mapped_column(Text)
    local_relative_path: Mapped[str | None] = mapped_column(Text)
    display_strategy: Mapped[str] = mapped_column(String(20), default="remote")
    retention_status: Mapped[str] = mapped_column(String(30), default="not_retained")
    media_type: Mapped[str | None] = mapped_column(String(100))
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class ObservationImage(Base):
    __tablename__ = "observation_images"

    observation_id: Mapped[str] = mapped_column(
        ForeignKey("listing_observations.id"), primary_key=True
    )
    image_asset_id: Mapped[str] = mapped_column(
        ForeignKey("image_assets.id"), primary_key=True
    )
    ordinal: Mapped[int]
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)


class WatchlistListing(Base):
    __tablename__ = "watchlist_listings"
    __table_args__ = (
        Index(
            "ix_watchlist_feed", "watchlist_id", "role", "feed_state", "last_changed_at"
        ),
    )

    watchlist_id: Mapped[str] = mapped_column(
        ForeignKey("watchlists.id"), primary_key=True
    )
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), primary_key=True)
    first_discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    last_discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    last_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    feed_state: Mapped[str] = mapped_column(String(20), default="new")
    latest_analysis_id: Mapped[str | None] = mapped_column(String(36))


class ItemVersion(Base):
    __tablename__ = "item_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.id"))
    based_on_observation_id: Mapped[str] = mapped_column(
        ForeignKey("listing_observations.id")
    )
    previous_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("item_versions.id")
    )
    version_kind: Mapped[str] = mapped_column(String(30), default="extraction")
    make: Mapped[str | None] = mapped_column(String(100), index=True)
    model: Mapped[str | None] = mapped_column(String(100), index=True)
    model_year: Mapped[int | None] = mapped_column(index=True)
    displacement_cc: Mapped[int | None] = mapped_column(index=True)
    mileage: Mapped[int | None]
    running_state: Mapped[str | None] = mapped_column(String(30))
    title_state: Mapped[str | None] = mapped_column(String(30))
    normalized_condition: Mapped[str | None] = mapped_column(String(30))
    category_attributes_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    overall_confidence_bp: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    created_by: Mapped[str] = mapped_column(String(20), default="system")


class AttributeEvidence(Base):
    __tablename__ = "attribute_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    item_version_id: Mapped[str] = mapped_column(ForeignKey("item_versions.id"))
    field_path: Mapped[str] = mapped_column(String(200))
    value_json: Mapped[Any] = mapped_column(JSON)
    evidence_kind: Mapped[str] = mapped_column(String(30))
    observation_id: Mapped[str | None] = mapped_column(
        ForeignKey("listing_observations.id")
    )
    confidence_bp: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class OutcomeEvidence(Base):
    __tablename__ = "outcome_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    listing_source_id: Mapped[str] = mapped_column(ForeignKey("listing_sources.id"))
    outcome_type: Mapped[str] = mapped_column(String(30))
    final_price_minor: Mapped[int | None]
    currency: Mapped[str | None] = mapped_column(String(3))
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    provenance_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    confidence_bp: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class MarketEvidence(Base):
    __tablename__ = "market_evidence"
    __table_args__ = (
        Index("ix_market_evidence_lookup", "evidence_type", "observed_at", "currency"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    evidence_type: Mapped[str] = mapped_column(String(30))
    listing_observation_id: Mapped[str | None] = mapped_column(
        ForeignKey("listing_observations.id")
    )
    outcome_evidence_id: Mapped[str | None] = mapped_column(
        ForeignKey("outcome_evidence.id")
    )
    item_version_id: Mapped[str | None] = mapped_column(ForeignKey("item_versions.id"))
    provider: Mapped[str] = mapped_column(String(40))
    price_minor: Mapped[int]
    shipping_minor: Mapped[int] = mapped_column(default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    location_text: Mapped[str | None] = mapped_column(String(200))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    provenance_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    natural_fingerprint: Mapped[str | None] = mapped_column(String(64), unique=True)


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (Index("ix_analyses_history", "listing_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.id"))
    candidate_observation_id: Mapped[str] = mapped_column(
        ForeignKey("listing_observations.id")
    )
    item_version_id: Mapped[str | None] = mapped_column(ForeignKey("item_versions.id"))
    valuation_policy_version: Mapped[str] = mapped_column(
        String(30), default="moped-v0.1"
    )
    analysis_status: Mapped[str] = mapped_column(String(30))
    fair_value_low_minor: Mapped[int | None]
    fair_value_midpoint_minor: Mapped[int | None]
    fair_value_high_minor: Mapped[int | None]
    total_cost_low_minor: Mapped[int | None]
    total_cost_high_minor: Mapped[int | None]
    conservative_advantage_minor: Mapped[int | None]
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    confidence_bp: Mapped[int] = mapped_column(default=0)
    opportunity_label: Mapped[str] = mapped_column(String(30))
    evidence_summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    risk_summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class AnalysisComparable(Base):
    __tablename__ = "analysis_comparables"

    analysis_id: Mapped[str] = mapped_column(
        ForeignKey("analyses.id"), primary_key=True
    )
    market_evidence_id: Mapped[str] = mapped_column(
        ForeignKey("market_evidence.id"), primary_key=True
    )
    decision: Mapped[str] = mapped_column(String(20))
    similarity_bp: Mapped[int]
    reliability_bp: Mapped[int]
    recency_bp: Mapped[int]
    geography_bp: Mapped[int]
    final_weight_bp: Mapped[int]
    rank: Mapped[int | None]
    reason_codes_json: Mapped[list[str]] = mapped_column(JSON, default=list)


class AnalysisCost(Base):
    __tablename__ = "analysis_costs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"))
    cost_kind: Mapped[str] = mapped_column(String(30))
    low_minor: Mapped[int]
    high_minor: Mapped[int]
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    basis: Mapped[str] = mapped_column(String(20))
    confidence_bp: Mapped[int]
    rationale: Mapped[str] = mapped_column(Text)
