# Development workflow

## Purpose

This document is the durable engineering workflow for Resale Monitor. Prompts
should describe the current outcome, not repeat these standing rules. `AGENTS.md`
contains the concise instructions that apply to every task; this document
contains the rationale and detailed contract.

## Branch model

- `main` is stable, protected, and suitable for a tagged release.
- Every code change uses a short-lived branch from current `main`:
  `feat/<scope>`, `fix/<scope>`, or `chore/<scope>`.
- Pull requests target `main`; do not commit directly to `main`.
- Before review, bring the branch up to date with `main`, resolve conflicts on
  the feature branch, and rerun the complete local CI equivalent.
- Delete the feature branch after squash merging.

A long-lived `dev` branch is deliberately excluded while this is a solo project
without a staging deployment. Add an integration branch only when multiple
parallel contributors, release trains, or a real staging environment create a
demonstrable need.

## Pull-request contract

Each pull request should deliver one coherent outcome and include:

- Problem and intended behavior.
- Scope and explicit non-goals.
- Tests added or changed.
- Commands run and their results.
- Migration, data, security, and source-compliance impact where applicable.
- Screenshots for material user-interface changes.
- Remaining risks and follow-up work.
- Synchronized living documentation when product direction or project state
  changed.

Prefer squash merging so the permanent branch history contains one meaningful
commit per pull request. Never merge a red or partially understood build.

## Test-driven development

Use red-green-refactor for behavior whose correctness matters:

1. **Red:** add the smallest failing test that expresses the intended behavior
   or reproduces the defect.
2. **Green:** implement the smallest clear change that passes it.
3. **Refactor:** improve structure while keeping the suite green.
4. Run the relevant focused checks during development and the complete local CI
   equivalent before requesting review.

Test-first development is required for valuation and confidence rules,
deduplication, listing lifecycle transitions, provider normalization, database
constraints and migrations, user-correction precedence, and bug fixes.

Documentation-only edits, mechanical configuration, generated files, and
time-boxed exploratory spikes do not require a contrived failing test. They still
require proportionate validation. A spike cannot merge as production behavior
until its behavior is covered.

Do not over-mock. Prefer deterministic domain tests, temporary SQLite databases,
saved authorized provider fixtures, and tests at stable boundaries. Never call a
live marketplace or paid model from the default test suite.

## Test layers

### Backend

- Pure unit tests for valuation, matching, filtering, state transitions, and
  category rules.
- Repository and migration tests against temporary SQLite databases with foreign
  keys and WAL behavior configured as production expects.
- API integration tests through FastAPI's test client and dependency overrides.
- Provider adapter contract tests from sanitized, permitted fixtures.

### Frontend

- Unit tests for pure transformations and formatting.
- React Testing Library tests for user-visible component behavior.
- Mock Service Worker or an equivalent boundary for deterministic API states
  once frontend API integration exists.
- A small Playwright suite for critical journeys; do not duplicate every
  component assertion end to end.

### End-to-end

Add end-to-end coverage incrementally for the four durable journeys: create a
watchlist, inspect the deal feed, open a listing workspace, and correct evidence.
Tests use local fixtures and never automate restricted third-party sites.

## Continuous integration

GitHub Actions begins with the foundation pull request. Workflows run on pull
requests targeting `main` and on pushes to `main`.

Required backend checks:

- Locked dependency installation with uv.
- Ruff formatting check and lint.
- mypy type checking.
- pytest with coverage reporting and no live external calls.
- Fresh-database `alembic upgrade head` migration test.

Required frontend checks:

- Locked dependency installation with `npm ci`.
- Prettier check and ESLint.
- TypeScript type checking.
- Vitest component and unit tests.
- Production frontend build.

Add Playwright as a separate required check when the first complete user journey
exists. Add an OpenAPI generated-client drift check once generation is wired in.
Keep check names stable after branch protection references them.

The complete local CI equivalent is `make check`. It checks Ruff and Prettier
formatting, Python and TypeScript linting and types, pytest and Vitest coverage,
a fresh Alembic upgrade, the production frontend build, and generated OpenAPI
contract drift. `README.md` and `AGENTS.md` contain the focused setup and run
commands.

CI must fail on formatting drift rather than rewrite the branch. Cache only
dependency downloads and safe build inputs; correctness cannot depend on a warm
cache. Pin third-party GitHub Actions to trusted maintained releases and grant
the workflow the minimum token permissions it needs.

## Branch protection

After the first workflow has completed successfully, protect `main`:

- Require pull requests.
- Require the relevant CI checks to pass.
- Block force pushes and branch deletion.
- Do not require another human approval while the repository has one developer.
- Prefer squash merging and a linear, understandable permanent history.

Emergency fixes still branch from `main`, pass the same checks, and return by
pull request; urgency does not justify bypassing the test and review trail.

## Continuous delivery

There is no deployment target in the local MVP, so CD is deliberately deferred.
When hosting is selected, add a separate decision covering environments,
secrets, migrations, rollback, artifact promotion, and deployment approvals.
CI should be established now without pretending that a GitHub workflow is a
deployment strategy.

## Initial pull-request sequence

1. `feat/project-foundation`: backend and frontend skeletons, dependency locks,
   health checks, test harnesses, Alembic infrastructure, and CI.
2. `feat/watchlist-source-schema`: watchlists, search scopes, source runs, and
   their tests and migration.
3. `feat/listing-observation-schema`: listings, provider identities,
   observations, images, and lifecycle tests.
4. `feat/evidence-analysis-schema`: item versions, evidence, comparables, costs,
   and analysis persistence.
5. `feat/valuation-baseline`: the deterministic version 0.1 contract developed
   test-first.
6. `feat/ebay-discovery`: official eBay acquisition and reference searches using
   fixture-first adapter tests.

The sequence is a planning baseline. Split a pull request further if its review
surface becomes too large; do not combine unrelated outcomes to preserve the
numbering.
