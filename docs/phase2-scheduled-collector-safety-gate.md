# Phase 2 — scheduled collector safety gate

**Status:** design gate only; no external collector is enabled or scheduled.

The local JSON budget ledger passes serialization tests, but GitHub-hosted runners have ephemeral filesystems. A JSON file in a runner is **not** durable storage between scheduled jobs. The collector must not be activated until a persistent, concurrency-safe store is selected and verified.

## Required before enablement

1. **Durable ledger:** Load the prior day's per-source request usage from a persistent store. Missing state on first-ever initialization must be an explicit administrator action; missing or corrupt state on later runs must stop fetching (fail closed).
2. **Single writer:** Prevent overlapping refresh runs, and use optimistic concurrency/version checks when updating the ledger. GitHub Actions `concurrency` can reduce overlap, but it does not make a separate storage backend transactional.
3. **Count before fetch:** Reserve the request budget durably before any network request. Timeouts and HTTP errors consume a request; a retry requires another budget reservation.
4. **Provider limits:** Respect 429 responses and Retry-After, and enforce whichever cap is lower: the configured cap or the provider's published limits.
5. **Cache:** Deduplicate by canonical HTTPS URL/source ID, avoid storing full copyrighted articles, and retain only metadata permitted by source terms.
6. **Recovery:** Keep the existing verified-event calendar usable if collection fails. Display last-success time and a clear stale/failed state.
7. **Verification:** Test two simultaneous runs, persistence after runner restart, SGT midnight rollover, corrupt ledger, 429/backoff, and zero requests from disabled sources.

## Zero-cost rollout

Do not add a paid database or a new scheduled job for this design phase. Evaluate a repository-backed state file or an existing free-tier storage service only after considering commit conflicts, token permissions, data integrity and public visibility. Do not write live counters to `main` or modify existing production workflows before approval.

**Decision:** External feed ingestion stays disabled until the durable store and concurrency gates pass CI and Android preview testing.
