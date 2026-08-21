import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Protocol, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from resale_monitor.models import (
    Analysis,
    AnalysisComparable,
    AnalysisCost,
    ImageAsset,
    ItemVersion,
    Listing,
    ListingObservation,
    ListingSource,
    MarketEvidence,
    ObservationImage,
    SearchScope,
    SourceRecord,
    SourceRun,
    Watchlist,
    WatchlistListing,
    utc_now,
)
from resale_monitor.providers.ebay import ProviderListing
from resale_monitor.valuation import ComparableInput, ValuationInput, valuate


class ListingProvider(Protocol):
    async def search(
        self, *, query: str, purpose: str, radius_miles: int
    ) -> list[ProviderListing]: ...


@dataclass(frozen=True)
class RunSummary:
    records_seen: int
    new_listings: int
    changed_listings: int


async def run_watchlist(
    session: Session, watchlist_id: str, provider: ListingProvider
) -> RunSummary:
    watchlist = session.get(Watchlist, watchlist_id)
    if watchlist is None:
        raise LookupError("watchlist not found")
    scopes = list(
        session.scalars(
            select(SearchScope)
            .where(
                SearchScope.watchlist_id == watchlist_id, SearchScope.enabled.is_(True)
            )
            .order_by(SearchScope.purpose)
        ).all()
    )
    totals = RunSummary(0, 0, 0)
    for scope in scopes:
        found = await provider.search(
            query=str(scope.query_json["keywords"]),
            purpose=scope.purpose,
            radius_miles=round(watchlist.radius_meters / 1609),
        )
        summary = _ingest_scope(session, watchlist, scope, found)
        totals = RunSummary(
            totals.records_seen + summary.records_seen,
            totals.new_listings + summary.new_listings,
            totals.changed_listings + summary.changed_listings,
        )
    _analyze_acquisition_feed(session, watchlist_id)
    watchlist.last_successful_run_at = utc_now()
    return totals


def _ingest_scope(
    session: Session,
    watchlist: Watchlist,
    scope: SearchScope,
    found: list[ProviderListing],
) -> RunSummary:
    now = utc_now()
    fingerprint = _hash({"scope": scope.id, "query": scope.query_json})
    run = SourceRun(
        search_scope_id=scope.id,
        provider="ebay",
        purpose=scope.purpose,
        status="running",
        adapter_version=scope.adapter_version,
        request_fingerprint=fingerprint,
        started_at=now,
    )
    session.add(run)
    session.flush()
    new_count = 0
    changed_count = 0
    for item in found:
        content_hash = _hash(asdict(item))
        record = SourceRecord(
            source_run_id=run.id,
            provider="ebay",
            provider_record_id=item.provider_listing_id,
            source_url=item.canonical_url,
            content_hash=content_hash,
            payload_json=item.payload,
        )
        session.add(record)
        source = session.scalar(
            select(ListingSource).where(
                ListingSource.provider == "ebay",
                ListingSource.provider_listing_id == item.provider_listing_id,
            )
        )
        if source is None:
            listing = Listing()
            session.add(listing)
            session.flush()
            source = ListingSource(
                listing_id=listing.id,
                provider="ebay",
                provider_listing_id=item.provider_listing_id,
                canonical_url=item.canonical_url,
                content_fingerprint=content_hash,
            )
            session.add(source)
            session.flush()
            observation = _add_observation(
                session, listing, source, record, item, content_hash
            )
            _add_item_version(session, listing, observation)
            _add_image(session, observation, item)
            new_count += 1
        else:
            listing = session.get_one(Listing, source.listing_id)
            source.last_checked_at = now
            source.last_seen_at = now
            listing.last_seen_at = now
            if source.content_fingerprint != content_hash:
                source.content_fingerprint = content_hash
                observation = _add_observation(
                    session, listing, source, record, item, content_hash
                )
                _add_item_version(session, listing, observation)
                _add_image(session, observation, item)
                changed_count += 1
        projection = session.get(
            WatchlistListing,
            {
                "watchlist_id": watchlist.id,
                "listing_id": listing.id,
                "role": scope.purpose,
            },
        )
        if projection is None:
            session.add(
                WatchlistListing(
                    watchlist_id=watchlist.id,
                    listing_id=listing.id,
                    role=scope.purpose,
                )
            )
        else:
            projection.last_discovered_at = now
        if scope.purpose == "reference":
            latest_observation = session.scalar(
                select(ListingObservation)
                .where(ListingObservation.listing_id == listing.id)
                .order_by(ListingObservation.observed_at.desc())
            )
            assert latest_observation is not None
            natural = f"ebay:{item.provider_listing_id}:{content_hash}"
            exists = session.scalar(
                select(MarketEvidence.id).where(
                    MarketEvidence.natural_fingerprint == natural
                )
            )
            if exists is None:
                session.add(
                    MarketEvidence(
                        evidence_type="active_asking",
                        listing_observation_id=latest_observation.id,
                        provider="ebay",
                        price_minor=item.asking_price_minor,
                        shipping_minor=item.shipping_price_minor,
                        currency=item.currency,
                        location_text=item.location_text,
                        observed_at=latest_observation.observed_at,
                        provenance_json={"fixture": item.payload.get("fixture", False)},
                        natural_fingerprint=natural,
                    )
                )
    run.status = "succeeded"
    run.finished_at = utc_now()
    run.records_seen = len(found)
    run.new_listings = new_count
    run.changed_listings = changed_count
    scope.last_succeeded_at = run.finished_at
    return RunSummary(len(found), new_count, changed_count)


def _add_observation(
    session: Session,
    listing: Listing,
    source: ListingSource,
    record: SourceRecord,
    item: ProviderListing,
    content_hash: str,
) -> ListingObservation:
    observation = ListingObservation(
        listing_id=listing.id,
        listing_source_id=source.id,
        source_record_id=record.id,
        title=item.title,
        location_text=item.location_text,
        asking_price_minor=item.asking_price_minor,
        shipping_price_minor=item.shipping_price_minor,
        currency=item.currency,
        content_hash=content_hash,
    )
    session.add(observation)
    session.flush()
    return observation


def _add_item_version(
    session: Session, listing: Listing, observation: ListingObservation
) -> None:
    title = (observation.title or "").lower()
    session.add(
        ItemVersion(
            listing_id=listing.id,
            based_on_observation_id=observation.id,
            make="Honda" if "honda" in title else None,
            model="Metropolitan" if "metropolitan" in title else None,
            displacement_cc=50 if "50cc" in title else None,
            normalized_condition="used",
            overall_confidence_bp=9000,
        )
    )


def _add_image(
    session: Session, observation: ListingObservation, item: ProviderListing
) -> None:
    if item.image_url is None:
        return
    image = session.scalar(
        select(ImageAsset).where(ImageAsset.original_url == item.image_url)
    )
    if image is None:
        image = ImageAsset(original_url=item.image_url)
        session.add(image)
        session.flush()
    session.add(
        ObservationImage(
            observation_id=observation.id,
            image_asset_id=image.id,
            ordinal=0,
            is_primary=True,
        )
    )


def _analyze_acquisition_feed(session: Session, watchlist_id: str) -> None:
    comparables = list(session.scalars(select(MarketEvidence)).all())
    comparable_inputs = [
        ComparableInput(
            price_minor=item.price_minor + item.shipping_minor, weight_bp=4500
        )
        for item in comparables
    ]
    projections = session.scalars(
        select(WatchlistListing).where(
            WatchlistListing.watchlist_id == watchlist_id,
            WatchlistListing.role == "acquisition",
        )
    ).all()
    for projection in projections:
        observation = session.scalar(
            select(ListingObservation)
            .where(ListingObservation.listing_id == projection.listing_id)
            .order_by(ListingObservation.observed_at.desc())
        )
        assert observation is not None
        existing = session.scalar(
            select(Analysis).where(
                Analysis.listing_id == projection.listing_id,
                Analysis.candidate_observation_id == observation.id,
            )
        )
        if existing is not None:
            projection.latest_analysis_id = existing.id
            continue
        result = valuate(
            ValuationInput(
                asking_price_minor=observation.asking_price_minor,
                additional_cost_low_minor=15_000,
                additional_cost_high_minor=35_000,
                comparables=comparable_inputs,
            )
        )
        version = session.scalar(
            select(ItemVersion)
            .where(ItemVersion.listing_id == projection.listing_id)
            .order_by(ItemVersion.created_at.desc())
        )
        analysis = Analysis(
            listing_id=projection.listing_id,
            candidate_observation_id=observation.id,
            item_version_id=version.id if version else None,
            analysis_status="complete",
            fair_value_low_minor=result.fair_value_low_minor,
            fair_value_midpoint_minor=result.fair_value_midpoint_minor,
            fair_value_high_minor=result.fair_value_high_minor,
            total_cost_low_minor=result.total_cost_low_minor,
            total_cost_high_minor=result.total_cost_high_minor,
            conservative_advantage_minor=result.conservative_advantage_minor,
            confidence_bp=result.confidence_bp,
            opportunity_label=result.opportunity_label,
            evidence_summary_json={"comparable_count": len(comparables)},
            risk_summary_json={},
        )
        session.add(analysis)
        session.flush()
        projection.latest_analysis_id = analysis.id
        for rank, comparable in enumerate(comparables, start=1):
            session.add(
                AnalysisComparable(
                    analysis_id=analysis.id,
                    market_evidence_id=comparable.id,
                    decision="included",
                    similarity_bp=8000,
                    reliability_bp=4500,
                    recency_bp=10000,
                    geography_bp=7000,
                    final_weight_bp=4500,
                    rank=rank,
                    reason_codes_json=["same_make_model", "active_asking"],
                )
            )
        session.add(
            AnalysisCost(
                analysis_id=analysis.id,
                cost_kind="risk_reserve",
                low_minor=15_000,
                high_minor=35_000,
                basis="rule",
                confidence_bp=6000,
                rationale="Initial moped transport and unresolved-condition reserve",
            )
        )


def watchlist_detail(session: Session, watchlist_id: str) -> dict[str, object]:
    reference_count = session.scalar(
        select(func.count())
        .select_from(WatchlistListing)
        .where(
            WatchlistListing.watchlist_id == watchlist_id,
            WatchlistListing.role == "reference",
        )
    )
    rows = session.scalars(
        select(WatchlistListing).where(
            WatchlistListing.watchlist_id == watchlist_id,
            WatchlistListing.role == "acquisition",
        )
    ).all()
    feed: list[dict[str, object]] = []
    for row in rows:
        observation = session.scalar(
            select(ListingObservation)
            .where(ListingObservation.listing_id == row.listing_id)
            .order_by(ListingObservation.observed_at.desc())
        )
        analysis = (
            session.get(Analysis, row.latest_analysis_id)
            if row.latest_analysis_id
            else None
        )
        image_url = (
            session.scalar(
                select(ImageAsset.original_url)
                .join(
                    ObservationImage, ObservationImage.image_asset_id == ImageAsset.id
                )
                .where(ObservationImage.observation_id == observation.id)
            )
            if observation
            else None
        )
        if observation:
            feed.append(
                {
                    "listing_id": row.listing_id,
                    "title": observation.title,
                    "asking_price_minor": observation.asking_price_minor,
                    "image_url": image_url,
                    "opportunity_label": analysis.opportunity_label
                    if analysis
                    else "pending",
                    "confidence_bp": analysis.confidence_bp if analysis else 0,
                    "fair_value_low_minor": analysis.fair_value_low_minor
                    if analysis
                    else None,
                    "conservative_advantage_minor": (
                        analysis.conservative_advantage_minor if analysis else None
                    ),
                }
            )
    feed.sort(
        key=lambda item: cast(int | None, item["conservative_advantage_minor"]) or -1,
        reverse=True,
    )
    return {"reference_count": reference_count or 0, "feed": feed}


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
