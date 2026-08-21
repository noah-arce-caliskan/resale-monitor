# Technology stack

## Decision

Resale Monitor uses a Python-first modular monolith with a separate React
frontend. This keeps acquisition, extraction, valuation, and data work in the
language the project owner knows best while adding a production-style typed web
interface.

## Backend and domain pipeline

- **Python 3.13** is the backend, worker, ingestion, extraction, and valuation
  language.
- **FastAPI** exposes the HTTP API and generates an OpenAPI contract.
- **Pydantic 2** validates untrusted API, marketplace, configuration, and model
  output at runtime. It is the Python equivalent of the role Zod would have
  played in a TypeScript backend.
- **SQLAlchemy 2** maps Python domain persistence models to relational tables and
  keeps the path from SQLite to PostgreSQL practical. It fills the ORM role that
  Drizzle would have filled in a TypeScript backend.
- **Alembic** versions database schema changes so a database can be upgraded
  without deleting it.
- **HTTPX** performs async calls to authorized marketplace and model APIs.
- **APScheduler** triggers recurring searches in a separately launched worker.
  Resale Monitor's own source-run tables remain the durable record of work,
  retries, leases, and outcomes; request handlers do not own long-running jobs.
- **pydantic-settings** loads typed configuration from environment variables.

## Persistence

- **SQLite in WAL mode** is the personal proof-of-concept database.
- **Local content-addressed files** retain permitted images using SHA-256 names;
  SQLite stores their metadata and paths.
- **PostgreSQL and object storage** are migration targets only when a hosted,
  concurrent, multi-user product makes them necessary.

## Frontend

- **React with TypeScript** implements the four-screen local web interface.
- **Vite** provides the development server and production build.
- **React Router** owns client-side routes.
- **TanStack Query** owns API fetching, caching, refetching, and source-run status
  instead of spreading request state through UI components.
- **Generated OpenAPI TypeScript types** keep frontend/backend contracts aligned.
- Start with ordinary CSS and a small token system. Do not add a component or
  utility-CSS framework until the interface demonstrates a repeated need.

Node.js 24 is the frontend runtime baseline. npm 11 or 12 installs the committed
lockfile; Python dependencies remain owned by uv.

## Dependency and quality tooling

- **uv** manages Python, `pyproject.toml`, the virtual environment, and the
  committed `uv.lock` dependency lockfile.
- **npm** manages frontend dependencies and the committed `package-lock.json`.
- **Ruff** formats and lints Python; **mypy** checks Python types.
- **pytest** runs backend unit and integration tests.
- **ESLint** and **Prettier** lint and format TypeScript and frontend files.
- **Vitest** and React Testing Library cover frontend units and components.
- **Playwright** covers a small number of end-to-end flows in Resale Monitor's
  own interface. It is not a mechanism for bypassing marketplace access rules.
- **GitHub Actions** runs formatting, linting, type checking, tests, migration
  checks, and the frontend build.

## Architecture boundary

The backend starts as one deployable codebase with two process entry points:

1. `api` serves user-facing HTTP requests.
2. `worker` schedules and executes source searches, refreshes, extraction, and
   analysis jobs.

Both call the same application services and persist explicit job state. This is
simpler than Celery and Redis for the local MVP but leaves job execution behind
an interface so a hosted version can replace it later.

## Deliberately excluded from the initial stack

- Next.js, because server rendering is unnecessary for a private local tool and
  would split domain work between Python and Node.
- Drizzle ORM and Zod, because SQLAlchemy and Pydantic provide those roles in the
  selected Python backend.
- Docker as a prerequisite for local development.
- Redis, Celery, Kafka, microservices, and cloud object storage before scale or
  reliability requirements justify them.
- A heavy frontend component framework before the product's visual language is
  established.

## Revisit triggers

- Move SQLite to PostgreSQL when multiple concurrent users or deployed workers
  need database-level concurrency beyond the personal app.
- Move image files to object storage when the application is hosted or data must
  be shared across machines.
- Replace the local worker implementation when jobs must run across multiple
  machines, survive stronger failure modes, or support materially higher volume.
- Add a UI framework only after repeated accessible components are expensive to
  maintain by hand.
