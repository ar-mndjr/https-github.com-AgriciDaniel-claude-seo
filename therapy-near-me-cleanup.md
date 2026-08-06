# Therapy Near Me — Cleanup Remediation Map

**Domain:** https://therapynearme.com.au/
**Date of audit:** 2026-08-06
**Scope:** (1) remove AirVolt, (2) correct psAIch launch date, (3) remove junk author records

---

## How this was scoped (and what could not be verified)

Direct HTTP access to `therapynearme.com.au` is blocked by this session's egress policy
(the proxy returned `403` to `CONNECT therapynearme.com.au:443`; all outbound fetching,
including `example.com`, is denied). **No page HTML was read.**

Everything below is derived from two sources that were reachable:

- **Google Search Console** (`sc-domain:therapynearme.com.au`, via the Windsor.ai connector) —
  authoritative for which URLs exist, are indexed, and get impressions.
- **Web search result snippets** — used for on-page wording, quoted below as *reported copy*.

**Consequence:** URLs and their traffic are verified. The *exact sentences and their exact
position in the template* are not — whoever applies these edits must confirm each wording
against the live page before deleting or rewriting it.

**Platform:** WordPress. Evidence: `https://therapynearme.com.au/sitemap_index.xml`
(sitemap index, **1,179 URLs submitted**, last downloaded 2026-07-30) and paginated
`/author/{slug}/page/N` archives — both Yoast/RankMath-on-WordPress signatures.
A legacy GoDaddy Website Builder blog still runs in parallel at `/mental-health-blog/f/{slug}`.

---

## 1. Remove AirVolt from the Therapy Near Me domain

### 1a. The dedicated page — delete

| URL | Impressions (12mo) | Impressions (3mo) | Avg. position |
|---|---|---|---|
| `https://therapynearme.com.au/airvolt/` | 370 | 127 | **6.5** |

Current title tag: *"AirVolt | Sustainable Energy Powering AI Mental Health Support | Therapy Near Me"*

It ranks for the brand query `airvolt` (46 impressions) and also surfaces for `psaich`
(6 impressions), so it is cross-linked with the psAIch page.

**Actions**
1. Delete the WordPress page (don't just unpublish — unpublished WP pages can stay reachable
   via cached/attachment routes).
2. Return **`410 Gone`**, not a `301`. The content is being retracted, not moved; there is no
   equivalent destination, and a 301 to the homepage passes retracted claims' equity forward
   and keeps the URL alive in Search Console.
3. Remove the URL from `sitemap_index.xml` and resubmit.
4. Remove every nav entry, footer link, and in-body internal link pointing at `/airvolt/`.
5. Submit a **removal request** in Search Console for `/airvolt/` to drop it from the SERP
   faster than the 410 alone will.

> ⚠️ **Do not redirect to `airvolt.energy`.** That domain belongs to an unrelated third-party
> wind-energy company, not to Therapy Near Me. Redirecting there would point users at a
> stranger's commercial site.

### 1b. AirVolt claims embedded in other pages — strip

These pages carry AirVolt copy in-body and will still assert the claims after `/airvolt/` is gone:

| URL | Why it's in scope |
|---|---|
| `https://therapynearme.com.au/psaich/` | Carries the "psAIch is powered by AirVolt" block |
| `https://therapynearme.com.au/about-us` | Carries the patent + dual-turbine claim; surfaces for the `psaich` query |

**Reported copy to locate and remove** (verify wording on the live pages first):

- "holds the patents behind AirVolt"
- "converting kinetic and thermal energy into electricity using a **dual-turbine mechanism**"
- "a patented form of **atmospheric energy conversion** that does not rely on wind, solar, or
  grid infrastructure"
- "AirVolt units are designed to be compact, portable, and scalable"
- "AirVolt actively offsets the computing power used by psAIch — every chat and insight
  powered by renewable energy"
- "so psAIch and the upcoming mobile app can scale without contributing to carbon emissions"

**Also check** (not visible via GSC, needs a live crawl once access is restored):
`Organization` / `Product` schema blocks, OG tags, any `sameAs` array pointing at AirVolt
properties, and the media/press page if one exists.

**Why this matters beyond tidiness:** these are unverifiable energy-generation and
carbon-offset claims sitting on a registered health-service domain. Both the ACCC
(misleading conduct / environmental claims) and AHPRA advertising guidelines apply. This is
the highest-risk item of the three.

---

## 2. Correct psAIch — remove the September 2025 launch promise, change to 2026

| URL | Impressions (12mo) | Impressions (3mo) | Avg. position |
|---|---|---|---|
| `https://therapynearme.com.au/psaich/` | 877 | 239 | **6.5** |

The brand query `psaich` drew **386 impressions / 10 clicks**, so this is a page real people
reach by name — a stale launch date is visible to exactly the audience that cares.

**Secondary page:** `https://therapynearme.com.au/about-us` also surfaces for `psaich` and
carries launch framing.

**The problem in the reported copy:** the page simultaneously says Therapy Near Me is
*"preparing to launch psAIch"* and that the app is *"currently in beta at
therapynearme.com.au"*. A September 2025 date on a page read in August 2026 is eleven months
past due, and "preparing to launch" contradicts "in beta".

**Actions**
1. Replace every "September 2025" with the intended **2026** date.
2. Resolve the contradiction — pick either "in beta now" or "launching [2026 date]", not both.
   If the date is not firm, drop the date entirely rather than setting up the next stale promise.
3. **Sweep all the places a date hides**, not just the visible hero:
   - H1 / hero subheading
   - meta description and `<title>`
   - Open Graph / Twitter card description
   - FAQ schema `acceptedAnswer` text
   - any `Event`, `Product`, or `SoftwareApplication` schema with a `releaseDate` /
     `startDate` / `datePublished`
   - the `/about-us` paragraph
   - alt text and any hero image with the date baked into the graphic
4. Update `dateModified` so the correction is picked up on recrawl.

---

## 3. Remove anonymous, obsolete, and email-address author records

The site runs **two** author systems. One is legitimate and should stay; the other is
WordPress default author archives leaking junk into the index.

### Keep — the curated author profiles

| URL | Impressions (12mo) | Clicks |
|---|---|---|
| `/authors/julia-tilling-phd` | 86 | 2 |
| `/authors/rona-castaneda` | 77 | 3 |
| `/authors/chantal-santacaterina` | 56 | 10 |
| `/authors` (index) | 6 | 0 |

These are real, named, credentialed people. They are the E-E-A-T asset. Leave them alone.

### Remove — the WordPress `/author/` archives

| URL | Problem | Impressions (12mo) | Still live in last 3mo? |
|---|---|---|---|
| `/author/franklinwee79gmail-com/` | **Email address as author slug** — `franklinwee79@gmail.com` is exposed in the URL. Indexed at `/page/12`, `/page/87`, `/page/96`. | 6 | No |
| `/author/fantasive/` | Anonymous handle, no real identity | 3 | Yes (avg. position 31) |
| `/author/therapynearme/` | Generic/obsolete non-person. Archives paginate to **`/page/106`** — roughly a thousand posts attributed to nobody. Indexed at `/page/29`, `/page/31`, `/page/106`. | 8 | Yes |

The `franklinwee79gmail-com` record is the urgent one: a personal Gmail address is sitting in
a public, indexed URL path. That is a privacy exposure, not just an SEO defect — treat it as
the first fix in this section.

**Actions**
1. **WP Admin → Users:** for each of the three accounts, delete the user and use
   *"Attribute all content to…"* to reassign posts to a real author from `/authors/`.
   Deleting without reassigning will delete the posts.
2. **Disable author archives entirely.** Since `/authors/` is the real author system,
   `/author/*` serves no purpose. In Yoast: *Search Appearance → Archives → Author archives →
   Disabled*. In RankMath: *Titles & Meta → Authors → Author Archives → Off*. This kills every
   current and future junk archive in one setting.
3. Return **`410 Gone`** for `/author/*` (a 301 to `/authors/` would be a soft-404 —
   the destinations aren't equivalent pages).
4. Remove all `/author/*` URLs from `sitemap_index.xml`.
5. **Search Console removal request** for `/author/franklinwee79gmail-com/*` specifically,
   to pull the email address out of the SERP without waiting for recrawl.
6. **Fix the underlying schema.** Deleting the archive page does not fix the `author` field in
   each post's `Article` JSON-LD. Audit article schema for `author.name` values that are
   email addresses, `fantasive`, or `therapynearme`, and repoint them at named humans.
7. Check the visible post bylines on the ~1,000 reassigned posts render the new author
   correctly rather than falling back to a blank or "admin".

---

## Adjacent issue found while scoping (out of scope — flagging only)

The site is serving **the same articles on two URL paths**: the WordPress root permalink and
the legacy GoDaddy blog path. Examples from GSC:

| Article | Root URL | Legacy blog URL |
|---|---|---|
| Solution-focused therapy | `/solution-focused-therapy-…` (458 impr) | `/mental-health-blog/f/solution-focused-therapy-…` (719 impr) |
| Holistic psychology | `/holistic-psychology-…` (1 impr) | `/mental-health-blog/f/holistic-psychology-…` (137 impr) |
| Psychological tips / attractive | `/psychological-tips-…` (10 impr) | `/mental-health-blog/f/psychological-tips-…` (808 impr) |
| Virtual reality therapy | `/virtual-reality-therapy-…` (3 impr) | `/mental-health-blog/f/virtual-reality-therapy-…` (32 impr) |

This is site-wide duplicate content splitting ranking signals across paired URLs. It is a
larger consolidation project than the three items requested here — raising it, not actioning it.

---

## Suggested order of work

1. `/author/franklinwee79gmail-com/*` — personal email in a public URL (privacy)
2. AirVolt removal — `/airvolt/` + the in-body claims on `/psaich/` and `/about-us` (regulatory)
3. psAIch date correction (credibility, and it's a small edit)
4. Remaining author archives + the Yoast/RankMath author-archive kill switch
5. Sitemap resubmission and Search Console removal requests for everything 410'd

## Verification once egress is restored

- `curl -I` each removed URL → expect `410`
- Re-fetch `sitemap_index.xml` → submitted count should drop from 1,179
- Grep live HTML of `/psaich/` and `/about-us` for `AirVolt`, `airvolt`, `September 2025`, `2025`
- Grep article JSON-LD for `author.name` matching `@`, `fantasive`, `therapynearme`
- Re-run the GSC page query in ~4 weeks to confirm the `/author/*` and `/airvolt` rows drop out
