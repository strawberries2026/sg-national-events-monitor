# Phase 2 — opt-in feed cost and caching policy

Based on the review comment on issue #11. This is a design policy, **not an enabled network collector**.

- Keep each external source disabled until its documented endpoint, permissions and terms are verified. Existing official-event functionality is unchanged.
- For each enabled source, configure a daily request cap (default proposal: 24 requests/day/source, at most once per hour); actual caps must respect the provider's lower limits. Do not make any request when the daily cap is exhausted.
- Track counters by source and Singapore calendar day. Store a last-success timestamp, HTTP outcome and freshness state. A failure must not trigger unbounded retries.
- Use conditional GET (ETag / Last-Modified) where supported; a 304 response counts as a request but requires no duplicate payload storage.
- Store each raw item only once by stable source ID or canonical HTTPS URL plus a content hash. Keep a bounded, source-attributed cache and re-run analysis on cached records without re-downloading.
- Do not archive full publisher articles unless permitted; prefer metadata, brief allowed excerpts and outbound links. Apply explicit retention periods and remove stale cache items.
- Budget estimate per source: daily requests = min(configured daily cap, scheduled opportunities). Total = sum of enabled source caps. A disabled source costs zero fetch requests.
- Before enabling any collector, test request-cap enforcement, day rollover, cache deduplication, 304 handling, rate-limit backoff, error states and zero-secret exposure.
- No private itinerary tracking, personal data collection, paywall bypass or unapproved scraping.

**Release gate:** source permission verification, cost-budget review, CI, Android tests and explicit merge/deployment approval.
