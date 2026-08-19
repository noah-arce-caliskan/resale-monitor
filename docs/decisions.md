# Decision log

This file records durable product and architecture decisions. Add new entries
instead of silently changing direction. Revisit a decision when evidence changes.

## 2026-08-18: Repository is the durable project memory

**Decision:** Keep product scope, architecture, decisions, data policy, and
evaluation plans in version-controlled files. Chats may explore ideas but are not
the sole record of important decisions.

**Reason:** Future sessions and contributors need a concise, reviewable source of
truth that evolves with the implementation.

## 2026-08-18: Project memory is living and synchronized

**Decision:** Treat the checked-in Markdown files as mutable source-of-truth
documents. Every material task must reconcile its outcome with the relevant
documents and refresh a concise `docs/current-state.md` handoff. Clear adopted
changes replace stale prose, while reversals remain visible as superseding
decision-log entries.

**Reason:** The product will evolve through conversation and experimentation.
Updating memory in the same task keeps future Codex sessions and contributors
aligned without mistaking every brainstorm for an accepted requirement.

## 2026-08-18: Moped-first, category-extensible

**Decision:** Build the first complete workflow for mopeds and scooters while
keeping category behavior behind explicit interfaces.

**Reason:** Valuation factors differ substantially across mopeds, cars, watches,
and other goods. A narrow first category makes evaluation possible without
preventing later expansion.

## 2026-08-18: Evidence-backed ranges over opaque scores

**Decision:** Present comparable evidence, assumptions, a value range, an
additional-cost range, and confidence. A summary score may be added later only if
its components remain visible.

**Reason:** Asking prices and condition evidence are noisy. False precision would
reduce trust and obscure missing information.

## 2026-08-18: Human approval for seller communication

**Decision:** The system may draft questions and negotiation strategies but will
not automatically impersonate the user, send messages, or commit to purchases in
the initial product.

**Reason:** Communication can create financial, reputational, safety, and platform
risks. Human review is also a better product experience while reliability is
unproven.

## 2026-08-18: Compliance-first, replaceable ingestion

**Decision:** Keep source acquisition behind adapters and do not make prohibited
scraping or access-control bypasses a project dependency.

**Reason:** Marketplace access rules and page structures change. The core product
must remain useful with user-supplied data and permitted providers.

## 2026-08-18: Asking prices are not sale prices

**Decision:** Store the price type and provenance of every comparable. A removed
listing cannot be labeled sold without supporting evidence.

**Reason:** Disappearance may mean a sale, deletion, expiration, moderation, or
relisting, and the final negotiated price is usually unknown.

## 2026-08-18: Personal-first, public later

**Decision:** Prove Resale Monitor as a personal tool for the project owner, then
add deployment, accounts, tenancy, and onboarding for public users as a separate
phase.

**Reason:** This produces a usable vertical slice quickly while preserving a
strong resume story about evolving a validated personal workflow into a real
multi-user product.

## 2026-08-18: Local web application first

**Decision:** Build the initial experience as a local web application. A browser
capture extension may be considered later but is not required for the MVP.

**Reason:** A local web app can provide a complete interface, durable research
history, and background tracking without prematurely introducing browser-store
distribution or public hosting.

## 2026-08-18: Multi-source input, capability-specific automation

**Decision:** Accept user-supplied listings from Facebook Marketplace, OfferUp,
Craigslist, and other providers through replaceable adapters and one canonical
listing model. Enable automated tracking separately for each provider only when
the acquisition method is permitted.

**Reason:** Users should be able to analyze listings regardless of origin, while
input compatibility must not be confused with authorization to scrape or poll a
source.

## 2026-08-18: Hartford longitudinal thin slice

**Decision:** The MVP targets mopeds and scooters in the Hartford, Connecticut
area. Its vertical slice imports one listing, extracts and corrects attributes,
stores images and immutable observations, produces an opportunity report, and
tracks later price and availability observations when permitted.

**Reason:** Combining analysis with history proves the product's complete data
loop while keeping category, geography, and monitoring scope narrow.

## 2026-08-18: Transparent opportunity assessment

**Decision:** Describe a listing as an opportunity using visible components for
asking-price anomaly, condition, likely costs, comparable support, local
liquidity, missing information, risk, and confidence. Do not promise profit or
present disappearance as a transaction.

**Reason:** Opportunity better represents the buyer's decision than an opaque AI
score or unsupported sold-price estimate.

## 2026-08-18: Images remain viewable

**Decision:** Use a reviewed, durable remote image URL when appropriate;
otherwise retain a private local copy of every user-supplied or permitted image
needed for analysis and history. If retention is not permitted, require user
upload instead of collecting the image automatically.

**Reason:** Visual evidence is essential to condition analysis and a useful
research history, but reliability does not override source rights or privacy.

## 2026-08-18: Notifications are deferred

**Decision:** Do not include push notifications in the first thin slice. Add
watchlists and notifications after analysis and longitudinal tracking are
working and evaluated.

**Reason:** Notifications amplify the output of the core system but do not prove
that its recommendations are useful.

## 2026-08-18: Four-screen decision workspace

**Decision:** Organize the thin slice around four primary screens: Listings, Add
Listing, Review Extraction, and Listing Workspace. Keep the opportunity report,
comparable evidence, images, and tracking history within one listing workspace
rather than splitting them into separate products or navigation branches.

**Reason:** The complete user job is to capture, verify, judge, and follow one
listing. A small screen set keeps that decision loop coherent while still making
model corrections and longitudinal evidence explicit.

## 2026-08-18: Watchlist-first discovery supersedes manual-first MVP

**Decision:** Replace the add-one-listing primary journey with saved watchlists
that automatically search enabled sources, ingest and deduplicate new listings,
rank opportunities, and track them. Manual listing entry and correction remain
fallback capabilities. This supersedes the manual-first emphasis in the earlier
Hartford longitudinal thin-slice decision.

**Reason:** The user's real job is to monitor the Hartford resale market for
`moped` opportunities without repeatedly finding and entering listings by hand.
Continuous discovery also creates the longitudinal dataset that differentiates
the product from an API wrapper.

## 2026-08-18: eBay is the first automated source

**Decision:** Prove the watchlist pipeline with eBay's official Browse API. Keep
Facebook Marketplace, OfferUp, Craigslist, and additional marketplaces as
adapter targets, but do not activate automated collection without an authorized
method.

**Reason:** eBay provides supported discovery and refresh interfaces, while the
other initial targets currently restrict the automated collection needed by the
product. One legitimate end-to-end source proves the architecture without
making terms violations a project dependency.

## 2026-08-18: Reuse audited components without inheriting the wrong product

**Decision:** Audit existing open-source collectors and monitoring projects
before implementing infrastructure. Prefer maintained official-API clients and
permissively licensed components. Use AGPL projects as architectural references
unless the project deliberately adopts AGPL, and do not reuse code whose core
behavior bypasses authentication, CAPTCHA, bot detection, or access controls.

**Reason:** Reuse can accelerate adapters, scheduling, deduplication, filtering,
and tests, but license obligations and collection behavior matter independently
from whether a repository is publicly available.

## 2026-08-18: Four-screen watchlist flow supersedes listing-entry flow

**Decision:** The primary screens are Watchlists, Create or Edit Watchlist, Deal
Feed, and Listing Workspace. Attribute review lives inside Listing Workspace and
manual add is secondary. This supersedes the earlier four-screen decision that
made Add Listing and Review Extraction primary screens.

**Reason:** Discovery should happen continuously from saved intent. Human review
is valuable for correcting evidence but should not block every listing before it
can be ranked.

## 2026-08-19: Separate acquisition and reference markets

**Decision:** A watchlist creates a frequently refreshed local acquisition
search and a less frequently refreshed broad reference search, while known
listings receive separate lifecycle refreshes. For the first watchlist, Hartford
results are potential purchases and nationwide eBay results are comparable
context. Only acquisition results appear in the deal feed.

**Reason:** A Hartford-only sample will initially be too sparse for useful price
context, but nationwide listings may have different delivery, regional, and
market conditions. Separating the scopes gives the valuation engine more data
without pretending every national listing is a practical local deal.

## 2026-08-19: Deterministic valuation over a labeled evidence hierarchy

**Decision:** Calculate fair-value and total-cost ranges from attributed,
reliability-weighted comparable evidence. The primary conservative opportunity
measure is fair-value low minus total-acquisition-cost high. Verified final
transactions, explicit sold records, valuation guides, active asking prices,
and unknown disappearances remain distinct evidence types. LLM output is not a
pricing evidence tier.

**Reason:** This makes the product testable and grounded in saved market data.
It also prevents active asks, disappeared listings, and persuasive model prose
from being mistaken for verified sale truth.

## 2026-08-19: Models extract evidence but do not appraise independently

**Decision:** Use language and vision models to extract structured attributes,
condition, damage, missing accessories, and risk signals with provenance and
confidence. Deterministic code selects comparables, calculates ranges and
confidence, and ranks opportunities.

**Reason:** Models are useful for interpreting unstructured listings but are not
a reliable source of price truth. This boundary lowers cost and makes important
product behavior reproducible.

## 2026-08-19: SQLite and content-addressed files for the personal proof of concept

**Decision:** Store structured POC data in SQLite with WAL and migrations. Store
permitted retained images as SHA-256-addressed local files with metadata in the
database, not as database blobs. Keep observations immutable and version
extractions and analyses. Revisit PostgreSQL and object storage for public or
multi-user deployment.

**Reason:** This is durable and simple for a local single-user app while
preserving a clean migration path when concurrency and hosting requirements
become real.

## 2026-08-19: Python modular monolith with a typed React frontend

**Decision:** Build the initial product with Python 3.13, FastAPI, Pydantic 2,
SQLAlchemy 2, Alembic, SQLite, and a separate Python scheduler/worker process.
Build the frontend with React, TypeScript, and Vite. Generate frontend API types
from the backend's OpenAPI contract. Use uv and npm for reproducible dependency
management and standard Python, frontend, and end-to-end test tooling.

**Reason:** Python matches the project owner's strongest language and the
project's ingestion, AI, and valuation workload. React preserves existing
frontend familiarity, while TypeScript and generated contracts demonstrate
production-oriented full-stack engineering. A modular monolith and local worker
provide strong boundaries without premature distributed infrastructure.

## 2026-08-19: Immutable evidence with mutable current projections

**Decision:** Persist raw source facts, material listing observations, item
versions, attribute evidence, outcomes, comparable selections, cost lines, and
analyses as append-only records. Keep mutable current pointers and
watchlist-listing feed state as derived conveniences. Store money as integer
minor units, timestamps in UTC, and confidence as bounded basis points.

**Reason:** Reproducibility and user trust require the system to explain what it
knew at analysis time. Separating evidence from projections preserves history
without forcing every UI query to reconstruct current state from the full event
stream.

## 2026-08-19: Versioned weighted-quantile valuation baseline

**Decision:** Version 0.1 selects comparables through explicit widening stages,
multiplies inspectable similarity, reliability, recency, geography, and
completeness weights, and estimates a range from weighted quantiles only when
effective sample size is sufficient. Regional adjustments shrink toward a
national baseline. Opportunity labels derive deterministically from conservative
advantage, confidence, and blocking risks. Initial weights and thresholds are
evaluation hypotheses stored in category policy.

**Reason:** This provides a concrete, testable baseline without presenting
arbitrary constants as learned market truth. Versioning makes later calibration
and backtesting reviewable.

## 2026-08-19: MIT license for the public repository

**Decision:** Release the repository under the MIT License.

**Reason:** A permissive, familiar license makes the resume project easy to
inspect, run, and build upon without imposing a copyleft commitment on a product
whose eventual commercial direction is still unknown.

## 2026-08-19: TDD, required CI, and dev integration workflow

**Decision:** Use test-driven development for behavioral code, establish GitHub
Actions in the foundation pull request, and require its checks before merge.
Develop on short-lived feature branches targeting a protected `dev` integration
branch, then promote coherent milestones through pull requests from `dev` to
protected `main`. Defer continuous deployment until a deployment target exists.

**Reason:** Tests and automated checks make rapid AI-assisted implementation
reviewable and repeatable. Repository-level instructions prevent each prompt
from restating the workflow, while feature branches and pull requests preserve a
clear engineering history. CD without an environment would add configuration
without delivering or protecting a real product.

## 2026-08-19: Direct feature pull requests to main supersede dev integration

**Decision:** Create short-lived feature, fix, and chore branches from current
`main` and merge them directly back through protected pull requests. Do not keep
a long-lived `dev` branch unless a staging environment, release train, or
multiple parallel contributors later creates a concrete need. This supersedes
the `dev` integration portion of the earlier TDD and CI workflow decision; its
TDD, CI, protection, and CD-deferral decisions remain in force.

**Reason:** For a solo project, `dev` adds branch drift, duplicate promotion pull
requests, and larger review surfaces without providing a separate environment or
coordination benefit. Small direct pull requests exercise CI on the exact unit
being merged and keep `main` continuously understandable.

## Open decisions

- Future deployment target.
- AI model provider strategy.
- Programmatic completed-transaction evidence beyond active eBay inventory.
- Authorized acquisition strategy for Facebook Marketplace, OfferUp, and
  Craigslist.
