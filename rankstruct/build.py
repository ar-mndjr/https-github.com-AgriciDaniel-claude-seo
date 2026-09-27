"""Make every page self-contained.

The shared styles and scripts live in styles.css, blog.css, pages.css,
main.js and pages.js. Each HTML page gets its own copy of the ones it uses,
so a page still renders correctly when opened or shared on its own.

Edit the .css/.js files, then run:  python3 build.py
Running it again is safe: previously inlined blocks are replaced.
"""
import base64
import pathlib
import re

HERE = pathlib.Path(__file__).parent


def inline(page: pathlib.Path) -> bool:
    html = page.read_text()
    before = html

    # <link rel="stylesheet" href="x.css" />  or a previous <style data-src="x.css">
    def css(m):
        name = m.group(1)
        return f'<style data-src="{name}">\n{(HERE / name).read_text()}</style>'
    html = re.sub(r'<link rel="stylesheet" href="([\w-]+\.css)" ?/?>', css, html)
    html = re.sub(r'<style data-src="([\w-]+\.css)">.*?</style>', css, html, flags=re.S)

    # <script src="x.js"></script>  or a previous <script data-src="x.js">
    def js(m):
        name = m.group(1)
        return f'<script data-src="{name}">\n{(HERE / name).read_text()}</script>'
    html = re.sub(r'<script src="([\w-]+\.js)"></script>', js, html)
    html = re.sub(r'<script data-src="([\w-]+\.js)">.*?</script>', js, html, flags=re.S)

    # Favicon as a data URI so the tab icon also travels with the page
    icon = 'data:image/svg+xml;base64,' + base64.b64encode((HERE / 'logo.svg').read_bytes()).decode()
    html = re.sub(r'<link rel="icon" type="image/svg\+xml" href="[^"]*" />',
                  f'<link rel="icon" type="image/svg+xml" href="{icon}" />', html)

    if html != before:
        page.write_text(html)
    return html != before


if __name__ == '__main__':
    for page in sorted(HERE.glob('*.html')):
        print(('updated ' if inline(page) else 'ok      ') + page.name)
