import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/'history.html').read_text(encoding='utf-8')
INDEX=(ROOT/'index.html').read_text(encoding='utf-8')
class HistoryUITests(unittest.TestCase):
    def test_linked_from_dashboard(self):
        self.assertIn("./history.html",INDEX)
    def test_verified_only(self):
        self.assertIn("e.verification_status==='verified'",PAGE)
        self.assertIn("e.lifecycle_status==='completed'",PAGE)
    def test_source_links_and_safe_text(self):
        self.assertIn("noopener noreferrer",PAGE)
        self.assertIn("textContent=e.title",PAGE)
    def test_no_fake_history(self):
        self.assertIn("No completed verified events",PAGE)
        self.assertIn("data/event-history.json",PAGE)
if __name__=='__main__':unittest.main()
