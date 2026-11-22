# Phase 2 news feed permissions assessment (2026-11-22)

## CNA
- CNA publishes official RSS endpoints at https://www.channelnewsasia.com/rss .
- Singapore category endpoint: https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416 .
- Terms: https://www.channelnewsasia.com/rss/rssterms .
- **Decision: do not ingest, redistribute, cache, or embed this feed in the public/shared SG National Events Monitor without permission.** CNA describes RSS as for personal, non-commercial use and restricts transfer/distribution to third parties. A shared monitoring app is not clearly authorized. Keep registry entry disabled.
- Safe interim experience: source-directory link to CNA's website; readers open CNA directly.

## Official government sources
- Existing curated official-announcement dataset remains the only integrated Phase 2 source.
- NEA publicly documents RSS News Release and Upcoming Events endpoints at https://www.nea.gov.sg/rss/rss-feeds ; assess relevance, data format, operational availability, and usage conditions before enabling.
- Validate source dates as publication dates, not confirmed event dates. Preserve source links and distinguish reporting from verified calendar events.

## Release controls
- Do not enable any external feed merely because its endpoint is publicly accessible.
- Require verified permitted usage, freshness checks, safe rendering, deduplication, attribution, and Android PWA checks.
- No production merge or deployment under this assessment.
