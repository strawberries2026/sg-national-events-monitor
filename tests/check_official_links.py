from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={"width":360,"height":740},has_touch=True,is_mobile=True)
        page.context.route("https://**/*",lambda r:r.fulfill(status=200,body="External destination test"))
        page.goto(f"http://127.0.0.1:{server.server_port}/index.html")
        page.locator("#visits-details").evaluate("(e)=>e.open=true")
        links=[("visit-pmo-link","https://www.pmo.gov.sg/newsroom/"),("visit-istana-link","https://www.istana.gov.sg/newsroom/")]
        for id,url in links:
            link=page.locator("#"+id)
            assert link.get_attribute("href")==url
            assert link.get_attribute("target")=="_blank"
            assert "noopener" in link.get_attribute("rel")
            link.scroll_into_view_if_needed()
            with page.expect_popup() as popup:
                link.tap()
            child=popup.value
            child.wait_for_load_state()
            assert child.url==url, child.url
            child.close()
        assert page.locator("#visit-pmo-link").bounding_box()["height"]>=44
        assert page.locator("#visit-istana-link").bounding_box()["height"]>=44
        browser.close()
finally:
    server.shutdown()
