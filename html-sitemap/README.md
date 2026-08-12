# Therapy Near Me — categorised HTML sitemap

A single, self-contained HTML block listing 989 URLs from `post-sitemap.xml`
and `page-sitemap.xml`, organised into seven categories. Sections render in
this order, with Blogs last:

| Category | Count | Grouping |
| --- | ---: | --- |
| Services | 24 | the site's Services menu, in the site's own order |
| Locations | 115 | by state / territory |
| Practitioners | 13 | flat, with role labels |
| Referrals | 2 | NDIS, then GP |
| Resources | 9 | Guides & Information, About & Policies |
| Reports | 4 | flat, A–Z |
| Blogs | 822 | A–Z letter groups, with last-modified dates |

## Files

- `therapy-near-me-sitemap.html` — the deliverable. Paste into a WordPress
  **Custom HTML** block on `/sitemap/`.
- `build_sitemap.py` — regenerates the HTML from the XML sitemaps.
- `data/page-sitemap.xml`, `data/post-sitemap.xml` — the source sitemaps
  (snapshot: 12 Aug 2026).

## Installing

1. Edit the `/sitemap/` page in WordPress.
2. Add a **Custom HTML** block (not a Paragraph block — it must not be
   auto-formatted).
3. Paste the entire contents of `therapy-near-me-sitemap.html`.
4. Publish.

The block ships its own scoped CSS (everything is namespaced under
`.tnm-sitemap`) and a small inline script, so it cannot leak styles into the
rest of the page.

## Styling

The block sets **no font-family, text colour or heading size anywhere** — it
inherits every one of them from the theme, so it renders in the site's own
typography and palette by construction, and keeps matching if the theme ever
changes.

The secondary greys (counts, dates, blurbs, group headings, borders, the
toolbar background) are not fixed hex values either. They are mixed from the
theme's own text colour:

```css
--tnm-muted: #8a8a8a;                                        /* fallback */
--tnm-muted: color-mix(in srgb, currentColor 58%, transparent);
```

The first declaration is a neutral fallback for browsers without `color-mix()`;
modern browsers use the second, so the whole block is tinted by the site's text
colour. Because everything derives from `currentColor`, dark themes work with
no extra rules.

Verified by rendering the block inside a deliberately mismatched host page
(Georgia body text in dark green, Trebuchet headings in brown): headings, links
and muted text all took the host's fonts and colours exactly.

Two knobs at the top of the `<style>` block:

- `--tnm-accent` — hover/focus colour for links, `currentColor` by default.
  Set it to the brand colour for a tinted hover.
- `--tnm-gap` — column gutter, `48px` on desktop.

Layout follows the Services section on the site: three columns, no bullets,
generous row spacing. Columns drop to two below 900px and one below 600px.

## Regenerating after publishing new pages

```sh
curl -s https://therapynearme.com.au/page-sitemap.xml -o data/page-sitemap.xml
curl -s https://therapynearme.com.au/post-sitemap.xml -o data/post-sitemap.xml
python3 build_sitemap.py
```

No dependencies beyond the Python 3 standard library.

## How pages are categorised

All rules live in the tables at the top of `build_sitemap.py` — edit those
rather than the generated HTML, or your changes will be overwritten on the
next run.

- **Locations** — any slug prefixed with a state code (`nsw-`, `vic-`, `qld-`,
  `wa-`, `sa-`, `tas-`, `nt-`, `act-`), plus the unprefixed city pages listed
  in `BARE_CITIES`, which maps each to its state so it files under the right
  heading. New state-prefixed pages are picked up automatically.
- **Practitioners** — the `PRACTITIONER_SLUGS` list, plus anything matching
  `PRACTITIONER_RE` (`firstname-lastname-role`), plus `/authors/*`. The role
  suffix is stripped from the link text and shown as a muted label, so
  `alyson-dunn-psychologist` renders as **Alyson Dunn** · Psychologist.
- **Services** — `SERVICE_ORDER` holds the 24 pages in the site's Services
  menu, in the site's own order (not alphabetical); reorder that list to
  reorder the section. It is an explicit list because service slugs and
  practitioner slugs are otherwise indistinguishable (`child-psychologist` is
  a service, `ana-turino-psychologist` is a person).
- **Referrals** — `REFERRAL_ORDER`, rendered in list order rather than
  alphabetically.
- **Reports** — `REPORT_SLUGS`: the three research reports plus the
  `/mental-health-research-and-resources/` hub.
- **Blogs** — everything in `post-sitemap.xml`. This mirrors the site's own
  post/page split. A handful of posts read like service pages
  (`adhd-assessment`, `couples-therapy`, `mental-health-treatment`); if you
  want those under Services, add their slugs to `SERVICE_SLUGS` and they will
  move.
- **Resources** — `RESOURCE_SLUGS` (pricing, FAQ, blog hub, student
  placements) and `ABOUT_SLUGS` (home, about, complaints, privacy, terms),
  rendered as two sub-groups so the corporate pages stay out of the way. Any
  *new* page that no rule recognises also lands here, so nothing is ever
  silently dropped.

Excluded pages are listed in `EXCLUDED_SLUGS`:

- `/sitemap/` — this page, so it does not link to itself.
- `/authors/` — the authors index. The individual `/authors/*` profiles are
  kept, under Practitioners.
- `/therapy/`, `/therapy-near-me/`, `/therapist-near-me/`,
  `/mental-health-support-after-hospital-discharge/` and
  `/neurodiversity-affirming-mental-health-support-in-australia/` — service
  pages that are not in the site's Services menu. Delete a slug from that set
  and add it to `SERVICE_ORDER` to bring it back.

One further special case: `/relationship-counselling/` appears in both XML
sitemaps; the page version is kept under Services and the duplicate dropped.

Where two links would otherwise show identical text (for example
`/burleigh-heads/` and `/qld-burleigh-heads/`), the URL path is appended in
muted text so both are distinguishable.

## Link text

Sitemaps carry no titles, so link text is derived from the slug. The generator
handles acronym casing (NDIS, ADHD, PTSD, EAP, GP, PhD…), restores apostrophes
that WordPress strips from slugs (`whats` → *What's*), lowercases minor words,
fixes proper nouns like WorkCover, and drops WordPress's `-2` collision
suffixes.

Spot-check the output after regenerating; new topics may need an entry in
`ACRONYMS`, `APOSTROPHES` or `CASE_FIXES`. Where the site's own wording differs
from the slug, add it to `LABEL_OVERRIDES` — for example
`at-home-ndis-psychologist` renders as *At-Home Psychologist* to match the
Services menu.

## Behaviour

- Every link is present in the static HTML, so crawlers see all 989 URLs
  without executing JavaScript.
- The search box filters as you type across link text, role and slug, hides
  empty groups and sections, and live-updates every count. Escape clears it.
  It is progressive enhancement — with JS disabled the full list still renders.
- Category chips jump to each section; the toolbar stays pinned while
  scrolling. Print styles drop the toolbar and use two columns.
