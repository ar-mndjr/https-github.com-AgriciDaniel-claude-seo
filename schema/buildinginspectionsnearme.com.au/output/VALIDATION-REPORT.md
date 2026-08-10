# Schema validation report

Generated files: 11 self-contained service page graphs.

Every value below was left empty in the config and was therefore omitted from the
generated JSON-LD rather than shipped as placeholder text. The markup is valid as
generated; filling these in makes it complete.

- `business.logo` is empty and was omitted. Absolute URL to the logo image.
- `business.image` is empty and was omitted. Absolute URL to a business photo.
- `business.email` is empty and was omitted. Public contact email address.
- `business.address` is incomplete and the whole address node was omitted. Missing: streetAddress, addressLocality, addressRegion, postalCode. LocalBusiness types require an address; add the registered or trading address, or drop the LocalBusiness subtype and keep Organization only.
- `business.geo` is empty and was omitted. Use at least 5 decimal places.
- `business.openingHoursSpecification` is empty and was omitted. Add real hours that match the website and Google Business Profile.
- `business.sameAs` is empty and was omitted. Add the Google Business Profile, Facebook, LinkedIn and any directory profiles that confirm the entity.
- `business.aggregateRating` is empty and was omitted. Only add it if genuine reviews are visible on the page itself.
- `image` is empty and was omitted for these services: existing-buildings, renovations-and-extensions, new-buildings, adjoining-works-protection, pre-purchase-inspection, strata-inspection, building-insurance-assessment, building-warranty-defect-inspection, building-and-pest-inspections, commercial-building-inspections, pre-auction-building-inspection. Add the hero image URL from each page.

## Before publishing

1. Confirm each `description` matches the copy actually on that page.
2. Run every generated file through https://validator.schema.org/ and the
   Google Rich Results Test.
3. Confirm the page URLs resolve exactly as written (trailing slash, https).
