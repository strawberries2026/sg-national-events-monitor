"""Regression checks for presentation mode's safe, read-only contract."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "presentation.html").read_text(encoding="utf-8")
DATA = json.loads((ROOT / "data/verified-events.json").read_text(encoding="utf-8"))

class PresentationModeTests(unittest.TestCase):
    def test_separate_page_and_return_link(self):
        self.assertIn('href="./index.html"', HTML)
        self.assertIn("PRESENTATION VIEW", HTML)

    def test_verified_only_and_no_fabricated_archive(self):
        self.assertIn("e.verification_status==='verified'", HTML)
        self.assertIn("No historical verified records are retained", HTML)
        self.assertNotIn("sampleEvent", HTML)

    def test_all_filters_exist(self):
        for value in ("all", "upcoming", "ongoing", "past"):
            self.assertIn('data-filter="'+value+'"', HTML)

    def test_source_link_safety(self):
        self.assertIn("parsed.protocol==='https:'", HTML)
        self.assertIn("noopener noreferrer", HTML)

    def test_official_source_and_disclaimer(self):
        self.assertIn("Official announcements remain authoritative", HTML)
        self.assertIn("not operational decision-making", HTML)

    def test_verified_dataset_shape(self):
        self.assertIsInstance(DATA.get("events"), list)
        self.assertTrue(any(e.get("verification_status")=="verified" for e in DATA["events"]))

if __name__ == "__main__":
    unittest.main()
