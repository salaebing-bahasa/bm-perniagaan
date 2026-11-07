#!/usr/bin/env python3
"""Bina pdf/bab-NN.pdf daripada halaman bab (isi sama dengan laman web).
สร้างไฟล์ PDF รายบทจากหน้าเว็บบทเรียน (เนื้อหาเหมือนหน้าเว็บ รวมถึงเฉลยถ้าเปิดแล้ว)

    python3 _src/build.py
    pip install playwright && playwright install chromium
    python3 _src/pdf.py [--fontsource /path/to/node_modules/@fontsource]
"""
import functools, http.server, re, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pdf"
FONT_DIR = sys.argv[sys.argv.index("--fontsource") + 1] if "--fontsource" in sys.argv else None


def local_fonts(page):
    """Guna fon Sarabun setempat jika Google Fonts tidak dapat dicapai."""
    base = Path(FONT_DIR) / "sarabun"
    css = []
    for w in ("400", "600", "700"):
        f = base / f"{w}.css"
        if f.exists():
            css.append(re.sub(r"url\(\./files/([^)]+)\)", r"url(https://fonts.gstatic.com/local/\1)", f.read_text()))
    page.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(body="\n".join(css), content_type="text/css"))
    page.route("https://fonts.gstatic.com/local/**", lambda r: r.fulfill(
        body=(base / "files" / r.request.url.rsplit("/", 1)[1]).read_bytes(), content_type="font/woff2"))


def main():
    OUT.mkdir(exist_ok=True)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.route("**/gc.zgo.at/**", lambda r: r.abort())
        if FONT_DIR:
            local_fonts(page)
        for f in sorted((ROOT / "bab").glob("*.html")):
            n = int(f.stem)
            page.goto(f"http://127.0.0.1:{port}/bab/{f.name}", wait_until="networkidle")
            page.evaluate("""() => {
              document.body.classList.remove('tanpa-th');
              document.querySelectorAll('details').forEach(d => d.open = true);
              document.querySelectorAll('details.jawapan summary').forEach(s => s.textContent = 'Jawapan · เฉลย');
            }""")
            page.evaluate("document.fonts.ready")
            title = page.evaluate("document.querySelector('.bab-kepala h1 .ms').textContent.trim()")
            head = ('<div style="font:8.5px Sarabun,sans-serif;color:#1F5D40;width:100%;padding:0 14mm;display:flex;justify-content:space-between">'
                    f'<span>1503250 Bahasa Melayu untuk Perniagaan · ภาษามลายูเพื่อธุรกิจ</span><span>Bab {n} · {title}</span></div>')
            foot = ('<div style="font:9px Sarabun,sans-serif;color:#B8860B;width:100%;text-align:center">'
                    '— <span class="pageNumber"></span> / <span class="totalPages"></span> —</div>')
            page.emulate_media(media="print")
            page.pdf(path=str(OUT / f"bab-{n:02d}.pdf"), format="A4", print_background=True,
                     display_header_footer=True, header_template=head, footer_template=foot,
                     margin={"top": "18mm", "bottom": "16mm", "left": "15mm", "right": "15mm"})
            page.emulate_media(media="screen")
            print("PDF:", f"bab-{n:02d}.pdf")
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
