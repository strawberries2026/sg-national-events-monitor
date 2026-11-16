"""Create an unverified review queue from collected official ASEAN 2027 announcements.
Never promote scraped dates to confirmed dates.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SOURCE = Path("data/events.json")
OUT = Path("data/asean-2027-review.json")
KEYWORDS = re.compile(r"\\basean\\b|50th\\s+asean|51st\\s+asean", re.I)
YEAR = re.compile(r"\\b2027\\b|\\b50th\\s+asean\\b|\\b51st\\s+asean\\b", re.I)
DATES = re.compile(r"\\b\\d{1,2}\\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\\s+2027\\b", re.I)
HOSTS = {"mfa.gov.sg", "www.mfa.gov.sg", "pmo.gov.sg", "www.pmo.gov.sg", "istana.gov.sg", "www.istana.gov.sg"}
def main():
    feed = json.loads(SOURCE.read_text(encoding="utf-8"))
    candidates = {}
    for event in feed.get("events", []):
        title = event.get("title", "")
        url = event.get("source_url", "")
        host = urlparse(url).hostname
        if event.get("agency") not in ("MFA", "PMO", "Istana") or host not in HOSTS:
            continue
        if not KEYWORDS.search(title) or not YEAR.search(title):
            continue
        candidates[url] = {
            "title": title,
            "agency": event.get("agency"),
            "source": url,
            "published_date": event.get("published_date"),
            "date_mentions_in_title": sorted(set(DATES.findall(title))),
            "verification_status": "candidate_unverified",
            "review_required": True,
            "note": "Headline discovery only. Check the primary announcement for the exact event, date, venue and whether it supersedes the forecast."
        }
    result = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "review_queue_only",
        "candidate_count": len(candidates),
        "candidates": list(candidates.values())[:30],
        "note": "No candidate is automatically confirmed or published as a verified summit date."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ASEAN 2027 review candidates:", len(candidates))
if __name__ == "__main__":
    main()
