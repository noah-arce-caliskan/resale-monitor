# Current project state

This file is the short, present-tense handoff for the next work session. Rewrite
it after material changes; do not use it as a historical log.

## Current direction

Resale Monitor is an evidence-backed deal intelligence tool for secondhand
buyers. It is being proven as a personal local web application for mopeds and
scooters around Hartford, Connecticut before public deployment or additional
category modules.

## Current phase

The project-foundation milestone is implemented on `feat/project-foundation`.
The repository now contains the selected Python 3.13 FastAPI modular monolith,
APScheduler worker entry point, React and TypeScript Vite frontend, SQLAlchemy
SQLite policy, Alembic baseline, locked uv and npm environments, generated
OpenAPI types, test harnesses, and GitHub Actions CI.

The first vertical slice is database-aware health. `/api/health/live` reports
process liveness, `/api/health` verifies SQLite readiness, and the React shell
renders ready, unavailable, and retry states through TanStack Query. SQLite
connections enable foreign keys and WAL. The Alembic foundation revision is an
explicit empty baseline; canonical domain tables have not been added yet.

Local development and CI commands are exposed through the root `Makefile` and
documented in `README.md` and `AGENTS.md`. `make check` runs formatting checks,
linting, Python and TypeScript type checks, backend and frontend tests with 90%
coverage floors, a fresh migration test, a production frontend build, and
generated API-contract drift detection.

## Product and data boundaries

The product remains watchlist-first and moped-first. Local acquisition and broad
reference searches remain separate, valuation remains deterministic and
evidence-backed, and model output cannot independently determine price or deal
quality. eBay remains the first planned automated source through its official
API; restricted marketplaces remain disabled without an authorized method.

No marketplace integration, production credentials, collected listing data,
seller communication, authentication, deployment target, or public-user scope
is part of the foundation.

## Next implementation step

After the foundation pull request is reviewed and merged, create
`feat/watchlist-source-schema` from current `main`. Implement watchlists, search
scopes, and source runs test-first in the first domain migration, preserving the
constraints in `docs/data-model.md`. Follow with the listing-observation and
evidence-analysis schema pull requests already sequenced in
`docs/development-workflow.md`.

Protect `main` after the initial CI checks have completed successfully. Require
the stable `Backend`, `Frontend`, and `API contract` jobs before merge; do not add
continuous deployment until a real deployment target exists.
