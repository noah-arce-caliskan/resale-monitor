# Architecture

## Status

The initial product is a local web application. The personal proof of concept
uses SQLite in WAL mode for structured data and content-addressed local files for
permitted retained images. It uses a Python FastAPI backend and worker with a
React and TypeScript frontend. See `docs/stack.md` for the complete stack and
tool responsibilities. The future hosting platform and model providers remain
undecided.

## Proposed components

1. **Watchlist service** stores local acquisition and broad reference scopes,
   queries, geography, source selection, rules, and personal buying preferences.
2. **Scheduler** runs watchlist-source jobs with rate limits, backoff, leases,
   observability, and failure isolation.
3. **Source adapters** search and refresh through user input, permitted APIs, or
   authorized integrations and produce source records.
4. **Normalizer and deduplicator** map provider fields into a canonical listing
   model and identify repeated observations and likely cross-source duplicates.
5. **Deterministic prefilter** applies keyword, location, source, price, and
   obvious exclusion rules before model calls.
6. **Multimodal extractor** derives structured item attributes from text and
   images while preserving provenance and uncertainty.
7. **Category module** defines required fields, risk rules, cost factors,
   comparable matching, and buyer questions for one category.
8. **Comparable retriever** finds candidates and ranks similarity.
9. **Opportunity engine** deterministically produces ranges and transparent
   components from weighted comparable evidence, regional adjustments, likely
   costs, and uncertainty.
10. **Feed ranker and report generator** order watchlist results and explain
    evidence, assumptions, risks, and next actions.
11. **Persistence layer** stores watchlists, source runs, listings, immutable
   observations, image assets,
   analyses, corrections, and outcomes without conflating asking prices with
   verified sales.
12. **Notification service** is deferred until after the thin slice works.

The backend is a modular monolith: one Python codebase exposes the API and the
same application services to a separately launched scheduler/worker process.
This preserves clear domain boundaries without introducing distributed services
or Redis for a single-user local application. Source-run and observation state
belongs in Resale Monitor's database rather than only in scheduler memory.

The multimodal model is an evidence extractor, not an appraisal oracle. It may
normalize attributes and identify visible condition, missing accessories,
damage, or scam signals. Deterministic code selects comparable cohorts,
calculates value and cost ranges, and assigns confidence from evidence quality.

## Core domain records

This section describes the domain boundaries. `docs/data-model.md` is the
implementation contract for tables, relationships, constraints, indexes, and
lifecycle behavior.

### Watchlist

- Name, category, search phrases, exclusions, and price bounds.
- Center location, radius, enabled sources, and source-specific filters.
- Acquisition and reference search definitions with independent schedules.
- Personal travel and repair tolerances.
- Schedule state and created, updated, and last-successful-run timestamps.

### Source run

- Watchlist, provider, adapter version, start and finish timestamps, and status.
- Run purpose: local acquisition, broad reference, or listing refresh.
- Request fingerprint, pagination cursor, counts, rate-limit metadata, and error
  classification.
- Acquisition permission mode and raw response provenance.

### Source record

- Provider and source URL.
- Acquisition method and timestamp.
- Raw user-supplied or permitted source content.
- Content hash for provenance and deduplication.

### Listing

- Provider listing identifier when available.
- Title, description, price, currency, location, and timestamps.
- Current image references linked to image asset records.
- Listing status and status confidence.

### Listing observation

- Listing identifier and observation timestamp.
- Observed asking price, availability, explicit status, and content hash.
- Acquisition method, status confidence, and retrieval outcome.
- First-missing time without an unsupported sold inference.

### Image asset

- Original source URL, source provider, observation timestamp, and content hash.
- Display strategy: approved remote URL or retained local copy.
- Local storage reference when retention is permitted and required for reliable
  display.
- Acquisition method, media type, provenance, and retention status.

### Extracted item

- Category, make, model, year, condition, and category-specific attributes.
- Value, provenance, and confidence for every extracted field.

### Comparable

- Source listing or transaction reference.
- Similarity factors and exclusions.
- Price type: asking, verified sold, or unknown.
- Observation timestamp and provenance.
- Reliability tier, similarity weight, regional adjustment, and exclusion
  reason when rejected.

### Analysis

- Fair-value range and confidence.
- Additional-cost range.
- Opportunity assessment, component values, and confidence.
- Evidence, adjustments, risks, questions, and model/version metadata.

## Initial persistence

- Store structured records in SQLite with WAL enabled, foreign keys enforced,
  migrations, and immutable observation rows.
- Preserve permitted raw API responses or normalized source payloads with their
  hashes and acquisition metadata so ingestion can be reproduced.
- Store permitted images outside the database using SHA-256 content-hash names;
  store paths, source URLs, media metadata, and retention state in SQLite rather
  than image blobs.
- Version extraction and analysis outputs instead of overwriting prior results.
- Move to PostgreSQL and object storage only when hosting, concurrency, or
  multi-user requirements justify the operational cost.
- Keep immutable evidence and version rows separate from mutable current-state
  pointers and feed projections. See `docs/data-model.md`.

## Valuation boundary

Valuation follows the evidence hierarchy and formulas in `docs/valuation.md`.
The core conservative comparison is:

`conservative advantage = fair value low - total acquisition cost high`

Sparse Hartford evidence shrinks toward a broader model- and condition-specific
baseline. Hartford evidence gains influence as its sample size and reliability
increase.

## Design constraints

- Provider adapters may depend on source formats; domain and valuation layers may
  not depend on marketplace HTML.
- Model providers must be replaceable behind interfaces.
- An analysis must be reproducible from its stored inputs and versions.
- Deterministic calculations should remain separate from generative explanations.
- External content is untrusted and must not be treated as system instructions.
- Facebook Marketplace, OfferUp, Craigslist, and future providers share a
  canonical domain model but keep independent acquisition and tracking policies.
- Images must remain viewable for the personal research workflow. Use a trusted,
  durable remote URL when appropriate; otherwise retain a permitted local copy.

## Initial presentation routes

- `/watchlists` presents saved searches, source health, and recent opportunities.
- `/watchlists/new` and `/watchlists/{id}/edit` configure a saved search.
- `/watchlists/{id}` presents its ranked deal feed and run status.
- `/listings/{id}` is the durable listing workspace containing the opportunity
  report, editable attributes, evidence, images, and observation history.

These are product-level routes rather than a required framework convention. An
implementation may adjust URL syntax while preserving the four screen contracts.

## Initial repository layout

- `backend/pyproject.toml` and `backend/src/resale_monitor/` contain the FastAPI
  app, worker entry point, domain services, provider adapters, and valuation code.
- `backend/alembic/` contains database migrations and `backend/tests/` contains
  unit, integration, adapter-contract, and migration tests.
- `frontend/` contains the Vite React TypeScript application and its tests.
- `data/local/` is ignored runtime storage for SQLite, retained permitted images,
  and generated artifacts; fixtures safe for Git live under test directories.
- API request and response types originate in Pydantic/OpenAPI and generate
  TypeScript contracts for the frontend.

## Decisions still required

- AI providers and structured-output strategy.
- Programmatic access to reliable completed-transaction evidence beyond active
  eBay listings.
- Authorized acquisition strategy for Facebook Marketplace, OfferUp, and
  Craigslist.
- Authentication, tenancy, and hosting strategy for the later public product.
