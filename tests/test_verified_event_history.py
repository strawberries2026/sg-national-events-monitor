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

    def test_reviewed_visit_dates_not_publication_dates(self):
        import json
        root = Path(__file__).resolve().parents[1]
        records = json.loads((root / "data/event-history.json").read_text(encoding="utf-8"))["events"]
        for marker, publication, start, end in (
            ("working-visit-by-president-tharman-shanmugaratnam-to-the-kingdom-of-thailand-on-12-october-2026", "2026-10-11", "2026-10-12", "2026-10-12"),
            ("/23nov26-nr/", "2026-11-23", "2026-11-24", "2026-11-25"),
        ):
            matches = [e for e in records if marker in e.get("source", "")]
            self.assertEqual(len(matches), 1)
            e = matches[0]
            self.assertEqual((e["published_date"], e["start"], e["end"]), (publication, start, end))
            self.assertEqual(e["verification_status"], "verified")
            self.assertEqual(e["lifecycle_status"], "completed")
            self.assertTrue(e["verified_source"].startswith("https://"))
            self.assertTrue(e["date_evidence"])

if __name__ == "__main__":
    unittest.main()
