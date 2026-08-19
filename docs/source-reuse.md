# Open-source source-reuse audit

## Policy

Do not reinvent generic scheduling, adapter, filtering, deduplication, API, and
testing patterns when a maintained and compatible component exists. Before
copying code or adding a dependency, record its license, maintenance state,
security and credential behavior, source-access method, tests, and fit with the
canonical domain model.

Public source code grants only the rights in its software license. It does not
grant permission to collect data from the marketplace the code targets.

## Initial audit: 2026-08-18

### hendt/ebay-api

- Repository: <https://github.com/hendt/ebay-api>
- License: MIT.
- State inspected: version 10.0.1, active in August 2026.
- Useful parts: maintained TypeScript client for eBay's Browse, Feed,
  Notification, and other official APIs; authentication and typed request and
  response support.
- Decision: preferred dependency candidate if the project selects TypeScript.
  Otherwise use the official eBay REST API directly while preserving the same
  adapter contract.

### BoPeng/ai-marketplace-monitor

- Repository: <https://github.com/BoPeng/ai-marketplace-monitor>
- License: AGPL-3.0.
- State inspected: active in July 2026 with a substantial test suite.
- Useful ideas: marketplace abstraction, watchlist configuration, job
  scheduling, keyword filtering, cache and deduplication, model-provider
  interfaces, notifications, and fixture-based parser tests.
- Risks: the Facebook collector uses browser automation, credentials, and an
  interactive path for CAPTCHA or login challenges. The repository itself warns
  that Facebook automation is prohibited without authorization.
- Decision: use as an architectural reference. Do not copy or derive code unless
  the project deliberately adopts AGPL and the source acquisition is authorized.

### stephanlensky/hyacinth

- Repository: <https://github.com/stephanlensky/hyacinth>
- License: AGPL-3.0-only.
- State inspected: last repository change observed in June 2024.
- Useful ideas: plugin interface, batched searches, complex deterministic filter
  expressions, scheduler design, SQL persistence, and fixture-based source
  tests.
- Decision: study the plugin and batching architecture; do not copy code unless
  AGPL is intentionally selected.

### regek/facebook-marketplace-rss

- Repository: <https://github.com/regek/facebook-marketplace-rss>
- License: BSD-3-Clause.
- State inspected: small project, last change observed in December 2024.
- Useful ideas: scheduled searches, SQLite seen-item state, deterministic title
  filters, content hashing, and RSS output.
- Risks: brittle page selectors and Selenium settings intended to conceal
  webdriver or reduce fingerprinting.
- Decision: permissive license, but do not reuse the collector or stealth
  behavior. Small generic scheduling and deduplication ideas may be reimplemented
  with attribution where code is copied.

### ovidubya/offerup-deals-server

- Repository: <https://github.com/ovidubya/offerup-deals-server>
- Declared package license: ISC.
- State inspected: last change observed in June 2020; Playwright 1.1-era code.
- Useful ideas: extracting OfferUp's page bootstrap data and separating cleanup
  from retrieval.
- Risks: obsolete dependencies, brittle internal page state, no meaningful test
  suite observed, and collection conflicts with current OfferUp restrictions.
- Decision: do not fork or depend on it. At most use it as historical evidence
  for the shape of an adapter.

### irahorecka/pycraigslist

- Repository: <https://github.com/irahorecka/pycraigslist>
- License: MIT.
- State inspected: repository active in August 2026.
- Useful ideas: query construction, category and filter normalization, listing
  parsing, and pagination.
- Risks: documentation recommends a Cloudflare-bypass service when blocked, and
  Craigslist terms prohibit unlicensed software collection.
- Decision: do not activate or ship this collector without a separate Craigslist
  license or permission. Query and parser concepts may inform a fixture-only
  adapter contract.

## Adoption checklist

- Confirm the exact license and preserve required notices.
- Prefer a package dependency over copying source when practical.
- Pin a version and record upstream repository and commit.
- Review transitive dependencies and credential handling.
- Run or add fixture-based contract tests before connecting live data.
- Map provider output into canonical records; never leak provider HTML into the
  domain model.
- Document authorization, retention, rate limits, and failure behavior.
- Keep the adapter removable without changing opportunity analysis.
