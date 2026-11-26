import pathlib, re, subprocess, unittest

class DashboardURLSecurity(unittest.TestCase):
    def test_url_validator(self):
        source = pathlib.Path('index.html').read_text()
        helper = re.search(r"const safeOfficialUrl=.*?catch\{return '';\}\};", source).group(0)
        script = helper + """
const assert = require('node:assert/strict');
for(const value of ['javascript:alert(1)','data:text/html,x','http://example.com','//example.com','https://user:pass@example.com','',null]) assert.equal(safeOfficialUrl(value),'');
for(const value of ['https://www.pmo.gov.sg/newsroom/','https://www.istana.gov.sg/newsroom/']) assert.equal(safeOfficialUrl(value),value);
"""
        subprocess.run(['node','-e',script],check=True)
    def test_dynamic_href_guards(self):
        source = pathlib.Path('index.html').read_text()
        self.assertNotRegex(source, r"""href="'\+esc\((?!safeOfficialUrl\()""")
        self.assertIn("a.href=safeOfficialUrl(x.source)",source)
        self.assertIn("link.href=safeOfficialUrl(record.source)",source)
