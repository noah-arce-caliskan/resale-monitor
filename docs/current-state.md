# Current project state

This file is the short, present-tense handoff for the next work session. Rewrite
it after material changes; do not use it as a historical log.

## Current direction

Resale Monitor is an evidence-backed deal intelligence tool for secondhand
buyers. It will first be proven as a personal local web application, then opened
to public users after the core workflow works. The first market is mopeds and
scooters around Hartford, Connecticut; the core design supports later category
modules such as cars and watches.

## Current phase

The project is completing Phase 0: product and architecture planning. The
repository has its product contract, safety constraints, selected application
stack, database model, and initial valuation contract, but no application code
or migrations have been created.

## Product focus

The first milestone is a watchlist-driven Hartford thin slice. The user saves a
`moped` watchlist with geography, source, price, and preference rules. Scheduled
source adapters run a frequent Hartford acquisition search, a less frequent
nationwide reference search, and lifecycle refreshes for known listings. They
normalize and deduplicate results, apply cheap filters, extract moped-specific
attributes, and rank only local candidates in the deal feed. Listing
Workspace provides the transparent opportunity report, editable evidence,
images, and tracking timeline.

Valuation is deterministic and evidence-backed. Comparable records retain a
truth tier, similarity factors, geography, recency, and provenance. The system
calculates a fair-value range, total-acquisition-cost range, and conservative
advantage (`fair value low - total acquisition cost high`). Sparse Hartford
evidence shrinks toward a clearly labeled broader baseline. Models extract
structured condition and risk evidence but do not decide price or deal quality.

The personal POC stores structured records in SQLite with WAL and migrations.
Permitted retained images use SHA-256-addressed local files with metadata in the
database. Observations are immutable; extraction and analysis results are
versioned.

The selected implementation is a Python 3.13 modular monolith using FastAPI,
Pydantic 2, SQLAlchemy 2, Alembic, HTTPX, and a separate APScheduler-backed
worker. The frontend uses React, TypeScript, and Vite with generated OpenAPI
types. uv and npm provide locked dependency environments. Testing spans pytest,
Vitest, and Playwright. See `docs/stack.md`.

The first Alembic migration will implement `docs/data-model.md`. Immutable source
facts, material observations, item versions, field evidence, outcomes, and
analyses are separate from mutable current pointers and feed projections. Money
uses integer minor units, times are UTC, and user corrections create new item
versions rather than being overwritten.

Valuation contract 0.1 uses auditable multiplicative comparable weights,
weighted quantiles, effective sample size, regional shrinkage, explicit cost
lines, deterministic opportunity thresholds, and confidence caps. Its initial
constants are versioned hypotheses that must be evaluated with fixtures and
real reviewed evidence.

The interface has four primary screens: Watchlists, Create or Edit Watchlist,
Deal Feed, and Listing Workspace. Manual listing entry and attribute correction
remain available without defining the primary journey.

eBay is the first automated source through its official API. Facebook
Marketplace, OfferUp, Craigslist, and other marketplaces remain adapter targets,
but automated capabilities stay disabled until an authorized method exists.
Notifications, public accounts, and seller communication come later.

## Decisions in force

- Build moped-first and keep category behavior modular.
- Prefer evidence-backed ranges and explicit uncertainty over opaque scores.
- Keep data-source adapters separate from the domain and valuation layers.
- Treat asking prices as asking prices unless a final sale price is supported.
- Do not depend on access-control evasion or prohibited scraping.
- Keep seller outreach human-approved.
- Build a local web application for personal use before a public multi-user
  product.
- Support multiple marketplaces as inputs through provider adapters, with
  automation enabled only for permitted capabilities.
- Target mopeds and scooters around Hartford, Connecticut first.
- Build a thin slice that automatically discovers, analyzes, ranks, and tracks
  listings from a saved watchlist.
- Use a transparent opportunity assessment rather than an opaque deal score.
- Keep permitted listing images viewable in saved research.
- Defer notifications until the core analysis and tracking loop works.
- Use a four-screen watchlist flow with one durable listing workspace.
- Reuse maintained, appropriately licensed open-source components after a source
  and license audit; do not inherit access-control bypass behavior.
- Keep project Markdown synchronized as living memory after material changes.
- Separate local acquisition discovery, broad reference collection, and listing
  lifecycle tracking.
- Use a labeled evidence hierarchy and deterministic comparable-based valuation.
- Limit LLMs to structured evidence extraction and explanation support.
- Use SQLite plus content-addressed image files for the personal proof of concept.
- Use a Python/FastAPI backend and worker with a React/TypeScript/Vite frontend.
- Start as a modular monolith and defer distributed job infrastructure.
- License the public repository under MIT.
- Preserve immutable evidence and analyses while using mutable current
  projections for efficient product queries.
- Implement the versioned weighted-quantile valuation baseline before adding a
  more complex pricing model.

## Open decisions

- Future deployment target.
- AI model provider strategy.
- Programmatic completed-transaction evidence beyond active eBay inventory.
- Authorized acquisition strategy for Facebook Marketplace, OfferUp, and
  Craigslist.

## Next implementation step

Begin in a fresh task by creating the application skeleton and initial Alembic
migration, followed by the eBay vertical slice with separate Hartford acquisition
and nationwide reference runs. After that loop works, research and fixture-test
a Facebook adapter; do not activate automated collection without an authorized
method.
