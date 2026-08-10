# Schema validation report

Generated files: 11 service pages + 1 site-wide graph.

Every value below was left empty in the config and was therefore omitted from the
generated JSON-LD rather than shipped as placeholder text. The markup is valid as
generated; filling these in makes it complete.

- `business.telephone` is empty and was omitted. Phone number. Must match the site's NAP and Google Business Profile.
- `business.logo` is empty and was omitted. Absolute URL to the logo image.
- `business.image` is empty and was omitted. Absolute URL to a business photo.
- `business.description` is empty and was omitted. One-paragraph description of the business.
- `business.priceRange` is empty and was omitted. Short price indicator, e.g. '$$'. Under 100 characters.
- `business.email` is empty and was omitted. Public contact email address.
- `business.address` is incomplete and the whole address node was omitted. Missing: streetAddress, addressLocality, addressRegion, postalCode. LocalBusiness types require an address; add the registered or trading address, or drop the LocalBusiness subtype and keep Organization only.
- `business.geo` is empty and was omitted. Use at least 5 decimal places.
- `business.openingHoursSpecification` is empty and was omitted. Add real hours that match the website and Google Business Profile.
- `business.sameAs` is empty and was omitted. Add the Google Business Profile, Facebook, LinkedIn and any directory profiles that confirm the entity.
- `business.aggregateRating` is empty and was omitted. Only add it if genuine reviews are visible on the page itself.
- `business.areaServed` is still the default (Australia). Replace it with the cities and regions actually serviced.
- `services[existing-buildings].image` is empty and was omitted.
- `services[renovations-and-extensions].image` is empty and was omitted.
- `services[new-buildings].image` is empty and was omitted.
- `services[adjoining-works-protection].image` is empty and was omitted.
- `services[pre-purchase-inspection].image` is empty and was omitted.
- `services[strata-inspection].image` is empty and was omitted.
- `services[building-insurance-assessment].image` is empty and was omitted.
- `services[building-warranty-defect-inspection].image` is empty and was omitted.
- `services[building-and-pest-inspections].image` is empty and was omitted.
- `services[commercial-building-inspections].image` is empty and was omitted.
- `services[pre-auction-building-inspection].image` is empty and was omitted.

## Before publishing

1. Confirm each `description` matches the copy actually on that page.
2. Run every generated file through https://validator.schema.org/ and the
   Google Rich Results Test.
3. Confirm the page URLs resolve exactly as written (trailing slash, https).
