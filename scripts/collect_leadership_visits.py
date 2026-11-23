"""Track newly collected official leadership-visit announcements for review.

Discovery is not event-date verification. No unreviewed candidate is promoted.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from collect_verified_events import leadership_visit_candidate

FEED = Path("data/events.json")
OUTPUT = Path("data/leadership-visit-discovery.json")

def build(feed, previous):
    now = datetime.now(timezone.utc).isoformat()
    old = {item["source_url"]: item for item in previous.get("candidates", [])}
    candidates = []
    for record in feed.get("events", []):
        if not leadership_visit_candidate(record):
            continue
        url = record.get("source_url", "")
        if not url.startswith("https://"):
            continue
        prior = old.get(url, {})
        candidates.append({
            "title": record.get("title", ""),
            "agency": record.get("agency", ""),
            "source_url": url,
            "published_date": record.get("published_date"),
            "first_detected_at": prior.get("first_detected_at", now),
            "last_detected_at": now,
            "status": "needs_official_date_and_identity_review",
            "date_verified": False,
        })
    return {
        "updated_at": now,
        "source_snapshot_at": feed.get("updated_at"),
        "collection_errors": feed.get("errors", []),
        "candidates": candidates,
        "note": "Discovery only. Verify leader, destination, event dates and original official source before display as confirmed."
    }

def main():
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    previous = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    result = build(feed, previous)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Leadership visit discovery:", len(result["candidates"]), "candidates requiring review")

if __name__ == "__main__":
    main()
