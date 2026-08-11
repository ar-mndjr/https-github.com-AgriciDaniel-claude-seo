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

# The Melbourne page's published question set, used as the template.
FAQ_TEMPLATES = [
    (
        "Are your {city} building inspectors qualified?",
        "Every {city} inspection is carried out by a state-registered expert: a Chartered "
        "Engineer, a Licensed Builder, or both. Practitioner registration in {state} is "
        "administered by {regulator}. Because the inspection starts at engineer level, "
        "structural concerns can be assessed on the spot rather than referred to a separate "
        "engineering firm.",
    ),
    (
        "How quickly can I get a building inspection in {city}?",
        "{availability} in {city}. Call 1800 796 776 or book online and we will confirm your "
        "inspection time.",
    ),
    (
        "How much does a building inspection cost in {city}?",
        "From ${priceFrom} inc. GST for a three-bedroom home. Pricing depends on property size, "
        "type and the report level selected, and is confirmed before booking. Because every "
        "inspection starts at engineer level, there is no second inspection fee if you later "
        "need an engineering or dispute-level report.",
    ),
    (
        "What does a pre-purchase building inspection cover in {city}?",
        "All accessible areas of the property: structural elements, roof space and roof "
        "covering, subfloor where accessible, external walls and cladding, internal walls and "
        "ceilings, windows and doors, wet areas, drainage and site conditions. Observations are "
        "documented with photographs and the report follows AS 4349.1.",
    ),
    (
        "Can your report be used in {tribunalShort} proceedings?",
        "Yes. Reports are prepared by a Chartered Engineer to the evidentiary standard required "
        "for {tribunalLong}. Because the inspection data is captured at engineer level on the "
        "first visit, a standard report can be escalated to a dispute-ready expert report "
        "without a second inspection.",
    ),
    (
        "Which suburbs and areas around {city} do you cover?",
        "We cover {city} and the surrounding area, including {surrounds}. If you are outside "
        "that area, call 1800 796 776 and we will confirm availability.",
    ),
]


def fill(text, loc):
    return text.format(**loc)


def build_faq(loc, url):
    """FAQPage mainEntity. Must mirror Q&A published on the page itself."""
    questions = [(fill(q, loc), fill(a, loc)) for q, a in FAQ_TEMPLATES]
    local = loc.get("localRisk")
    if local:
        questions.append((local["question"], local["answer"]))

    return [
        {
            "@type": "Question",
            "@id": f"{url}#faq-{i}",
            "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": answer},
        }
        for i, (question, answer) in enumerate(questions, start=1)
    ]


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
    """WebPage and FAQPage are the same node: one URL, one page entity."""
    site = cfg["site"]["url"].rstrip("/")
    return {
        "@type": ["WebPage", "FAQPage"],
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
        "mainEntity": build_faq(loc, url),
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

    faq_count = sum(len(build_faq({**defaults, **l}, "x")) for l in locations)
    print(f"Wrote {len(locations) * 2 + 1} files to {OUT}")
    print(f"{len(locations)} location pages, {faq_count} FAQ questions total")
    print(
        "\nBefore publishing: every FAQ answer must also be visible on the page.\n"
        "Confirm coverage in WA, ACT, NT and TAS, and that same-week availability\n"
        "and the $495 entry price hold for the regional towns."
    )


if __name__ == "__main__":
    main()
