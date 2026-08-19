# Data sources and compliance

## Purpose

Resale Monitor's value should come from analysis, not from evading marketplace
controls. Every source adapter must document permission, data provenance,
retention, rate limits, personal-data handling, and failure behavior before it is
enabled outside tests.

This is an engineering policy, not legal advice. Recheck source terms before an
integration is implemented or released.

## Preferred acquisition order

1. User-entered structured data and uploaded screenshots or images.
2. Public datasets with a compatible license.
3. Official or licensed APIs used within their documented terms.
4. User-authorized exports.
5. User-triggered local extraction only after a terms and privacy review.
6. Automated website collection only with explicit permission.

The product is watchlist-first, but automated discovery is activated only for
authorized sources. Each provider adapter must expose its permitted capabilities
separately, such as manual import, image retention, single-listing refresh,
search, and scheduled tracking. Unsupported capabilities remain disabled rather
than silently falling back to an unofficial scraper.

## Initial source capability plan

- **eBay:** automated search and refresh through official developer APIs. This is
  the first live MVP source.
- **Facebook Marketplace:** product target, but automated search and refresh are
  disabled without Meta's express written permission or another explicitly
  authorized method.
- **OfferUp:** product target and manual input source; third-party automated
  collection remains disabled without prior written consent.
- **Craigslist:** product target and manual input source; software collection
  remains disabled without a separate license or permission.
- **Additional marketplaces:** evaluate official APIs, licensed feeds, user
  exports, and source terms before implementation.

## Known source constraints

### Facebook Marketplace

Meta's automated data collection terms require express written permission for
automated collection. Do not implement unattended collection, automated login,
CAPTCHA handling, or session-cookie storage without a documented authorization.

Reference: <https://www.facebook.com/legal/automated_data_collection_terms>

### OfferUp

OfferUp's terms prohibit automated means used to access the service or collect
data and prohibit unapproved third-party applications. Treat OfferUp as manual
input only unless written permission or a suitable authorized interface exists.

Reference: <https://offerup.com/terms>

### Craigslist

Craigslist's terms prohibit unlicensed software interaction and automated or
manual-equivalent collection of its content. Treat Craigslist as manual input
only unless a separate license or permission is obtained.

Reference: <https://www.craigslist.org/about/terms>

### NHTSA vPIC

The NHTSA vehicle API can provide manufacturer-reported VIN and vehicle metadata.
Follow its use policy and rate controls; it is not a pricing source.

References: <https://vpic.nhtsa.dot.gov/api/> and <https://api.nhtsa.gov/>

### eBay

Use official APIs and their licenses for supported inventory discovery. Historical
sold-item access through Marketplace Insights is limited release and must not be
assumed available.

Seller Hub Product Research may be used as a manual validation aid when the user
has access, but it is not an assumed programmatic source. Nationwide active eBay
records remain asking-price evidence and must be labeled accordingly.

Reference: <https://www.edp.ebay.com/api-docs/buy/marketplace-insights/static/overview.html>

## Data handling rules

- Store the minimum source content needed to reproduce an analysis.
- Avoid storing seller names, profile photos, contact information, or messages.
- Strip personal information from fixtures and evaluation examples.
- Record acquisition method, source, timestamp, and price type.
- Do not train models on collected content without separate rights and review.
- Define deletion and retention behavior before accepting user accounts.
- Never place marketplace credentials or session cookies in the repository.

## Image display and retention

- Keep images viewable in the personal research history when their acquisition
  and retention are permitted.
- Display an approved remote URL when it is HTTPS, contains no credentials or
  session tokens, comes from a reviewed source, and is expected to remain
  available.
- Otherwise retain a private local copy when the image is user-supplied or the
  source permits retention. Store its content hash, source, acquisition time,
  media type, and retention status.
- If neither remote display nor local retention is permitted, require the user
  to upload an image or screenshot instead of copying it automatically.
- Do not commit collected listing images to Git. Public-product retention and
  deletion periods must be decided before accepting external users.

## Adapter review checklist

- What grants access to the data?
- Which fields may be collected and displayed?
- Is commercial or derivative use restricted?
- What rate and retention limits apply?
- Does the source include personal data?
- Can the adapter work without storing raw content?
- How will changes, revocation, and deletion requests be handled?
- What test fixtures can replace the live source during development?
