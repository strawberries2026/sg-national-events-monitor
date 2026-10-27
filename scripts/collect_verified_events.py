"""Conservative future-event extraction from official announcement titles.

Never infer an event date from an article's publication date.
"""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCE = Path("data/events.json")
TARGET = Path("data/verified-events.json")
PATTERN = re.compile(r"(?<!\\d)(\\d{1,2})\\s+(January|February|March|April|May|June|July|August|September|October|November|December)\\s+(20\\d{2})(?!\\d)", re.I)
EVENT_TERMS = {
    "VIP visit": ("official visit", "state visit", "working visit", "visit by", "visiting"),
    "International summit": ("summit", "ministerial meeting", "leaders' meeting"),
    "National event": ("national day parade", "national day rally", "state ceremony"),
    "Major public event": ("grand prix", "fintech festival", "international conference"),
}
def main():
    feed = json.loads(SOURCE.read_text(encoding="utf-8"))
    today = (datetime.now(timezone.utc) + timedelta(hours=8)).date()
    output = []
    for record in feed.get("events", []):
        title = record.get("title", "")
        lower = title.lower()
        kind = next((kind for kind, terms in EVENT_TERMS.items() if any(t in lower for t in terms)), None)
        if not kind or record.get("type") == "Official reference":
            continue
        dates = []
        for day, month, year in PATTERN.findall(title):
            try:
                from datetime import datetime as dt
                dates.append(dt.strptime(f"{day} {month} {year}", "%d %B %Y").date())
            except ValueError:
                pass
        # Strictly require an explicit future date in the headline itself.
        future = sorted({d for d in dates if today <= d <= today + timedelta(days=365)})
        if not future:
            continue
        url = record.get("source_url", "")
        if not url.startswith("https://"):
            continue
        output.append({
            "title": title, "type": kind, "start": future[0].isoformat(),
            "end": future[-1].isoformat(), "venue": "Not confirmed",
            "source": url, "date_evidence": "Explicit date in official announcement headline",
            "agency": record.get("agency", "")
        })
    unique = {e["source"]: e for e in output}
    result = {"updated_at": datetime.now(timezone.utc).isoformat(),
              "events": list(unique.values()),
              "note": "Candidate dates extracted from official headlines; verify original article before operational use."}
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Saved", len(unique), "dated event candidates")
if __name__ == "__main__":
    main()
