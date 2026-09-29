import sys, json, pathlib
from playwright.sync_api import sync_playwright

JS = """
() => {
  const cs = (el, p) => getComputedStyle(el)[p];
  const b = document.body;
  const sections = [...document.querySelectorAll('header,nav,section,footer,main > div')].slice(0, 25).map(el => ({
    tag: el.tagName.toLowerCase(), text: el.innerText.trim().slice(0, 400),
    bg: cs(el,'backgroundColor'), color: cs(el,'color'),
    padding: cs(el,'padding'), height: Math.round(el.getBoundingClientRect().height)}));
  const links = [...document.querySelectorAll('nav a, header a')].slice(0, 15)
    .map(a => ({text: a.innerText.trim(), href: a.getAttribute('href')}));
  const images = [...document.images].slice(0, 20)
    .map(i => ({src: i.currentSrc || i.src, alt: i.alt, w: i.naturalWidth}));
  const headings = [...document.querySelectorAll('h1,h2,h3')].slice(0, 30).map(h => ({
    tag: h.tagName, text: h.innerText.trim(), font: cs(h,'fontFamily'),
    size: cs(h,'fontSize'), weight: cs(h,'fontWeight')}));
  const btn = document.querySelector('button, a[class*=btn], a[class*=button]');
  return {title: document.title, bodyFont: cs(b,'fontFamily'), bodyBg: cs(b,'backgroundColor'),
    bodyColor: cs(b,'color'), bodySize: cs(b,'fontSize'), sections, links, images, headings,
    button: btn ? {bg: cs(btn,'backgroundColor'), color: cs(btn,'color'), radius: cs(btn,'borderRadius')} : null};
}
"""

def scrape(url, out="out"):
    out = pathlib.Path(out); out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=45000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        page.evaluate("window.scrollTo(0, 0)")
        (out / "desktop.jpg").write_bytes(page.screenshot(full_page=True, type="jpeg", quality=60))
        (out / "data.json").write_text(json.dumps(page.evaluate(JS)), encoding="utf-8")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(500)
        (out / "mobile.jpg").write_bytes(page.screenshot(full_page=True, type="jpeg", quality=60))
        browser.close()

if __name__ == "__main__":
    scrape(sys.argv[1])