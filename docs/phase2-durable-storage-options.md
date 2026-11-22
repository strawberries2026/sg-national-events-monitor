# Phase 2 — zero-cost durable request-budget storage decision

**Decision status:** candidate evaluation only. No provider, repository workflow, or external news feed has been enabled.

| Candidate | Benefits | Limitations / risks | Decision |
| --- | --- | --- | --- |
| GitHub Actions artifact | No additional provider; good for offline previews and CI diagnostics | Artifacts are not an atomic mutable database; retrieving latest state and concurrent updates are unsafe without a coordination mechanism | Do not use as authoritative budget |
| GitHub repository state file on a dedicated branch | Uses existing infrastructure; Git commits have optimistic concurrency checks | Public repository exposes the state; permissions and write-token scope need review; conflicting writes and stale clones must be handled | Potential prototype, not approved |
| Existing free-tier external key-value or database service | Can provide durable state and possibly atomic conditional writes | Provider-specific limits, credentials, egress, account administration and billing policy need verification | Evaluate only if truly free and atomic |
| Runner-local JSON | Already tested; easy to inspect | Disappears when a runner ends | Development tests only |

## Required contract

- Persist **per-source**, **Singapore-day** used count and last-attempt timestamp.
- On each attempt, perform a **single atomic compare-and-swap** reservation before any network call. A conflict must trigger reload and bounded retry; after repeated conflicts, skip fetching.
- Do not silently initialize a missing ledger during normal scheduled runs; initial provisioning is a separate, explicit action.
- Count timeouts, failed responses and retries as consumed attempts.
- Restrict writes to the intended state location; no write permission for external feed adapters.
- Keep data minimal: no credentials, personal information, full article bodies or operational data.
- A collector must not start if storage is unavailable, malformed, out of quota or cannot guarantee atomic writes.
- Verify concurrent jobs and persistence between runners with integration tests before production enablement.

## Deployment boundary

No changes to production `main`, existing scheduled event refreshes, Pages hosting, Android PWA, or repository access controls. Keep all external sources disabled until a backend is selected, verified and approved.
