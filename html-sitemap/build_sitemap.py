#!/usr/bin/env python3
"""Build a categorised HTML sitemap for therapynearme.com.au.

Reads the two Yoast XML sitemaps in ./data and writes a self-contained HTML
block to therapy-near-me-sitemap.html, ready to paste into a WordPress
"Custom HTML" block.

Usage:
    python3 build_sitemap.py

To refresh after publishing new pages, re-download the two sitemaps into
./data and run the script again. Classification is driven by the tables
below -- edit those, not the generated HTML.
"""

from __future__ import annotations

import html
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE / "therapy-near-me-sitemap.html"
SITE = "https://therapynearme.com.au"

# Pages deliberately kept off the HTML sitemap. "sitemap" is this page itself;
# the rest are service pages that are not part of the site's Services menu.
EXCLUDED_SLUGS = {
    "sitemap",
    "authors",  # the authors index; individual /authors/* profiles are kept
    "therapy",
    "therapy-near-me",
    "therapist-near-me",
    "mental-health-support-after-hospital-discharge",
    "neurodiversity-affirming-mental-health-support-in-australia",
}

# --------------------------------------------------------------------------
# Classification tables
# --------------------------------------------------------------------------

STATES = {
    "nsw": "New South Wales",
    "vic": "Victoria",
    "qld": "Queensland",
    "wa": "Western Australia",
    "sa": "South Australia",
    "tas": "Tasmania",
    "nt": "Northern Territory",
    "act": "Australian Capital Territory",
}

STATE_ORDER = ["nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt"]

# City pages published without a state prefix, mapped to their state.
BARE_CITIES = {
    "sydney": "nsw",
    "parramatta": "nsw",
    "melbourne": "vic",
    "southbank": "vic",
    "brisbane": "qld",
    "noosa": "qld",
    "burleigh-heads": "qld",
    "gladstone": "qld",
    "adelaide": "sa",
    "canberra": "act",
}

# Individual team-member profiles. The regex below catches future profiles
# that follow the same "firstname-lastname-role" pattern.
PRACTITIONER_SLUGS = {
    "team",
    "alyson-dunn-psychologist",
    "ana-turino-psychologist",
    "dr-ross-leembruggen-psychologist",
    "jimmy-nweke-counsellor-social-worker",
    "lidija-ivicevich-counsellor",
    "mohamed-abdelsalam-behaviour-support-practitioner",
    "nadia-sologuren-guevara-psychologist",
    "shine-yin-teoh-speech-pathologist",
    "victoria-nguyen-behaviour-support-practitioner",
}

PRACTITIONER_RE = re.compile(
    r"^(dr-)?[a-z]+-[a-z]+(-[a-z]+)?-"
    r"(psychologist|psychotherapist|counsellor|social-worker|"
    r"speech-pathologist|behaviour-support-practitioner|occupational-therapist)$"
)

# The Services menu exactly as it appears on the site, in the site's own
# order (not alphabetical). Reorder this list to reorder the Services section.
SERVICE_ORDER = [
    "anxiety-therapy",
    "depression-treatment",
    "treatment-for-autism",
    "treatment-for-adhd",
    "treatment-for-ptsd",
    "schizophrenia-treatments",
    "treatment-for-bpd",
    "treatment-for-bipolar",
    "speech-therapy",
    "ndis-psychology-services",
    "workcover-psychologist",
    "psychologist-near-me-1",
    "online-psychologist",
    "at-home-ndis-psychologist",
    "telehealth-psychologist",
    "eap-psychology-services",
    "child-psychologist",
    "relationship-counselling",
    "support-work-services",
    "support-coordination",
    "counselling-services",
    "behaviour-support-services",
    "early-intervention",
    "board-approved-supervisor",
]

SERVICE_SLUGS = set(SERVICE_ORDER)

# Referral pathways, in the order they should appear.
REFERRAL_ORDER = [
    "ndis-psychology-referrals",
    "gp-psychology-referrals",
]

# Research reports and the research hub.
REPORT_SLUGS = {
    "australian-mental-health-access-report-2026",
    "australian-psychology-fees-and-affordability-evidence-review-2026",
    "global-mental-health-care-access-and-affordability-benchmark-2027",
    "mental-health-research-and-resources",
}

# Resources, split into two on-page groups.
RESOURCE_SLUGS = {
    "affordable-pricing",
    "faq",
    "mental-health-blog",
    "student-placements",
}

ABOUT_SLUGS = {
    "",  # home page
    "about-us",
    "complaints-form",
    "privacy-policy",
    "terms-of-service",
}

# --------------------------------------------------------------------------
# Slug -> readable label
# --------------------------------------------------------------------------

ACRONYMS = {
    "ndis": "NDIS", "ndia": "NDIA", "adhd": "ADHD", "asd": "ASD",
    "ptsd": "PTSD", "bpd": "BPD", "ocd": "OCD", "dbt": "DBT", "cbt": "CBT",
    "emdr": "EMDR", "eap": "EAP", "ahpra": "AHPRA", "apa": "APA",
    "gp": "GP", "gps": "GPs", "faq": "FAQ", "faqs": "FAQs", "iq": "IQ",
    "ai": "AI", "tms": "TMS", "asmr": "ASMR", "phd": "PhD",
    "lgbtq": "LGBTQ", "lgbtqia": "LGBTQIA", "nsw": "NSW", "vic": "VIC",
    "qld": "QLD", "tas": "TAS",
}

# Apostrophes are stripped from WordPress slugs; put the common ones back.
APOSTROPHES = {
    "whats": "What's", "thats": "That's", "heres": "Here's",
    "theres": "There's", "dont": "Don't", "doesnt": "Doesn't",
    "didnt": "Didn't", "wont": "Won't", "cant": "Can't",
    "couldnt": "Couldn't", "shouldnt": "Shouldn't", "wouldnt": "Wouldn't",
    "isnt": "Isn't", "arent": "Aren't", "wasnt": "Wasn't",
    "werent": "Weren't", "hasnt": "Hasn't", "havent": "Haven't",
    "im": "I'm", "ive": "I've", "youre": "You're", "youve": "You've",
    "youll": "You'll", "theyre": "They're", "theyve": "They've",
    "lets": "Let's",
}

# Link text that should match the site's own wording rather than the slug.
LABEL_OVERRIDES = {
    "at-home-ndis-psychologist": "At-Home Psychologist",
}

# Proper nouns that simple title-casing gets wrong.
CASE_FIXES = {
    "workcover": "WorkCover", "medicare": "Medicare", "telehealth": "Telehealth",
    "betterhelp": "BetterHelp", "headspace": "Headspace", "beyond": "Beyond",
}

# Role suffixes on individual practitioner profile URLs.
ROLE_SUFFIXES = [
    "counsellor-social-worker",
    "behaviour-support-practitioner",
    "occupational-therapist",
    "speech-pathologist",
    "psychotherapist",
    "psychologist",
    "counsellor",
    "social-worker",
]

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into",
    "nor", "of", "on", "or", "the", "to", "vs", "with",
}

# Trailing "-1"/"-2" are WordPress slug collisions, not part of the title.
DUP_SUFFIX_RE = re.compile(r"-(?:1|2|3)$")


def titleise(slug: str) -> str:
    """Turn a URL slug into readable link text."""
    if slug in LABEL_OVERRIDES:
        return LABEL_OVERRIDES[slug]
    slug = slug.rsplit("/", 1)[-1]  # nested paths: use the final segment
    slug = DUP_SUFFIX_RE.sub("", slug)
    words = [w for w in slug.split("-") if w]
    if not words:
        return "Home"

    out = []
    for i, word in enumerate(words):
        low = word.lower()
        if low in ACRONYMS:
            out.append(ACRONYMS[low])
        elif low in APOSTROPHES:
            out.append(APOSTROPHES[low])
        elif low in CASE_FIXES:
            out.append(CASE_FIXES[low])
        elif low in SMALL_WORDS and i != 0:
            out.append(low)
        elif low.isdigit():
            out.append(low)
        else:
            out.append(word[:1].upper() + word[1:])
    return " ".join(out)


# --------------------------------------------------------------------------
# Sitemap parsing
# --------------------------------------------------------------------------

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def parse_sitemap(path: Path) -> list[dict]:
    root = ET.parse(path).getroot()
    entries = []
    for url in root.findall("sm:url", NS):
        loc = url.findtext("sm:loc", default="", namespaces=NS).strip()
        if not loc:
            continue
        lastmod = url.findtext("sm:lastmod", default="", namespaces=NS).strip()
        entries.append({"loc": loc, "lastmod": lastmod[:10]})
    return entries


def slug_of(loc: str) -> str:
    return loc.replace(SITE, "").strip("/")


# --------------------------------------------------------------------------
# Categorisation
# --------------------------------------------------------------------------

def classify_page(slug: str) -> tuple[str, str]:
    """Return (category, group) for a page-sitemap slug."""
    head = slug.split("-", 1)[0]
    if head in STATES and "-" in slug:
        return "locations", head
    if slug in BARE_CITIES:
        return "locations", BARE_CITIES[slug]
    if slug in PRACTITIONER_SLUGS or slug.startswith("authors/"):
        return "practitioners", ""
    if PRACTITIONER_RE.match(slug) and slug not in SERVICE_SLUGS:
        return "practitioners", ""
    if slug in SERVICE_SLUGS:
        return "services", ""
    if slug in REFERRAL_ORDER:
        return "referrals", ""
    if slug in REPORT_SLUGS:
        return "reports", ""
    if slug in RESOURCE_SLUGS:
        return "resources", "guides"
    if slug in ABOUT_SLUGS:
        return "resources", "about"
    # Anything new and unrecognised lands in Resources > Guides rather than
    # being dropped, so it is still linked and easy to spot.
    return "resources", "guides"


def build_items() -> dict:
    pages = parse_sitemap(DATA / "page-sitemap.xml")
    posts = parse_sitemap(DATA / "post-sitemap.xml")

    buckets = {
        "services": [],
        "locations": defaultdict(list),
        "practitioners": [],
        "referrals": [],
        "resources": defaultdict(list),
        "reports": [],
        "blogs": defaultdict(list),
    }
    seen = set()

    for entry in pages:
        slug = slug_of(entry["loc"])
        if slug in EXCLUDED_SLUGS:
            continue
        seen.add(slug)
        category, group = classify_page(slug)
        note = ""
        if category == "locations":
            label = location_label(slug)
        elif category == "practitioners":
            label, note = practitioner_label(slug)
        else:
            label = titleise(slug)
        item = {
            "url": entry["loc"],
            "slug": slug,
            "date": entry["lastmod"],
            "label": label,
            "note": note,
        }
        if category in ("locations", "resources"):
            buckets[category][group].append(item)
        else:
            buckets[category].append(item)

    for entry in posts:
        slug = slug_of(entry["loc"])
        if slug in seen or slug in EXCLUDED_SLUGS:
            continue  # already listed as a page, or deliberately excluded
        seen.add(slug)
        label = titleise(slug)
        letter = label[0].upper() if label[:1].isalpha() else "#"
        buckets["blogs"][letter].append(
            {
                "url": entry["loc"],
                "slug": slug,
                "date": entry["lastmod"],
                "label": label,
                "note": "",
            }
        )

    return buckets


HUB_LABELS = {"team": "Our Team"}


def practitioner_label(slug: str) -> tuple[str, str]:
    """'alyson-dunn-psychologist' -> ('Alyson Dunn', 'Psychologist')."""
    if slug in HUB_LABELS:
        return HUB_LABELS[slug], ""
    if slug.startswith("authors/"):
        return titleise(slug), "Author"
    for suffix in ROLE_SUFFIXES:
        if slug.endswith("-" + suffix):
            name = slug[: -(len(suffix) + 1)]
            return titleise(name), titleise(suffix).replace(" Social Worker", " / Social Worker")
    return titleise(slug), ""


def location_label(slug: str) -> str:
    """'nsw-bondi-junction' -> 'Bondi Junction'."""
    head = slug.split("-", 1)[0]
    if head in STATES and "-" in slug:
        slug = slug.split("-", 1)[1]
    return titleise(slug)


def disambiguate(items: list[dict]) -> None:
    """Where two links in a group share link text, append the URL path."""
    counts = defaultdict(int)
    for item in items:
        counts[item["label"]] += 1
    for item in items:
        item["hint"] = "/" + item["slug"] + "/" if counts[item["label"]] > 1 else ""


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def esc(text: str) -> str:
    return html.escape(text, quote=True)


def render_list(items: list[dict], show_date: bool = False, sort: bool = True) -> str:
    disambiguate(items)
    rows = []
    ordered = sorted(items, key=lambda i: i["label"].lower()) if sort else items
    for item in ordered:
        note = (
            f'<span class="tnm-note">{esc(item["note"])}</span>' if item.get("note") else ""
        )
        hint = (
            f'<span class="tnm-hint">{esc(item["hint"])}</span>' if item["hint"] else ""
        )
        date = (
            f'<span class="tnm-date">{esc(item["date"])}</span>'
            if show_date and item["date"]
            else ""
        )
        search = f'{item["label"]} {item.get("note", "")} {item["slug"]}'.lower()
        rows.append(
            f'<li class="tnm-item" data-search="{esc(search)}">'
            f'<a href="{esc(item["url"])}">{esc(item["label"])}</a>{note}{hint}{date}</li>'
        )
    return "\n".join(rows)


def render_section(
    section_id: str, title: str, blurb: str, body: str, count: int
) -> str:
    return f"""<section class="tnm-section" id="{section_id}" data-section="{section_id}">
  <header class="tnm-section-head">
    <h2>{esc(title)} <span class="tnm-count" data-count-for="{section_id}">{count}</span></h2>
    <p class="tnm-blurb">{esc(blurb)}</p>
  </header>
{body}
</section>"""


def render_group(
    title: str, items: list[dict], show_date: bool = False, sort: bool = True
) -> str:
    return f"""  <div class="tnm-group">
    <h3 class="tnm-group-title">{esc(title)} <span class="tnm-group-count">{len(items)}</span></h3>
    <ul class="tnm-links">
{render_list(items, show_date, sort)}
    </ul>
  </div>"""


def build_html(buckets: dict) -> str:
    services = buckets["services"]
    practitioners = buckets["practitioners"]
    locations = buckets["locations"]
    referrals = buckets["referrals"]
    resources = buckets["resources"]
    reports = buckets["reports"]
    blogs = buckets["blogs"]

    loc_total = sum(len(v) for v in locations.values())
    blog_total = sum(len(v) for v in blogs.values())
    res_total = sum(len(v) for v in resources.values())
    grand_total = (
        len(services)
        + loc_total
        + len(practitioners)
        + len(referrals)
        + res_total
        + len(reports)
        + blog_total
    )

    sections = []

    # Services keep the site's own menu order rather than being sorted.
    by_slug = {item["slug"]: item for item in services}
    menu = [by_slug[s] for s in SERVICE_ORDER if s in by_slug]

    sections.append(
        render_section(
            "services",
            "Services",
            "Therapy, assessment and support services offered across Australia.",
            f'  <div class="tnm-group">\n    <ul class="tnm-links">\n'
            f"{render_list(menu, sort=False)}\n    </ul>\n  </div>",
            len(services),
        )
    )

    loc_groups = []
    for state in STATE_ORDER:
        if locations.get(state):
            loc_groups.append(render_group(STATES[state], locations[state]))
    sections.append(
        render_section(
            "locations",
            "Locations",
            "Clinic and telehealth coverage, grouped by state and territory.",
            "\n".join(loc_groups),
            loc_total,
        )
    )

    sections.append(
        render_section(
            "practitioners",
            "Practitioners",
            "Psychologists, counsellors and allied health practitioners.",
            f'  <div class="tnm-group">\n    <ul class="tnm-links">\n{render_list(practitioners)}\n    </ul>\n  </div>',
            len(practitioners),
        )
    )

    ref_by_slug = {item["slug"]: item for item in referrals}
    ordered_referrals = [ref_by_slug[s] for s in REFERRAL_ORDER if s in ref_by_slug]
    sections.append(
        render_section(
            "referrals",
            "Referrals",
            "How to refer a client, or get a referral to see us.",
            f'  <div class="tnm-group">\n    <ul class="tnm-links">\n'
            f"{render_list(ordered_referrals, sort=False)}\n    </ul>\n  </div>",
            len(referrals),
        )
    )

    res_groups = []
    if resources.get("guides"):
        res_groups.append(render_group("Guides & Information", resources["guides"]))
    if resources.get("about"):
        res_groups.append(render_group("About & Policies", resources["about"]))
    sections.append(
        render_section(
            "resources",
            "Resources",
            "Pricing, frequently asked questions and company information.",
            "\n".join(res_groups),
            res_total,
        )
    )

    sections.append(
        render_section(
            "reports",
            "Reports",
            "Original research and evidence reviews on access, affordability "
            "and mental health care in Australia.",
            f'  <div class="tnm-group">\n    <ul class="tnm-links">\n{render_list(reports)}\n    </ul>\n  </div>',
            len(reports),
        )
    )

    blog_groups = []
    for letter in sorted(blogs):
        blog_groups.append(render_group(letter, blogs[letter], show_date=True))
    sections.append(
        render_section(
            "blogs",
            "Blogs",
            "Every article, A to Z. Use the search box above to jump to a topic.",
            "\n".join(blog_groups),
            blog_total,
        )
    )

    nav = "\n".join(
        f'      <a class="tnm-chip" href="#{sid}">{esc(name)} <span>{count}</span></a>'
        for sid, name, count in [
            ("services", "Services", len(services)),
            ("locations", "Locations", loc_total),
            ("practitioners", "Practitioners", len(practitioners)),
            ("referrals", "Referrals", len(referrals)),
            ("resources", "Resources", res_total),
            ("reports", "Reports", len(reports)),
            ("blogs", "Blogs", blog_total),
        ]
    )

    return TEMPLATE.format(
        nav=nav,
        sections="\n\n".join(sections),
        total=grand_total,
    )


TEMPLATE = """<!-- Therapy Near Me - HTML sitemap
     Generated by html-sitemap/build_sitemap.py from the XML sitemaps.
     Paste this whole block into a WordPress "Custom HTML" block. -->
<div class="tnm-sitemap">
  <style>
    /* Body typography, taken from the site's own text styles. Change these
       six values here and the whole block follows.
       Headings are left alone so they keep the theme's heading styles. The
       greys below are mixed from the text colour rather than being separate
       fixed values, so the palette stays consistent with it; the first
       declaration of each pair is a fallback for browsers without
       color-mix(). To tint links on hover, set --tnm-accent. */
    .tnm-sitemap{{--tnm-accent:currentColor;--tnm-gap:48px;
      font-family:"Helvetica",Sans-serif;
      font-size:16px;
      font-weight:400;
      font-style:normal;
      line-height:28px;
      color:#7A7A7A;
      --tnm-muted:#a5a5a5;--tnm-muted:color-mix(in srgb,currentColor 68%,transparent);
      --tnm-line:rgba(122,122,122,.3);--tnm-line:color-mix(in srgb,currentColor 28%,transparent);
      --tnm-surface:rgba(122,122,122,.06);--tnm-surface:color-mix(in srgb,currentColor 6%,transparent);}}
    .tnm-sitemap *{{box-sizing:border-box;}}
    .tnm-toolbar{{position:sticky;top:0;z-index:5;background:var(--tnm-surface);backdrop-filter:blur(6px);border:1px solid var(--tnm-line);border-radius:8px;padding:16px;margin-bottom:36px;}}
    .tnm-search{{display:block;width:100%;padding:11px 14px;font-size:16px;font-family:inherit;color:inherit;background:transparent;border:1px solid var(--tnm-line);border-radius:6px;}}
    .tnm-search:focus{{outline:2px solid var(--tnm-accent);outline-offset:1px;}}
    .tnm-nav{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}}
    .tnm-chip{{display:inline-flex;align-items:center;gap:6px;padding:6px 13px;font-size:14px;text-decoration:none;color:inherit;border:1px solid var(--tnm-line);border-radius:999px;}}
    .tnm-chip:hover,.tnm-chip:focus{{border-color:currentColor;text-decoration:none;}}
    .tnm-chip span{{font-size:12px;color:var(--tnm-muted);}}
    .tnm-status{{margin:10px 0 0;font-size:14px;color:var(--tnm-muted);}}
    .tnm-section{{margin:0 0 56px;scroll-margin-top:100px;}}
    .tnm-section-head{{border-bottom:1px solid var(--tnm-line);padding-bottom:10px;margin-bottom:26px;}}
    .tnm-section h2{{margin:0;line-height:1.25;display:flex;align-items:baseline;gap:12px;}}
    .tnm-count{{font-size:14px;font-weight:400;color:var(--tnm-muted);}}
    .tnm-blurb{{margin:8px 0 0;font-size:15px;color:var(--tnm-muted);}}
    .tnm-group{{margin-bottom:34px;}}
    .tnm-group:last-child{{margin-bottom:0;}}
    .tnm-group-title{{margin:0 0 16px;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--tnm-muted);display:flex;align-items:baseline;gap:8px;}}
    .tnm-group-count{{font-size:12px;font-weight:400;text-transform:none;letter-spacing:0;opacity:.8;}}
    .tnm-links{{list-style:none;margin:0;padding:0;columns:3;column-gap:var(--tnm-gap);}}
    .tnm-item{{break-inside:avoid;margin:0 0 16px;}}
    .tnm-item a{{color:inherit;text-decoration:none;}}
    .tnm-item a:hover,.tnm-item a:focus{{color:var(--tnm-accent);text-decoration:underline;text-underline-offset:3px;}}
    /* Blog titles are long and often wrap, so tighten their rhythm a little. */
    #blogs .tnm-item{{margin-bottom:14px;}}
    .tnm-hint,.tnm-date,.tnm-note{{display:inline-block;margin-left:8px;font-size:12px;color:var(--tnm-muted);}}
    .tnm-note{{white-space:nowrap;}}
    .tnm-sitemap [hidden]{{display:none !important;}}
    @media (max-width:900px){{.tnm-links{{columns:2;--tnm-gap:32px;}}}}
    @media (max-width:600px){{.tnm-links{{columns:1;}}}}
    @media print{{.tnm-toolbar{{display:none;}}.tnm-links{{columns:2;}}}}
  </style>

  <div class="tnm-toolbar">
    <label class="tnm-visually-hidden" for="tnm-search-input" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);">Search the sitemap</label>
    <input id="tnm-search-input" class="tnm-search" type="search" autocomplete="off"
           placeholder="Search {total} pages by name, suburb or topic&hellip;">
    <nav class="tnm-nav" aria-label="Sitemap categories">
{nav}
    </nav>
    <p class="tnm-status" role="status" aria-live="polite" data-tnm-status></p>
  </div>

{sections}
</div>

<script>
(function () {{
  var root = document.querySelector('.tnm-sitemap');
  if (!root) return;
  var input = root.querySelector('#tnm-search-input');
  var status = root.querySelector('[data-tnm-status]');
  var items = Array.prototype.slice.call(root.querySelectorAll('.tnm-item'));
  var groups = Array.prototype.slice.call(root.querySelectorAll('.tnm-group'));
  var sections = Array.prototype.slice.call(root.querySelectorAll('.tnm-section'));
  var timer;

  function apply(query) {{
    var q = query.trim().toLowerCase();
    var terms = q ? q.split(/\\s+/) : [];
    var shown = 0;

    items.forEach(function (item) {{
      var haystack = item.getAttribute('data-search') || '';
      var match = terms.every(function (t) {{ return haystack.indexOf(t) !== -1; }});
      item.hidden = !match;
      if (match) shown++;
    }});

    groups.forEach(function (group) {{
      group.hidden = !group.querySelector('.tnm-item:not([hidden])');
    }});

    sections.forEach(function (section) {{
      var visible = section.querySelectorAll('.tnm-item:not([hidden])').length;
      section.hidden = terms.length > 0 && visible === 0;
      var counter = section.querySelector('.tnm-count');
      if (counter) counter.textContent = visible;
      var chip = root.querySelector('.tnm-chip[href="#' + section.id + '"]');
      if (chip) {{
        var chipCount = chip.querySelector('span');
        if (chipCount) chipCount.textContent = visible;
      }}
    }});

    root.querySelectorAll('.tnm-group-count').forEach(function (el) {{
      var list = el.closest('.tnm-group');
      if (list) el.textContent = list.querySelectorAll('.tnm-item:not([hidden])').length;
    }});

    status.textContent = terms.length
      ? shown + (shown === 1 ? ' page matches ' : ' pages match ') + '"' + query.trim() + '"'
      : '';
  }}

  input.addEventListener('input', function () {{
    clearTimeout(timer);
    timer = setTimeout(function () {{ apply(input.value); }}, 120);
  }});

  input.addEventListener('keydown', function (event) {{
    if (event.key === 'Escape') {{ input.value = ''; apply(''); }}
  }});
}})();
</script>
"""


def main() -> int:
    missing = [p.name for p in (DATA / "page-sitemap.xml", DATA / "post-sitemap.xml") if not p.exists()]
    if missing:
        print(f"missing sitemap file(s) in {DATA}: {', '.join(missing)}", file=sys.stderr)
        return 1

    buckets = build_items()
    OUT.write_text(build_html(buckets), encoding="utf-8")

    counts = [
        ("services", len(buckets["services"])),
        ("locations", sum(len(v) for v in buckets["locations"].values())),
        ("practitioners", len(buckets["practitioners"])),
        ("referrals", len(buckets["referrals"])),
        ("resources", sum(len(v) for v in buckets["resources"].values())),
        ("reports", len(buckets["reports"])),
        ("blogs", sum(len(v) for v in buckets["blogs"].values())),
    ]
    print(f"wrote {OUT.relative_to(BASE.parent)}")
    for name, count in counts:
        print(f"  {name:<14}{count:>4}")
    print(f"  {'total':<14}{sum(c for _, c in counts):>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
