"""Monitor official national-event landing pages for review, never auto-verify dates."""
import json
import re
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

TARGET = Path("data/national-event-source-health.json")
SOURCES = [
    ("Singapore Grand Prix (F1)", "https://singaporegp.sg/en/", ("grand prix", "2027")),
    ("Marina Bay year-end countdown", "https://www.marinabaycountdown.gov.sg/", ("countdown",)),
    ("National Day celebrations", "https://www.ndp.gov.sg/", ("national day",)),
    ("Chingay Parade", "https://www.chingay.gov.sg/", ("chingay",)),
    ("Shangri-La Dialogue", "https://www.iiss.org/events/iiss-shangri-la-dialogue/", ("shangri-la",)),
    ("Major international summits", "https://www.mfa.gov.sg/", ("summit",)),
]
class VisibleText(HTMLParser):
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
def check(name, url, terms):
    result = {"event": name, "source": url, "status": "unavailable",
              "date_verification": "not_performed", "review_required": True}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SGNationalEventsMonitor/4.8"})
        with urllib.request.urlopen(req, timeout=12) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type.lower():
                result["status"] = "unexpected_content_type"
                return result
            raw = response.read(300000).decode("utf-8", "replace")
        parser = VisibleText()
        parser.feed(raw)
        visible = re.sub(r"\s+", " ", " ".join(parser.parts)).lower()
        result["status"] = "source_reachable" if any(t in visible for t in terms) else "content_unrecognized"
    except Exception as exc:
        result["error_type"] = type(exc).__name__
    return result
def main():
    now = datetime.now(timezone.utc).isoformat()
    results = [check(*source) for source in SOURCES]
    payload = {"checked_at": now, "sources": results,
               "note": "Source availability and keyword recognition only. No dates are automatically verified or published."}
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("National event sources:", len(results), "checked;",
          sum(x["status"] == "source_reachable" for x in results), "recognized")
if __name__ == "__main__":
    main()
