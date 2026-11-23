import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collect_leadership_visits import build

class LeadershipDiscoveryTests(unittest.TestCase):
    def test_official_visit_is_queued_not_verified(self):
        feed = {"updated_at": "2026-11-23T00:00:00Z", "events": [
            {"agency": "PMO", "title": "PM Lawrence Wong to Visit Australia", "source_url": "https://www.pmo.gov.sg/newsroom/visit", "published_date": "2026-11-22"},
            {"agency": "MHA", "title": "PM Lawrence Wong to Visit Australia", "source_url": "https://www.mha.gov.sg/newsroom/visit"},
        ]}
        result = build(feed, {})
        self.assertEqual(len(result["candidates"]), 1)
        self.assertFalse(result["candidates"][0]["date_verified"])
        self.assertEqual(result["candidates"][0]["status"], "needs_official_date_and_identity_review")

    def test_first_detection_is_preserved(self):
        url = "https://www.istana.gov.sg/newsroom/visit"
        feed = {"events": [{"agency": "Istana", "title": "President Tharman to Visit Australia", "source_url": url}]}
        prior = {"candidates": [{"source_url": url, "first_detected_at": "2026-11-22T00:00:00Z"}]}
        result = build(feed, prior)
        self.assertEqual(result["candidates"][0]["first_detected_at"], "2026-11-22T00:00:00Z")

if __name__ == "__main__":
    unittest.main()
