import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Protocol

from sqlalchemy import select
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
from resale_monitor.providers.ebay import (
    ProviderError,
    ProviderListing,
    ProviderRateLimitError,
)
from resale_monitor.schemas.feed import (
    ComparableRead,
    CostRead,
    FeedItemRead,
    ListingDetailRead,
    ObservationRead,
    ReferenceRead,
    SourceHealthRead,
    WatchlistDetailRead,
)
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
    succeeded = False
    for scope in scopes:
        run = _start_run(session, scope)
        try:
            found = await provider.search(
                query=str(scope.query_json["keywords"]),
                purpose=scope.purpose,
                radius_miles=round(watchlist.radius_meters / 1609),
            )
        except ProviderRateLimitError as error:
            run.status = "rate_limited"
            run.finished_at = utc_now()
            run.error_code = "provider_rate_limited"
            run.error_detail = (
                f"Retry after {error.retry_after_seconds} seconds."
                if error.retry_after_seconds is not None
                else "Retry later."
            )
            continue
        except ProviderError:
            run.status = "failed"
            run.finished_at = utc_now()
            run.error_code = "provider_error"
            run.error_detail = "The provider request failed."
            continue
        summary = _ingest_scope(session, watchlist, scope, run, found)
        succeeded = True
        totals = RunSummary(
            totals.records_seen + summary.records_seen,
            totals.new_listings + summary.new_listings,
            totals.changed_listings + summary.changed_listings,
        )
    _analyze_acquisition_feed(session, watchlist_id)
    if succeeded:
        watchlist.last_successful_run_at = utc_now()
    return totals


def _start_run(session: Session, scope: SearchScope) -> SourceRun:
    run = SourceRun(
        search_scope_id=scope.id,
        provider="ebay",
        purpose=scope.purpose,
        status="running",
        adapter_version=scope.adapter_version,
        request_fingerprint=_hash({"scope": scope.id, "query": scope.query_json}),
        started_at=utc_now(),
    )
    session.add(run)
    session.flush()
    scope.last_started_at = run.started_at
    return run


def _ingest_scope(
    session: Session,
    watchlist: Watchlist,
    scope: SearchScope,
    run: SourceRun,
    found: list[ProviderListing],
) -> RunSummary:
    now = utc_now()
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
            natural = ":".join(
                [
                    "ebay",
                    item.provider_listing_id,
                    "active_asking",
                    str(item.asking_price_minor),
                    str(item.shipping_price_minor),
                    item.currency,
                ]
            )
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
                        provenance_json={
                            "fixture": item.payload.get("fixture", False),
                            "provider_listing_id": item.provider_listing_id,
                        },
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
        local_fixture = item.image_url.startswith("/")
        image = ImageAsset(
            original_url=item.image_url,
            local_relative_path=item.image_url.removeprefix("/")
            if local_fixture
            else None,
            display_strategy="local" if local_fixture else "remote",
            retention_status="bundled_fixture" if local_fixture else "not_retained",
        )
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
    comparables = _unique_market_evidence(session, watchlist_id)
    evidence_fingerprint = _hash([item.id for item in comparables])
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
        candidates = session.scalars(
            select(Analysis).where(
                Analysis.listing_id == projection.listing_id,
                Analysis.candidate_observation_id == observation.id,
            )
        ).all()
        existing = next(
            (
                item
                for item in candidates
                if item.evidence_summary_json.get("evidence_fingerprint")
                == evidence_fingerprint
            ),
            None,
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
            evidence_summary_json={
                "comparable_count": len(comparables),
                "evidence_fingerprint": evidence_fingerprint,
            },
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


def watchlist_detail(session: Session, watchlist_id: str) -> WatchlistDetailRead:
    if session.get(Watchlist, watchlist_id) is None:
        raise LookupError("watchlist not found")
    scopes = session.scalars(
        select(SearchScope).where(SearchScope.watchlist_id == watchlist_id)
    ).all()
    health: list[SourceHealthRead] = []
    for scope in scopes:
        run = session.scalar(
            select(SourceRun)
            .where(SourceRun.search_scope_id == scope.id)
            .order_by(SourceRun.queued_at.desc())
        )
        health.append(
            SourceHealthRead(
                purpose=scope.purpose,
                status=run.status if run else "never_run",
                records_seen=run.records_seen if run else 0,
                new_listings=run.new_listings if run else 0,
                changed_listings=run.changed_listings if run else 0,
                error_code=run.error_code if run else None,
                error_detail=run.error_detail if run else None,
                finished_at=run.finished_at if run else None,
            )
        )
    projections = session.scalars(
        select(WatchlistListing).where(WatchlistListing.watchlist_id == watchlist_id)
    ).all()
    feed: list[FeedItemRead] = []
    references: list[ReferenceRead] = []
    for projection in projections:
        observation = _latest_observation(session, projection.listing_id)
        if observation is None:
            continue
        if projection.role == "reference":
            evidence = session.scalar(
                select(MarketEvidence)
                .join(
                    ListingObservation,
                    ListingObservation.id == MarketEvidence.listing_observation_id,
                )
                .where(ListingObservation.listing_id == projection.listing_id)
                .order_by(MarketEvidence.observed_at.desc())
            )
            if evidence:
                references.append(
                    ReferenceRead(
                        listing_id=projection.listing_id,
                        title=observation.title or "Untitled listing",
                        price_minor=evidence.price_minor + evidence.shipping_minor,
                        location_text=evidence.location_text,
                        evidence_type=evidence.evidence_type,
                    )
                )
            continue
        analysis = (
            session.get(Analysis, projection.latest_analysis_id)
            if projection.latest_analysis_id
            else None
        )
        image_url = session.scalar(
            select(ImageAsset.original_url)
            .join(ObservationImage, ObservationImage.image_asset_id == ImageAsset.id)
            .where(ObservationImage.observation_id == observation.id)
        )
        feed.append(
            FeedItemRead(
                listing_id=projection.listing_id,
                title=observation.title or "Untitled listing",
                asking_price_minor=observation.asking_price_minor or 0,
                image_url=image_url,
                opportunity_label=analysis.opportunity_label if analysis else "pending",
                confidence_bp=analysis.confidence_bp if analysis else 0,
                fair_value_low_minor=analysis.fair_value_low_minor
                if analysis
                else None,
                conservative_advantage_minor=(
                    analysis.conservative_advantage_minor if analysis else None
                ),
            )
        )
    feed.sort(key=lambda item: item.conservative_advantage_minor or -1, reverse=True)
    return WatchlistDetailRead(
        reference_count=len(references),
        source_health=sorted(health, key=lambda item: item.purpose),
        feed=feed,
        references=references,
    )


def listing_detail(session: Session, listing_id: str) -> ListingDetailRead:
    listing = session.get(Listing, listing_id)
    source = session.scalar(
        select(ListingSource).where(ListingSource.listing_id == listing_id)
    )
    observations = list(
        session.scalars(
            select(ListingObservation)
            .where(ListingObservation.listing_id == listing_id)
            .order_by(ListingObservation.observed_at.desc())
        ).all()
    )
    if listing is None or source is None or not observations:
        raise LookupError("listing not found")
    current = observations[0]
    version = session.scalar(
        select(ItemVersion)
        .where(ItemVersion.listing_id == listing_id)
        .order_by(ItemVersion.created_at.desc())
    )
    analysis = session.scalar(
        select(Analysis)
        .where(Analysis.listing_id == listing_id)
        .order_by(Analysis.created_at.desc())
    )
    image_urls = list(
        session.scalars(
            select(ImageAsset.original_url)
            .join(ObservationImage, ObservationImage.image_asset_id == ImageAsset.id)
            .where(
                ObservationImage.observation_id.in_([item.id for item in observations])
            )
            .distinct()
        ).all()
    )
    comparables: list[ComparableRead] = []
    costs: list[CostRead] = []
    if analysis:
        audits = session.scalars(
            select(AnalysisComparable)
            .where(AnalysisComparable.analysis_id == analysis.id)
            .order_by(AnalysisComparable.rank)
        ).all()
        for audit in audits:
            evidence = session.get_one(MarketEvidence, audit.market_evidence_id)
            comparable_observation = (
                session.get(ListingObservation, evidence.listing_observation_id)
                if evidence.listing_observation_id
                else None
            )
            comparables.append(
                ComparableRead(
                    market_evidence_id=evidence.id,
                    title=(
                        comparable_observation.title
                        if comparable_observation and comparable_observation.title
                        else "Comparable evidence"
                    ),
                    price_minor=evidence.price_minor + evidence.shipping_minor,
                    evidence_type=evidence.evidence_type,
                    provider=evidence.provider,
                    final_weight_bp=audit.final_weight_bp,
                    reason_codes=audit.reason_codes_json,
                )
            )
        costs = [
            CostRead(
                kind=item.cost_kind,
                low_minor=item.low_minor,
                high_minor=item.high_minor,
                rationale=item.rationale,
            )
            for item in session.scalars(
                select(AnalysisCost).where(AnalysisCost.analysis_id == analysis.id)
            ).all()
        ]
    return ListingDetailRead(
        listing_id=listing_id,
        title=current.title or "Untitled listing",
        source_url=source.canonical_url,
        provider_status=source.current_provider_status,
        image_urls=image_urls,
        attributes={
            "make": version.make if version else None,
            "model": version.model if version else None,
            "model_year": version.model_year if version else None,
            "displacement_cc": version.displacement_cc if version else None,
            "condition": version.normalized_condition if version else None,
        },
        opportunity_label=analysis.opportunity_label if analysis else "pending",
        confidence_bp=analysis.confidence_bp if analysis else 0,
        fair_value_low_minor=analysis.fair_value_low_minor if analysis else None,
        fair_value_midpoint_minor=analysis.fair_value_midpoint_minor
        if analysis
        else None,
        fair_value_high_minor=analysis.fair_value_high_minor if analysis else None,
        total_cost_low_minor=analysis.total_cost_low_minor if analysis else None,
        total_cost_high_minor=analysis.total_cost_high_minor if analysis else None,
        conservative_advantage_minor=(
            analysis.conservative_advantage_minor if analysis else None
        ),
        observations=[
            ObservationRead(
                observed_at=item.observed_at,
                retrieval_outcome=item.retrieval_outcome,
                asking_price_minor=item.asking_price_minor,
                provider_status=item.provider_status,
            )
            for item in observations
        ],
        comparables=comparables,
        costs=costs,
    )


def _latest_observation(session: Session, listing_id: str) -> ListingObservation | None:
    return session.scalar(
        select(ListingObservation)
        .where(ListingObservation.listing_id == listing_id)
        .order_by(ListingObservation.observed_at.desc())
    )


def _unique_market_evidence(
    session: Session, watchlist_id: str
) -> list[MarketEvidence]:
    evidence_rows = session.scalars(
        select(MarketEvidence)
        .join(
            ListingObservation,
            ListingObservation.id == MarketEvidence.listing_observation_id,
        )
        .join(
            WatchlistListing,
            WatchlistListing.listing_id == ListingObservation.listing_id,
        )
        .where(
            WatchlistListing.watchlist_id == watchlist_id,
            WatchlistListing.role == "reference",
        )
        .order_by(MarketEvidence.observed_at.desc())
    ).all()
    unique: dict[tuple[str, str, str], MarketEvidence] = {}
    for evidence in evidence_rows:
        provider_listing_id = evidence.provenance_json.get("provider_listing_id")
        if not provider_listing_id and evidence.listing_observation_id:
            observation = session.get(
                ListingObservation, evidence.listing_observation_id
            )
            source = (
                session.get(ListingSource, observation.listing_source_id)
                if observation
                else None
            )
            provider_listing_id = source.provider_listing_id if source else evidence.id
        key = (
            evidence.provider,
            str(provider_listing_id or evidence.id),
            evidence.evidence_type,
        )
        unique.setdefault(key, evidence)
    return list(unique.values())


def record_retrieval_outcome(
    session: Session, listing_id: str, retrieval_outcome: str
) -> ListingObservation:
    allowed = {
        "available",
        "explicitly_sold",
        "explicitly_ended",
        "missing",
        "blocked",
        "error",
    }
    if retrieval_outcome not in allowed:
        raise ValueError("unsupported retrieval outcome")
    listing = session.get(Listing, listing_id)
    source = session.scalar(
        select(ListingSource).where(ListingSource.listing_id == listing_id)
    )
    previous = _latest_observation(session, listing_id)
    if listing is None or source is None or previous is None:
        raise LookupError("listing not found")
    now = utc_now()
    provider_status = {
        "available": "available",
        "explicitly_sold": "sold",
        "explicitly_ended": "ended",
        "missing": "unavailable_unknown",
        "blocked": "unknown",
        "error": "unknown",
    }[retrieval_outcome]
    observation = ListingObservation(
        listing_id=listing_id,
        listing_source_id=source.id,
        observed_at=now,
        retrieval_outcome=retrieval_outcome,
        title=previous.title,
        description=previous.description,
        location_text=previous.location_text,
        asking_price_minor=previous.asking_price_minor,
        shipping_price_minor=previous.shipping_price_minor,
        currency=previous.currency,
        provider_status=provider_status,
        content_hash=_hash(
            {
                "previous": previous.content_hash,
                "outcome": retrieval_outcome,
                "observed_at": now.isoformat(),
            }
        ),
    )
    session.add(observation)
    source.last_checked_at = now
    source.current_provider_status = provider_status
    if retrieval_outcome == "missing":
        if source.first_missing_at is None:
            source.first_missing_at = now
        listing.current_status = "unavailable_unknown"
        listing.status_confidence_bp = 5000
    elif retrieval_outcome == "explicitly_sold":
        listing.current_status = "sold"
        listing.status_confidence_bp = 10000
    elif retrieval_outcome == "explicitly_ended":
        listing.current_status = "ended"
        listing.status_confidence_bp = 10000
    elif retrieval_outcome == "available":
        source.first_missing_at = None
        source.last_seen_at = now
        listing.last_seen_at = now
        listing.current_status = "available"
        listing.status_confidence_bp = 10000
    else:
        listing.current_status = "unknown"
        listing.status_confidence_bp = 0
    session.flush()
    return observation


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
