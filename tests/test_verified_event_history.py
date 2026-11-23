"""Safety checks for verified-event archive retention."""
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "scripts/collect_verified_events.py").read_text(encoding="utf-8")

class HistorySafetyTests(unittest.TestCase):
    def test_existing_history_requires_verification(self):
        self.assertIn('e.get("verification_status") == "verified"', SOURCE)
    def test_only_verified_previous_events_archived(self):
        self.assertIn('if e.get("verification_status") == "verified" and e.get("end", "") < today.isoformat():', SOURCE)
    def test_no_duplicate_active_archive(self):
        self.assertIn('archived.pop(source, None)', SOURCE)
    def test_candidate_never_auto_promoted(self):
        self.assertIn('"verification_status": "candidate_unverified"', SOURCE)
        self.assertIn('Never silently upgrade a candidate to verified', SOURCE)

if __name__ == "__main__":
    unittest.main()
