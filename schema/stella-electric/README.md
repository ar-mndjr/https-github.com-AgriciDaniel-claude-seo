# Stella Electric LLC — structured data (11 pages)

JSON-LD for eleven stellaelectricllc.com pages, plus one site-wide organization
block. Every file is valid JSON-LD; every value that could not be verified is an
explicit `{{PLACEHOLDER}}` that must be filled in before the markup goes live.

## Important: these were written without reading the live pages

The domain is blocked by this environment's network egress policy, so the pages
could not be fetched. Page topics, business details and the cost figures below
came from search results for the site's own service pages. That means:

- **Titles, meta descriptions, dates, images, author and word counts are
  placeholders.** They must be copied from each live page.
- **The FAQ questions and answers are drafts.** Google requires FAQ markup to
  match content that is visible on the page. Either paste each draft Q&A into
  the page's visible FAQ section, or replace the draft text with the page's
  actual Q&A. Do not ship FAQ markup for content that is not on the page.
- **The HowTo steps are drafts** written from standard practice and code, in the
  same way. Reconcile them with each article's actual steps.
- Cost figures reused here (surge protector $350-$750; panel upgrade $500-$2,000;
  rewire $7.79 per linear foot plus $1,200-$2,500 for the panel) come from other
  pages on the site. Confirm each blog states the same numbers before leaving
  them in the markup, since price data in schema should match the page.

## Business facts used (verify before deploy)

| Field | Value | Source |
|---|---|---|
| Name | Stella Electric LLC | site |
| Address | 532 Church Rd, Reisterstown, MD 21136 | Yelp listing |
| Phone | 410-429-0479 | site / directories |
| Email | stellaelectricco@gmail.com | directory listing |
| Hours | Mon-Fri 6:00 am - 7:00 pm | Yelp listing |
| Founded | 2016, Reisterstown MD | site (About) |
| Service area | MD, VA, PA, DE, Washington D.C.; Baltimore metro | site |

The address, hours and email are from third-party directories rather than the
site itself - confirm them against the Google Business Profile before publishing,
because NAP data in schema that disagrees with the GBP does more harm than good.
If the business does not run 24/7, do not add 24/7 `openingHoursSpecification`
to the emergency page.

## Files

```
build_schema.py                     generator - edit page data here, re-run
output/00-sitewide-organization.*   Electrician + WebSite; install once, site-wide
output/01..11-<slug>.jsonld         one @graph per page
output/01..11-<slug>.html           same, wrapped in a <script> tag for pasting
```

Regenerate after editing page data:

```bash
python3 build_schema.py            # writes output/, reports remaining placeholders
```

## Schema per page

| # | Page | Types |
|---|---|---|
| 01 | whole-house-surge-protector-benefits | BlogPosting, FAQPage, Service (offer $350-$750), WebPage, BreadcrumbList |
| 02 | cost-to-rewire-an-old-house | BlogPosting, FAQPage, Service (unit price $7.79/linear ft), Service (panel $1,200-$2,500) |
| 03 | electrical-code-inspection-for-home-sale | BlogPosting, FAQPage, Service (+ OfferCatalog of inspection scope) |
| 04 | outlet-sparks-when-plugging-in | BlogPosting, HowTo (what to do when an outlet sparks), FAQPage, Service |
| 05 | hardwired-smoke-detector-installation | BlogPosting, HowTo (install + interconnect), FAQPage, Service |
| 06 | hot-tub-electrical-wiring-requirements | BlogPosting, ItemList (requirements), FAQPage, Service |
| 07 | bathroom-exhaust-fan-electrical-installation | BlogPosting, HowTo, FAQPage, Service |
| 08 | how-to-install-recessed-lighting | BlogPosting, HowTo (tools + supplies), FAQPage, Service |
| 09 | smart-home-electrical-installation | BlogPosting, ItemList (devices), FAQPage, Service (+ OfferCatalog) |
| 10 | emergency-electrician-baltimore | WebPage, Service (+ OfferCatalog), FAQPage, Electrician, BreadcrumbList |
| 11 | electrical-panel-upgrade-baltimore | WebPage, Service (offer $500-$2,000, + OfferCatalog), FAQPage, Electrician |

Pages 10 and 11 read as local service landing pages rather than articles, so they
use `WebPage` + `Service` with the service as `mainEntity` and no author/dateline.
If either is actually a blog post, change its `"kind"` to `"article"` in
`build_schema.py` and re-run - that swaps in the `BlogPosting` and `Person` nodes.

Every page repeats a compact `#organization` node so the `@id` references resolve
within that page. The site-wide file defines the same `@id` with the full detail
(hours, geo, contact points, offer catalog, `sameAs`); the two merge cleanly.

## What each placeholder needs

| Placeholder | Fill with |
|---|---|
| `{{PAGE_TITLE}}` | the page's `<title>` / H1 |
| `{{META_DESCRIPTION}}` | the page's meta description |
| `{{DATE_PUBLISHED}}` / `{{DATE_MODIFIED}}` | ISO 8601 with offset, e.g. `2026-03-14T09:00:00-04:00` |
| `{{PRIMARY_IMAGE_URL/WIDTH/HEIGHT}}` | the page's featured image (1200px wide or more preferred) |
| `{{AUTHOR_NAME/JOB_TITLE/PROFILE_URL}}` | a real, named author with a bio page - E-E-A-T matters on electrical safety content |
| `{{WORD_COUNT}}` | integer, or delete the property |
| `{{HOWTO_TOTAL_TIME}}` | ISO 8601 duration, e.g. `PT2H` |
| `{{LOGO_URL}}`, `{{LOGO_WIDTH/HEIGHT}}` | logo image |
| `{{LATITUDE}}`, `{{LONGITUDE}}`, `{{GOOGLE_MAPS_URL}}` | from the Google Business Profile |
| `{{GOOGLE_BUSINESS_PROFILE_URL}}`, `{{FACEBOOK_URL}}`, `{{YELP_URL}}`, `{{BBB_PROFILE_URL}}`, `{{INSTAGRAM_URL}}` | real profile URLs; delete any that do not exist |
| `{{PAYMENT_ACCEPTED}}` | e.g. `Cash, Check, Credit Card` |
| `{{SMOKE_DETECTOR_SERVICE_URL}}`, `{{HOT_TUB_SERVICE_URL}}`, `{{EXHAUST_FAN_SERVICE_URL}}` | the matching service page URL, or delete the property if none exists |
| `{{EMERGENCY_RESPONSE_TIME_ANSWER}}`, `{{EMERGENCY_PRICING_ANSWER}}` | the answers as written on the page - do not promise a response time or a no-fee policy the business has not committed to |

Delete any property you cannot fill honestly. An omitted property is fine;
a placeholder or an invented value is not.

## Installing

1. Publish `00-sitewide-organization.html` once, in `<head>` on every page
   (a header/footer include, or Yoast/RankMath's schema settings if the site
   already emits an organization block - in that case do not add a second one,
   merge the extra properties into the existing block instead).
2. Paste each page's `.html` file into the `<head>` of that page. In WordPress,
   a per-page custom field with a header hook, a code-snippets plugin, or
   the SEO plugin's schema tab all work.
3. Check for duplicates first. If Yoast or RankMath is already outputting
   `Article`/`WebPage`/`BreadcrumbList` for these URLs, either disable the
   plugin's graph for those pages or keep only the nodes it does not emit
   (`FAQPage`, `HowTo`, `Service`, `ItemList`). Two conflicting `Article` nodes
   on one URL is worse than none.

## Validating

- Rich Results Test - https://search.google.com/test/rich-results - for each URL.
- Schema Markup Validator - https://validator.schema.org/ - catches vocabulary
  errors Google's tool ignores.
- Search Console, Enhancements report, a few days after deploying.

Note on expectations: Google retired FAQ and HowTo rich results for most sites in
2023, so this markup will not usually produce those SERP features. It is still
worth shipping - the entity, service, price, area-served and Q&A data is what
Google's local systems and AI search surfaces read to understand who the business
is and what each page answers. The nodes that can still produce visible SERP
features here are `BreadcrumbList`, the `Article`/`BlogPosting` byline data and
the local business panel.

## Not included, deliberately

- `AggregateRating` / `Review` - only valid with real reviews displayed on the
  page, and self-serving review markup is a manual action risk. Add it only if
  genuine reviews are rendered on the page itself.
- `Product` markup on the cost pages - these are services, not products;
  `Service` with a `PriceSpecification` is the correct type.
- `speakable` - restricted to news publishers.
