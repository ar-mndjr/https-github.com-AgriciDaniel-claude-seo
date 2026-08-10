#!/usr/bin/env python3
"""Generate Service JSON-LD for buildinginspectionsnearme.com.au service pages.

Reads business-profile.json + services.json and writes, per service page, a
JSON-LD @graph containing WebPage, BreadcrumbList and Service nodes, plus one
site-wide LocalBusiness/WebSite graph.

Design rules:
  * Empty config values are omitted, never emitted as placeholder text. Missing
    recommended fields are collected into output/VALIDATION-REPORT.md.
  * Every node carries a stable @id so nodes reference each other instead of
    being duplicated across pages.

Usage: python3 generate.py
"""

import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent
OUT = BASE / "output"

# A node carrying only these keys has no content of its own and is dropped.
# `@id` is deliberately absent: `{"@id": "..."}` is a reference to another node
# in the graph and must survive pruning.
STRUCTURAL_KEYS = {"@type", "@context"}

# Recommended-but-missing fields worth flagging in the validation report.
BUSINESS_CHECKS = [
    ("telephone", "Phone number. Must match the site's NAP and Google Business Profile."),
    ("logo", "Absolute URL to the logo image."),
    ("image", "Absolute URL to a business photo."),
    ("description", "One-paragraph description of the business."),
    ("priceRange", "Short price indicator, e.g. '$$'. Under 100 characters."),
    ("email", "Public contact email address."),
]
ADDRESS_CHECKS = ["streetAddress", "addressLocality", "addressRegion", "postalCode"]


def load(name):
    path = BASE / name
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        sys.exit(f"Missing config file: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"Invalid JSON in {path}: {exc}")


def prune(node):
    """Drop empty values recursively; drop nodes left with no real content."""
    if isinstance(node, dict):
        cleaned = {}
        for key, value in node.items():
            if key.startswith("_") or key.startswith("$"):
                continue
            value = prune(value)
            if value in (None, "", [], {}):
                continue
            cleaned[key] = value
        if not set(cleaned) - STRUCTURAL_KEYS:
            return None
        return cleaned
    if isinstance(node, list):
        items = [prune(item) for item in node]
        return [item for item in items if item not in (None, "", [], {})]
    if isinstance(node, str):
        return node.strip()
    return node


def page_url(site_url, slug):
    return f"{site_url.rstrip('/')}/{slug}/"


def build_area_served(entries):
    areas = []
    for entry in entries or []:
        areas.append({
            "@type": entry.get("type", "Place"),
            "name": entry.get("name", ""),
            "sameAs": entry.get("sameAs", ""),
        })
    return areas


def build_business(cfg):
    business = cfg["business"]
    site = cfg["site"]
    business_id = f"{site['url'].rstrip('/')}/#business"

    address = dict(business.get("address", {}))
    address["@type"] = "PostalAddress"
    if not any(address.get(field) for field in ADDRESS_CHECKS):
        # An address with only a country is not useful; let prune drop it.
        address = {}

    geo = business.get("geo", {})
    rating = business.get("aggregateRating", {})

    hours = []
    for spec in business.get("openingHoursSpecification", []):
        hours.append({
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": spec.get("dayOfWeek", []),
            "opens": spec.get("opens", ""),
            "closes": spec.get("closes", ""),
        })

    identifier = business.get("identifier", {})
    identifier_node = ""
    if identifier.get("value"):
        identifier_node = {
            "@type": "PropertyValue",
            "propertyID": identifier.get("propertyID", ""),
            "value": identifier["value"],
        }

    node = {
        "@type": business.get("types", ["LocalBusiness"]),
        "@id": business_id,
        "name": business.get("name", ""),
        "legalName": business.get("legalName", ""),
        "alternateName": business.get("slogan", ""),
        "description": business.get("description", ""),
        "url": business.get("url", "") or site["url"],
        "logo": business.get("logo", ""),
        "image": business.get("image", "") or business.get("logo", ""),
        "telephone": business.get("telephone", ""),
        "email": business.get("email", ""),
        "priceRange": business.get("priceRange", ""),
        "currenciesAccepted": business.get("currenciesAccepted", ""),
        "paymentAccepted": business.get("paymentAccepted", ""),
        "foundingDate": business.get("foundingDate", ""),
        "identifier": identifier_node,
        "address": address,
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": geo.get("latitude", ""),
            "longitude": geo.get("longitude", ""),
        },
        "hasMap": business.get("hasMap", ""),
        "areaServed": build_area_served(business.get("areaServed")),
        "knowsAbout": business.get("knowsAbout", []),
        "sameAs": business.get("sameAs", []),
        "openingHoursSpecification": hours,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": rating.get("ratingValue", ""),
            "reviewCount": rating.get("reviewCount", ""),
            "bestRating": rating.get("bestRating", "") if rating.get("ratingValue") else "",
            "worstRating": rating.get("worstRating", "") if rating.get("ratingValue") else "",
        },
    }
    # A rating with no value must not ship as an empty shell.
    if not rating.get("ratingValue") or not rating.get("reviewCount"):
        node["aggregateRating"] = ""
    return node


def build_website(cfg):
    site = cfg["site"]
    base = site["url"].rstrip("/")
    return {
        "@type": "WebSite",
        "@id": f"{base}/#website",
        "url": f"{base}/",
        "name": site.get("name", ""),
        "inLanguage": site.get("inLanguage", ""),
        "publisher": {"@id": f"{base}/#business"},
    }


def build_breadcrumb(cfg, service, url):
    site = cfg["site"]
    base = site["url"].rstrip("/")
    hub = site.get("breadcrumbHub", {})

    items = [{
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": f"{base}/",
    }]
    if hub.get("name") and hub.get("url"):
        items.append({
            "@type": "ListItem",
            "position": 2,
            "name": hub["name"],
            "item": hub["url"],
        })
    items.append({
        "@type": "ListItem",
        "position": len(items) + 1,
        "name": service["name"],
        "item": url,
    })
    return {
        "@type": "BreadcrumbList",
        "@id": f"{url}#breadcrumb",
        "itemListElement": items,
    }


def build_webpage(cfg, service, url):
    base = cfg["site"]["url"].rstrip("/")
    return {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": service["name"],
        "description": service.get("description", ""),
        "inLanguage": cfg["site"].get("inLanguage", ""),
        "isPartOf": {"@id": f"{base}/#website"},
        "about": {"@id": f"{base}/#business"},
        "primaryImageOfPage": service.get("image", ""),
        "breadcrumb": {"@id": f"{url}#breadcrumb"},
    }


def build_service(cfg, service, url, by_slug):
    base = cfg["site"]["url"].rstrip("/")
    business_id = f"{base}/#business"

    catalog_items = []
    for position, item in enumerate(service.get("items", []), start=1):
        catalog_items.append({
            "@type": "Offer",
            "position": position,
            "itemOffered": {"@type": "Service", "name": item},
        })

    related = []
    for slug in service.get("related", []):
        sibling = by_slug.get(slug)
        if not sibling:
            continue
        sibling_url = page_url(cfg["site"]["url"], slug)
        related.append({
            "@type": "Service",
            "@id": f"{sibling_url}#service",
            "name": sibling["name"],
            "url": sibling_url,
        })

    areas = build_area_served(service.get("areaServed")) or build_area_served(
        cfg["business"].get("areaServed")
    )

    channel = {"@type": "ServiceChannel", "serviceUrl": url}
    if cfg["business"].get("telephone"):
        channel["servicePhone"] = {
            "@type": "ContactPoint",
            "telephone": cfg["business"]["telephone"],
            "contactType": "customer service",
        }

    offers = ""
    if service.get("price"):
        offers = {
            "@type": "Offer",
            "price": service["price"],
            "priceCurrency": service.get("priceCurrency", "AUD"),
            "availability": "https://schema.org/InStock",
            "url": url,
            "priceSpecification": {
                "@type": "PriceSpecification",
                "price": service["price"],
                "priceCurrency": service.get("priceCurrency", "AUD"),
                "valueAddedTaxIncluded": True,
            },
        }

    return {
        "@type": "Service",
        "@id": f"{url}#service",
        "name": service["name"],
        "alternateName": service.get("alternateName", ""),
        "serviceType": service.get("serviceType", ""),
        "description": service.get("description", ""),
        "url": url,
        "image": service.get("image", ""),
        "provider": {"@id": business_id},
        "providerMobility": "dynamic",
        "areaServed": areas,
        "audience": {
            "@type": "Audience",
            "audienceType": service.get("audience", ""),
        },
        "serviceOutput": {
            "@type": "Thing",
            "name": service.get("serviceOutput", ""),
        },
        "availableChannel": channel,
        "offers": offers,
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "@id": f"{url}#offer-catalog",
            "name": f"{service['name']} inclusions",
            "itemListElement": catalog_items,
        },
        "isRelatedTo": related,
        "mainEntityOfPage": {"@id": f"{url}#webpage"},
    }


def as_script_tag(graph):
    body = json.dumps(graph, indent=2, ensure_ascii=False)
    return f'<script type="application/ld+json">\n{body}\n</script>\n'


def collect_warnings(cfg):
    warnings = []
    business = cfg["business"]
    for field, note in BUSINESS_CHECKS:
        if not business.get(field):
            warnings.append(f"`business.{field}` is empty and was omitted. {note}")

    address = business.get("address", {})
    missing_address = [f for f in ADDRESS_CHECKS if not address.get(f)]
    if missing_address:
        warnings.append(
            "`business.address` is incomplete and the whole address node was omitted. "
            "Missing: " + ", ".join(missing_address) + ". LocalBusiness types require "
            "an address; add the registered or trading address, or drop the "
            "LocalBusiness subtype and keep Organization only."
        )

    geo = business.get("geo", {})
    if not geo.get("latitude") or not geo.get("longitude"):
        warnings.append("`business.geo` is empty and was omitted. Use at least 5 decimal places.")

    if not business.get("openingHoursSpecification"):
        warnings.append(
            "`business.openingHoursSpecification` is empty and was omitted. "
            "Add real hours that match the website and Google Business Profile."
        )

    if not business.get("sameAs"):
        warnings.append(
            "`business.sameAs` is empty and was omitted. Add the Google Business Profile, "
            "Facebook, LinkedIn and any directory profiles that confirm the entity."
        )

    rating = business.get("aggregateRating", {})
    if not rating.get("ratingValue"):
        warnings.append(
            "`business.aggregateRating` is empty and was omitted. Only add it if genuine "
            "reviews are visible on the page itself."
        )

    areas = business.get("areaServed", [])
    if len(areas) == 1 and areas[0].get("name") == "Australia":
        warnings.append(
            "`business.areaServed` is still the default (Australia). Replace it with the "
            "cities and regions actually serviced."
        )

    for service in cfg["_services"]:
        if not service.get("image"):
            warnings.append(f"`services[{service['slug']}].image` is empty and was omitted.")
    return warnings


def main():
    profile = load("business-profile.json")
    services_cfg = load("services.json")
    services = services_cfg["services"]
    profile["_services"] = services

    by_slug = {service["slug"]: service for service in services}
    site_url = profile["site"]["url"]

    OUT.mkdir(exist_ok=True)

    business_node = build_business(profile)
    website_node = build_website(profile)

    sitewide = prune({
        "@context": "https://schema.org",
        "@graph": [business_node, website_node],
    })
    (OUT / "_sitewide-business.json").write_text(
        json.dumps(sitewide, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT / "_sitewide-business.html").write_text(as_script_tag(sitewide), encoding="utf-8")

    combined = []
    for service in services:
        url = page_url(site_url, service["slug"])
        graph = prune({
            "@context": "https://schema.org",
            "@graph": [
                build_webpage(profile, service, url),
                build_breadcrumb(profile, service, url),
                build_service(profile, service, url, by_slug),
            ],
        })
        (OUT / f"{service['slug']}.json").write_text(
            json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (OUT / f"{service['slug']}.html").write_text(as_script_tag(graph), encoding="utf-8")
        combined.append({"url": url, "jsonld": graph})

    (OUT / "all-services.json").write_text(
        json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    warnings = collect_warnings(profile)
    report = [
        "# Schema validation report",
        "",
        f"Generated files: {len(services)} service pages + 1 site-wide graph.",
        "",
        "Every value below was left empty in the config and was therefore omitted from the",
        "generated JSON-LD rather than shipped as placeholder text. The markup is valid as",
        "generated; filling these in makes it complete.",
        "",
    ]
    if warnings:
        report += [f"- {warning}" for warning in warnings]
    else:
        report.append("No missing recommended fields. ")
    report += [
        "",
        "## Before publishing",
        "",
        "1. Confirm each `description` matches the copy actually on that page.",
        "2. Run every generated file through https://validator.schema.org/ and the",
        "   Google Rich Results Test.",
        "3. Confirm the page URLs resolve exactly as written (trailing slash, https).",
        "",
    ]
    (OUT / "VALIDATION-REPORT.md").write_text("\n".join(report), encoding="utf-8")

    print(f"Wrote {len(services) * 2 + 4} files to {OUT}")
    for warning in warnings:
        print(f"  ! {warning}")


if __name__ == "__main__":
    main()
