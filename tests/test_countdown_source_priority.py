"""Offline regression checks for countdown source priority and date safeguards."""
import importlib.util
import unittest
from unittest.mock import patch
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "national_sources", Path("scripts/check_national_event_sources.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CountdownSourceTests(unittest.TestCase):
    def test_ura_first_then_media_then_countdown_fallback(self):
        attempted = []
        def fetch(url):
            attempted.append(url)
            return "unrelated content" if "marinabaycountdown.gov.sg" not in url else "countdown"
        with patch.object(module, "fetch_visible", side_effect=fetch):
            result = module.check("Marina Bay year-end countdown", "https://www.ura.gov.sg/", ("countdown", "marina bay"))
        self.assertEqual(attempted, [
            "https://www.ura.gov.sg/",
            "https://www.ura.gov.sg/Corporate/Media-Room/Media-Releases",
            "https://www.marinabaycountdown.gov.sg/",
        ])
        self.assertEqual(result["status"], "source_reachable")
        self.assertEqual(result["date_verification"], "not_performed")
        self.assertTrue(result["review_required"])

    def test_historical_content_never_verifies_future_date(self):
        with patch.object(module, "fetch_visible", return_value="Marina Bay Countdown 2026 31 December 2025"):
            result = module.check("Marina Bay year-end countdown", "https://www.ura.gov.sg/", ("countdown", "marina bay"))
        self.assertEqual(result["date_verification"], "not_performed")
        self.assertNotIn("verified_date", result)
        self.assertTrue(result["review_required"])

    def test_unrecognized_pages_remain_unverified(self):
        with patch.object(module, "fetch_visible", return_value="unrelated content"):
            result = module.check("Marina Bay year-end countdown", "https://www.ura.gov.sg/", ("countdown", "marina bay"))
        self.assertEqual(result["status"], "content_unrecognized")
        self.assertEqual(result["date_verification"], "not_performed")

if __name__ == "__main__":
    unittest.main()
