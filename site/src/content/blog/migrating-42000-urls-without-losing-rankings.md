---
title: "Migrating 42,000 URLs without losing a single ranking"
description: "The exact redirect mapping, staging checks and launch-day runbook behind our +185% enterprise migration. Copy it for your next replatform."
date: "2026-08-07"
category: "seo"
subcategory: "Migrations / Case Study"
read_time: 15
cover: "migrate"
cover_image: ""
metric: "+185%"
metric_label: "Organic clicks (6 mo)"
featured: false
popular: true
draft: false
author: "April"
tags: ["migrations", "technical-seo", "redirects", "case-study"]
tldr: ["Build the URL inventory from logs and backlinks, not just a crawl. Ours found 6,140 hidden URLs.", "Keep redirects in version control and fail CI on chains or broken targets.", "Replay every URL against staging before launch, then again in production."]
highlights: [{"value": "42,318", "label": "URLs migrated"}, {"value": "+185%", "label": "Organic clicks"}, {"value": "40 min", "label": "Launch window"}]
---

When a B2B SaaS company asked us to move their marketing site, docs and blog onto a new platform, they had one condition: **organic traffic could not drop**. It was their largest acquisition channel, driving 61% of qualified pipeline.

Most replatforms lose 10–40% of organic traffic for months. Ours grew 185% in six months. Nothing clever happened on launch day. We treated the migration as an engineering project with tests, not a marketing project with a checklist.

## Why migrations kill rankings

Google doesn't rank "your site". It ranks individual URLs, each carrying years of links, click history and relevance signals. A migration breaks the link between those signals and the content unless every old URL points cleanly to its new equivalent.

In practice, rankings are lost in three ways:

- **Orphaned URLs** that 404 because nobody knew they existed.
- **Redirect chains** (A → B → C) that leak authority and slow down crawling.
- **Content drift**, where the new page no longer matches the query the old one ranked for.

## Build a complete URL inventory

Your sitemap is not your inventory. We merged five sources and de-duplicated them into one list of **42,318 URLs**:

1. A full crawl of the live site.
2. Twelve months of server logs (every URL Googlebot actually requested).
3. Search Console pages with at least one impression.
4. Every URL with an external backlink.
5. Analytics landing pages with at least one session.

> **The logs found 6,140 URLs the crawler missed.** Old campaign pages and PDF guides, still linked from partner sites, still sending traffic.

## Write the redirect map as code

Spreadsheets break at this scale. We kept the redirect map as a versioned file with rules for patterns and explicit entries for the exceptions, then generated edge redirects from it:

```ts
// Pattern rules cover ~90% of URLs; explicit entries win on conflict
export const rules = [
  { from: "/blog/:year/:month/:slug", to: "/blog/:slug" },
  { from: "/docs/v1/:path*",         to: "/docs/:path*" },
  { from: "/resources/guides/:slug.pdf", to: "/guides/:slug" },
];

export const explicit = loadCsv("./redirects/explicit.csv"); // 3,904 rows

// CI fails if any rule creates a chain or points to a non-200 page
assertNoChains(rules, explicit);
assertAllTargetsResolve(rules, explicit);
```

Because it's code, every change is reviewed, and the checks at the bottom run on every commit. A redirect chain can't reach production.

## Validate on staging, not in production

Before launch, we replayed all 42,318 URLs against staging and checked the status code, final destination, title and canonical for each one:

| Check | URLs tested | Pass rate | Status |
| --- | --- | --- | --- |
| Single-hop 301 to a 200 page | 42,318 | 100% | ✓ PASS |
| Canonical matches final URL | 38,412 | 100% | ✓ PASS |
| Title similarity ≥ 80% | 38,412 | 98.7% | ✓ REVIEWED |
| Internal links point to final URLs | 211,906 | 100% | ✓ PASS |

> A migration that hasn't been replayed against staging is a guess. We don't ship guesses to a channel that drives 61% of pipeline.

## Launch day runbook

Launch day itself should be boring. Ours took 40 minutes:

1. Deploy the new site and edge redirects together, in a single release.
2. Re-run the staging replay against production. Any failure triggers an instant rollback.
3. Submit the new sitemaps and keep the old sitemap live for 30 days so Google re-crawls the redirects.
4. Watch 404s and crawl stats in real time for the first 72 hours.

> **Don't remove the old sitemap on launch day.** Keeping it live is how you get Google to find your redirects fast instead of over several months.

## Results after six months

Organic clicks grew **+185%**, with **zero 404 indexing errors** and a **0.71s median LCP**.

Traffic didn't just hold. It grew, because the new platform was faster, had cleaner internal linking and let us fix years of thin, duplicated pages at the same time.

## Key takeaways

- Build your inventory from logs and backlinks, not just a crawl.
- Keep redirects in version control and test them in CI.
- Replay every URL against staging before launch.
- Keep the old sitemap live for 30 days after launch.

Planning a replatform? [Send us your URL count](/contact/) and we'll tell you where the risk is, free.
