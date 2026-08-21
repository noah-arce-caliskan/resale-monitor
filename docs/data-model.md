# Database model

## Purpose

This document is the implementation contract for the initial domain migration
sequence. The foundation establishes an empty Alembic baseline; the focused
schema pull requests in `docs/development-workflow.md` add these tables in
reviewable relationship groups. The completed sequence supports one personal
user while preserving the histories and boundaries required for a later hosted
product. It distinguishes raw acquisition, canonical listing identity,
immutable observations, resolved item versions, market evidence, and
reproducible analyses.

## Storage conventions

The first MVP migration establishes the relationship skeleton and fields needed
by fixture-backed acquisition, observations, market evidence, costs, and
analysis. Fields in this document that support leases, rejected discoveries,
user correction provenance, richer lifecycle outcomes, or hosted operation are
still contractual targets and must be added by migration before their behavior
ships; application code must not pretend an unimplemented field is persisted.

- Application-generated UUIDs are stored as canonical text primary keys. Public
  APIs never expose sequential database meaning.
- All timestamps represent UTC and use timezone-aware Python datetimes.
- Money is stored as non-negative integer minor units, initially United States
  cents, with an adjacent ISO 4217 currency code. Never use binary floats.
- Distances use integer meters. Confidence and normalized weights use integer
  basis points from `0` through `10000` where practical.
- Structured provider payloads and evolving category fields use JSON only at
  explicit boundaries and carry a schema version. Frequently filtered or joined
  fields remain typed columns.
- SQLite foreign keys are enabled. Enumerated states use check constraints.
- Immutable evidence, observation, version, outcome, and analysis rows are never
  updated in place. Corrections create new versions.
- Mutable tables are limited to user configuration, scheduling state, current
  pointers, and feed projections. Every mutable table has `created_at` and
  `updated_at` where applicable.

## Relationship overview

```text
watchlists -> search_scopes -> source_runs -> source_records
     |              |                |              |
     |              +---------- discoveries --------+
     |                              |
     +------ watchlist_listings <- listings -> listing_sources
                                      |
                         listing_observations -> observation_images -> image_assets
                                      |
                                 item_versions -> attribute_evidence
                                      |
                                market_evidence <- analysis_comparables <- analyses
                                      |                                  |
                                outcome_evidence                    analysis_costs
```

## Configuration and scheduling

### `watchlists`

Represents persistent buying intent.

- `id`, `name`, `category`, `status` (`active`, `paused`, `archived`).
- `center_place`, `center_latitude`, `center_longitude`, `radius_meters`.
- Optional `minimum_price_minor`, `maximum_price_minor`, and `currency`.
- `preferences_json` for versioned travel, repair, and condition assumptions.
- `created_at`, `updated_at`, `last_successful_run_at`.
- Check maximum price is not below minimum price and radius is positive.

### `search_scopes`

Compiles one watchlist into provider-specific acquisition and reference work.

- `id`, `watchlist_id`, `provider`.
- `purpose` (`acquisition`, `reference`). Listing refreshes do not masquerade as
  search scopes.
- `query_json`, `geography_json`, `provider_filters_json`, and their explicit
  schema-version columns.
- `cadence_seconds`, `enabled`, `authorization_mode`, `adapter_version`.
- `next_run_at`, `last_started_at`, `last_succeeded_at`, `created_at`, `updated_at`.
- Unique `(watchlist_id, provider, purpose)` for the first version.

### `source_runs`

Durable record of one search or refresh attempt.

- `id`, nullable `search_scope_id`, `provider`.
- `purpose` (`acquisition`, `reference`, `listing_refresh`).
- `status` (`queued`, `running`, `succeeded`, `partial`, `rate_limited`,
  `failed`, `cancelled`).
- `adapter_version`, `request_fingerprint`, nullable cursor/checkpoint JSON.
- `queued_at`, `started_at`, `finished_at`.
- `lease_owner`, `lease_expires_at`, `attempt_number`.
- Counts for requested pages, completed pages, records seen, new listings,
  changed listings, and rejected records.
- Nullable `error_code` and sanitized `error_detail`.
- A refresh run records nullable `target_listing_source_id`; secrets and session
  material are prohibited from every run field.

## Acquisition and canonical identity

### `source_records`

Immutable provider material acquired during a run.

- `id`, `source_run_id`, `provider`, nullable `provider_record_id`, `source_url`.
- `acquired_at`, `acquisition_method`, `content_hash`.
- Nullable `payload_json` and `payload_schema_version`; retention policy may keep
  only a minimized normalized payload.
- Unique `(source_run_id, content_hash)` prevents duplicate pagination material
  within one run.

### `listings`

Canonical item identity independent of one provider page.

- `id`, `category`, nullable `canonical_fingerprint`.
- `current_status`, `status_confidence_bp`.
- Nullable `current_observation_id` and `current_item_version_id` convenience
  pointers. Their targets remain immutable.
- `first_seen_at`, `last_seen_at`, `created_at`, `updated_at`.
- Cross-provider merges are never automatic solely from a fingerprint; preserve
  candidate matches until evidence is sufficient.

### `listing_sources`

Maps canonical listings to provider identities.

- `id`, `listing_id`, `provider`, `provider_listing_id`, `canonical_url`.
- `first_seen_at`, `last_seen_at`, `last_checked_at`, nullable `first_missing_at`.
- `current_provider_status`, `status_confidence_bp`, `content_fingerprint`.
- Unique `(provider, provider_listing_id)` is the primary provider deduplication
  rule. Canonical URL is indexed but not assumed immutable.

### `discoveries`

Records why a source result entered or was rejected by a watch process.

- `id`, `source_run_id`, `source_record_id`, `search_scope_id`, nullable
  `listing_id`, `discovered_at`.
- `decision` (`accepted`, `rejected`, `duplicate`, `deferred`).
- `reason_codes_json`, deterministic filter version, and relevance confidence.
- Unique `(source_run_id, source_record_id)`.

### `watchlist_listings`

Mutable feed projection connecting a listing to one watchlist and role.

- `watchlist_id`, `listing_id`, `role` (`acquisition`, `reference`).
- `first_discovered_at`, `last_discovered_at`, `last_changed_at`.
- `feed_state` (`new`, `seen`, `saved`, `dismissed`, `archived`).
- Nullable `latest_analysis_id` and `updated_at`.
- Composite primary key `(watchlist_id, listing_id, role)`.
- Only `acquisition` rows appear as deal-feed candidates.

## Observation and image history

### `listing_observations`

Immutable snapshot of visible provider state.

- `id`, `listing_id`, `listing_source_id`, nullable `source_record_id`.
- `observed_at`, `retrieval_outcome` (`available`, `explicitly_sold`,
  `explicitly_ended`, `missing`, `blocked`, `error`).
- Nullable title, description, location text and coordinates.
- Nullable `asking_price_minor`, `shipping_price_minor`, and currency.
- Nullable provider publication and end timestamps.
- `provider_status`, `status_confidence_bp`, `content_hash`.
- Append a row when material content, price, or status changes, and on the first
  missing or recovery event. An unchanged successful check updates
  `listing_sources.last_checked_at` instead of creating noise.

### `image_assets`

Metadata for remotely displayed or permitted retained images.

- `id`, nullable `sha256`, `original_url`, nullable `local_relative_path`.
- `display_strategy` (`remote`, `local`, `unavailable`) and `retention_status`.
- Media type, byte size, width, height, acquisition method, and `acquired_at`.
- Unique non-null SHA-256 values deduplicate retained content.
- Local paths are relative to the configured data directory and may not escape it.

### `observation_images`

- `observation_id`, `image_asset_id`, `ordinal`, `is_primary`.
- Composite primary key `(observation_id, image_asset_id)` and unique
  `(observation_id, ordinal)`.

## Structured item evidence

### `item_versions`

Immutable resolved view of an item's attributes at one point in time.

- `id`, `listing_id`, `based_on_observation_id`, nullable `previous_version_id`.
- `version_kind` (`extraction`, `user_correction`, `merge`, `migration`).
- Typed searchable fields: make, model, model year, displacement cc, mileage,
  running state, title state, registration state, and normalized condition.
- `category_attributes_json` and `schema_version` for moped-specific fields that
  have not earned dedicated columns.
- Extractor/model/prompt/rule versions, overall confidence, `created_at`, and
  `created_by` (`system`, `user`).
- A new extraction starts from the prior resolved version and may not silently
  overwrite user-confirmed fields.

### `attribute_evidence`

Field-level support for one item version.

- `id`, `item_version_id`, `field_path`, `value_json`.
- `evidence_kind` (`source_text`, `source_image`, `provider_field`, `user`,
  `inference`, `unknown`).
- Nullable `observation_id`, `image_asset_id`, and structured `locator_json`.
- `confidence_bp`, extractor version, and `created_at`.
- Store a short locator or minimal excerpt, not an unnecessary copy of an entire
  listing description.

## Pricing evidence and outcomes

### `market_evidence`

Normalized comparable evidence. A row may point to one active observation, a
supported outcome, or an external guide record.

- `id`, `evidence_type` (`verified_transaction`, `explicit_sold`,
  `valuation_guide`, `active_asking`, `disappeared_unknown`).
- Nullable `listing_observation_id`, `outcome_evidence_id`, `item_version_id`,
  and `source_record_id`.
- `provider`, price and shipping minor units, currency, location, observed time,
  and nullable transaction time.
- `provenance_json`, `natural_fingerprint`, and `created_at`.
- Unique non-null natural fingerprints prevent the same source fact from being
  counted repeatedly. Model-generated prices never enter this table.
- For active eBay asks, the natural fact identity includes provider listing ID,
  price, shipping, and currency—not cosmetic text or image hashes. Analyses also
  use only the latest fact per provider identity within that watchlist, so
  display-only or price changes cannot multiply a comparable's weight. Older
  facts remain immutable history.

### `outcome_evidence`

Immutable claims about what happened to a listing.

- `id`, `listing_source_id`, `outcome_type` (`explicit_sold`, `user_verified_sale`,
  `ended_unknown`, `expired`, `removed`, `relisted`).
- Nullable final price and currency, `occurred_at`, `observed_at`.
- `provenance_json`, `confidence_bp`, and `created_at`.
- Missing or disappeared listings default to an unknown outcome and cannot
  generate a verified-transaction record.

## Reproducible analysis

### `analyses`

Immutable output of one complete opportunity calculation.

- `id`, `listing_id`, `candidate_observation_id`, `item_version_id`.
- `valuation_policy_version`, `cost_rule_version`, `analysis_status`.
- Nullable fair-value low, midpoint, and high; total-acquisition-cost low and
  high; conservative-advantage minor units; currency.
- `confidence_bp`, deterministic `opportunity_label`, evidence summary JSON,
  risk summary JSON, generated explanation, questions JSON, and `created_at`.
- Store model identifiers only for extraction or explanation stages; calculated
  amounts must be reproducible without asking a model to price the item.

### `analysis_comparables`

Audit trail for included and rejected comparable candidates.

- `analysis_id`, `market_evidence_id`, `decision` (`included`, `excluded`).
- Similarity, evidence reliability, recency, geography, and final weight basis
  points; nullable rank.
- Inclusion and exclusion reason codes JSON.
- Composite primary key `(analysis_id, market_evidence_id)`.

### `analysis_costs`

Line items behind the total-acquisition-cost range.

- `id`, `analysis_id`, `cost_kind` (`shipping`, `transport`, `tax`, `title`,
  `registration`, `repair`, `risk_reserve`, `other`).
- Low and high minor units, currency, `basis` (`provider`, `user`, `rule`,
  `inferred`), confidence, rule version, and rationale.

## Required indexes

- Due work: `search_scopes(enabled, next_run_at)` and
  `source_runs(status, lease_expires_at)`.
- Provider identity: unique `listing_sources(provider, provider_listing_id)`.
- Listing timelines: `listing_observations(listing_id, observed_at desc)`.
- Feed: `watchlist_listings(watchlist_id, role, feed_state, last_changed_at desc)`.
- Comparable retrieval: typed item-version make/model/year/displacement indexes,
  plus `market_evidence(evidence_type, observed_at, currency)`.
- Analysis history: `analyses(listing_id, created_at desc)`.
- Content deduplication: source-record, observation, and image content hashes.

Do not add speculative indexes until query plans or realistic fixture volume
show a need beyond these access paths.

## Transaction boundaries and invariants

1. A source page is processed in a transaction that saves its source record,
   resolves provider identity, appends any material observation, and records the
   discovery decision atomically.
2. Extraction creates an item version and all its field evidence atomically,
   then advances the listing's current-version pointer.
3. Analysis saves its result, comparable audit rows, and cost rows atomically,
   then advances the relevant feed projection.
4. A failed or partial run never deletes prior listing state or implies that
   unseen records disappeared.
5. One missing refresh does not imply sold. Explicit source status or separately
   supported outcome evidence is required.
   Missing and later recovery checks append observations and update current
   confidence while preserving both events in history.
6. User corrections create new versions and outrank later automated extraction
   until the user changes or withdraws them.

## Deferred tables

Do not add users, organizations, notification deliveries, seller messages,
subscriptions, payments, or generalized category-definition tables in the
personal MVP. Add them with explicit product requirements and migrations when
the project reaches the corresponding roadmap phase.
