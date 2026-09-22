# Website Outline — April Rose P. Mondejar, SEO Services

## Assumptions behind this structure
- **Goal:** lead generation for freelance/contract SEO work, not a blog or portfolio for its own sake.
- **Primary market:** Australia (your current contracts), with US/UK/NZ remote as secondary.
- **Platform:** WordPress, since it is your strongest and cheapest to iterate on.
- **Launch lean.** Phase 1 is 10-12 pages. Do not publish 40 thin pages on a new domain.

If any of these are wrong — especially the market — the location and industry sections change.

---

## 1. URL map

```
/                                            Home
/services/                                   Services hub
  /services/technical-seo-audit/
  /services/ecommerce-seo/
  /services/local-seo/
  /services/generative-engine-optimization/
  /services/seo-content-optimization/
  /services/wordpress-website-development/
/case-studies/                               Results hub
  /case-studies/{client-or-niche}/
/about/
/free-seo-audit/                             Lead magnet / conversion page
/contact/
/blog/
  /blog/{post}/
/industries/                                 PHASE 2
  /industries/ecommerce-seo/
  /industries/healthcare-seo/
  /industries/real-estate-seo/
  /industries/construction-seo/
/seo-services-{city}/                        PHASE 3, only if genuinely localised
/privacy-policy/   /terms/   /thank-you/     Utility
```

**Why this shape.** Services are the money pages and sit one click from home. Industries are a
second commercial layer that catches "SEO for [vertical]" searches without diluting the service
pages. The blog is informational only — keep commercial intent out of it, or it will cannibalise
the pages that need to rank.

---

## 2. Page-by-page

### Home `/`
- **Intent:** branded and "SEO specialist / consultant" searches. Not your hardest-working ranking page — its job is routing and conversion.
- **Sections:** value proposition above the fold (who you help, what result, how) → proof strip (client logos or results numbers) → services grid linking to all six service pages → one flagship case study → how you work (3-4 steps) → credentials and certifications → FAQ → primary CTA.
- **CTA:** book a call, with free audit as the secondary.
- **Links out to:** every service page, top case study, about, contact.

### Services hub `/services/`
- **Intent:** "SEO services" commercial.
- **Sections:** short intro framing your approach → card per service with a one-line outcome and link → engagement models (one-off audit, project, monthly retainer) → pricing signal, even just "from $X" or "projects start at" → FAQ → CTA.
- Do not let this page duplicate the child pages. It routes and frames; children sell.

### Individual service pages (six, same template)
One page, one primary keyword, one intent. Template:
- **Problem** the client has, in their words.
- **What is included** — concrete deliverables, not adjectives.
- **Process** — what happens week by week.
- **What you will get** — the actual artifacts (audit doc, keyword map, monthly report).
- **Proof** — a relevant case study or result, linked.
- **Pricing or engagement model.**
- **FAQ** — 5-8 real questions, marked up with FAQPage schema.
- **CTA.**

Suggested primary targets:
| Page | Primary intent |
|---|---|
| `/services/technical-seo-audit/` | "technical SEO audit" — your strongest differentiator, highest-value entry offer |
| `/services/ecommerce-seo/` | "ecommerce SEO" / "Shopify SEO" |
| `/services/local-seo/` | "local SEO services" |
| `/services/generative-engine-optimization/` | "GEO" / "AI search optimization" — low competition now, high growth |
| `/services/seo-content-optimization/` | "SEO content optimization" |
| `/services/wordpress-website-development/` | "WordPress SEO / website development" |

### Case studies `/case-studies/`
- Hub page listing results, each with the headline number visible before the click.
- One page per study: client context → problem → what you did → results with real numbers and a timeframe → tools used → testimonial if you can get one.
- **These do triple duty:** conversion proof, long-tail rankings ("Shopify SEO case study"), and E-E-A-T signals for both Google and AI assistants.
- You already have a case-study workflow — reuse it here.

### About `/about/`
- More important than most freelancers think. It is your main E-E-A-T and entity page.
- **Sections:** your story and why SEO → credentials, certifications, education → tools and methodology → industries served → photo → CTA.
- Mark up with Person schema, link your LinkedIn and any author profiles, and keep your name, role, and location stated as plain facts — this is what AI assistants extract when someone asks "who is a good SEO specialist for X".

### Free SEO audit `/free-seo-audit/`
- Your lead magnet and likely your highest-converting page.
- Set a boundary: what they get (e.g. a 10-point technical review and a short Loom), and what it is not (a full audit).
- Short form: URL, email, main goal. Every field you add costs conversions.
- Route to `/thank-you/` so you can track the conversion in GA4.

### Contact `/contact/`
- Form, email, timezone and working hours, expected response time, and what to include in the message.
- LocalBusiness or Person schema with contact details.

### Blog `/blog/`
- Informational intent only. Purpose: topical authority, internal links to service pages, and AI citation surface.
- Post types that earn links and citations: original data or teardowns, "how to fix X" technical guides, and GEO/AI-search commentary while the topic is still underserved.
- Every post links to a relevant service page. That is the whole point.

### Industries `/industries/{vertical}/` — Phase 2
- One per vertical you have real experience in: ecommerce, healthcare, real estate, construction.
- Each needs genuinely vertical-specific content — the compliance issues in healthcare SEO, the listing-page architecture problem in real estate. If you cannot write something specific, do not publish the page.

### Location pages — Phase 3, conditional
- Only build these if you are genuinely targeting named cities and can differentiate each page. Duplicating a template with the city swapped is the fastest way to a thin-content problem.
- If your positioning is "remote specialist for Australian businesses", a single well-optimised page plus the about page covers it better.

---

## 3. GEO layer — practise what you sell

You are selling Generative Engine Optimization, so the site has to be a demonstration of it.
Prospects and AI assistants will both check.

- **Answer-first structure.** Lead sections with a direct, quotable answer, then elaborate. AI assistants cite the extractable sentence.
- **Schema:** Person, Service, FAQPage, Article, BreadcrumbList.
- **Entity clarity.** State your name, role, location, and specialisms as plain facts in consistent wording across the site, and keep them consistent with your LinkedIn.
- **FAQ blocks** on every commercial page — these are what get pulled into AI Overviews.
- **`/llms.txt`** at the root describing who you are and what you offer.
- **Track it.** Monitor brand mentions and citations in ChatGPT, Claude, Gemini, and Perplexity, and use the results as case-study material.

---

## 4. Build order

**Phase 1 — launch (10-12 pages).** Home, services hub, 3 strongest service pages, about, contact,
free audit, thank you, privacy, terms. Ship it and start collecting leads.

**Phase 2 — depth.** Remaining 3 service pages, first 3 case studies, blog with 5-8 posts.

**Phase 3 — expansion.** Industry pages, location pages if justified, more case studies.

Resist building everything before launch. A live 10-page site collecting leads beats a perfect
40-page site that never ships.

---

## 5. Before you write a word of copy

1. **Keyword research per page.** One primary keyword and intent per URL, mapped in a sheet, before any drafting. Your own discipline — apply it here.
2. **Check for cannibalisation** between the service pages, industry pages, and blog. This is the most common failure in a services site.
3. **Decide on pricing transparency.** Showing a starting price filters out bad leads and increases qualified conversions. Most freelancers hide it and regret it.
4. **Set up GA4, Search Console, and conversion tracking on day one**, not after launch.

---

## 6. Open questions

- Is Australia the primary market, or are you positioning globally?
- Do you want to lead with the audit as a paid entry offer, or keep it free as a lead magnet?
- Are you selling retainers, projects, or both? This changes the services hub and pricing sections.
- Do you have client permission to publish named case studies, or do they need anonymising?
