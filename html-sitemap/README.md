# Therapy Near Me — categorised HTML sitemap

A single, self-contained HTML block that lists all 995 indexable URLs from
`post-sitemap.xml` and `page-sitemap.xml`, organised into five categories:

| Category | Count | Grouping |
| --- | ---: | --- |
| Services | 29 | the site's 24-item Services menu in its own order, then 5 related pages |
| Locations | 115 | by state / territory |
| Practitioners | 14 | flat, with role labels |
| Blogs | 822 | A–Z letter groups, with last-modified dates |
| Resources | 15 | Guides & Reports, About & Policies |

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

The block deliberately sets no fonts, text colours or heading styles — it
inherits all of them from the theme, so it picks up the site's typography
automatically and keeps matching if the theme changes. Links render in the
body text colour with no underline, in three columns, matching the Services
layout on the site.

Two knobs at the top of the `<style>` block:

- `--tnm-accent` — hover/focus colour for links, `currentColor` by default.
  Set it to the brand colour for a tinted hover.
- `--tnm-gap` — column gutter, `48px` on desktop.

Columns drop to two below 900px and one below 600px. Dark mode is inherited
too; `data-theme="light"` on the wrapping div forces light styling.

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
  reorder the section. `SERVICE_RELATED` holds five service pages that are not
  in that menu (`/therapy/`, `/therapy-near-me/`, `/therapist-near-me/`,
  `/mental-health-support-after-hospital-discharge/`,
  `/neurodiversity-affirming-mental-health-support-in-australia/`); they render
  in a second group headed *Related service pages* so nothing is dropped. Move
  a slug between the two lists to promote or demote it.

  Both lists are explicit because service slugs and practitioner slugs are
  otherwise indistinguishable (`child-psychologist` is a service,
  `ana-turino-psychologist` is a person).
- **Blogs** — everything in `post-sitemap.xml`. This mirrors the site's own
  post/page split. A handful of posts read like service pages
  (`adhd-assessment`, `couples-therapy`, `mental-health-treatment`); if you
  want those under Services, add their slugs to `SERVICE_SLUGS` and they will
  move.
- **Resources** — `RESOURCE_SLUGS` (reports, referral guides, FAQ, pricing)
  and `ABOUT_SLUGS` (home, about, complaints, privacy, terms), rendered as two
  sub-groups so the corporate pages stay out of the way. Any *new* page that
  no rule recognises also lands here, so nothing is ever silently dropped.

Two pages are handled specially:

- `/sitemap/` is excluded so the page does not link to itself.
- `/relationship-counselling/` appears in both XML sitemaps; the page version
  is kept under Services and the duplicate is dropped.

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

- Every link is present in the static HTML, so crawlers see all 995 URLs
  without executing JavaScript.
- The search box filters as you type across link text, role and slug, hides
  empty groups and sections, and live-updates every count. Escape clears it.
  It is progressive enhancement — with JS disabled the full list still renders.
- Category chips jump to each section; the toolbar stays pinned while
  scrolling. Print styles drop the toolbar and use two columns.
