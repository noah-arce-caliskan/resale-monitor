# Resale Monitor

Resale Monitor is an evidence-backed deal intelligence tool for secondhand
marketplaces. It analyzes listing text and images, retrieves relevant
comparables, estimates a fair-value range, explains risk and uncertainty, and
helps a buyer decide what to investigate next.

The first category is mopeds and scooters. The underlying system is intended
to support additional categories, such as cars and watches, through
category-specific extraction and valuation modules.

## Project status

The project foundation is implemented for a personal, local web application.
The repository contains a Python 3.13 FastAPI service and worker entry point, a
React and TypeScript frontend, SQLite connection policy, an Alembic migration
baseline, generated OpenAPI types, test harnesses, and required GitHub Actions
checks. The first vertical slice reports API and database readiness in the web
interface.

The next product milestone begins the canonical schema for the Hartford,
Connecticut moped market. A user will save a watchlist such as `moped`; the
system will search enabled sources in separate Hartford acquisition and
nationwide reference scopes, normalize and deduplicate new listings, rank local
opportunities, and track their price and availability history. Deterministic
calculations—not an LLM opinion—combine labeled comparable evidence with total
acquisition cost.

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
- [Development workflow](docs/development-workflow.md)
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

Install Python 3.13, [uv](https://docs.astral.sh/uv/), Node.js 24, and npm 11 or
12. Then run from the repository root:

```bash
cp .env.example .env
make setup
make migrate
```

Start the API and frontend in separate terminals:

```bash
make api
make frontend-dev
```

The frontend is available at `http://127.0.0.1:5173` and proxies `/api` to the
backend at `http://127.0.0.1:8000`. Run the complete local CI equivalent with:

```bash
make check
```

Focused commands are `make format`, `make format-check`, `make lint`,
`make typecheck`, `make test`, `make migration-check`, `make build`, and
`make contract-check`. Regenerate the checked-in OpenAPI document and frontend
types with `make generate-api` after changing the API contract.

The selected stack is a Python 3.13 FastAPI backend and worker, a React and
TypeScript frontend built with Vite, and SQLite persistence through SQLAlchemy
and Alembic. See `docs/stack.md` for responsibilities and rationale.

Development uses short-lived branches with pull requests directly into protected
`main`, test-driven development for behavioral changes, and required GitHub
Actions checks. See `docs/development-workflow.md`.

Local secrets belong in `.env`, which is ignored by Git. Copy `.env.example`
when configuration is introduced; never commit credentials.

## License

Resale Monitor is available under the [MIT License](LICENSE).
