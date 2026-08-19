# Vision

## Problem

Secondhand buyers must compare incomplete listings across fragmented
marketplaces. Asking prices are noisy, descriptions omit important details,
photos hide or reveal condition, and a superficially cheap item can become
expensive after repairs, transportation, fees, title problems, or fraud.

Existing alert products usually optimize for matching keywords quickly, while
AI appraisal tools often produce opaque scores. Resale Monitor should combine
continuous discovery with evidence-backed understanding of why a listing may be
worth acting on.

## Product statement

Resale Monitor is a category-aware resale intelligence system built around saved
watchlists. It continuously discovers listings from enabled sources, extracts
item attributes from text and images, builds local history, ranks opportunities,
and turns each promising listing into an evidence-backed buying report. It
estimates total acquisition cost and fair value, exposes uncertainty, flags
risks, and proposes the questions a buyer should ask next.

Each watchlist separates listings the user could realistically buy from a wider
reference market. For the first watchlist, Hartford-area results are acquisition
candidates while broader United States results help establish model- and
condition-specific price context. National context is adjusted for regional
conditions, transportation, transaction costs, and the quality of the evidence;
it is not treated as Hartford truth by itself.

## Initial user

The initial user is the project owner shopping for a used moped or scooter in
the Hartford, Connecticut area. The first version is a personal local web app
that proves the workflow before public users, accounts, and hosted deployment
are introduced.

## Long-term users

- Individuals buying infrequent, high-consideration used goods.
- Enthusiasts monitoring a specific model or local market.
- Resellers who need transparent comparisons and alert prioritization.
- Public users served by a hosted version after the personal workflow is proven.

## Differentiation

- Evidence-backed valuation rather than an opaque AI score.
- Personal total-cost estimates, including transport and likely repairs.
- Explicit confidence and missing-information penalties.
- Category modules with specialized fields, risks, and buyer questions.
- Longitudinal local-market history and relisting detection.
- A growing first-party comparable dataset built from reproducible listing
  observations rather than one-off model opinions.
- A human-controlled path from discovery to seller outreach.

## Product principles

1. Show the evidence behind every important conclusion.
2. Distinguish observed facts, inferred attributes, and unknowns.
3. Optimize for decision quality, not notification volume.
4. Prefer honest ranges over precise but unsupported predictions.
5. Preserve user control over communication and purchasing decisions.
6. Use data only through documented, reviewable acquisition methods.

## Initial success

The first version succeeds when the user can save a Hartford-area `moped`
watchlist, receive a continuously refreshed feed from at least one authorized
live source, and understand why the highest-ranked listings are attractive,
risky, or insufficiently documented.
