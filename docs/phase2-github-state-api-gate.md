# Phase 2 — GitHub Contents API state-store feasibility gate

**Status:** API design review only; no GitHub state branch, token, or live writer is created.

GitHub's repository contents update endpoint accepts the **current file blob SHA**. When the stored file has changed, a stale update can be rejected (commonly HTTP 409). This is a useful optimistic concurrency mechanism, but the prototype must verify real API behavior before relying on it for request-budget enforcement.

## Proposed adapter contract

1. Read the budget ledger from a dedicated state branch with the Contents API. Capture the returned blob SHA and decode/validate the JSON.
2. On reservation, submit the complete updated ledger with the previously observed SHA. Never perform an unconditional overwrite.
3. On a conflict, fetch fresh state and retry only a bounded number of times; do not fetch the external source until the state reservation is confirmed.
4. If GitHub is unavailable, the branch/file is missing, authentication fails, state is invalid, or conflicts persist: **skip the external fetch**.
5. The GitHub write token should have minimum necessary permissions and should never appear in browser JavaScript, Pages output, preview artifacts or logs.
6. A state branch is not secret storage. Public repositories may expose the state file and its history.
7. Never use this state adapter to modify `main` or interfere with the existing official-event refresh workflow.

## Important limitations

- A file-SHA check is **not** a proven distributed transaction guarantee until tested with actual competing API calls.
- Two requests can also conflict with other writers or branch updates; retry logic must be bounded and idempotent.
- The public repository's rate limits, abuse protections, and storage semantics must be reviewed.
- The earlier in-memory tests do **not** validate token scopes, network failures, GitHub API response formats, or cross-run persistence.

## Acceptance criteria before activation

- Two independent runners racing to reserve a final allowance result in exactly one successful reservation.
- Re-run after a fresh runner starts sees the same persisted usage.
- Missing or malformed state, stale SHA, 401/403/404, 409 and 5xx cases fail closed.
- Disabled sources never initiate HTTP requests.
- Existing Android PWA and event refreshes remain unaffected.
- Explicit deployment approval is obtained before any live collector is enabled.

No additional paid services or automatic schedule changes are authorized by this document.
