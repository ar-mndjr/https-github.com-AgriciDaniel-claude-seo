# Service schema — buildinginspectionsnearme.com.au

JSON-LD markup for the 11 BINM service pages. Each page gets one self-contained
block carrying the local business, the page, its breadcrumb and the service.

## Where the data came from

The live site could not be fetched from the build environment (outbound network
egress is blocked), so the business data was sourced from the BINM project files
in Google Drive rather than from the published HTML:

| Value | Source |
|-------|--------|
| Phone `1800 796 776`, `$495 inc. GST` entry price | `EXISTING BUILDINGS \| BINM`, `RENOVATIONS AND EXTENSIONS \| BINM`, `BUILDING INSPECTIONS MELBOURNE \| BINM` page copy docs |
| Service inclusions per stream | `BINM Website – Service Streams Structure & Targeting Logic` |
| Page URLs, primary keywords | `BINM_Keyword_Mapping` (June 2026) + the client-supplied live URLs |
| Service area | Four metro location pages live; widened to Australia-wide per the 2 June 2026 INV-001 line item |
| Positioning, standards, report tiers | About page copy, metro page copy, content map |

**Brand only, by instruction.** The business is marked up as *Building Inspections
Near Me*. The operating company's legal name, ABN and registered office are
deliberately excluded — they identify a separately named entity, and schema NAP
should mirror the contact details the site publishes under its own brand. If BINM
ever publishes a trading address or ABN on the site, fill `legalName`,
`identifier.value` and `address` in `business-profile.json` and regenerate.

**Consequence to be aware of:** with no address, this graph is not a complete
Google *LocalBusiness* entry, which wants `address` and `geo`. That is the right
trade for now — a service-area business with no published address should not
invent one — and nothing else in the markup depends on it. Adding a real address
later upgrades it with no restructuring.

**Also still empty:** `logo`, `image`, `email`, `openingHoursSpecification` and
`sameAs`. No source records them, and `BINM - Strategy Plan` lists "create and
verify Google Business Profile" and "create and optimise social profiles" as
outstanding tasks — so these values may not exist yet. They are omitted from the
markup rather than guessed.

**One description to verify:** `building-insurance-assessment`. The June keyword
map targets that page at *insurance valuation / reinstatement cost assessment*,
while every other BINM document frames insurance work as *engineer-led damage and
causation assessment for claims*. The markup follows the damage-assessment
framing. Check the live page and correct `services.json` if it sells valuations.

**URL drift:** five of the client-supplied live URLs differ from the June keyword
map, which lists `/building-and-pest-inspection/`, `/commercial-building-inspection/`,
`/pre-auction-inspection/`, `/insurance-assessment/` and `/warranty-defect-inspection/`.
The live URLs are used here, since every `@id` is built from them. Worth updating
the keyword map so internal links and tracking do not point at the older slugs.

## Layout

| Path | What it is |
|------|------------|
| `business-profile.json` | Every business-specific value, in one place. **Edit this.** |
| `services.json` | The 11 service definitions: name, description, inclusions, related services. |
| `generate.py` | Renders the config into JSON-LD. No dependencies, Python 3. |
| `make-docx.js` | Builds the Word hand-off files from `output/`. Needs the `docx` npm package. |
| `output/docx/*.docx` | One Word document per page: the JSON-LD plus paste instructions. |
| `output/*.json` | Generated JSON-LD graph per page. |
| `output/*.html` | The same graph wrapped in a `<script type="application/ld+json">` tag, ready to paste. |
| `output/all-services.json` | All 11 graphs in one file, keyed by URL, for bulk import. |
| `output/VALIDATION-REPORT.md` | What is still missing from the config and why it matters. |

Regenerate after any config edit:

```bash
python3 generate.py     # rebuilds output/*.json and output/*.html
node make-docx.js       # rebuilds the Word files from that output
```

Always run `generate.py` first. `make-docx.js` reads the generated `output/*.html`
verbatim, so the Word files cannot drift from the markup they document.

## Graph design

There is no site-wide block. Each page carries the local business in full, so a
page can be shipped on its own with nothing else to install. Every copy uses the
same `@id`, `#organization` — the id Yoast also uses — so the 11 repetitions
resolve to **one** business entity rather than 11 near-duplicates. That is what
makes repeating it safe: the `@id` does the consolidating, not the placement.

Each page emits this graph:

```
<page>/#organization  LocalBusiness   HomeAndConstructionBusiness + ProfessionalService
   └── hasOfferCatalog → all 11 services by @id
<page>/#website       WebSite         publisher → #organization
<page>/#webpage       WebPage         isPartOf → #website, about → #organization
<page>/#breadcrumb    BreadcrumbList
<page>/#service       Service         provider → #organization, mainEntityOfPage → #webpage
     ├── hasOfferCatalog → OfferCatalog of that page's inclusions
     └── isRelatedTo    → the sibling service pages
```

(The business and website `@id`s are absolute and identical across pages —
`https://buildinginspectionsnearme.com.au/#organization` — not per-page.)

Keep the business `@id` identical on every page. Changing it per page is what
would actually create 11 competing entities.

Per-service properties used, and why:

- `serviceType` — the plain-language category Google reads for service classification.
- `provider` — an `@id` reference to the business node in the same block.
- `areaServed` + `providerMobility: "dynamic"` — a service-area business that travels to the customer. Australia plus the four metros with live location pages, each linked to Wikidata.
- `serviceOutput` — the report the client actually receives. This is BINM's differentiator (one inspection, upgradeable report) and the part AI answer engines can quote.
- `audience` — separates pre-purchase (buyers) from warranty defect (owners inside warranty) from strata (owners corporations).
- `hasOfferCatalog` — the page's inclusion list as structured items rather than prose.
- `isRelatedTo` — cross-links the 11 services into one connected cluster.
- `offers` — only on the three pages with a published entry price, and modelled as `minPrice` inside a `PriceSpecification`, because "$495 inc. GST" is a floor, not a fixed price. `valueAddedTaxIncluded: true` carries the GST-inclusive part.

No `FAQPage` is included, even though most of these pages carry FAQ blocks: Google
retired FAQ rich results for all sites on 7 May 2026, so it earns no SERP surface.
The FAQ copy still does useful work as on-page content.

## The 11 pages

| URL slug | `Service` name | Entry price in markup |
|----------|----------------|----------------------|
| `existing-buildings` | Existing Building Inspections | from $495 |
| `renovations-and-extensions` | Renovation and Extension Inspections | — |
| `new-buildings` | New Building Inspections | — |
| `adjoining-works-protection` | Adjoining Works Protection and Dilapidation Reporting | — |
| `pre-purchase-inspection` | Pre-Purchase Building Inspection | from $495 |
| `strata-inspection` | Strata Inspection Report | — |
| `building-insurance-assessment` | Building Insurance Assessment | — |
| `building-warranty-defect-inspection` | Building Warranty and Defect Inspection | — |
| `building-and-pest-inspections` | Building and Pest Inspection | — |
| `commercial-building-inspections` | Commercial Building Inspection | — |
| `pre-auction-building-inspection` | Pre-Auction Building Inspection | from $495 |

Pages marked — are "contact for quote" in the copy docs, so no `Offer` is emitted.
Add a `priceFrom` in `services.json` if that changes.

## Implementation

Paste the matching `output/<slug>.html` into that page's `<head>`. That is the
whole install — nothing global to add.

The site runs WordPress + Elementor with Yoast/RankMath in play, so:

- **Rank Math** — Page → Rank Math → Schema → Custom Schema (Code Validation tab), paste the `@graph` array contents. Turn off its auto-generated `WebPage`/`Article` schema for these pages so nodes are not duplicated.
- **Yoast** — Yoast already outputs `WebPage`, `WebSite`, `BreadcrumbList` and an `Organization` at `#organization`. In that case drop those four nodes from these files and keep only the `Service` node: its `provider` already points at `#organization`, so it attaches to Yoast's existing organisation node with no further edits. That is why this id was chosen.
- **No SEO plugin** — a `wp_head` hook or a per-page custom HTML block.

Render the JSON-LD server-side, in the initial HTML. Structured data injected
later by JavaScript can face delayed processing.

**Do not ship two of the same node type on one page.** If the theme or plugin
already emits `BreadcrumbList` or an organisation node, drop the duplicate here
instead of shipping both.

## Before you publish

1. **Fill the remaining gaps** in `business-profile.json`: `logo`, `image`, `email`, `openingHoursSpecification`, `sameAs`. `output/VALIDATION-REPORT.md` lists them. `sameAs` matters most — it is what ties the entity to the Google Business Profile once that exists. Add `address` and `geo` only if BINM publishes an address on the site under its own brand.
2. **Verify the `building-insurance-assessment` description** against the live page (see above).
3. **Reconcile each description with the live page.** Structured data must describe what is actually on the page; where the published wording differs, the page wins — edit `services.json` and regenerate.
4. **Confirm the $495 entry price** is still current and still shown on those three pages. A price in markup that is not on the page is a mismatch.
5. **Only add `aggregateRating` once genuine reviews are visible on the page.** Google's review snippet policy disallows marked-up ratings a visitor cannot see, and self-serving `LocalBusiness` ratings are ignored.
6. **Confirm the URLs resolve exactly as written** — https, trailing slash — since every `@id` is built from them.
7. **Validate** each file through <https://validator.schema.org/> and Google's Rich Results Test, then watch Search Console → Unparsable structured data.

## Expected outcome

`Service` markup produces no rich result of its own. It is entity and eligibility
work: it tells Google and AI answer engines what each page sells, who it is for,
what the customer receives, and that all 11 services belong to one engineer-led
business with an ABN and a registered address. The `BreadcrumbList` node is the
part with a visible SERP surface. Schema is not a ranking factor — treat this as
clarity and eligibility, not as a rankings lever.
