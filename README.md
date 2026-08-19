# Resale Monitor

Resale Monitor is an evidence-backed deal intelligence tool for secondhand
marketplaces. It analyzes listing text and images, retrieves relevant
comparables, estimates a fair-value range, explains risk and uncertainty, and
helps a buyer decide what to investigate next.

The first category is mopeds and scooters. The underlying system is intended
to support additional categories, such as cars and watches, through
category-specific extraction and valuation modules.

## Project status

The project is in product and architecture planning. The first milestone is a
personal, local web application for the Hartford, Connecticut moped market. A
user saves a watchlist such as `moped`; the system repeatedly searches enabled
sources in separate Hartford acquisition and nationwide reference scopes,
normalizes and deduplicates new listings, ranks local opportunities, and tracks
their price and availability history. Deterministic calculations—not an LLM
opinion—combine labeled comparable evidence with total acquisition cost.

The product will be proven as a personal tool before it is opened to other
users. Provider-specific access remains behind adapters so public deployment can
add supported sources without making prohibited collection a dependency. eBay
is the first automated source because it provides official discovery APIs.
Facebook Marketplace, OfferUp, Craigslist, and other sources remain product
targets but are enabled only through an authorized acquisition method.

## Product principles

- Evidence before scores: show comparisons and assumptions behind estimates.
- Opportunity, not certainty: combine price, condition, liquidity, costs, and
  confidence without claiming a guaranteed profit.
- Ranges before false precision: communicate uncertainty explicitly.
- Category expertise: use category-specific rules instead of one generic prompt.
- Human control: draft questions and actions; do not impersonate the user.
- Replaceable data sources: keep ingestion separate from valuation logic.
- Compliance by design: do not build around bypassing access controls or terms.

## Documentation

- [Current project state](docs/current-state.md)
- [Vision](docs/vision.md)
- [MVP scope](docs/mvp.md)
- [Thin-slice screens and user journey](docs/user-journey.md)
- [Architecture](docs/architecture.md)
- [Technology stack](docs/stack.md)
- [Database model](docs/data-model.md)
- [Valuation and evidence policy](docs/valuation.md)
- [Roadmap](docs/roadmap.md)
- [Decisions](docs/decisions.md)
- [Data sources and compliance](docs/data-and-compliance.md)
- [Open-source reuse audit](docs/source-reuse.md)
- [Evaluation plan](docs/evaluation.md)

These files are living project memory. Material decisions and changes should be
reflected in them during the same task, while `docs/current-state.md` stays a
short handoff for the next session. Exploratory ideas remain proposals until they
are explicitly adopted.

## Development

The selected stack is a Python 3.13 FastAPI backend and worker, a React and
TypeScript frontend built with Vite, and SQLite persistence through SQLAlchemy
and Alembic. See `docs/stack.md` for responsibilities and rationale. Exact setup,
run, test, lint, and formatting commands will be added when the application
skeleton is created.

Local secrets belong in `.env`, which is ignored by Git. Copy `.env.example`
when configuration is introduced; never commit credentials.

## License

Resale Monitor is available under the [MIT License](LICENSE).
