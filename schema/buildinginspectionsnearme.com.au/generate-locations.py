#!/usr/bin/env python3
"""Generate location-page JSON-LD for buildinginspectionsnearme.com.au.

Writes one self-contained @graph per location page, containing:

  LocalBusiness  the same #organization node the service pages carry
  WebSite
  WebPage + FAQPage  dual-typed, one node for one URL, carrying mainEntity Q&A
  BreadcrumbList
  Service        "Building Inspections in <City>", whose OfferCatalog links the
                 eleven service pages by @id

The business, website and service-page nodes are shared with generate.py so the
two batches cannot describe the same entity two different ways.

Usage: python3 generate-locations.py
"""

import json
import sys

import generate as base

OUT = base.BASE / "output" / "locations"

def build_faq(loc, url):
    """FAQPage mainEntity, built only from Q&A transcribed off the live page.

    There is no template and no fallback: whatever is in the `faq` array is what
    ships. An empty array yields no questions, and the caller then leaves the
    page as a plain WebPage. Generating plausible-sounding questions here would
    put text in the markup that no visitor can see on the page, which breaches
    Google's structured data guidelines.
    """
    questions = []
    for i, entry in enumerate(loc.get("faq", []), start=1):
        question = (entry.get("question") or "").strip()
        answer = (entry.get("answer") or "").strip()
        if not question or not answer:
            sys.exit(
                f"{loc['slug']}: FAQ entry {i} is missing a question or an answer. "
                "Transcribe both from the live page or remove the entry."
            )
        questions.append({
            "@type": "Question",
            "@id": f"{url}#faq-{i}",
            "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": answer},
        })
    return questions


def build_area(loc):
    return {
        "@type": "City",
        "name": loc["city"],
        "containedInPlace": {
            "@type": "State",
            "name": loc["state"],
            "sameAs": loc.get("stateSameAs", ""),
        },
        "sameAs": loc.get("sameAs", ""),
    }


def build_page(cfg, loc, url):
    """The page node. Dual-typed WebPage + FAQPage only when real Q&A exists,
    so one URL stays one page entity rather than two."""
    site = cfg["site"]["url"].rstrip("/")
    faq = build_faq(loc, url)
    return {
        "@type": ["WebPage", "FAQPage"] if faq else "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": f"Building Inspections in {loc['city']}",
        "description": (
            f"Engineer-led building inspections across {loc['city']} and {loc['state']}, "
            f"carried out by Chartered Engineers and Licensed Builders. One inspection covers "
            f"every report level, including engineering and dispute-ready reports."
        ),
        "inLanguage": cfg["site"].get("inLanguage", ""),
        "isPartOf": {"@id": f"{site}/#website"},
        "about": {"@id": base.business_id(cfg)},
        "breadcrumb": {"@id": f"{url}#breadcrumb"},
        "primaryImageOfPage": loc.get("image", ""),
        "mainEntity": faq,
    }


def build_breadcrumb(cfg, loc, url):
    site = cfg["site"]["url"].rstrip("/")
    return {
        "@type": "BreadcrumbList",
        "@id": f"{url}#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site}/"},
            {
                "@type": "ListItem",
                "position": 2,
                "name": f"Building Inspections {loc['city']}",
                "item": url,
            },
        ],
    }


def build_local_service(cfg, loc, url, services):
    """The service offered in this city, cataloguing the eleven service pages."""
    site_url = cfg["site"]["url"]
    catalog = [
        {
            "@type": "Offer",
            "position": position,
            "itemOffered": {
                "@type": "Service",
                "@id": f"{base.page_url(site_url, svc['slug'])}#service",
                "name": svc["name"],
                "url": base.page_url(site_url, svc["slug"]),
            },
        }
        for position, svc in enumerate(services, start=1)
    ]

    channel = {"@type": "ServiceChannel", "serviceUrl": url}
    if cfg["business"].get("telephone"):
        channel["servicePhone"] = {
            "@type": "ContactPoint",
            "telephone": cfg["business"]["telephone"],
            "contactType": "customer service",
        }

    offers = ""
    if loc.get("priceFrom"):
        offers = {
            "@type": "Offer",
            "url": url,
            "availability": "https://schema.org/InStock",
            "priceSpecification": {
                "@type": "PriceSpecification",
                "minPrice": loc["priceFrom"],
                "priceCurrency": loc.get("priceCurrency", "AUD"),
                "valueAddedTaxIncluded": True,
            },
        }

    return {
        "@type": "Service",
        "@id": f"{url}#service",
        "name": f"Building Inspections in {loc['city']}",
        "serviceType": "Building inspection",
        "description": (
            f"Engineer-led building inspections in {loc['city']}, {loc['state']}, covering "
            f"pre-purchase, building and pest, construction stage, defect and dispute "
            f"inspections. Every inspection is conducted by a Chartered Engineer or Licensed "
            f"Builder, so the same site data supports a standard, engineering or "
            f"dispute-ready report without a second visit."
        ),
        "url": url,
        "image": loc.get("image", ""),
        "provider": {"@id": base.business_id(cfg)},
        "providerMobility": "dynamic",
        "areaServed": build_area(loc),
        "serviceOutput": {
            "@type": "Thing",
            "name": (
                "Engineer-led inspection report, upgradeable to an engineering-level or "
                "dispute-ready expert report with no second inspection fee."
            ),
        },
        "availableChannel": channel,
        "offers": offers,
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "@id": f"{url}#offer-catalog",
            "name": f"Building inspection services in {loc['city']}",
            "itemListElement": catalog,
        },
        "mainEntityOfPage": {"@id": f"{url}#webpage"},
    }


def main():
    profile = base.load("business-profile.json")
    services = base.load("services.json")["services"]
    config = base.load("locations.json")
    defaults = config.get("defaults", {})
    locations = config["locations"]

    site_url = profile["site"]["url"]
    OUT.mkdir(parents=True, exist_ok=True)

    business_node = base.build_business(profile, services)
    website_node = base.build_website(profile)

    slugs = set()
    combined = []
    for raw in locations:
        loc = {**defaults, **raw}
        if loc["slug"] in slugs:
            sys.exit(f"Duplicate slug in locations.json: {loc['slug']}")
        slugs.add(loc["slug"])

        url = base.page_url(site_url, loc["slug"])
        graph = base.prune({
            "@context": "https://schema.org",
            "@graph": [
                business_node,
                website_node,
                build_page(profile, loc, url),
                build_breadcrumb(profile, loc, url),
                build_local_service(profile, loc, url, services),
            ],
        })
        (OUT / f"{loc['slug']}.json").write_text(
            json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (OUT / f"{loc['slug']}.html").write_text(base.as_script_tag(graph), encoding="utf-8")
        combined.append({"url": url, "jsonld": graph})

    (OUT / "all-locations.json").write_text(
        json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    with_faq = [l["slug"] for l in locations if l.get("faq")]
    without_faq = [l["slug"] for l in locations if not l.get("faq")]
    priced = [l["slug"] for l in locations if {**defaults, **l}.get("priceFrom")]

    print(f"Wrote {len(locations) * 2 + 1} files to {OUT}")
    print(f"{len(locations)} location pages; {len(with_faq)} carry FAQPage, {len(without_faq)} do not")

    if without_faq:
        print(
            "\nNo FAQ transcribed for these pages, so they emit a plain WebPage with no\n"
            "FAQPage type. That is correct until the real page Q&A is available. To add it,\n"
            "copy each page's published questions and answers verbatim into its `faq` array\n"
            "in locations.json and re-run this script:"
        )
        for slug in without_faq:
            print(f"  - {slug}")

    if len(priced) < len(locations):
        print(
            f"\n{len(locations) - len(priced)} pages emit no Offer, because `priceFrom` is "
            "empty. Set it only where the page publishes a price."
        )

    print(
        "\nAlso confirm: BINM services WA, ACT, NT and TAS with practitioners registered\n"
        "there, and that the generated page and service descriptions match the copy\n"
        "actually published on each page."
    )


if __name__ == "__main__":
    main()
