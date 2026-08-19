# Minimum viable product

## MVP question

Given a saved Hartford-area `moped` watchlist, can Resale Monitor automatically
discover listings from an authorized live source, rank useful opportunities,
produce an evidence-backed report, and preserve price and availability history?

## Input

The user creates a watchlist with:

- Name and search phrases, initially `moped` plus useful moped and scooter
  synonyms.
- Hartford, Connecticut as the center and a configurable search radius.
- Enabled sources.
- Optional minimum and maximum asking price, exclusions, and condition rules.
- Personal assumptions such as travel tolerance and repair tolerance.

The watchlist creates two distinct search scopes:

- A frequently refreshed Hartford acquisition scope containing listings the
  user could plausibly buy.
- A broader, less frequently refreshed United States reference scope used to
  build comparable cohorts and price context, not to fill the local deal feed.

The system also accepts a manually supplied URL, text, and images as a fallback,
but manual entry is not the primary journey.

## Processing

1. Schedule local acquisition and broader reference runs according to each
   enabled source's documented limits.
2. Search through a provider adapter and save the raw acquisition record.
3. Normalize and deduplicate listings using provider IDs, URLs, and content
   fingerprints.
4. Apply deterministic keyword, location, and price filters before model calls.
5. Extract normalized moped attributes and preserve field-level provenance and
   uncertainty.
6. Persist image records and an immutable first observation.
7. Retrieve a model- and condition-matched comparable cohort, distinguish its
   evidence types, and calculate a transparent fair-value range.
8. Estimate total acquisition cost from asking price, transport or shipping,
   taxes and registration, likely repairs, and a risk reserve.
9. Calculate conservative advantage from the low end of fair value minus the
   high end of total acquisition cost, then expose the components and confidence.
10. Rank the local watchlist feed and explain the leading opportunities.
11. Record later price and status observations through permitted refresh methods
   without treating disappearance as proof of sale.

## Output

- Ranked deal feed for the watchlist.
- Listing summary and normalized attributes for each inspected result.
- Fair-value range with confidence.
- Estimated additional-cost range.
- Opportunity assessment with visible components and confidence, not a single
  guaranteed profit.
- Ranked comparable evidence.
- Price and availability timeline for the tracked listing.
- Explanation of positive and negative factors.
- Red flags and missing information.
- Recommended next questions and inspection checks.

## Screens and user journey

The MVP uses four primary screens: Watchlists, Create or Edit Watchlist, Deal
Feed, and Listing Workspace. Attribute correction and manual listing entry are
secondary actions rather than blocking screens. See `docs/user-journey.md` for
screen contracts, states, and end-to-end flows.

## Explicit non-goals

- Supporting every marketplace in the first release.
- Automated collection from providers that have not authorized it.
- Real-time, email, or push notifications.
- Automatic seller messaging or negotiation.
- Automatic purchases or deposits.
- Supporting every resale category.
- Claiming to know the final sale price of a disappeared listing.
- Mechanical, legal, title, or authenticity guarantees.

## Acceptance criteria

- A `moped` watchlist automatically discovers listings from eBay through its
  official API.
- Repeated source runs are idempotent and do not duplicate listings.
- Cheap deterministic filters run before model extraction and vision analysis.
- Every valuation cites the comparisons and assumptions used.
- The local candidate feed and nationwide reference dataset remain separate.
- LLM output can supply structured attributes and risk evidence but cannot by
  itself determine fair value or the opportunity result.
- Unknown critical attributes lower confidence.
- The user can correct extracted attributes and rerun the analysis.
- The system stores enough provenance to reproduce an analysis.
- Provider adapters map into one canonical model and can be tested from saved
  fixtures without live access.
- A supported listing can receive later observations without overwriting its
  history.
- Unknown disappearance is never reported as a verified sale.
- A small labeled evaluation set measures extraction and recommendation quality.
