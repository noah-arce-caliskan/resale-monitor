# Evaluation plan

## Purpose

Resale Monitor should be evaluated as a decision-support system, not judged by
whether an explanation sounds persuasive. Each pipeline stage needs measurable
behavior and a reproducible test set.

## Initial evaluation set

Create a small, versioned set of moped and scooter listings using content the
project is allowed to retain. Remove personal data and record:

- Ground-truth make, model, year, displacement, mileage, and condition fields.
- Whether title, VIN, running state, and visible damage are known or unknown.
- Expert or user-reviewed comparable relevance.
- Expected questions and red flags.
- Outcome information only when its source and meaning are known.

Do not commit copyrighted listing images unless their use and redistribution are
permitted. Tests may use synthetic, licensed, or locally generated fixtures.

## Metrics

### Watchlist ingestion

- New-listing discovery recall against a reviewed source sample.
- Duplicate rate within and across repeated source runs.
- Source-run success, partial-failure, retry, and stale-data rates.
- Time from source publication to Resale Monitor ingestion where publication
  time is available.
- Percentage of collected listings eliminated by deterministic filters before a
  model call, with false-negative review.

### Attribute extraction

- Exact or normalized accuracy for categorical fields.
- Numeric error for year, mileage, and displacement.
- Precision and recall for condition and risk flags.
- Unknown-detection accuracy: missing data should remain unknown.

### Comparable retrieval

- Precision at K for relevant comparisons.
- Ranking quality based on make, model, year, condition, mileage, and location.
- Rate of comparisons incorrectly mixing asking and sold prices.
- Cohort quality separately for local acquisition and broad reference records.
- Accuracy of evidence-tier labels and comparable exclusion reasons.

### Valuation

- Median absolute error and median absolute percentage error when reliable target
  prices exist.
- Coverage: how often the target falls inside the predicted range.
- Range width, so high coverage cannot be achieved with uselessly broad ranges.
- Calibration: whether stated confidence matches observed reliability.
- Improvement over a weighted-median asking-price baseline.
- Sensitivity of conservative advantage to transport, repair, and risk-reserve
  assumptions.
- Correct fallback from sparse Hartford data to a clearly labeled broader
  baseline.
- Effective-sample-size and confidence-cap behavior at boundary cases.
- Stability under duplicate comparable insertion; deduplication should prevent a
  repeated source fact from moving the range.
- Backtests of each versioned opportunity threshold rather than treating initial
  moped constants as established truth.

### Decision support

- User-rated usefulness of explanations and seller questions.
- Alert precision: proportion of alerts the user considers worth investigating.
- Correction rate for extracted attributes.
- Frequency of unsupported or misleading claims.
- Precision at K for the ranked watchlist feed.

### Opportunity assessment

- Agreement between the component evidence and the displayed opportunity result.
- Sensitivity to asking price, condition, likely costs, comparable support,
  liquidity, and missing information.
- Calibration of opportunity confidence against later user-reviewed outcomes.
- Minimum comparable sample size and fallback behavior for sparse Hartford data.

### Longitudinal tracking

- Snapshot completeness and idempotency.
- Price-change and explicit-status detection accuracy.
- Relisting and duplicate-detection precision.
- Rate of unavailable listings incorrectly presented as verified sales; the
  target is zero.
- Image availability in saved analyses and correct retention metadata.
- Correct append-only behavior for observations, item versions, outcomes, and
  analyses, including preservation of user corrections.

## Evaluation rules

- Keep training/development examples separate from final evaluation examples.
- Version prompts, models, deterministic rules, and datasets with results.
- Compare new approaches against a simple baseline, such as median price of
  manually selected comparables.
- Record failures and use them to update tests before changing prompts or models.
- Do not optimize only for aggregate accuracy; review high-cost false positives.
