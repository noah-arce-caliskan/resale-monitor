# Roadmap

## Phase 0: Foundation

- Define the product vision, MVP, logical architecture, and data policy.
- Define the four-screen thin-slice contract and end-to-end user journey.
- Maintain a concise current-state handoff and synchronize material changes into
  the project documentation as part of each task.
- Implement the selected Python/FastAPI and React/TypeScript stack recorded in
  `docs/stack.md`.
- Create the application skeleton, local development workflow, and CI checks.
- Protect `dev` and `main` after the initial GitHub Actions checks exist, and use
  the pull-request flow in `docs/development-workflow.md`.
- Implement the canonical schema defined in `docs/data-model.md` through an
  initial reviewed Alembic migration.
- Implement and fixture-test the versioned deterministic calculation contract in
  `docs/valuation.md`.

## Phase 1: eBay watchlist thin slice

- Build a personal local web application.
- Implement Watchlists, Create or Edit Watchlist, Deal Feed, and Listing
  Workspace.
- Create a Hartford-area `moped` watchlist and run it on a schedule.
- Run separate Hartford acquisition and nationwide reference searches from that
  watchlist.
- Integrate eBay through its official Browse API and keep the adapter behind the
  canonical source interface.
- Normalize, deduplicate, and snapshot newly discovered listings.
- Apply rule-based keyword, location, and price filters before model calls.
- Implement moped/scooter attribute extraction with provenance.
- Make attribute correction available from the listing workspace without
  blocking feed generation.
- Build comparable cohorts from collected eBay records, preserve their evidence
  type, and validate samples manually against eBay Product Research.
- Implement SQLite WAL persistence and content-addressed permitted image files.
- Produce an explainable opportunity assessment, value range, cost range, risks,
  and seller questions.
- Store immutable observations and keep listing images viewable.
- Refresh discovered listings through permitted source capabilities and show
  price and availability timelines.
- Build and publish the first evaluation dataset and metrics.

## Phase 2: Hartford market observatory

- Add authorized marketplace adapters one at a time, using saved fixtures and
  contract tests before live activation.
- Accumulate permitted listings and reproducible analyses across the local moped
  market.
- Record price changes, availability, and user-observed outcomes.
- Deduplicate listings and identify likely relistings.
- Compare local inventory, asking-price distributions, listing age, and seasonal
  movement without labeling disappearance as a verified sale.
- Estimate time-to-unavailability and local liquidity with explicit uncertainty.
- Research an authorized Facebook Marketplace acquisition path and implement a
  fixture-backed adapter contract, but activate live collection only if the
  acquisition method is authorized.

## Phase 3: Marketplace monitoring

- Expand source coverage only after documenting permitted acquisition behavior.
- Schedule source checks with rate limits, observability, and failure isolation.
- Rank alerts by opportunity and confidence.
- Add watchlists and notifications for supported data sources.
- Measure alert precision and user actions.

## Phase 4: Public product

- Add accounts, authentication, per-user data isolation, and deletion controls.
- Deploy the application and provide onboarding for supported sources.
- Validate the opportunity workflow with users beyond the project owner.
- Define public image-retention, privacy, and operational policies.

## Phase 5: Additional categories

- Add cars as a separate category module with VIN, trim, mileage, title, accident,
  registration, and transportation considerations.
- Add watches as a separate category module with reference, authenticity,
  provenance, service, condition, and box/papers considerations.
- Reuse the core pipeline while evaluating each module independently.

## Phase 6: Human-in-the-loop buying assistant

- Draft seller questions and negotiation options.
- Require user review and approval before any communication.
- Track answers as new evidence and update the analysis.
- Consider direct integrations only when explicitly permitted and safe.
