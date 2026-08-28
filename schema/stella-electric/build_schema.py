#!/usr/bin/env python3
"""Generate JSON-LD schema for Stella Electric LLC blog and service pages.

Each page gets one @graph containing the organization, website, webpage,
article (or service), breadcrumb, FAQ and — where applicable — HowTo nodes.

Values that could not be verified against the live pages are emitted as
{{PLACEHOLDER}} strings. The build prints a report of every placeholder left
in the output; none of them may survive to production.

Usage:  python3 build_schema.py [--outdir output]
"""

import argparse
import json
import os
import re

SITE = "https://stellaelectricllc.com"
ORG_ID = f"{SITE}/#organization"
SITE_ID = f"{SITE}/#website"
LOGO_ID = f"{SITE}/#logo"

# --------------------------------------------------------------------------
# Verified business facts (sources listed in README.md). Confirm before deploy.
# --------------------------------------------------------------------------
NAP = {
    "name": "Stella Electric LLC",
    "alternateName": "Stella Electric",
    "telephone": "+1-410-429-0479",
    "email": "stellaelectricco@gmail.com",
    "streetAddress": "532 Church Rd",
    "addressLocality": "Reisterstown",
    "addressRegion": "MD",
    "postalCode": "21136",
    "foundingDate": "2016",
}

AREA_SERVED = [
    {"@type": "City", "name": "Baltimore", "containedInPlace": {"@type": "State", "name": "Maryland"}},
    {"@type": "State", "name": "Maryland"},
    {"@type": "State", "name": "Virginia"},
    {"@type": "State", "name": "Pennsylvania"},
    {"@type": "State", "name": "Delaware"},
    {"@type": "AdministrativeArea", "name": "Washington, D.C."},
]


def organization():
    """Compact org node, repeated on every page so @id references resolve locally."""
    return {
        "@type": ["Electrician", "LocalBusiness"],
        "@id": ORG_ID,
        "name": NAP["name"],
        "alternateName": NAP["alternateName"],
        "url": f"{SITE}/",
        "telephone": NAP["telephone"],
        "email": NAP["email"],
        "foundingDate": NAP["foundingDate"],
        "priceRange": "$$",
        "logo": {
            "@type": "ImageObject",
            "@id": LOGO_ID,
            "url": "{{LOGO_URL}}",
            "contentUrl": "{{LOGO_URL}}",
            "caption": NAP["name"],
        },
        "image": {"@id": LOGO_ID},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": NAP["streetAddress"],
            "addressLocality": NAP["addressLocality"],
            "addressRegion": NAP["addressRegion"],
            "postalCode": NAP["postalCode"],
            "addressCountry": "US",
        },
        "areaServed": AREA_SERVED,
        "sameAs": ["{{GOOGLE_BUSINESS_PROFILE_URL}}", "{{FACEBOOK_URL}}", "{{YELP_URL}}"],
    }


def website():
    return {
        "@type": "WebSite",
        "@id": SITE_ID,
        "url": f"{SITE}/",
        "name": NAP["name"],
        "publisher": {"@id": ORG_ID},
        "inLanguage": "en-US",
    }


def author_node(page):
    return {
        "@type": "Person",
        "@id": f"{SITE}/#/schema/person/author",
        "name": "{{AUTHOR_NAME}}",
        "jobTitle": "{{AUTHOR_JOB_TITLE}}",
        "worksFor": {"@id": ORG_ID},
        "url": "{{AUTHOR_PROFILE_URL}}",
    }


def webpage(page):
    url = f"{SITE}/{page['slug']}/"
    node = {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "isPartOf": {"@id": SITE_ID},
        "about": {"@id": ORG_ID},
        "primaryImageOfPage": {"@id": f"{url}#primaryimage"},
        "breadcrumb": {"@id": f"{url}#breadcrumb"},
        "inLanguage": "en-US",
        "datePublished": "{{DATE_PUBLISHED}}",
        "dateModified": "{{DATE_MODIFIED}}",
    }
    if page["kind"] == "service":
        node["mainEntity"] = {"@id": f"{url}#service"}
    return node


def primary_image(page):
    url = f"{SITE}/{page['slug']}/"
    return {
        "@type": "ImageObject",
        "@id": f"{url}#primaryimage",
        "url": "{{PRIMARY_IMAGE_URL}}",
        "contentUrl": "{{PRIMARY_IMAGE_URL}}",
        "width": "{{PRIMARY_IMAGE_WIDTH}}",
        "height": "{{PRIMARY_IMAGE_HEIGHT}}",
        "caption": page["image_caption"],
    }


def article(page):
    url = f"{SITE}/{page['slug']}/"
    return {
        "@type": "BlogPosting",
        "@id": f"{url}#article",
        "isPartOf": {"@id": f"{url}#webpage"},
        "mainEntityOfPage": {"@id": f"{url}#webpage"},
        "headline": page["headline"],
        "description": page["description"],
        "articleSection": page["section"],
        "keywords": page["keywords"],
        "author": {"@id": f"{SITE}/#/schema/person/author"},
        "publisher": {"@id": ORG_ID},
        "image": {"@id": f"{url}#primaryimage"},
        "datePublished": "{{DATE_PUBLISHED}}",
        "dateModified": "{{DATE_MODIFIED}}",
        "inLanguage": "en-US",
        "about": [{"@type": "Thing", "name": t} for t in page["about"]],
        "wordCount": "{{WORD_COUNT}}",
    }


def breadcrumb(page):
    url = f"{SITE}/{page['slug']}/"
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"}]
    if page.get("parent"):
        items.append({
            "@type": "ListItem",
            "position": 2,
            "name": page["parent"]["name"],
            "item": page["parent"]["url"],
        })
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": page["breadcrumb_name"]})
    return {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": items}


def faq(page):
    url = f"{SITE}/{page['slug']}/"
    return {
        "@type": "FAQPage",
        "@id": f"{url}#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "@id": f"{url}#faq-{i}",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for i, (q, a) in enumerate(page["faqs"], start=1)
        ],
    }


def howto(page):
    url = f"{SITE}/{page['slug']}/"
    h = page["howto"]
    node = {
        "@type": "HowTo",
        "@id": f"{url}#howto",
        "name": h["name"],
        "description": h["description"],
        "totalTime": h["totalTime"],
        "image": {"@id": f"{url}#primaryimage"},
        "step": [
            {
                "@type": "HowToStep",
                "position": i,
                "name": s["name"],
                "text": s["text"],
                "url": f"{url}#step-{i}",
            }
            for i, s in enumerate(h["steps"], start=1)
        ],
    }
    if h.get("tools"):
        node["tool"] = [{"@type": "HowToTool", "name": t} for t in h["tools"]]
    if h.get("supplies"):
        node["supply"] = [{"@type": "HowToSupply", "name": s} for s in h["supplies"]]
    if h.get("estimatedCost"):
        node["estimatedCost"] = {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": h["estimatedCost"],
        }
    return node


def service(page, svc):
    url = f"{SITE}/{page['slug']}/"
    node = {
        "@type": "Service",
        "@id": svc.get("id", f"{url}#service"),
        "name": svc["name"],
        "serviceType": svc["serviceType"],
        "description": svc["description"],
        "provider": {"@id": ORG_ID},
        "areaServed": AREA_SERVED,
        "category": "Electrical Services",
    }
    if svc.get("url"):
        node["url"] = svc["url"]
    if svc.get("price_min") is not None:
        node["offers"] = {
            "@type": "Offer",
            "url": svc.get("url", url),
            "availability": "https://schema.org/InStock",
            "priceSpecification": {
                "@type": "PriceSpecification",
                "priceCurrency": "USD",
                "minPrice": svc["price_min"],
                "maxPrice": svc["price_max"],
                "valueAddedTaxIncluded": False,
            },
        }
    elif svc.get("unit_price") is not None:
        node["offers"] = {
            "@type": "Offer",
            "url": svc.get("url", url),
            "availability": "https://schema.org/InStock",
            "priceSpecification": {
                "@type": "UnitPriceSpecification",
                "priceCurrency": "USD",
                "price": svc["unit_price"],
                "unitText": svc["unit_text"],
                "valueAddedTaxIncluded": False,
            },
        }
    if svc.get("catalog"):
        node["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": svc["catalog_name"],
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": c}}
                for c in svc["catalog"]
            ],
        }
    return node


def item_list(page):
    url = f"{SITE}/{page['slug']}/"
    il = page["item_list"]
    return {
        "@type": "ItemList",
        "@id": f"{url}#itemlist",
        "name": il["name"],
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": len(il["items"]),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "description": d}
            for i, (n, d) in enumerate(il["items"], start=1)
        ],
    }


def build_graph(page):
    graph = [organization(), website(), webpage(page), primary_image(page)]
    if page["kind"] == "article":
        graph.append(author_node(page))
        graph.append(article(page))
    graph.append(breadcrumb(page))
    if page.get("faqs"):
        graph.append(faq(page))
    if page.get("howto"):
        graph.append(howto(page))
    if page.get("item_list"):
        graph.append(item_list(page))
    for svc in page.get("services", []):
        graph.append(service(page, svc))
    return {"@context": "https://schema.org", "@graph": graph}


# --------------------------------------------------------------------------
# Page data. FAQ questions/answers are DRAFTS: they must match the visible
# copy on each page word for word before the markup goes live.
# --------------------------------------------------------------------------
PAGES = [
    {
        "slug": "whole-house-surge-protector-benefits",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Whole-House Surge Protector Benefits",
        "breadcrumb_name": "Whole-House Surge Protector Benefits",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Safety",
        "keywords": "whole house surge protector, whole home surge protection, surge protector benefits, Baltimore electrician",
        "about": ["Surge protector", "Power surge", "Electrical safety", "Home electrical system"],
        "image_caption": "Whole-house surge protector installed at a residential electrical panel",
        "faqs": [
            ("What does a whole-house surge protector actually protect?",
             "A whole-house surge protector is installed at the electrical panel, so it absorbs surges before they reach anything wired into the home. That covers hardwired equipment a power strip can never protect - HVAC systems, the furnace board, the range, the garage door opener, hardwired smart devices and lighting - in addition to everything plugged into your outlets."),
            ("How much does a whole-house surge protector cost in Baltimore?",
             "A whole-house surge protector typically costs around $350 to $750 installed in the Baltimore area. The final price depends on the size and model of the device, the condition of your panel and the contractor's labor rate."),
            ("Do I still need power strips if I have whole-house surge protection?",
             "Yes. Whole-house protection is the first layer and stops the large surges coming in from the utility. Point-of-use surge strips are the second layer for sensitive electronics like computers, televisions and gaming consoles, and they catch the smaller surges generated inside the home."),
            ("Do power surges only happen during storms?",
             "No. Lightning gets the attention, but most surges come from everyday sources: utility switching and grid faults, downed lines, work on the local distribution system, and large appliances such as HVAC compressors cycling on and off inside your own home."),
            ("Are whole-house surge protectors required by code?",
             "The 2020 National Electrical Code (Article 230.67) requires a surge protective device on new and replacement dwelling unit services. Whether that applies to your project depends on the code edition your Maryland jurisdiction has adopted, so a licensed electrician should confirm it before a panel replacement or service upgrade."),
        ],
        "services": [
            {
                "name": "Whole-House Surge Protection Installation",
                "serviceType": "Whole-house surge protector installation",
                "description": "Installation of a panel-mounted surge protective device that protects a home's hardwired equipment and appliances from utility and internal power surges.",
                "url": f"{SITE}/whole-house-surge-protection/",
                "price_min": 350,
                "price_max": 750,
            }
        ],
    },
    {
        "slug": "cost-to-rewire-an-old-house",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Cost to Rewire an Old House",
        "breadcrumb_name": "Cost to Rewire an Old House",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Costs",
        "keywords": "cost to rewire a house, old house rewiring cost, knob and tube replacement, home rewiring Baltimore",
        "about": ["Home rewiring", "Electrical wiring", "Knob-and-tube wiring", "Home renovation cost"],
        "image_caption": "Electrician replacing outdated branch circuit wiring in an older home",
        "faqs": [
            ("How much does it cost to rewire an old house?",
             "A practical way to estimate a whole-home rewire is $7.79 per linear foot of wall space in the home, plus $1,200 to $2,500 for the electrical panel. The total moves with the size of the house, how many circuits and devices are added, and how much of the structure has to be opened up to run new cable."),
            ("What are the signs an old house needs to be rewired?",
             "Knob-and-tube or cloth-insulated wiring, aluminum branch circuits, two-prong ungrounded outlets, a fuse box or an undersized panel, breakers that trip repeatedly, warm or discolored outlets and switches, and lights that dim when appliances start are all reasons to have the wiring evaluated."),
            ("How long does it take to rewire a house?",
             "Most whole-home rewires run several days to a couple of weeks. The schedule depends on square footage, how many circuits are being added, whether walls and ceilings are already open, and the inspection scheduling in your jurisdiction."),
            ("Do I have to move out while my house is rewired?",
             "Usually not. The work is normally staged room by room or floor by floor so power stays on in most of the house, though individual circuits are down while they are replaced and the whole service is off for the panel changeover."),
            ("Does rewiring a house require a permit in Maryland?",
             "Yes. Rewiring is permitted work in Maryland jurisdictions and has to be inspected. A licensed electrical contractor pulls the permit, schedules the rough-in and final inspections, and leaves you with documentation that the work was approved."),
        ],
        "services": [
            {
                "name": "Whole-House Rewiring",
                "serviceType": "Residential rewiring",
                "description": "Replacement of outdated or unsafe branch circuit wiring - including knob-and-tube, cloth-insulated and aluminum wiring - with modern copper circuits, permitted and inspected.",
                "url": f"{SITE}/home-rewire/",
                "unit_price": 7.79,
                "unit_text": "linear foot of wall space",
            },
            {
                "id": f"{SITE}/cost-to-rewire-an-old-house/#service-panel",
                "name": "Electrical Panel Replacement",
                "serviceType": "Electrical panel replacement",
                "description": "Replacement of the main electrical panel as part of a rewiring project, including permitting and utility coordination.",
                "url": f"{SITE}/electrical-panel-upgrades/",
                "price_min": 1200,
                "price_max": 2500,
            },
        ],
    },
    {
        "slug": "electrical-code-inspection-for-home-sale",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Electrical Code Inspection for a Home Sale",
        "breadcrumb_name": "Electrical Code Inspection for a Home Sale",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Inspections",
        "keywords": "electrical code inspection, home sale electrical inspection, pre-sale electrical inspection Baltimore",
        "about": ["Electrical inspection", "Building code", "Home sale", "Real estate transaction"],
        "image_caption": "Licensed electrician performing a pre-sale electrical code inspection",
        "faqs": [
            ("What is an electrical code inspection for a home sale?",
             "It is a documented review of the home's electrical system by a licensed electrician before the property goes under contract. The inspection covers the panel and service, grounding and bonding, GFCI and AFCI protection, wiring condition, smoke alarms and any visible safety hazards, and it ends in a written report."),
            ("Why should a seller get an electrical inspection before listing?",
             "Because a buyer's inspection that turns up unexpected damage can sink the sale or force a last-minute price concession. Finding the problems first lets you price the repairs, schedule them on your own timeline and hand buyers a report instead of a surprise."),
            ("What electrical problems come up most often in home inspections?",
             "Ungrounded two-prong outlets, missing GFCI protection in kitchens, baths, garages and outdoors, missing AFCI protection, double-tapped breakers, open splices and unsecured junction boxes, undersized or recalled panels, remaining knob-and-tube wiring, and smoke alarms that are missing, expired or not interconnected."),
            ("Does Maryland require smoke alarms to be updated before a sale?",
             "Maryland law requires battery-only smoke alarms that are more than ten years old to be replaced with sealed ten-year lithium battery units, and hardwired alarms are still required where the code called for them. Alarm compliance is one of the first things flagged during a sale."),
            ("How long does an electrical code inspection take?",
             "A typical single-family home inspection takes a few hours on site, and the written report follows. The exact time depends on the size of the home, the number of panels and subpanels and how accessible the wiring is."),
        ],
        "services": [
            {
                "name": "Electrical Code Inspection",
                "serviceType": "Electrical code compliance inspection",
                "description": "Pre-sale and pre-purchase electrical code inspection covering panel condition, grounding, circuit protection, code compliance and safety hazards, delivered with a written report.",
                "url": f"{SITE}/electrical-code-inspection/",
                "catalog_name": "Electrical code inspection scope",
                "catalog": [
                    "Electrical panel and service inspection",
                    "Grounding and bonding verification",
                    "GFCI and AFCI protection check",
                    "Outlet, switch and fixture inspection",
                    "Smoke and carbon monoxide alarm compliance check",
                    "Written inspection report",
                ],
            }
        ],
    },
    {
        "slug": "outlet-sparks-when-plugging-in",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Why an Outlet Sparks When You Plug Something In",
        "breadcrumb_name": "Outlet Sparks When Plugging In",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Troubleshooting",
        "keywords": "outlet sparks when plugging in, sparking outlet, outlet arcing, electrical outlet repair Baltimore",
        "about": ["Electrical outlet", "Electrical arcing", "Electrical safety", "Electrical troubleshooting"],
        "image_caption": "Damaged electrical outlet showing scorch marks around the receptacle",
        "howto": {
            "name": "What to Do When an Outlet Sparks",
            "description": "Safe steps to take the moment an outlet sparks, and how to tell a harmless plug-in spark from a hazard that needs a licensed electrician.",
            "totalTime": "PT10M",
            "tools": ["Flashlight", "Non-contact voltage tester"],
            "steps": [
                {"name": "Stop using the outlet",
                 "text": "Unplug whatever you were connecting and leave the outlet empty. Do not keep using a receptacle that sparked, and do not plug in a different device to test it."},
                {"name": "Shut off the circuit at the breaker",
                 "text": "Find the breaker that feeds the outlet and switch it off. If you cannot identify the circuit, or if you see smoke or flame, shut off the main breaker and call 911 first."},
                {"name": "Look for signs of damage",
                 "text": "With the power off, check the faceplate and receptacle for scorch marks, melted plastic, discoloration or a burning smell, and note whether the outlet or plug felt hot. These signs point to arcing rather than a normal plug-in spark."},
                {"name": "Note what kind of spark you saw",
                 "text": "A single brief blue spark as the prongs make contact is inrush current and is often normal. Repeated sparking, yellow or white sparks, buzzing, crackling or sparks with nothing being plugged in indicate a loose connection, a short or a failing receptacle."},
                {"name": "Leave the outlet closed and call a licensed electrician",
                 "text": "Do not remove the faceplate or attempt a repair. Have a licensed electrician find the fault - worn contacts, back-stabbed or loose wiring, moisture, an overloaded circuit or damaged cable - and replace the receptacle or repair the circuit."},
            ],
        },
        "faqs": [
            ("Is it normal for an outlet to spark when you plug something in?",
             "A single quick blue spark as the plug makes contact can be normal. It is the inrush of current as the device draws power, and it happens most often with appliances that have motors or large power supplies. Anything more than that brief spark is not normal."),
            ("When is a sparking outlet dangerous?",
             "Treat it as dangerous when the sparks are yellow or white, when they repeat or continue after the plug is seated, when the outlet sparks with nothing plugged in, or when you notice buzzing, a burning smell, scorch marks, melted plastic or an outlet that is warm to the touch. Shut the circuit off and call an electrician."),
            ("What causes an outlet to spark?",
             "Common causes are worn receptacle contacts, loose or back-stabbed wire connections behind the outlet, moisture in the box, an overloaded circuit, short circuits from damaged cable or a device fault, and aging aluminum or deteriorated wiring."),
            ("Can I keep using an outlet that sparked?",
             "No. Arcing generates enough heat to ignite the box, the wiring insulation and surrounding framing. Turn the circuit off at the breaker and leave it off until a licensed electrician has inspected and repaired it."),
            ("Should a sparking outlet be treated as an electrical emergency?",
             "If there is smoke, flame, a burning smell, a hot outlet or sparking that will not stop with the breaker on, yes - shut off the power and call for emergency electrical service. A single brief spark on plug-in with no other symptoms can wait for a scheduled repair visit."),
        ],
        "services": [
            {
                "name": "Electrical Outlet Repair and Troubleshooting",
                "serviceType": "Electrical repair and troubleshooting",
                "description": "Diagnosis and repair of sparking, arcing, dead or overheating outlets, including receptacle replacement, loose connection repair and circuit troubleshooting.",
                "url": f"{SITE}/electrical-repair-troubleshooting/",
            }
        ],
    },
    {
        "slug": "hardwired-smoke-detector-installation",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Hardwired Smoke Detector Installation",
        "breadcrumb_name": "Hardwired Smoke Detector Installation",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Safety",
        "keywords": "hardwired smoke detector installation, interconnected smoke alarms, smoke detector wiring, Baltimore electrician",
        "about": ["Smoke detector", "Fire safety", "Electrical installation", "Building code"],
        "image_caption": "Hardwired interconnected smoke detector installed on a residential ceiling",
        "howto": {
            "name": "How Hardwired Smoke Detectors Are Installed",
            "description": "The steps a licensed electrician follows to install and interconnect hardwired smoke detectors in a home.",
            "totalTime": "{{HOWTO_TOTAL_TIME}}",
            "tools": ["Drill", "Drywall saw", "Wire strippers", "Non-contact voltage tester", "Fish tape"],
            "supplies": ["Hardwired smoke detectors with battery backup", "14/3 NM-B cable", "Old-work ceiling boxes", "Wire connectors"],
            "steps": [
                {"name": "Plan the alarm locations",
                 "text": "Place an alarm inside every bedroom, outside each separate sleeping area, and on every level of the home including the basement. Keep alarms away from bathroom doors, supply registers and the immediate area over cooking appliances to limit nuisance alarms."},
                {"name": "Shut off and verify the power",
                 "text": "Turn off the circuit that will feed the alarms at the panel and confirm the wires are dead with a non-contact voltage tester before opening any box."},
                {"name": "Run the interconnect cable",
                 "text": "Pull three-conductor cable between alarm locations so the hot, neutral and interconnect travel together. The interconnect conductor is what makes every alarm sound when one detects smoke."},
                {"name": "Mount the boxes and bases",
                 "text": "Install the ceiling boxes at each planned location and mount the manufacturer's base plate to each box."},
                {"name": "Wire each detector",
                 "text": "Connect hot to black, neutral to white and the interconnect to the third conductor at every alarm, following the manufacturer's instructions. Do not mix brands or models on one interconnect loop unless the manufacturer lists them as compatible."},
                {"name": "Install the batteries and seat the alarms",
                 "text": "Install the backup batteries, twist each alarm onto its base and confirm it locks in place."},
                {"name": "Restore power and test the interconnect",
                 "text": "Energize the circuit, then hold the test button on one alarm and confirm every other alarm in the home sounds. Test each alarm in turn, and have the work inspected where a permit was required."},
            ],
        },
        "faqs": [
            ("Are hardwired smoke detectors required?",
             "Hardwired, interconnected alarms with battery backup are required in new construction and are usually triggered by additions and major remodels. In existing homes, Maryland law requires battery-only alarms over ten years old to be replaced with sealed ten-year units, and hardwired alarms must be maintained where they were originally required."),
            ("How many smoke detectors does a house need and where do they go?",
             "One inside each bedroom, one outside each separate sleeping area, and at least one on every level of the home including the basement. Larger or multi-wing homes need more to cover each sleeping area."),
            ("What does interconnected mean?",
             "Interconnected alarms are linked so that when one detects smoke, every alarm in the home sounds. That matters most when a fire starts on a level far from the bedrooms, since it gives everyone the same warning at the same time."),
            ("How often should hardwired smoke detectors be replaced?",
             "Replace the alarms themselves every ten years from the manufacture date printed on the unit, and change the backup batteries on the schedule in the manufacturer's instructions. Sensors degrade whether or not the alarm has ever sounded."),
            ("Can I install hardwired smoke detectors myself?",
             "Running new cable and tying alarms into a branch circuit is licensed electrical work in Maryland and is typically permitted and inspected. Swapping an existing hardwired alarm for a compatible replacement on the same harness is straightforward, but new wiring or a new interconnect loop should be done by a licensed electrician."),
        ],
        "services": [
            {
                "name": "Hardwired Smoke Detector Installation",
                "serviceType": "Smoke detector installation",
                "description": "Installation, replacement and interconnection of hardwired smoke detectors with battery backup, wired and tested to code.",
                "url": "{{SMOKE_DETECTOR_SERVICE_URL}}",
            }
        ],
    },
]

PAGES.extend([
    {
        "slug": "hot-tub-electrical-wiring-requirements",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Hot Tub Electrical Wiring Requirements",
        "breadcrumb_name": "Hot Tub Electrical Wiring Requirements",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Installation",
        "keywords": "hot tub electrical wiring requirements, hot tub wiring, spa disconnect, 240v hot tub circuit, Baltimore electrician",
        "about": ["Hot tub", "Electrical wiring", "Ground fault circuit interrupter", "National Electrical Code"],
        "image_caption": "GFCI spa disconnect panel installed beside an outdoor hot tub",
        "item_list": {
            "name": "Electrical requirements for a hot tub installation",
            "items": [
                ("Dedicated circuit", "Most 240-volt hot tubs need their own dedicated circuit, commonly 50 amps, sized to the equipment nameplate rather than a rule of thumb."),
                ("GFCI protection", "The spa circuit must be GFCI protected, typically through a GFCI breaker in the spa disconnect panel."),
                ("Emergency shutoff and disconnect", "A readily accessible disconnect must be installed at least 5 feet from the inside wall of the tub, within sight of it, and not more than 50 feet away."),
                ("Equipotential bonding", "Metal parts, the pump, and the reinforcing steel or perimeter surface within 3 feet of the tub are bonded with a solid #8 copper conductor to eliminate voltage differences."),
                ("Correct wire size and burial depth", "Conductors are sized for the load and the run length, and any underground feed is installed in approved raceway at code burial depth."),
                ("Permit and inspection", "Hot tub circuits are permitted work and must pass electrical inspection before the tub is put into service."),
            ],
        },
        "faqs": [
            ("What size electrical circuit does a hot tub need?",
             "Most 240-volt hot tubs run on a dedicated GFCI-protected circuit, and 50 amps is the most common size. The correct size comes from the equipment nameplate and the manufacturer's installation manual, not from the size of the tub, because heater and pump loads vary by model."),
            ("Does a hot tub need a GFCI?",
             "Yes. The National Electrical Code requires GFCI protection for hot tub and spa circuits, normally provided by a GFCI breaker in the spa disconnect panel next to the tub."),
            ("How far from the hot tub does the disconnect have to be?",
             "The disconnect must be readily accessible, within sight of the tub, at least 5 feet from the inside wall of the tub, and no more than 50 feet away. The distance keeps someone in the water from reaching it while still allowing anyone nearby to cut power fast."),
            ("What is bonding and why does a hot tub need it?",
             "Bonding ties the metal parts of the installation together with a solid #8 copper conductor so they all sit at the same electrical potential. It is what prevents a dangerous voltage difference between the water, the tub shell and the surrounding surface if a fault occurs."),
            ("Can a hot tub just plug into a regular outlet?",
             "Only plug-and-play models designed for it, and even those need a dedicated 15 or 20 amp GFCI-protected circuit rather than a shared household outlet or an extension cord. Full-size 240-volt tubs always require hardwired service."),
            ("Do I need a permit to wire a hot tub in Maryland?",
             "Yes. Hot tub circuits require a permit and an electrical inspection in Maryland jurisdictions, and the work must be performed by a licensed electrician."),
        ],
        "services": [
            {
                "name": "Hot Tub and Spa Electrical Wiring",
                "serviceType": "Hot tub electrical installation",
                "description": "Installation of dedicated GFCI-protected 240-volt hot tub circuits, spa disconnect panels, equipotential bonding and underground feeds, permitted and inspected.",
                "url": "{{HOT_TUB_SERVICE_URL}}",
            }
        ],
    },
    {
        "slug": "bathroom-exhaust-fan-electrical-installation",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Bathroom Exhaust Fan Electrical Installation",
        "breadcrumb_name": "Bathroom Exhaust Fan Electrical Installation",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Installation",
        "keywords": "bathroom exhaust fan installation, bathroom fan wiring, exhaust fan electrical requirements, Baltimore electrician",
        "about": ["Exhaust fan", "Bathroom ventilation", "Electrical installation", "Building code"],
        "image_caption": "Bathroom exhaust fan housing wired and mounted between ceiling joists",
        "howto": {
            "name": "How a Bathroom Exhaust Fan Is Installed",
            "description": "The steps a licensed electrician follows to wire and install a bathroom exhaust fan, including circuit, switch and venting requirements.",
            "totalTime": "{{HOWTO_TOTAL_TIME}}",
            "tools": ["Drill", "Drywall saw", "Wire strippers", "Non-contact voltage tester", "Fish tape"],
            "supplies": ["Exhaust fan unit", "Rigid or insulated flexible duct", "Roof or wall vent cap", "14/2 or 12/2 NM-B cable", "Wall switch or timer switch"],
            "steps": [
                {"name": "Size the fan for the room",
                 "text": "Size the fan in CFM to the bathroom. A common rule is one CFM per square foot with a 50 CFM minimum, and larger or enclosed-fixture bathrooms need more capacity."},
                {"name": "Choose the fan and duct route",
                 "text": "Pick a location central to the shower or tub and plan the shortest duct run to an exterior wall or roof cap. The fan must exhaust outside the building, never into an attic, soffit or crawlspace."},
                {"name": "Shut off and verify the power",
                 "text": "Turn off the circuit at the panel and confirm the wires are dead with a non-contact voltage tester before opening any box."},
                {"name": "Cut the opening and mount the housing",
                 "text": "Cut the ceiling opening to the manufacturer's template and fasten the housing to the framing so the grille will sit flush against the finished ceiling."},
                {"name": "Run the circuit and switch legs",
                 "text": "Pull cable from the branch circuit to the fan and to the switch location. A fan with a heater draws enough current to need its own dedicated 20-amp circuit; check the nameplate before sharing a circuit with lighting."},
                {"name": "Wire the fan and the control",
                 "text": "Connect the fan per the manufacturer's diagram and terminate the wall control - a plain switch, a timer or a humidity-sensing control. Fan and light functions on combination units are wired to separate switch legs."},
                {"name": "Connect and seal the duct",
                 "text": "Attach the duct to the housing and to the exterior vent cap, seal the joints and insulate duct that runs through unconditioned space so condensation does not drip back into the fan."},
                {"name": "Restore power and test",
                 "text": "Energize the circuit, run the fan, confirm airflow at the exterior cap, and verify the vent damper opens and closes."},
            ],
        },
        "faqs": [
            ("Does a bathroom exhaust fan need its own circuit?",
             "A standard fan can normally share the bathroom's 20-amp circuit. A fan with a built-in heater draws far more current and typically requires its own dedicated 20-amp circuit, so the nameplate rating decides it."),
            ("Does a bathroom exhaust fan need GFCI protection?",
             "Bathroom receptacle outlets require GFCI protection, and a fan installed over a tub or shower must be GFCI protected and listed for that location. Confirm the unit's listing before installing it in a wet location."),
            ("What size exhaust fan do I need?",
             "Start with one CFM per square foot of bathroom floor area and a 50 CFM minimum, then increase capacity for bathrooms with high ceilings, a separate enclosed toilet room or a jetted tub."),
            ("Can a bathroom fan vent into the attic?",
             "No. Venting into an attic, soffit or crawlspace dumps humid air into the structure and causes mold and rot. The duct must terminate at an exterior wall or roof cap."),
            ("Is a bathroom exhaust fan required by code?",
             "Bathrooms need ventilation, and mechanical exhaust is required where there is no operable window. Many jurisdictions require a fan regardless, and it is the practical choice for controlling moisture even when a window is present."),
        ],
        "services": [
            {
                "name": "Bathroom Exhaust Fan Installation",
                "serviceType": "Exhaust fan installation",
                "description": "Wiring and installation of bathroom exhaust fans, fan and light combination units, heater units and humidity-sensing controls, including dedicated circuits where required.",
                "url": "{{EXHAUST_FAN_SERVICE_URL}}",
            }
        ],
    },
    {
        "slug": "how-to-install-recessed-lighting",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "How to Install Recessed Lighting",
        "breadcrumb_name": "How to Install Recessed Lighting",
        "description": "{{META_DESCRIPTION}}",
        "section": "Lighting",
        "keywords": "how to install recessed lighting, recessed lighting installation, can lights, LED downlights, Baltimore electrician",
        "about": ["Recessed lighting", "Lighting installation", "LED lighting", "Electrical wiring"],
        "image_caption": "Recessed LED downlights installed in a residential ceiling",
        "howto": {
            "name": "How to Install Recessed Lighting",
            "description": "The steps involved in laying out, wiring and installing recessed lights in a finished ceiling.",
            "totalTime": "{{HOWTO_TOTAL_TIME}}",
            "tools": ["Drill", "Hole saw or drywall saw", "Stud finder", "Wire strippers", "Non-contact voltage tester", "Fish tape"],
            "supplies": ["Recessed housings or canless LED downlights", "14/2 or 12/2 NM-B cable", "Old-work cable clamps", "Dimmer switch", "Wire connectors"],
            "steps": [
                {"name": "Plan the layout",
                 "text": "Space the lights evenly and keep them off the walls so the beams wash the room instead of the ceiling edge. A common starting point is spacing equal to half the ceiling height, with fixtures 24 to 36 inches from the walls, adjusted for work surfaces and furniture."},
                {"name": "Check what is above the ceiling",
                 "text": "Locate joists, ductwork, plumbing and existing cable before cutting. Where the housings will contact insulation, use IC-rated fixtures; non-IC fixtures require clearance from insulation."},
                {"name": "Shut off and verify the power",
                 "text": "Turn off the circuit at the panel and confirm the wires are dead with a non-contact voltage tester before opening any box or fixture."},
                {"name": "Cut the openings",
                 "text": "Mark each location with the manufacturer's template and cut clean openings to size, checking again for obstructions as you go."},
                {"name": "Run the cable",
                 "text": "Fish cable from the switch location through the ceiling to each opening, leaving enough slack at every hole to make up the connections comfortably."},
                {"name": "Wire and set the fixtures",
                 "text": "Connect each housing or canless unit to the cable, secure the cable in the connector, then set the fixture and let the spring clips grip the drywall."},
                {"name": "Install the switch or dimmer",
                 "text": "Terminate the switch leg at the wall box and install a dimmer that is listed as compatible with the LED fixtures, otherwise the lights will flicker or buzz at low output."},
                {"name": "Restore power, test and trim",
                 "text": "Energize the circuit, test each fixture through the full dimming range, then install the trims and aim any adjustable units."},
            ],
        },
        "faqs": [
            ("How many recessed lights do I need?",
             "Space the fixtures roughly half the ceiling height apart - about four feet on an eight-foot ceiling - and keep the outer row two to three feet off the walls. Adjust for the room's use: kitchens and work areas need more light on the counters, living spaces usually need less."),
            ("What is the difference between IC-rated and non-IC-rated recessed lights?",
             "IC-rated housings are built to be covered by insulation. Non-IC housings must be kept clear of insulation, which makes IC-rated fixtures the right choice for any ceiling below an insulated attic."),
            ("Can I replace old can lights with LED without rewiring?",
             "In most cases yes. LED retrofit modules screw into or clip inside the existing housing and use the same wiring, and canless LED units can replace the housings entirely when you are opening the ceiling anyway."),
            ("Do I need a permit to install recessed lighting?",
             "Adding a new circuit or extending wiring is permitted work in Maryland jurisdictions. Replacing existing fixtures in place generally is not, but your local permitting office has the final say."),
            ("Why do my recessed LED lights flicker on the dimmer?",
             "Almost always a compatibility problem. LED fixtures need a dimmer listed for LED loads and a load within the dimmer's rated range, and mixing fixture types on one dimmer makes the flicker worse."),
        ],
        "services": [
            {
                "name": "Recessed Lighting Installation",
                "serviceType": "Recessed lighting installation",
                "description": "Layout, wiring and installation of recessed and canless LED downlights in new and finished ceilings, including dimmer controls and circuit additions.",
                "url": f"{SITE}/indoor-lighting/",
            }
        ],
    },
    {
        "slug": "smart-home-electrical-installation",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Smart Home Electrical Installation",
        "breadcrumb_name": "Smart Home Electrical Installation",
        "description": "{{META_DESCRIPTION}}",
        "section": "Smart Home",
        "keywords": "smart home electrical installation, smart switch installation, smart home wiring, home automation electrician Baltimore",
        "about": ["Home automation", "Smart switch", "Electrical installation", "Smart home technology"],
        "image_caption": "Electrician installing a smart light switch in a residential wall box",
        "item_list": {
            "name": "Smart home devices that need electrical work",
            "items": [
                ("Smart switches and dimmers", "Most require a neutral conductor in the switch box, which older homes often do not have."),
                ("Smart thermostats", "Need a common (C) wire for continuous power, which frequently means pulling new thermostat cable."),
                ("Video doorbells", "Need adequate transformer voltage and capacity; many older door chime transformers are undersized."),
                ("Smart lighting and recessed fixtures", "Need dimmers and drivers listed as compatible with the fixtures to avoid flicker."),
                ("EV chargers", "Need a dedicated 240-volt circuit and enough spare panel capacity."),
                ("Smart panels and energy monitoring", "Install at the electrical panel and often pair with a panel upgrade."),
                ("Structured wiring and access points", "Hardwired network cable gives automation hubs and cameras a connection that does not depend on Wi-Fi coverage."),
            ],
        },
        "faqs": [
            ("Do smart switches need a neutral wire?",
             "Most do. Smart switches draw a small amount of power continuously to stay connected, and that requires a neutral in the switch box. Many older Baltimore-area homes have switch loops with no neutral, so an electrician either pulls a neutral or installs a no-neutral switch that is compatible with your fixtures."),
            ("Do I need an electrical panel upgrade for a smart home?",
             "Lights, switches and thermostats rarely change the load. A panel upgrade comes into play when you add high-draw equipment such as an EV charger, a heat pump or a smart panel with circuit-level monitoring, or when the existing panel is already full or undersized."),
            ("Can I install smart devices myself?",
             "Plug-in devices and screw-in bulbs are homeowner-friendly. Anything wired into a box - switches, dimmers, fan controls, doorbell transformers, hardwired hubs - is licensed electrical work in Maryland and is worth having done by an electrician, particularly where the box has no neutral or the wiring is aluminum."),
            ("What does a smart thermostat need to work?",
             "A C-wire that supplies continuous 24-volt power. If your thermostat cable does not have a spare conductor, the fix is either new cable to the air handler or a manufacturer-supplied power adapter at the equipment."),
            ("Should smart home devices be hardwired or wireless?",
             "Use wireless for convenience devices and hardwired connections for anything you depend on - cameras, automation hubs, access points and any device in a location with weak Wi-Fi. Hardwired network cable is the part that is far easier to install during a remodel than afterward."),
        ],
        "services": [
            {
                "name": "Smart Home Electrical Installation",
                "serviceType": "Smart home installation",
                "description": "Installation and wiring of smart switches, dimmers, thermostats, video doorbells, smart panels and structured wiring, including the neutral conductors and dedicated circuits these devices require.",
                "url": f"{SITE}/smart-home/",
                "catalog_name": "Smart home electrical services",
                "catalog": [
                    "Smart switch and dimmer installation",
                    "Smart thermostat wiring and C-wire installation",
                    "Video doorbell and transformer upgrades",
                    "Smart lighting and dimmer compatibility",
                    "EV charger circuit installation",
                    "Smart panel and energy monitoring installation",
                ],
            }
        ],
    },
    {
        "slug": "emergency-electrician-baltimore",
        "kind": "service",
        "title": "{{PAGE_TITLE}}",
        "headline": "Emergency Electrician in Baltimore, MD",
        "breadcrumb_name": "Emergency Electrician in Baltimore",
        "description": "{{META_DESCRIPTION}}",
        "section": "Emergency Service",
        "keywords": "emergency electrician Baltimore, 24 hour electrician Baltimore, emergency electrical repair Maryland",
        "about": ["Emergency electrical service", "Electrical repair", "Baltimore"],
        "image_caption": "Stella Electric emergency electrician responding to a service call in Baltimore, MD",
        "parent": {"name": "Electrical Services", "url": f"{SITE}/electrical-services/"},
        "faqs": [
            ("What counts as an electrical emergency?",
             "Burning smells, smoke or scorch marks at a panel, outlet or switch; sparking or arcing that will not stop; a breaker that trips immediately every time it is reset; a hot panel or outlet; exposed or downed wiring; water contacting electrical equipment; and a full loss of power that is not a utility outage."),
            ("What should I do while I wait for an emergency electrician?",
             "Shut off the affected circuit at the breaker, or the main breaker if you cannot identify the circuit. Keep people and pets away from the area, do not use the affected outlets or equipment, and call 911 first if there is smoke, flame or a downed line."),
            ("How fast can an emergency electrician get here?",
             "{{EMERGENCY_RESPONSE_TIME_ANSWER}}"),
            ("Is there an extra charge for emergency or after-hours service?",
             "{{EMERGENCY_PRICING_ANSWER}}"),
            ("What areas do you cover for emergency electrical service?",
             "Stella Electric serves Baltimore and the surrounding metro area, with service across Maryland and into Virginia, Pennsylvania, Delaware and the District of Columbia."),
        ],
        "services": [
            {
                "name": "Emergency Electrician in Baltimore, MD",
                "serviceType": "Emergency electrical repair",
                "description": "Emergency electrical response in Baltimore and the surrounding metro area for burning smells, sparking outlets, breaker failures, power loss, storm damage and other urgent electrical hazards.",
                "url": f"{SITE}/emergency-electrician/",
                "catalog_name": "Emergency electrical services",
                "catalog": [
                    "Power outage and partial power loss diagnosis",
                    "Sparking, arcing or burning outlet repair",
                    "Electrical panel and breaker failure repair",
                    "Storm and water damage electrical repair",
                    "Damaged service entrance and mast repair",
                    "Emergency circuit troubleshooting",
                ],
            }
        ],
    },
    {
        "slug": "electrical-panel-upgrade-baltimore",
        "kind": "service",
        "title": "{{PAGE_TITLE}}",
        "headline": "Electrical Panel Upgrade in Baltimore, MD",
        "breadcrumb_name": "Electrical Panel Upgrade in Baltimore",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Panels",
        "keywords": "electrical panel upgrade Baltimore, 200 amp service upgrade, breaker panel replacement Baltimore MD",
        "about": ["Electrical panel", "Electrical service upgrade", "Circuit breaker", "Baltimore"],
        "image_caption": "Newly installed 200-amp electrical panel in a Baltimore home",
        "parent": {"name": "Electrical Services", "url": f"{SITE}/electrical-services/"},
        "faqs": [
            ("How much does an electrical panel upgrade cost in Baltimore?",
             "Upgrading an electrical panel in Baltimore, MD typically costs between $500 and $2,000. A straight panel replacement generally runs $1,000 to $2,500, while a full service upgrade can range from $2,500 to $5,000 or more when the service entrance, meter or extensive rewiring are involved."),
            ("What are the signs I need a panel upgrade?",
             "Breakers that trip repeatedly, a fuse box or a panel with no room left for new circuits, reliance on tandem breakers and extension cords, lights that dim when large appliances start, a panel that is warm, rusted or buzzing, a recalled brand such as Federal Pacific or Zinsco, or planned additions like an EV charger, a heat pump or a finished basement."),
            ("Should I upgrade to 200 amps?",
             "A 100-amp service can still be adequate for a modest home with gas appliances. A 200-amp service is the practical choice for homes adding electric heat, an EV charger, central air, a hot tub or a large addition, because it provides both the capacity and the breaker spaces those loads need."),
            ("How long does a panel upgrade take and will my power be off?",
             "Most panel replacements are completed in a day, with the power off for several hours while the old panel is removed and the circuits are transferred. A full service upgrade adds time for utility coordination and inspection."),
            ("Do I need a permit for a panel upgrade in Baltimore?",
             "Yes. A panel upgrade requires a permit and an electrical inspection, and a service upgrade also requires coordination with BGE to disconnect and reconnect the service. A licensed electrical contractor handles the permit, the utility scheduling and the inspection."),
        ],
        "services": [
            {
                "name": "Electrical Panel Upgrade in Baltimore, MD",
                "serviceType": "Electrical panel upgrade",
                "description": "Electrical panel upgrades, breaker panel replacements and service upgrades for Baltimore-area homes, including permitting, utility coordination and inspection.",
                "url": f"{SITE}/electrical-panel-upgrades/",
                "price_min": 500,
                "price_max": 2000,
                "catalog_name": "Panel and service upgrade options",
                "catalog": [
                    "100 amp to 200 amp service upgrade",
                    "Breaker panel replacement",
                    "Subpanel installation",
                    "Fuse box replacement",
                    "Federal Pacific and Zinsco panel replacement",
                    "Service entrance and meter base repair",
                ],
            }
        ],
    },
])


PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def find_placeholders(obj, path="", found=None):
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_placeholders(v, f"{path}.{k}", found)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_placeholders(v, f"{path}[{i}]", found)
    elif isinstance(obj, str):
        for m in PLACEHOLDER_RE.findall(obj):
            found.append((m, path))
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    total_placeholders = 0
    for i, page in enumerate(PAGES, start=1):
        graph = build_graph(page)
        body = json.dumps(graph, indent=2, ensure_ascii=False)

        base = f"{i:02d}-{page['slug']}"
        with open(os.path.join(args.outdir, base + ".jsonld"), "w", encoding="utf-8") as f:
            f.write(body + "\n")
        with open(os.path.join(args.outdir, base + ".html"), "w", encoding="utf-8") as f:
            f.write('<script type="application/ld+json">\n' + body + "\n</script>\n")

        placeholders = find_placeholders(graph)
        total_placeholders += len(placeholders)
        types = sorted({n.get("@type") if isinstance(n.get("@type"), str) else "/".join(n["@type"])
                        for n in graph["@graph"]})
        names = sorted({p for p, _ in placeholders})
        print(f"{base}")
        print(f"    types:        {', '.join(types)}")
        print(f"    placeholders: {len(placeholders)} ({', '.join(names) if names else 'none'})")

    print(f"\n{len(PAGES)} pages written to {args.outdir}")
    print(f"{total_placeholders} placeholder values must be filled in before deploying.")


if __name__ == "__main__":
    main()
