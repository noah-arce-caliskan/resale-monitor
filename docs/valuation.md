# Valuation and evidence policy

## Purpose

Resale Monitor must decide whether a local listing deserves attention without
turning an LLM opinion or an asking-price average into false truth. Valuation is
a reproducible calculation over attributed evidence. Models assist with reading
messy text and images; they do not independently set prices.

## Three watch processes

One saved watchlist produces three related workloads:

1. **Local acquisition discovery** searches Hartford and the configured travel
   radius frequently for listings the user could realistically buy.
2. **Broad reference collection** searches a wider United States market less
   frequently to build model-, year-, displacement-, and condition-specific
   comparable cohorts.
3. **Listing lifecycle tracking** appends observations for known listings so
   price changes, availability, relistings, and explicit outcomes remain visible.

Only local acquisition results enter the deal feed. Reference results provide
context and can never silently widen the user's travel area.

## Evidence hierarchy

From strongest to weakest pricing evidence:

1. A verified transaction with the final price.
2. An explicit sold record whose final negotiated price may still be uncertain.
3. A licensed or professional valuation guide applicable to the item.
4. An active asking price.
5. A disappeared listing with an unknown outcome.
6. A model-generated estimate.

The sixth tier is not a pricing comparable. Disappearance is never converted to
a sale, and records from different tiers must remain labeled and separately
weighted.

## Comparable selection

Comparable candidates are filtered and weighted using observable factors:

- Make, model, trim, displacement, and item type.
- Model year and mileage.
- Running state, title or registration state, condition, damage, modifications,
  and included accessories.
- Evidence type and provenance.
- Geography, recency, and transaction or delivery context.

The system records why each comparable was included, excluded, and weighted.
When structured attributes are missing, the cohort widens cautiously and
confidence falls.

## Initial deterministic calculation

1. Normalize the candidate's evidence-backed attributes.
2. Select a comparable cohort and calculate a reliability-weighted median and
   percentile range.
3. Adjust the broad baseline using reliable Northeast and Hartford evidence as
   it accumulates.
4. Estimate total acquisition cost as asking price plus transport or shipping,
   tax, title and registration costs, likely repairs, and a risk reserve.
5. Calculate `conservative advantage = fair value low - total acquisition cost
   high`.
6. Derive confidence from sample size, similarity, evidence tiers, recency,
   missing attributes, and adjustment strength.

The user sees the fair-value range, total-cost range, conservative advantage,
confidence, comparable records, and all material assumptions. Product labels
such as `strong opportunity` summarize those visible components and are not
profit guarantees.

## Sparse local data

The first Hartford cohort will be small. Use a broad United States baseline for
the same item and condition, apply known transport and transaction costs, and
shrink local estimates toward that baseline. Increase Hartford's influence only
as independent, relevant, recent observations accumulate. Never represent a
national asking-price distribution as a local sold-price distribution.

## LLM boundary

Models may extract make, model, year, displacement, mileage, running state,
title status, condition, visible damage, missing accessories, modifications,
and scam signals. Every value carries provenance and confidence and may remain
unknown. Deterministic code owns comparable retrieval, price calculations,
confidence rules, and final ranking.

## Initial validation

- Compare the calculated baseline with manually reviewed eBay Product Research
  results when the user's Seller Hub access makes them available.
- Compare against simple baselines such as the weighted median of reviewed
  comparables.
- Record user corrections and known outcomes without treating them as verified
  facts unless their provenance supports that label.
- Version cohort rules, adjustments, cost assumptions, and calculation outputs.

## Version 0.1 calculation contract

### Current implementation status

The fixture-backed MVP implements effective-sample gating, weighted quartiles,
active-asking confidence caps, conservative cost bounds, advantage thresholds,
and persisted comparable/cost audit rows. Its first cohort assigns one reviewed
active-asking weight rather than claiming calibrated similarity, recency, and
regional models. Regional shrinkage and field-specific weights below remain the
next calibration step and must be fixture-tested before activation.

This section defines the first implementable baseline. Its constants are
versioned hypotheses to evaluate, not claims of market truth.

### Required candidate inputs

- Current immutable listing observation and resolved item version.
- Watchlist geography, travel tolerance, repair tolerance, and cost assumptions.
- Currency-normalized comparable candidates with evidence type and provenance.
- Versioned moped cost rules and valuation policy identifier.

If asking price or currency is unknown, the system may extract and show evidence
but must return `insufficient_evidence` instead of an opportunity label.

### Comparable eligibility

Hard-exclude the candidate itself, duplicate source facts, model-generated price
opinions, incompatible currencies without a timestamped conversion, obvious
parts-only records for a complete vehicle, category mismatches, and records with
invalid or unsupported price provenance.

Start with exact make/model cohorts. Widen in explicit stages only when evidence
is sparse: nearby model years, equivalent displacement and vehicle class, then
same-category market context. Every widening step lowers similarity and is
visible in reason codes.

### Weight components

Each eligible record receives independently inspectable values from `0` to `1`:

- Item similarity: make/model, year, displacement, mileage, running state,
  title state, condition, damage, modifications, and included accessories.
- Evidence reliability: determined by the evidence hierarchy, never by model
  confidence.
- Recency: decays by category policy from the evidence observation or transaction
  time.
- Geography: Hartford, Northeast, or broader United States context.
- Completeness: penalizes comparisons with unresolved attributes used for
  matching.

`final weight = similarity * reliability * recency * geography * completeness`

Version 0.1 begins with reviewable policy constants. Verified final transactions
may receive reliability `1.00`, explicit sold records at most `0.85`, valuation
guides at most `0.70`, active asks at most `0.45`, and disappeared-unknown records
at most `0.20` as asking-price evidence only. These initial caps must be tested
and changed through policy versions rather than hidden code edits.

### Effective sample and range

Compute effective sample size as:

`n_eff = (sum(weights) ^ 2) / sum(weight ^ 2)`

Use weighted price quantiles for the cohort. The provisional midpoint is the
weighted median; the provisional low and high are weighted 25th and 75th
percentiles. Do not emit a value range below `n_eff = 3`. Mark `3 <= n_eff < 8`
as sparse and apply a confidence cap. Preserve evidence-type composition beside
the range so an active-asking range cannot appear to be a sold-price range.

### Regional shrinkage

Estimate a regional log-price adjustment only from sufficiently matched strata.
Shrink it toward zero:

`regional adjustment = n_eff_local / (n_eff_local + 20) * local log-price ratio`

Apply the exponentiated adjustment to the broad baseline. With no reliable local
sample, the adjustment is zero and the result remains explicitly national. The
constant `20` is a versioned prior strength to validate, not an immutable truth.

### Total acquisition cost

Store every component as an `analysis_costs` row:

`total cost low = ask + sum(cost lows)`

`total cost high = ask + sum(cost highs)`

Components may include shipping or travel, tax, title, registration, immediate
repairs, and a risk reserve for unresolved high-impact facts. An unknown cost is
not silently zero: use a conservative versioned range or mark the analysis
insufficient when no defensible bound exists.

### Opportunity result

`conservative advantage = fair value low - total cost high`

Initial labels are deterministic and moped-specific:

- `strong`: advantage is at least both 20% of fair-value low and $300, confidence
  is at least `0.70`, and no blocking risk is present.
- `promising`: advantage is at least both 10% of fair-value low and $150,
  confidence is at least `0.50`, and no blocking risk is present.
- `watch`: advantage is positive but thresholds or confidence are not met.
- `not_attractive`: advantage is zero or negative.
- `insufficient_evidence`: required inputs, defensible costs, or comparable
  support are missing.

Dollar thresholds are stored in category policy, not embedded throughout the
application. Blocking risks initially include clear parts-only mismatch,
unsupported ownership/title where required for the intended use, and evidence
of a likely scam severe enough that price comparison would mislead.

### Confidence

Calculate confidence from evidence reliability, comparable similarity, effective
sample size, recency, candidate attribute completeness, and regional support.
Version 0.1 starts with weights of 30%, 25%, 20%, 10%, 10%, and 5% respectively.

Apply explicit caps after the weighted calculation:

- Active-asking-only evidence: at most `0.55`.
- Effective sample below `3`: no value range; `insufficient_evidence`.
- Effective sample from `3` to below `8`: at most `0.60`.
- Unresolved candidate make or model: at most `0.25`.
- Unresolved running state or title state: opportunity confidence at most `0.50`
  until cost risk is bounded.

Confidence is a property of the evidence and calculation, not the fluency of an
LLM explanation.

### Recalculation

Create a new immutable analysis whenever candidate price, resolved attributes,
cost assumptions, included evidence, valuation policy, or cost-rule version
changes. Never rewrite an old analysis to reflect a new algorithm.
