# Website Outline — April Rose P. Mondejar, SEO Services

## Confirmed decisions
- **Goal:** lead generation for freelance/contract SEO work.
- **Markets:** Australia, New Zealand, US, UK, Europe.
- **Lead magnet:** free basic SEO audit.
- **Pricing model:** one-time setup fee, then a monthly retainer.
- **Case studies:** anonymised — no client names.
- **Platform:** WordPress.

---

## 0. Decide this before you buy a domain

**Use a `.com`, not a `.com.au`.** A country-code domain signals a single market and will work
against you in the US, UK, and Europe. Since you are targeting five regions, `.com` is the only
option that does not handicap four of them. If you have already bought a `.com.au`, keep it as a
redirect and make the `.com` canonical.

Related choices that follow from a five-region target:
- **One English-language site.** No hreflang needed unless you later publish non-English content for Europe.
- **Quote in one currency** — USD is the safest default — and say so, so prospects do not have to ask.
- **State your timezone overlap explicitly.** You are in the Philippines selling to AU, NZ, US, UK, and EU. "Can she work my hours?" is a real objection, so answer it before it is asked: name the hours you overlap with each region.
- **No city or country landing pages at launch.** Five regions of templated location pages is thin content at scale. Build one only if a single market starts dominating your leads, and only when you can write something genuinely specific about it.

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
/pricing/                                    Engagement models + starting prices
/case-studies/                               Results hub (anonymised)
  /case-studies/{industry}-{region}/
/about/
/free-seo-audit/                             Lead magnet
/contact/
/blog/
  /blog/{post}/
/industries/                                 PHASE 2
  /industries/ecommerce-seo/
  /industries/healthcare-seo/
  /industries/real-estate-seo/
  /industries/construction-seo/
/privacy-policy/   /terms/   /thank-you/     Utility
```

Changes from the first draft: location pages are gone, and `/pricing/` is added because a setup fee
plus retainer needs explaining before a prospect will enquire — they need to self-qualify on budget.

---

## 2. The funnel

Your assets need to ladder, not compete:

```
Free basic SEO audit   →   Setup fee (one-time)   →   Monthly retainer
   (lead magnet)            full audit, strategy,       ongoing execution
                            technical fixes, tracking
```

Every service page routes to the free audit. The free audit's follow-up sells the setup. The setup
work ends with a roadmap that only makes sense to execute — which is the retainer.

**The full audit now lives inside the setup fee**, not as a separate product. That is the right call:
it removes a decision point from the funnel, and it stops clients buying the audit and walking away
with your strategy.

This is also why the free audit must stay *basic*. If it solves their problem, there is nothing
left to sell.

---

## 3. Page-by-page

### Home `/`
- **Intent:** branded and "SEO specialist / consultant" searches. Its job is routing and conversion, not heavy ranking.
- **Sections:** value proposition above the fold → **markets served + timezone overlap** → proof strip (anonymised results numbers) → services grid → one flagship case study → how you work → credentials and certifications → FAQ → CTA.
- **CTA:** free basic audit primary, book a call secondary.

### Services hub `/services/`
- **Intent:** "SEO services" commercial.
- **Sections:** how you work → card per service → **how engagements work (setup, then retainer)** → link to pricing → FAQ → CTA.
- Routes and frames; the child pages sell.

### Individual service pages (six, shared template)
One page, one primary keyword, one intent:
- **Problem** in the client's words → **what is included** (concrete deliverables) → **process** → **what you will get** (actual artifacts) → **proof** (linked case study) → **how it is delivered** (in setup, in the retainer, or both) → **FAQ** with FAQPage schema → **CTA to the free audit**.

| Page | Primary intent |
|---|---|
| `/services/technical-seo-audit/` | "technical SEO audit" — your strongest differentiator and the paid entry offer |
| `/services/ecommerce-seo/` | "ecommerce SEO" / "Shopify SEO" |
| `/services/local-seo/` | "local SEO services" |
| `/services/generative-engine-optimization/` | "GEO" / "AI search optimization" — low competition, high growth |
| `/services/seo-content-optimization/` | "SEO content optimization" |
| `/services/wordpress-website-development/` | "WordPress SEO / website development" |

### Pricing `/pricing/`
- **Model:** a one-time setup fee, then a monthly retainer.
- **Why it exists:** a two-part price is harder to grasp than a single number, and an unexplained setup fee reads as padding. This page is where it becomes obvious why the first month costs more.
- **Sections:** how engagements work (the two-part structure, in one short paragraph) → **what the setup covers**, itemised → **retainer tiers** with what each includes → minimum term → what changes the price → what you do not do → FAQ → CTA.

**Getting the setup fee to land:**
- **Itemise it.** Full technical audit, keyword and intent map, site architecture plan, priority fixes, GA4 and Search Console configuration, reporting setup. A setup fee is only defensible as a list of deliverables, never as a line item called "setup".
- **Name it for its value, not its function.** "Foundation & Strategy" or "SEO Onboarding" rather than "setup fee".
- **Common benchmark:** setup lands around 1-2x the monthly retainer. Enough to cover genuinely front-loaded work, not so much that it blocks the first yes.
- **State a minimum term** — 3 or 6 months. SEO cannot show results in one month, and saying so upfront filters out clients who will churn angry in week 6.
- **Tier the retainer** by scope (pages, content volume, channels), not by vague "hours". Hours invite micro-management.
- State the currency and that you invoice internationally.

**The one risk of this model:** it raises the barrier to the first yes, because the client pays the
most before seeing any results. Two things carry that weight — the free audit, which has to be good
enough that they already trust your judgement, and the itemised setup list, which has to read as
obviously worth it. Get both right and the setup fee stops being an objection.

### Case studies `/case-studies/` — anonymised
Anonymity costs you credibility, so replace the client name with **specificity everywhere else**:

- **Title the studies by industry and region**, not client: `/case-studies/shopify-fashion-retailer-au/`, `/case-studies/healthcare-clinic-network-uk/`.
- **Describe the client precisely without naming them:** "a 40-location Australian allied health network", "a UK Shopify fashion retailer, ~$2M annual revenue".
- **Lead with the number and the timeframe.** Anonymous studies live or die on whether the metrics feel real: "organic traffic +38% in 6 months", not "significant growth".
- **Use redacted screenshots** — GSC and GA4 graphs with the property name blurred. Far more convincing than a number in text.
- **Get a testimonial even if anonymous.** "Head of Marketing, Australian healthcare network" is worth much more than nothing.
- **Say why they are anonymised** in one line ("client work under NDA"). Unexplained anonymity reads as fabricated; explained anonymity reads as professional.
- These rank well for "[vertical] SEO case study" long-tail, and feed AI assistants asking for proof.

### About `/about/`
- Your main E-E-A-T and entity page, and it carries more weight now that case studies are anonymous — you are the verifiable credential.
- **Sections:** your story → credentials, certifications, education → tools and methodology → **markets and timezones** → industries served → photo → CTA.
- Person schema, linked LinkedIn, name/role/location stated as plain facts. This is what AI assistants extract.

### Free SEO audit `/free-seo-audit/`
- Scope it as **basic** and say so: name exactly what they get (e.g. a 10-point technical review plus a short Loom) and what it is not.
- Short form — URL, email, main goal. Every extra field costs conversions.
- Route to `/thank-you/` for GA4 conversion tracking.
- The follow-up email sequence is where the paid audit gets sold. Plan it alongside the page.

### Contact `/contact/`
- Form, email, **timezone and overlap hours per region**, expected response time.
- Person/LocalBusiness schema.

### Blog `/blog/`
- Informational intent only — keep commercial intent on the service pages or they will cannibalise each other.
- Earns links and citations: original data or teardowns, "how to fix X" technical guides, GEO/AI-search commentary while the topic is underserved.
- Every post links to a relevant service page.

### Industries `/industries/{vertical}/` — Phase 2
- Ecommerce, healthcare, real estate, construction — the four you have real experience in.
- Each needs genuinely vertical-specific substance (healthcare compliance constraints, real-estate listing-page architecture). If you cannot write something specific, do not publish it.

---

## 4. GEO layer — practise what you sell

You are selling GEO, so the site has to demonstrate it. Prospects and AI assistants will both check.

- **Answer-first structure.** Lead with the direct, quotable answer, then elaborate.
- **Schema:** Person, Service, FAQPage, Article, BreadcrumbList.
- **Entity clarity.** Name, role, location, specialisms stated as plain facts in consistent wording sitewide and matching your LinkedIn.
- **FAQ blocks** on every commercial page — this is what gets pulled into AI Overviews.
- **`/llms.txt`** at the root.
- **Track your own citations** across ChatGPT, Claude, Gemini, and Perplexity — and turn the results into a case study. "I rank in AI search for my own service terms" is the most direct proof you can offer a GEO client.

---

## 5. Build order

**Phase 1 — launch (12-14 pages).** Home, services hub, 3 strongest service pages, pricing, about,
contact, free audit, thank you, privacy, terms. Ship and start collecting leads.

**Phase 2 — depth.** Remaining 3 service pages, first 3 anonymised case studies, blog with 5-8 posts.

**Phase 3 — expansion.** Industry pages, more case studies. Revisit region pages only if one market
clearly dominates your leads.

---

## 6. Before you write copy

1. **Keyword research per page** — one primary keyword and intent per URL, mapped in a sheet, before drafting.
2. **Check cannibalisation** across service pages, industry pages, and blog. The most common failure mode for a services site.
3. **Plan the free-audit follow-up sequence** at the same time as the page. The lead magnet is worthless without it.
4. **GA4, Search Console, and conversion tracking on day one.**
5. **Collect testimonials now**, even anonymous role-level ones. They matter more than usual given anonymised case studies.
