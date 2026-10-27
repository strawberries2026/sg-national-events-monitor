"""Conservative future-event extraction from official announcement titles.

Never infer an event date from an article's publication date.
"""
import json
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCE = Path("data/events.json")
TARGET = Path("data/verified-events.json")
PATTERN = re.compile(r"(?<!\d)(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})(?!\d)", re.I)
EVENT_TERMS = {
    "VIP visit": ("official visit", "state visit", "working visit", "visit by", "visiting"),
    "International summit": ("summit", "ministerial meeting", "leaders' meeting"),
    "National event": ("national day parade", "national day rally", "state ceremony"),
    "Major public event": ("grand prix", "fintech festival", "international conference"),
}
class ArticleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "footer"):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer") and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

def official_article(url):
    parsed = urlparse(url)
    hosts = ("mha.gov.sg", "mof.gov.sg", "mfa.gov.sg", "mindef.gov.sg",
             "meti.gov.sg", "pmo.gov.sg", "istana.gov.sg")
    if parsed.scheme != "https" or not any(parsed.hostname == h or parsed.hostname == "www." + h for h in hosts):
        return ""
    request = urllib.request.Request(url, headers={"User-Agent": "SGNationalEventsMonitor/1.0"})
    with urllib.request.urlopen(request, timeout=8) as response:
        if "text/html" not in response.headers.get("Content-Type", ""):
            return ""
        page = response.read(500000).decode("utf-8", "replace")
    parser = ArticleText()
    parser.feed(page)
    return " ".join(" ".join(parser.parts).split())[:20000]

def main():
    feed = json.loads(SOURCE.read_text(encoding="utf-8"))
    today = (datetime.now(timezone.utc) + timedelta(hours=8)).date()
    output = []
    inspected = 0
    failures = 0
    for record in feed.get("events", []):
        title = record.get("title", "")
        lower = title.lower()
        kind = next((kind for kind, terms in EVENT_TERMS.items() if any(t in lower for t in terms)), None)
        if not kind or record.get("type") == "Official reference":
            continue
        url = record.get("source_url", "")
        if not url.startswith("https://"):
            continue
        article_text = title
        if inspected < 12:
            inspected += 1
            try:
                article_text += " " + official_article(url)
            except Exception:
                failures += 1
        dates = []
        for day, month, year in PATTERN.findall(article_text):
            try:
                from datetime import datetime as dt
                dates.append(dt.strptime(f"{day} {month} {year}", "%d %B %Y").date())
            except ValueError:
                pass
        # Candidate dates from article text require human verification.
        future = sorted({d for d in dates if today <= d <= today + timedelta(days=365)})
        if not future:
            continue
        output.append({
            "title": title, "type": kind, "start": future[0].isoformat(),
            "end": future[-1].isoformat(), "venue": "Not confirmed",
            "source": url, "date_evidence": "Date in official headline or article; event relationship unverified",
            "verification_status": "candidate_unverified",
            "agency": record.get("agency", "")
        })
    unique = {e["source"]: e for e in output}
    result = {"updated_at": datetime.now(timezone.utc).isoformat(),
              "events": list(unique.values()),
              "note": "Candidate dates extracted from official headlines; verify original article before operational use."}
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Saved", len(unique), "unverified event candidates; inspected", inspected, "fetch failures", failures)
if __name__ == "__main__":
    main()
