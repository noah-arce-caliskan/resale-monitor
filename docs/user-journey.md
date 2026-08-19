# Watchlist thin-slice screens and user journey

## Goal

The thin slice must let one person express persistent buying intent once and
receive a continuously refreshed, ranked feed of Hartford-area moped listings.
Manual entry and correction remain available, but repeated listing entry is not
the primary experience.

The initial live source is eBay through its official API. A watchlist runs a
Hartford acquisition search for the deal feed and a broader United States
reference search for comparable context. Every screen is source-independent so
authorized Facebook Marketplace, OfferUp, Craigslist, and other adapters can be
enabled later without redesigning the product.

## Navigation model

The persistent navigation contains only:

- Watchlists.
- Add watchlist.
- Manual add, as a secondary fallback action.

Authentication, notifications, account settings, and category switching are not
part of the personal MVP.

## Screen 1: Watchlists

### User question

What am I watching, is each source healthy, and did anything promising appear?

### Required content

- Primary **Add watchlist** action.
- Watchlist cards with name, geography, enabled sources, active filters, last
  successful run, next run, new-result count, and best recent opportunity.
- Source-health states: never run, running, healthy, partial, rate limited,
  authorization required, and failed.
- Pause, run now, edit, and archive actions.
- A compact recent-opportunities section across all active watchlists.

### Empty state

Explain the persistent-search workflow in one sentence and lead directly to
**Create your first watchlist**.

### Primary action

Open the selected watchlist's Deal Feed.

## Screen 2: Create or Edit Watchlist

### User question

What should Resale Monitor search for, where, and under what constraints?

### Required input

- Watchlist name, initially `Mopeds near Hartford`.
- Primary search phrase and optional synonyms such as scooter, moped, 50cc,
  125cc, and 150cc.
- Excluded phrases and sellers when supported.
- Hartford, Connecticut center and search radius.
- Minimum and maximum asking price.
- Enabled sources with capability and authorization state shown beside each.
- Travel tolerance, repair tolerance, and optional condition preferences.
- Search frequency constrained by each source's documented limits.
- Independent acquisition and reference schedules, with their purposes made
  clear rather than exposed as duplicate watchlists.

The source selector must not imply equal capability. An enabled source can be
automatic, manual-import-only, unavailable pending authorization, or fixture-only
in development.

### Preview

Show a plain-language summary before saving, for example: "Search eBay for
moped and scooter listings within the configured Hartford area, exclude parts-
only results, and prioritize listings under the selected price ceiling."

### Primary action

**Save and run** persists the watchlist, starts its first eligible source run,
and opens Deal Feed with progress visible.

## Screen 3: Deal Feed

### User question

Which newly discovered listings deserve my attention first?

### Required content

- Watchlist summary, last run, next run, enabled-source health, and **Run now**.
- Ranked listing cards with image, title, source, location or shipping context,
  asking price, first seen, opportunity label, confidence, and the strongest
  positive and negative factor.
- New, changed-price, uncertain, likely scam, unavailable, and archived states.
- Filters for source, price, opportunity, confidence, status, and first-seen
  time.
- Sort by opportunity, newest, price, distance, and confidence.
- Clear low-data warnings while the Hartford comparison set is sparse.

### Processing behavior

Listings appear after deterministic relevance and deduplication checks. Cheap
structured extraction may improve ranking asynchronously. Expensive vision work
is reserved for listings that survive cheap filters or are explicitly opened.
Cards may move as additional evidence arrives, and every change must be tied to
an analysis version.

### Secondary manual action

**Add missing listing** accepts a URL, pasted text, and images when a marketplace
cannot be searched automatically. It enters the same normalization and analysis
pipeline as discovered listings.

### Primary action

Open Listing Workspace.

## Screen 4: Listing Workspace

### User question

Is this opportunity worth investigating, why, and what has changed?

### Header

- Listing title, source, current asking price, location or delivery context, and
  current status.
- Image gallery.
- **Open original**, **Correct attributes**, **Update manually**, and, when the
  provider allows it, **Check now** actions.

### Overview section

- Plain-language opportunity label and confidence.
- Asking price beside fair-value and additional-cost ranges.
- Visible components for price position, condition, likely costs, comparable
  support, local liquidity, missing information, and risk.
- Short explanation, critical red flags, inspection priorities, and seller
  questions.

The label summarizes visible components; it is never an unexplained AI score or
guaranteed profit.

### Evidence and correction section

- Structured make, model, year, displacement, mileage, running condition, title
  status, registration status, visible damage, modifications, and included
  parts.
- Field-level provenance and confidence: source text, image, user, inferred, or
  unknown.
- Inline correction without forcing every feed item through a review screen.
- Ranked comparable records with similarity reasons, exclusions, price type,
  location, and observation time.
- Explicit sample-size warnings and version metadata.

User corrections are durable evidence and are never silently overwritten by a
later extraction run.

### History section

- First seen, last checked, and first missing times.
- Chronological observations of price, availability, and explicit status.
- Price history visualization once at least two prices exist.
- Acquisition method and status confidence for each observation.
- An unavailable listing remains **Unavailable—outcome unknown** unless there is
  supporting evidence for a sale.

## Primary user journey

1. The user opens Watchlists and chooses **Add watchlist**.
2. The user enters `moped`, confirms useful synonyms and exclusions, chooses
   Hartford and a radius, enables eBay, and sets buying preferences.
3. The user chooses **Save and run**.
4. The scheduler creates separate Hartford acquisition and nationwide reference
   runs through the official eBay API.
5. The adapter paginates results, records each run's purpose and provenance, and
   maps each item into the canonical listing model.
6. The pipeline deduplicates results and applies cheap keyword, price, and
   location rules.
7. Structured extraction enriches the survivors; vision runs only where
   justified. Deterministic code selects labeled comparable evidence, calculates
   fair-value and total-cost ranges, and derives conservative advantage.
8. Deal Feed ranks only acquisition candidates and makes incomplete analysis
   states and sparse-reference warnings visible.
9. The user opens a promising listing, examines evidence, corrects any extracted
   attributes, and uses the source link to investigate or contact the seller.
10. Later source runs append observations, detect new listings and price changes,
    refresh rankings, and preserve historical state.

## Source expansion journey

Adding a marketplace does not create a new user flow. A source adapter must:

1. Pass a documented permission and retention review.
2. Implement search and refresh capabilities separately.
3. Map fixture responses into canonical source records and listings.
4. Pass pagination, retry, idempotency, deduplication, and failure contract tests.
5. Expose source health and authorization state in Watchlist screens.
6. Be activated live only after its acquisition method is authorized.

## Failure and uncertainty paths

- Source run fails: preserve prior data, classify the failure, and show source
  health without presenting "no results."
- Partial pagination: retain collected pages, mark the run partial, and avoid
  concluding that missing listings disappeared.
- Extraction fails: keep the listing in the feed with low confidence and allow
  manual correction or retry.
- Insufficient comparable evidence: show low confidence and no fabricated value
  estimate.
- Image retrieval fails: preserve metadata and request a user upload when useful.
- Duplicate or relisted item: link possible matches and require confirmation
  before merging cross-source identity.
- Listing unavailable: record first missing time and unknown outcome unless an
  explicit status provides stronger evidence.

## Thin-slice completion criteria

- A first-time user can create `Mopeds near Hartford` and receive eBay results
  without entering individual listings.
- Repeated source runs do not create duplicate listing identities or overwrite
  observations.
- Every feed ranking links to visible opportunity components and evidence.
- Source failures, empty results, and unavailable listings remain distinct.
- Model extraction is not invoked for listings rejected by deterministic rules.
- Attributes can be corrected without blocking feed generation.
- The same adapter contract can run saved fixtures for sources that are not live.
- Images remain viewable through an approved URL or permitted retained copy.
