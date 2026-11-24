from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
base={"verification_status":"verified","start":"2020-01-01","end":"2020-01-02","source":"https://www.pmo.gov.sg/test","title":"Verified fixture","lifecycle_status":"completed"}
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={"width":360,"height":640})
    page.route("**/data/verified-events.json*",lambda r:r.fulfill(json={"events":[base]}))
    page.route("**/data/event-history.json*",lambda r:r.fulfill(json={"events":[base,{**base,"source":"https://www.pmo.gov.sg/second","title":"Archive only"},{**base,"source":"https://www.pmo.gov.sg/candidate","title":"Excluded candidate","verification_status":"candidate_unverified"}]}))
    page.goto((ROOT/'presentation.html').as_uri())
    page.get_by_role("button",name="Historical archive").click()
    page.get_by_text("Archive only",exact=True).wait_for()
    assert page.locator("#events article").count()==2
    assert page.get_by_text("Excluded candidate",exact=True).count()==0
    browser.close()
