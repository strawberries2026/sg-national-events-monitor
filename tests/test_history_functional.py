"""Functional archive regression using isolated temporary datasets."""
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("collector_under_test", ROOT / "scripts" / "collect_verified_events.py")
COLLECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COLLECTOR)

class ArchiveFunctionalTests(unittest.TestCase):
    def test_verified_completed_retained_candidates_excluded_active_not_archived(self):
        today = (datetime.now(timezone.utc) + timedelta(hours=8)).date()
        past = (today - timedelta(days=5)).isoformat()
        future = (today + timedelta(days=5)).isoformat()
        def record(source, status, end):
            return {"source": "https://www.pmo.gov.sg/newsroom/" + source,
                    "title": source, "type": "VIP visit", "start": end,
                    "end": end, "verification_status": status,
                    "agency": "PMO"}
        completed = record("verified-completed", "verified", past)
        candidate = record("unverified-completed", "candidate_unverified", past)
        active = record("verified-active", "verified", future)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "events.json").write_text(json.dumps({"events": []}), encoding="utf-8")
            (folder / "verified.json").write_text(json.dumps({"events": [completed, candidate, active]}), encoding="utf-8")
            (folder / "history.json").write_text(json.dumps({"events": [candidate, active]}), encoding="utf-8")
            with patch.object(COLLECTOR, "SOURCE", folder / "events.json"), \
                 patch.object(COLLECTOR, "TARGET", folder / "verified.json"), \
                 patch.object(COLLECTOR, "HISTORY", folder / "history.json"):
                COLLECTOR.main()
            archive = json.loads((folder / "history.json").read_text(encoding="utf-8"))["events"]
            current = json.loads((folder / "verified.json").read_text(encoding="utf-8"))["events"]
            self.assertEqual([e["source"] for e in archive], [completed["source"]])
            self.assertEqual(archive[0]["lifecycle_status"], "completed")
            self.assertEqual([e["source"] for e in current], [active["source"]])
            self.assertEqual(current[0]["verification_status"], "verified")

if __name__ == "__main__":
    unittest.main()
