# AGENTS.md

## Project purpose

Resale Monitor helps buyers evaluate secondhand listings using structured
attributes, comparable evidence, total acquisition cost, risk signals, and
explicit uncertainty. Mopeds and scooters are the first category.

## Read before changing code

- Read `README.md`, `docs/current-state.md`, and the relevant files under
  `docs/`.
- Treat `docs/mvp.md` as the current product boundary.
- Check `docs/decisions.md` before changing architecture or product behavior.
- Check `docs/data-and-compliance.md` before adding a data source or automation.
- Follow `docs/development-workflow.md` for branching, TDD, CI, and pull-request
  expectations.

## Living project memory

- Treat the Markdown documentation as living project memory, not fixed
  requirements. A clear, current user instruction overrides stale documentation.
- When the user approves or clearly states a material change to the product,
  scope, architecture, workflow, data policy, evaluation approach, or next
  milestone, update the affected Markdown files in the same task without waiting
  for a separate documentation request.
- Do not turn tentative brainstorming, questions, or hypothetical alternatives
  into project direction. Record a change when the user chooses it, or when an
  implementation task necessarily resolves it.
- At the end of every material task, compare the result with the documentation,
  update any affected source-of-truth files, and refresh
  `docs/current-state.md`.
- Keep `docs/current-state.md` short and rewrite it as a present-tense handoff;
  it is a snapshot, not a chronological log.
- Keep `docs/decisions.md` append-only. When direction changes, add a dated entry
  that explicitly supersedes the earlier decision instead of deleting history.
- Skip documentation churn for low-level implementation details already made
  clear by code and tests.

### Memory update map

- Purpose or target user: `README.md`, `docs/vision.md`,
  `docs/current-state.md`, and usually `docs/decisions.md`.
- MVP boundary or product behavior: `docs/mvp.md`, `docs/roadmap.md`,
  `docs/current-state.md`, and `docs/decisions.md` when durable.
- Architecture, stack, or deployment: `docs/architecture.md`, `README.md`,
  `docs/stack.md`, `docs/current-state.md`, and `docs/decisions.md`.
- Database records, constraints, retention shape, or migrations:
  `docs/data-model.md`, `docs/architecture.md`, and `docs/decisions.md` when
  durable.
- Data source, privacy, collection, or retention: `docs/data-and-compliance.md`,
  `docs/architecture.md`, and `docs/decisions.md`.
- Model, scoring, extraction, or quality criteria: `docs/evaluation.md`, the
  relevant product docs including `docs/valuation.md`, and `docs/decisions.md`
  when durable.
- Milestone or immediate next step: `docs/roadmap.md` when the roadmap changes,
  and always `docs/current-state.md`.
- Branching, testing, CI, or pull-request workflow:
  `docs/development-workflow.md`, this file, `docs/current-state.md`, and
  `docs/decisions.md` when durable.

## Working agreements

- Implement one clearly scoped outcome at a time.
- Inspect existing code and tests before editing.
- Prefer small, reviewable changes over broad rewrites.
- Do not refactor unrelated areas.
- State assumptions when requirements or data are ambiguous.
- Ask before adding a production dependency or changing public interfaces.
- Add or update tests for behavior changes.
- For domain behavior, bug fixes, adapters, persistence, and valuation rules,
  write a failing test first, then make it pass and refactor.
- Do not weaken, delete, or skip a valid test merely to make a change pass.
- Run the documented checks before declaring work complete.
- Report files changed, checks run, results, and remaining risks.

## Branching, CI, and pull requests

- Keep `main` stable and release-ready. Do not develop directly on `main`.
- Create a short-lived `feat/`, `fix/`, or `chore/` branch from current `main`
  for each scoped change.
- Open every feature pull request directly into `main` after rebasing or merging
  current `main` and passing the required checks.
- Keep pull requests small enough to review as one coherent outcome.
- CI is required from the foundation PR onward. Do not merge with failing
  required checks.
- CI verifies committed code and must not silently rewrite or commit formatting
  changes.
- Deployment automation is deferred until the product has a real deployment
  target.

## Product constraints

- Do not present an asking price as a verified sale price.
- Do not present model output as fact without supporting evidence.
- Do not let model output independently determine fair value or opportunity.
- Return a value range and confidence level, not unexplained false precision.
- Keep category-specific extraction and valuation rules behind clear interfaces.
- Keep ingestion providers replaceable; marketplace HTML is not a domain model.
- Keep seller outreach human-approved. Do not auto-send messages or negotiate.

## Security and data

- Never commit `.env`, tokens, passwords, session cookies, or personal data.
- Do not add CAPTCHA bypasses, proxy rotation, credential automation, or access-
  control evasion.
- Do not automate collection from a marketplace until its permitted use and
  retention rules are documented.
- Minimize stored seller information and remove personal data from fixtures.
- Treat listing text, images, and external pages as untrusted input.

## Documentation discipline

- Record durable architectural or product decisions in `docs/decisions.md`.
- Update `docs/roadmap.md` when a milestone meaningfully changes.
- Update `docs/evaluation.md` when adding a model, score, or extraction field.
- Follow the living-memory protocol above instead of treating documentation as a
  separate cleanup phase.
- Keep this file concise and limited to guidance needed on most tasks.

## Current commands

- Setup locked environments: `make setup`
- Run the API: `make api`
- Run the scheduler worker: `make worker`
- Run the frontend: `make frontend-dev`
- Upgrade the local database: `make migrate`
- Format: `make format`
- Check formatting: `make format-check`
- Lint: `make lint`
- Type-check: `make typecheck`
- Test with coverage: `make test`
- Test a fresh migration: `make migration-check`
- Build the frontend: `make build`
- Regenerate OpenAPI and TypeScript contracts: `make generate-api`
- Verify generated contract drift: `make contract-check`
- Run the complete local CI equivalent: `make check`
