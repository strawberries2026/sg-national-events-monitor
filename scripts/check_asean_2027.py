"""Read-only health check for the official MFA ASEAN 2027 planning notice.
Do not infer confirmed meeting dates from forecast months or arbitrary article text.
"""
import json
import re
from html import unescape
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://www.mfa.gov.sg/newsroom/announcements-and-highlights/invitation-for-proposals-for-sponsorship-of-food-and-drinks--furniture--audio-visual-equipment--event-tokens-and-medical-services-for-high-level-meetings-and-conferences-in-2027/"
OUT = Path("data/asean-2027-health.json")
def main():
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "source_status": "unavailable",
        "schedule_status": "forecast_only",
        "confirmed_exact_dates": [],
        "last_success_at": old.get("last_success_at"),
        "last_reachable_at": old.get("last_reachable_at"),
        "note": "MFA planning periods are forecasts, not confirmed dates. Automated retrieval does not verify new dates."
    }
    try:
        request = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (compatible; SGNationalEventsMonitor/1.0)"})
        with urllib.request.urlopen(request, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            body = response.read(500000).decode("utf-8", "replace")
        result["last_reachable_at"] = result["checked_at"]
        if "html" not in content_type:
            result["source_status"] = "unexpected_content_type"
        else:
            # Normalize markup and entities; do not infer exact event dates.
            without_scripts = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", body, flags=re.I | re.S)
            plain = unescape(re.sub(r"<[^>]+>", " ", without_scripts))
            plain = " ".join(plain.lower().split())
            # MFA renders ordinal suffixes as superscripts: 50 th / 51 st.
            plain = re.sub(r"\b(50|51)\s+(th|st)\b", r"\1\2", plain)
            has_year = "2027" in plain
            has_schedule = ("asean" in plain and "summit" in plain and
                            ("50th" in plain or "fiftieth" in plain) and
                            ("51st" in plain or "fifty-first" in plain))
            result["content_signals"] = {"year_2027": has_year, "asean": "asean" in plain, "summit": "summit" in plain, "50th": "50th" in plain, "51st": "51st" in plain}
            if has_year and has_schedule:
                result["source_status"] = "schedule_recognized"
                result["last_success_at"] = result["checked_at"]
            else:
                result["source_status"] = "content_unrecognized"
    except Exception as error:
        result["error"] = type(error).__name__
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("ASEAN 2027 official source:", result["source_status"])
if __name__ == "__main__":
    main()
