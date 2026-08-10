# Service schema — buildinginspectionsnearme.com.au

JSON-LD `Service` markup for the 11 service pages, plus one site-wide business
graph the service pages reference.

> **Data caveat.** The live pages could not be fetched from the environment this
> was built in (outbound network egress was blocked), so nothing here was copied
> from the published HTML. Service names, descriptions and inclusions were written
> from each URL's service type and standard Australian inspection practice, and
> every business-specific value (name, phone, address, hours, ratings, service
> area) is left empty in `business-profile.json` rather than invented. **Reconcile
> the descriptions against the actual page copy and fill in the profile before
> publishing** — see [Before you publish](#before-you-publish).

## Layout

| Path | What it is |
|------|------------|
| `business-profile.json` | Every business-specific value, in one place. **Edit this.** |
| `services.json` | The 11 service definitions: name, description, inclusions, related services. |
| `generate.py` | Renders the config into JSON-LD. No dependencies, Python 3. |
| `output/*.json` | Generated JSON-LD graph per page. |
| `output/*.html` | The same graph wrapped in a `<script type="application/ld+json">` tag, ready to paste. |
| `output/_sitewide-business.*` | The `LocalBusiness` + `WebSite` graph for the site-wide header. |
| `output/all-services.json` | All 11 graphs in one file, keyed by URL, for bulk import. |
| `output/VALIDATION-REPORT.md` | What is still missing from the config and why it matters. |

Regenerate after any config edit:

```bash
python3 generate.py
```

## Graph design

The site-wide block defines the business once, at `#business`. Every service page
then *references* that node instead of repeating it, so Google resolves one
business entity across the site rather than 11 near-duplicates.

```
https://buildinginspectionsnearme.com.au/#business    (HomeAndConstructionBusiness, ProfessionalService)
https://buildinginspectionsnearme.com.au/#website     (WebSite, publisher → #business)

  └── <page>/#webpage    WebPage      isPartOf → #website, about → #business
  └── <page>/#breadcrumb BreadcrumbList
  └── <page>/#service    Service      provider → #business, mainEntityOfPage → #webpage
        ├── hasOfferCatalog → OfferCatalog of the inclusions listed on the page
        └── isRelatedTo    → the sibling service pages
```

Per-service properties used, and why:

- `serviceType` — the plain-language category, the property Google reads for service classification.
- `provider` — an `@id` reference, so the business entity is stated once.
- `areaServed` + `providerMobility: "dynamic"` — marks this as a service-area business that travels to the customer.
- `serviceOutput` — the report the client actually receives. Useful for AI/LLM surfaces summarising what you deliver.
- `audience` — who the service is for, which separates e.g. pre-purchase (buyers) from warranty defect (owners).
- `hasOfferCatalog` — the inclusion list as structured items rather than prose.
- `isRelatedTo` — cross-links the 11 services into one connected cluster instead of 11 isolated pages.
- `availableChannel` — the page URL and phone as the channel for booking.

No `FAQPage` is included: Google retired FAQ rich results for all sites on
7 May 2026, so it earns no SERP surface. If genuine Q&A content exists on a page,
`QAPage` is the current type.

## The 11 pages

| URL slug | `Service` name | `serviceType` |
|----------|----------------|---------------|
| `existing-buildings` | Existing Building Inspection | Existing building inspection |
| `renovations-and-extensions` | Renovation and Extension Inspection | Renovation and extension inspection |
| `new-buildings` | New Building Inspection | New construction stage inspection |
| `adjoining-works-protection` | Adjoining Works Protection and Dilapidation Reporting | Dilapidation and adjoining property protection inspection |
| `pre-purchase-inspection` | Pre-Purchase Building Inspection | Pre-purchase building inspection |
| `strata-inspection` | Strata Inspection Report | Strata inspection report |
| `building-insurance-assessment` | Building Insurance Assessment | Building insurance damage assessment |
| `building-warranty-defect-inspection` | Building Warranty and Defect Inspection | Building defect and statutory warranty inspection |
| `building-and-pest-inspections` | Building and Pest Inspection | Building and timber pest inspection |
| `commercial-building-inspections` | Commercial Building Inspection | Commercial building inspection |
| `pre-auction-building-inspection` | Pre-Auction Building Inspection | Pre-auction building inspection |

## Implementation

**Site-wide (once):** paste `output/_sitewide-business.html` into the global
`<head>` — every page, including the service pages.

**Per page:** paste the matching `output/<slug>.html` into that page's `<head>`.
Both blocks coexist on a service page; that is the intent, since the page block
references the site-wide one by `@id`.

WordPress, depending on the stack:

- **Rank Math** — Page → Rank Math → Schema → Custom Schema (Code Validation tab), paste the `@graph` array contents. Turn off its auto-generated `WebPage`/`Article` schema for these pages so nodes are not duplicated.
- **Yoast** — Yoast already outputs `WebPage`, `WebSite`, `BreadcrumbList` and an `Organization`. In that case remove the `WebPage` and `BreadcrumbList` nodes from these files, keep the `Service` node, and point its `provider` at Yoast's existing `#organization` `@id` rather than `#business`.
- **No SEO plugin** — a header hook (`wp_head`) or a per-page custom field with a raw HTML block.

Render the JSON-LD server-side, in the initial HTML. Structured data injected
later by JavaScript can face delayed processing.

**Do not ship two of the same node type on one page.** If the theme or plugin
already emits `BreadcrumbList` or an organisation node, drop the duplicate from
these files instead of shipping both.

## Before you publish

1. **Fill in `business-profile.json`.** Everything left empty is omitted from the
   output — the markup stays valid, but thin. `output/VALIDATION-REPORT.md` lists
   exactly what is missing. At minimum: `telephone`, `address`, `logo`, `image`,
   `openingHoursSpecification`, `sameAs`.
2. **Replace the default `areaServed`.** It currently says Australia. Swap in the
   real cities and regions, with `sameAs` Wikidata links per entry.
3. **Reconcile each `description` with the page.** Structured data must describe
   what is actually on the page. Where the page's own wording differs, the page
   wins — edit `services.json` and regenerate.
4. **Check the inclusion lists** in `services.json` against what each page
   advertises, and drop anything the business does not actually offer.
5. **Add prices only if published on the page.** Set `price` in `services.json`
   and an `Offer` is emitted; leave empty and none is.
6. **Only add `aggregateRating` if genuine reviews are visible on that page.**
   Google's review snippet policy disallows marked-up ratings a visitor cannot
   see, and self-serving `LocalBusiness` ratings are ignored.
7. **Confirm the URLs resolve exactly as written** — https, trailing slash — since
   every `@id` is built from them.
8. **Validate** each page through <https://validator.schema.org/> and Google's
   Rich Results Test, then watch Search Console → Unparsable structured data.

## Expected outcome

`Service` markup produces no rich result of its own. It is entity and eligibility
work: it tells Google and AI search surfaces what each page sells, who it is for,
what the customer receives, and that all 11 services belong to one business. The
`BreadcrumbList` node is the part with a visible SERP surface. Schema is not a
ranking factor — treat this as clarity and eligibility, not as a rankings lever.
