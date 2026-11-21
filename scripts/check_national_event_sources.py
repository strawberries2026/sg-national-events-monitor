"""Monitor official national-event landing pages for review, never auto-verify dates."""
import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

TARGET = Path("data/national-event-source-health.json")
SOURCES = [
    ("Singapore Grand Prix (F1)", "https://singaporegp.sg/en/", ("grand prix", "2027")),
    ("Marina Bay year-end countdown", "https://www.ura.gov.sg/", ("countdown", "marina bay")),
    ("National Day celebrations", "https://www.ndp.gov.sg/", ("national day",)),
    ("Chingay Parade", "https://www.chingay.gov.sg/", ("chingay",)),
    ("Shangri-La Dialogue", "https://www.iiss.org/events/shangri-la-dialogue/shangri-la-dialogue-2027/", ("shangri-la",)),
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
def fetch_visible(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; SGNationalEventsMonitor/4.9; public-source-check)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=12) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type.lower():
            return None
        raw = response.read(300000).decode("utf-8", "replace")
    parser = VisibleText()
    parser.feed(raw)
    return re.sub(r"\\s+", " ", " ".join(parser.parts)).lower()

def check(name, url, terms):
    result = {"event": name, "source": url, "status": "unavailable",
              "date_verification": "not_performed", "review_required": True}
    urls = [url]
    if name == "Marina Bay year-end countdown":
        # URA is the preferred organiser reference; the dedicated countdown
        # site is a secondary source only. Neither confirms an event date.
        urls.append("https://www.marinabaycountdown.gov.sg/")
    if name == "Shangri-La Dialogue":
        # All fallback pages belong to the official IISS site. A successful
        # request still only recognises the source, never verifies a date.
        urls.extend([
            "https://www.iiss.org/events/",
            "https://www.iiss.org/iiss-asia/",
        ])
    attempts = []
    for candidate in urls:
        attempt = {"url": candidate}
        try:
            visible = fetch_visible(candidate)
            if visible is None:
                attempt["outcome"] = "unexpected_content_type"
            elif any(t in visible for t in terms):
                attempt["outcome"] = "recognized"
                attempts.append(attempt)
                result["status"] = "source_reachable"
                result["checked_source"] = candidate
                result["attempts"] = attempts
                if candidate != url:
                    result["access_note"] = (
                        "Recognised via secondary countdown website; URA remains "
                        "the preferred organiser reference. Event dates are not verified."
                        if name == "Marina Bay year-end countdown" else
                        "Recognised via alternate official IISS page; "
                        "primary page may restrict automated access. "
                        "Event dates are not verified by this check."
                    )
                return result
            else:
                attempt["outcome"] = "content_unrecognized"
        except urllib.error.HTTPError as exc:
            attempt["outcome"] = (
                "access_restricted" if exc.code in (401, 403, 429)
                else "http_error"
            )
            attempt["http_status"] = exc.code
        except Exception as exc:
            attempt["outcome"] = "connection_error"
            attempt["error_type"] = type(exc).__name__
        attempts.append(attempt)

    result["attempts"] = attempts
    outcomes = {attempt["outcome"] for attempt in attempts}
    result["status"] = (
        "access_restricted" if "access_restricted" in outcomes
        else "content_unrecognized" if "content_unrecognized" in outcomes
        else "unavailable"
    )
    result["access_note"] = (
        "Official pages were attempted but automated access was restricted; "
        "event dates remain unverified."
        if result["status"] == "access_restricted"
        else "Official page accessible but expected event name not recognised."
        if result["status"] == "content_unrecognized"
        else "Official pages could not be retrieved; event dates remain unverified."
    )
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
