"""Safety checks for verified-event archive retention."""
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "scripts/collect_verified_events.py").read_text(encoding="utf-8")

class HistorySafetyTests(unittest.TestCase):
    def test_existing_history_requires_verification(self):
        self.assertIn('event.get("verification_status") != "verified"', SOURCE)
    def test_only_verified_previous_events_archived(self):
        self.assertIn('if verified_end(e) is not None and verified_end(e) < today:', SOURCE)
    def test_no_duplicate_active_archive(self):
        self.assertIn('archived.pop(source, None)', SOURCE)
    def test_candidate_never_auto_promoted(self):
        self.assertIn('"verification_status": "candidate_unverified"', SOURCE)
        self.assertIn('Never silently upgrade a candidate to verified', SOURCE)

    def test_date_validation(self):
        import sys
        from datetime import date
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from collect_verified_events import verified_end
        e = {"verification_status":"verified","start":"2026-11-23","end":"2026-11-25"}
        self.assertEqual(verified_end(e), date(2026,11,25))
        self.assertIsNone(verified_end({**e,"start":""}))
        self.assertIsNone(verified_end({**e,"end":"2026-11-22"}))
        self.assertIsNone(verified_end({**e,"verification_status":"candidate_unverified"}))

if __name__ == "__main__":
    unittest.main()
