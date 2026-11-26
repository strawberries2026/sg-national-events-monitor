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

        for category in ("Leadership","Ministries","Parliament","Events"):
            page.goto((ROOT/'index.html').as_uri(),wait_until='domcontentloaded')
            page.locator('#search').evaluate("(e)=>e.value='no-match'")
            page.locator('#date-from').evaluate("(e)=>e.value='2099-01-01'")
            page.locator('#date-to').evaluate("(e)=>e.value='2099-01-02'")
            for flag in ('watch-only','new-only'):
                page.locator('#'+flag).evaluate("(e)=>e.checked=true")
            card=page.locator('.navcard[data-category="'+category+'"]')
            card.tap()
            page.wait_for_function("location.hash === '#calendar' && document.querySelector('#calendar').classList.contains('mobile-active')")
            assert page.locator('#calendar').is_visible(), (width,category)
            assert page.locator('#category').input_value()==category
            for field in ('agency','person','search','date-from','date-to'):
                assert page.locator('#'+field).input_value()=='', (category,field)
            for flag in ('watch-only','new-only'):
                assert not page.locator('#'+flag).is_checked()
            page.wait_for_function("document.activeElement === document.querySelector('#calendar h2')")
            assert page.locator('#matches').inner_text().startswith('Showing ')
            assert page.locator('#events').inner_text().strip()
        page.close()
    browser.close()
