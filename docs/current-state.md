# Current project state

This is the short, present-tense handoff. Rewrite it after material changes; do
not use it as a historical log.

## Direction

Resale Monitor is a personal, local, evidence-backed deal tool for mopeds around
Hartford, Connecticut. Local acquisition listings remain separate from broader
reference evidence. Asking prices are not presented as verified sales, and
deterministic code—not an LLM—owns valuation and opportunity labels.

## Implemented

The foundation is on `main`: Python 3.13/FastAPI, React/TypeScript/Vite,
SQLAlchemy/SQLite, Alembic, generated OpenAPI types, locked environments, tests,
and GitHub Actions CI.

`feat/ebay-watchlist-mvp` adds a credential-independent thin slice:

- Canonical watchlist, source-run, listing, immutable observation, image,
  evidence, comparable, cost, and analysis tables with a fresh migration.
- Hartford acquisition and United States reference scopes from one watchlist.
- Official eBay OAuth/Browse adapter with pagination, location filters,
  normalization, sanitized errors, and contract tests.
- Clearly labeled synthetic fixture mode as the default local experience;
  `SOURCE_MODE=live` requires eBay client credentials.
- Idempotent provider ingestion, immutable changed observations, active-asking
  market evidence, and persisted deterministic analyses.
- React watchlist creation, source run, ranked feed, and evidence workspace.

Backend and frontend coverage remain above 90%. The flow has been verified in a
real browser from watchlist creation through ranked listing inspection.

## Known boundary

Fixtures prove the local pipeline but are not market evidence. Live eBay
verification requires the owner's production credentials. Model-assisted
extraction, user correction, lifecycle refresh, completed-sale evidence,
notifications, deployment, and additional marketplaces remain deferred.

## Next step

Review and merge the MVP pull request. Then verify live Browse with eBay
credentials, replace fixture evidence with a reviewed dataset, and calibrate
comparable selection before adding model extraction or another source. Do not
merge this feature branch automatically.
