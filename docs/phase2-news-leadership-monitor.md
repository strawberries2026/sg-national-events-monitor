# Phase 2 — News & Leadership Monitoring (design and source audit)

Status: planning / isolated feature branch. Production unchanged. Tracks issue #11.

## Existing baseline
- README states official social-media directories are **not live feeds** and automated social-media ingestion is not configured.
- Dashboard reads data/events.json and data/verified-events.json; the latter contains separately verified primary-source events.
- Government announcement links and leadership/event cards exist. Do not mistake linked directories for automatic news monitoring.

## Proposed source classes (availability and terms require verification)
1. Official primary sources: Istana, PMO, MFA, Parliament, ministry announcement pages. Preserve current feeds.
2. Editorial reporting: CNA, The Straits Times and other Singapore publishers **only** via documented permitted RSS/API feeds or outbound links; no bypassing paywalls or access controls.
3. Official public social posts: links first; ingest only where documented APIs/feeds and platform terms allow. Never scrape restricted pages.

## Normalized record
id, title, canonical_url, publisher, source_class (official|news|social), published_at, event_start, event_end, persons[], categories[], fetched_at, verification_status (officially_verified|reported|unverified), verification_url, summary.

## Safeguards
- Never infer a confirmed event date from a news/social headline alone.
- Preserve source attribution and original URL; no full-article republication.
- Deduplicate canonical URLs and near-identical headlines.
- Safe HTTPS links, escaped text, no client secrets, no personal data or private itineraries.
- Stale/failed feeds show honest status and never erase verified event calendar.
- Keep zero-cost hosting, existing Android PWA, version/date and attribution, and public-data/non-operational disclaimer.

## Acceptance gates
- Confirm endpoint availability and license/terms before enabling each publisher.
- Fixture tests: source labels, deduplication, SGT timestamps, date provenance, stale/error handling and safe rendering.
- CI success plus isolated Android preview verification for filtering, expandable titles, source links and standalone PWA.
- Explicit user approval required before merge or deployment.

## Implementation stages
1. Source registry with disabled-by-default candidate feeds.
2. Deterministic normalizer and fixture tests.
3. Read-only dashboard news cards and category/person filters.
4. Preview-only CI, Android testing, security review.
