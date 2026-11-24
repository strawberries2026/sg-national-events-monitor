from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width,height in [(360,640),(393,740),(412,915)]:
        page=browser.new_page(viewport={"width":width,"height":height},is_mobile=True,has_touch=True)
        page.goto((ROOT/'index.html').as_uri(),wait_until='domcontentloaded')
        link=page.locator('#verified-history-link')
        nav=page.locator('.bottom-nav').first
        assert link.is_visible() and nav.is_visible()
        assert link.evaluate("(e)=>getComputedStyle(e).position")=='static'
        link.scroll_into_view_if_needed()
        a,b=link.bounding_box(),nav.bounding_box()
        assert a and b and a['y']+a['height']<=b['y'], (width,a,b)
        assert a['x']>=0 and a['x']+a['width']<=width+1
        page.close()
    browser.close()
