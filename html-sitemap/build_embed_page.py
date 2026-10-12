#!/usr/bin/env python3
"""Build the copy-paste handoff page for the generated sitemap block.

Wraps therapy-near-me-sitemap.html in a page with a one-click copy button and
the install steps, so the block can be handed over without anyone having to
select 250KB of markup by hand.

Usage:
    python3 build_embed_page.py [output.html]     # default: ./sitemap-embed.html

The output is a build artifact, not a deliverable in this repo -- it is in
.gitignore. Regenerate it after every build_sitemap.py run.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "therapy-near-me-sitemap.html"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "sitemap-embed.html"

code = SRC.read_text(encoding="utf-8")
escaped = html.escape(code, quote=False)

lines = code.count("\n") + 1
kb = round(len(code.encode()) / 1024)
links = len(re.findall(r'<li class="tnm-item"', code))
sections = len(re.findall(r'<section class="tnm-section"', code))

counts = re.findall(r'class="tnm-chip" href="#[^"]+">([^<]+)<span>(\d+)</span>', code)
rows = "\n".join(
    f'          <tr><td>{name.strip()}</td><td class="num">{n}</td></tr>'
    for name, n in counts
)

PAGE = f"""<title>Therapy Near Me Sitemap Embed</title>
<style>
  :root {{
    --ground:#FAFBFC; --surface:#FFFFFF; --raised:#EFF3F6;
    --ink:#16212A; --muted:#5C6D79; --line:#DAE2E8;
    --accent:#1C5C72; --on-accent:#FFFFFF; --ok:#136B45;
    --shadow:0 1px 2px rgba(22,33,42,.06), 0 8px 24px rgba(22,33,42,.05);
    --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  }}
  @media (prefers-color-scheme:dark) {{
    :root:not([data-theme="light"]) {{
      --ground:#0E151A; --surface:#141D24; --raised:#1B262E;
      --ink:#E6EDF2; --muted:#93A4B0; --line:#243039;
      --accent:#74BDD8; --on-accent:#0B1216; --ok:#5CCF9C;
      --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
    }}
  }}
  :root[data-theme="dark"] {{
    --ground:#0E151A; --surface:#141D24; --raised:#1B262E;
    --ink:#E6EDF2; --muted:#93A4B0; --line:#243039;
    --accent:#74BDD8; --on-accent:#0B1216; --ok:#5CCF9C;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
  }}

  * {{ box-sizing:border-box; }}
  body {{
    margin:0; background:var(--ground); color:var(--ink);
    font-family:var(--sans); font-size:16px; line-height:1.55;
    -webkit-font-smoothing:antialiased;
  }}
  .wrap {{ max-width:920px; margin:0 auto; padding:0 24px 72px; }}

  header {{ padding:56px 0 32px; display:flex; flex-direction:column; gap:12px; }}
  .eyebrow {{
    font-size:12px; font-weight:650; letter-spacing:.12em; text-transform:uppercase;
    color:var(--accent); margin:0;
  }}
  h1 {{ margin:0; font-size:34px; line-height:1.15; letter-spacing:-.02em; text-wrap:balance; }}
  .lede {{ margin:0; max-width:60ch; color:var(--muted); }}

  .facts {{
    display:flex; flex-wrap:wrap; gap:8px; margin-top:8px;
    font-variant-numeric:tabular-nums;
  }}
  .fact {{
    display:flex; align-items:baseline; gap:6px; padding:5px 11px;
    background:var(--raised); border:1px solid var(--line); border-radius:999px; font-size:13px;
  }}
  .fact b {{ font-weight:650; }}
  .fact span {{ color:var(--muted); }}

  .bar {{
    position:sticky; top:0; z-index:10; display:flex; align-items:center;
    flex-wrap:wrap; gap:12px 16px; padding:14px 0;
    background:color-mix(in srgb, var(--ground) 88%, transparent);
    backdrop-filter:blur(10px); border-bottom:1px solid var(--line);
  }}
  .file {{ font-family:var(--mono); font-size:13px; color:var(--muted); }}
  .spacer {{ flex:1; }}
  button {{
    font:inherit; font-weight:600; font-size:15px; cursor:pointer;
    display:inline-flex; align-items:center; gap:9px;
    padding:11px 20px; border-radius:8px; border:1px solid transparent;
    background:var(--accent); color:var(--on-accent);
    transition:transform .12s ease, opacity .12s ease;
  }}
  button:hover {{ opacity:.9; }}
  button:active {{ transform:translateY(1px); }}
  button:focus-visible {{ outline:2px solid var(--accent); outline-offset:3px; }}
  button svg {{ width:16px; height:16px; }}
  .said {{ font-size:14px; color:var(--ok); font-weight:600; min-height:1.4em; }}

  h2 {{ margin:44px 0 4px; font-size:15px; font-weight:650; letter-spacing:.08em;
        text-transform:uppercase; color:var(--muted); }}

  ol {{ margin:16px 0 0; padding:0; list-style:none; counter-reset:step;
        display:flex; flex-direction:column; gap:14px; }}
  ol li {{ counter-increment:step; display:grid; grid-template-columns:28px 1fr; gap:14px;
           align-items:start; max-width:64ch; }}
  ol li::before {{
    content:counter(step); grid-row:span 2;
    width:28px; height:28px; border-radius:50%; display:grid; place-items:center;
    background:var(--raised); border:1px solid var(--line);
    font-size:13px; font-weight:650; font-variant-numeric:tabular-nums; color:var(--ink);
  }}
  ol li em {{ display:block; font-style:normal; color:var(--muted); font-size:14.5px; }}
  code.inline {{ font-family:var(--mono); font-size:.9em; background:var(--raised);
                 border:1px solid var(--line); border-radius:4px; padding:1px 5px; }}

  table {{ border-collapse:collapse; margin-top:16px; font-size:14.5px; min-width:280px; }}
  td {{ padding:7px 0; border-bottom:1px solid var(--line); }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; color:var(--muted);
            padding-left:36px; }}
  tr:last-child td {{ border-bottom:none; }}

  .code-shell {{
    margin-top:16px; background:var(--surface); border:1px solid var(--line);
    border-radius:10px; box-shadow:var(--shadow); overflow:hidden;
  }}
  pre {{
    margin:0; padding:20px; max-height:60vh; overflow:auto;
    font-family:var(--mono); font-size:12.5px; line-height:1.65;
    tab-size:2; white-space:pre; color:var(--ink);
  }}
  footer {{ margin-top:40px; padding-top:20px; border-top:1px solid var(--line);
            color:var(--muted); font-size:14px; max-width:64ch; }}

  @media (prefers-reduced-motion:reduce) {{
    * {{ transition:none !important; animation:none !important; }}
  }}
  @media (max-width:600px) {{
    h1 {{ font-size:27px; }}
    header {{ padding:36px 0 24px; }}
    pre {{ font-size:11.5px; padding:14px; }}
  }}
</style>

<div class="wrap">
  <header>
    <p class="eyebrow">WordPress custom HTML block</p>
    <h1>Therapy Near Me sitemap</h1>
    <p class="lede">The finished sitemap block, ready to paste onto
      <code class="inline">/sitemap/</code>. Copy it below — no files to upload, no
      plugins, nothing to configure.</p>
    <div class="facts">
      <div class="fact"><b>{links}</b><span>links</span></div>
      <div class="fact"><b>{sections}</b><span>sections</span></div>
      <div class="fact"><b>{kb}</b><span>KB</span></div>
      <div class="fact"><b>{lines:,}</b><span>lines</span></div>
    </div>
  </header>

  <div class="bar">
    <button id="copy" type="button">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"
           stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect x="5.5" y="5.5" width="8.5" height="8.5" rx="1.8"/>
        <path d="M10.5 5.5V3.3A1.3 1.3 0 0 0 9.2 2H3.3A1.3 1.3 0 0 0 2 3.3v5.9A1.3 1.3 0 0 0 3.3 10.5h2.2"/>
      </svg>
      Copy code
    </button>
    <span class="said" id="said" role="status" aria-live="polite"></span>
    <span class="spacer"></span>
    <span class="file">therapy-near-me-sitemap.html</span>
  </div>

  <h2>How to install</h2>
  <ol>
    <li><span>Edit the <code class="inline">/sitemap/</code> page in WordPress.</span></li>
    <li><span>Add a <strong>Custom HTML</strong> block.
      <em>Not a Paragraph block — that one inserts &lt;br /&gt; at every line break,
      which breaks the stylesheet.</em></span></li>
    <li><span>Paste the copied code into the block.</span></li>
    <li><span>Publish, then load the page.
      <em>Links render in your theme's Helvetica at 16px/28px in #7A7A7A; headings keep your theme's own styles.</em></span></li>
  </ol>

  <h2>What's in it</h2>
  <table>
    <tbody>
{rows}
    </tbody>
  </table>

  <h2>The code</h2>
  <div class="code-shell">
    <pre id="code">{escaped}</pre>
  </div>

  <footer>
    Regenerate any time from <code class="inline">build_sitemap.py</code> after
    re-downloading the two XML sitemaps — categories, ordering and exclusions all
    live in editable tables at the top of that script.
  </footer>
</div>

<script>
  const btn = document.getElementById('copy');
  const said = document.getElementById('said');
  const code = document.getElementById('code');
  let timer;

  btn.addEventListener('click', async () => {{
    const text = code.textContent;
    try {{
      await navigator.clipboard.writeText(text);
      report('Copied — ' + text.length.toLocaleString() + ' characters');
    }} catch (err) {{
      const range = document.createRange();
      range.selectNodeContents(code);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      const ok = document.execCommand && document.execCommand('copy');
      report(ok ? 'Copied to clipboard' : 'Code selected — press Ctrl/Cmd + C');
    }}
  }});

  function report(message) {{
    said.textContent = message;
    clearTimeout(timer);
    timer = setTimeout(() => {{ said.textContent = ''; }}, 4000);
  }}
</script>
"""

OUT.write_text(PAGE, encoding="utf-8")
print(f"wrote {OUT} ({round(len(PAGE)/1024)} KB) — {links} links, {sections} sections")
