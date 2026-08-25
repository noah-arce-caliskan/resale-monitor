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
- Idempotent provider ingestion, durable rate-limit/source health, immutable
  changed and missing/recovered observations, deduplicated active-asking market
  evidence, and persisted deterministic analyses that refresh when a watchlist's
  reference facts change.
- React watchlist creation, source health, ranked acquisition feed, expandable
  reference inventory, and listing workspace with attributes, ranges, costs,
  five auditable comparables, images, and labeled observation history. A visible
  data-mode banner distinguishes synthetic from live inventory; fixtures never
  expose fake marketplace links, while live records retain their reviewed eBay
  source link.
- Read-time compatibility for local pre-release data collapses duplicate legacy
  comparables and suppresses obsolete remote placeholder images without deleting
  immutable evidence history.

Backend and frontend coverage remain above 90%. The flow has been verified from
a fresh migration in desktop and 390-pixel mobile browser layouts without
console errors or horizontal overflow.

## Known boundary

Fixtures prove the local pipeline but are not market evidence. Live eBay
verification is waiting on the owner's eBay developer-account approval and
production credentials. Model-assisted
extraction, user correction, lifecycle refresh, completed-sale evidence,
notifications, deployment, and additional marketplaces remain deferred.

## Next step

When eBay approves the developer account, configure the ignored `.env` and
verify live OAuth, Hartford acquisition, and nationwide reference searches.
Then review the MVP pull request. Do not merge this feature branch automatically.
