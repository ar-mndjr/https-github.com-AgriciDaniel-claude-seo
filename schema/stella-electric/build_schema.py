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


PAGES.extend([
    {
        "slug": "electrical-fire-prevention",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Electrical Fire Prevention",
        "breadcrumb_name": "Electrical Fire Prevention",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Safety",
        "keywords": "electrical fire prevention, electrical fire causes, home electrical safety, Baltimore electrician",
        "about": ["Electrical fire", "Fire prevention", "Electrical safety", "Home safety"],
        "image_caption": "Scorched electrical outlet showing the early warning signs of an electrical fire",
        "item_list": {
            "name": "How to prevent an electrical fire at home",
            "items": [
                ("Stop overloading circuits", "Power strips and extension cords used as permanent wiring are the most common overload. A circuit that needs a strip to keep up usually needs another circuit."),
                ("Replace damaged cords and devices", "Frayed insulation, cracked plugs, and cords run under rugs or pinched by furniture all fail in the same place - where nobody can see the damage."),
                ("Act on warm outlets and switches", "Outlets and switch plates should never be warm. Heat means a loose connection or an overloaded circuit, and both arc before they ignite."),
                ("Investigate breakers that trip repeatedly", "A breaker that trips is doing its job. One that trips over and over is reporting a fault that has not been fixed."),
                ("Add AFCI protection", "Arc-fault breakers detect the low-level arcing that a standard breaker never sees, which is the exact failure mode behind most wiring fires."),
                ("Use the right bulb wattage and fixtures", "Over-lamping a fixture bakes the socket and the wiring above it. Match the fixture's rating, and use fixtures rated for enclosed or insulated ceilings."),
                ("Have old wiring and panels evaluated", "Knob-and-tube, deteriorated cloth insulation, aluminum branch circuits and recalled panel brands all carry a documented fire history."),
                ("Keep working smoke alarms", "Prevention fails sometimes. Interconnected alarms on every level and in every bedroom are what turn a fire into an evacuation instead of a tragedy."),
            ],
        },
        "faqs": [
            ("What causes most electrical fires in homes?",
             "Faulty or deteriorated wiring and connections, overloaded circuits, damaged cords and plugs, misused extension cords and power strips, over-lamped or failing light fixtures, and space heaters on circuits that cannot carry them."),
            ("What are the warning signs of an electrical fire risk?",
             "A burning or fishy smell near outlets or the panel, scorch marks or discoloration on outlets and switch plates, outlets or plates that feel warm, buzzing or crackling, breakers that trip repeatedly, lights that flicker or dim when appliances start, and a panel that is warm or rusted."),
            ("Do AFCI breakers really prevent fires?",
             "Arc-fault circuit interrupters are designed to detect arcing that a standard breaker cannot - a loose terminal, a nicked conductor, a cord crushed under a chair leg - and cut power before that arc ignites what is around it. That is why the code has extended AFCI protection to most living-area circuits."),
            ("How often should home wiring be inspected?",
             "Have the electrical system evaluated when you buy a home, before a major renovation, after any signs of trouble, and periodically for homes over about 40 years old. Older wiring, aluminum branch circuits and recalled panels warrant an inspection regardless of symptoms."),
            ("What should I do if I smell burning near an outlet?",
             "Shut off the circuit at the breaker - the main breaker if you cannot identify the circuit - keep people away from the area, and call an electrician. If there is smoke or flame, get everyone out and call 911 first."),
        ],
        "services": [
            {
                "name": "Electrical Safety Inspection",
                "serviceType": "Electrical safety inspection",
                "description": "Whole-home electrical safety evaluation covering panel condition, wiring, connections, circuit protection and fire risk, with a written report and repair recommendations.",
                "url": f"{SITE}/electrical-code-inspection/",
            }
        ],
    },
    {
        "slug": "circuit-breaker-versus-fuse-box",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Circuit Breaker Panel vs. Fuse Box",
        "breadcrumb_name": "Circuit Breaker vs. Fuse Box",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Panels",
        "keywords": "circuit breaker vs fuse box, fuse box replacement, fuse panel upgrade, Baltimore electrician",
        "about": ["Circuit breaker", "Fuse box", "Electrical panel", "Electrical safety"],
        "image_caption": "Older screw-in fuse box beside a modern circuit breaker panel",
        "item_list": {
            "name": "Circuit breaker panel compared with a fuse box",
            "items": [
                ("Resetting after a fault", "A breaker is switched back on. A fuse is consumed and has to be replaced with the correct amperage, which is where trouble starts."),
                ("Risk of the wrong size", "Nothing physically stops someone from screwing a 30-amp fuse into a circuit wired for 15 amps. That leaves the wiring, not the fuse, as the weak point."),
                ("Modern protection", "Breaker panels accept AFCI and GFCI breakers. Fuse panels cannot provide arc-fault or ground-fault protection at the panel."),
                ("Capacity", "Most fuse panels are 60 amps or less with few circuits, well short of what a house with central air, electric appliances or an EV charger needs."),
                ("Insurance and resale", "Many insurers surcharge or decline homes with fuse panels, and buyers' inspectors flag them, which puts the panel on the table during a sale."),
                ("Availability of parts", "Breakers are stocked everywhere. Fuse panel parts are increasingly scarce, and no new dwelling is built with one."),
            ],
        },
        "faqs": [
            ("What is the difference between a circuit breaker and a fuse?",
             "Both cut power when a circuit draws too much current. A fuse does it by melting a metal element and has to be replaced; a breaker does it with a mechanism you can switch back on. The protection is comparable when both are sized correctly - the practical differences are convenience, capacity and the modern protection only breakers can provide."),
            ("Are fuse boxes unsafe?",
             "A fuse panel in good condition and correctly fused is not inherently dangerous. The risks are practical: oversized fuses defeating the protection, corroded or overheated connections in decades-old equipment, no room for the circuits a modern home needs, and no way to add arc-fault or ground-fault protection at the panel."),
            ("Should I replace my fuse box with a breaker panel?",
             "Replace it if the panel is at or near capacity, if it shows heat damage or corrosion, if you are adding significant load such as central air or an EV charger, if your insurer is asking, or if you are selling. A small home with modest load and a sound panel can wait - but the replacement is on the horizon either way."),
            ("How much does it cost to replace a fuse box with a breaker panel?",
             "A panel replacement generally runs $1,000 to $2,500. If the service itself is being increased - new service entrance, meter base and utility coordination - a service upgrade can range from $2,500 to $5,000 or more."),
            ("Do I need a permit to replace a fuse box?",
             "Yes. Replacing a panel requires a permit and an electrical inspection, and increasing the service size also requires coordination with the utility to disconnect and reconnect power."),
        ],
        "services": [
            {
                "name": "Fuse Box Replacement and Panel Upgrade",
                "serviceType": "Electrical panel replacement",
                "description": "Replacement of fuse panels with modern breaker panels, including service upgrades, permitting, utility coordination and inspection.",
                "url": f"{SITE}/electrical-panel-upgrades/",
                "price_min": 1000,
                "price_max": 2500,
            }
        ],
    },
    {
        "slug": "why-do-outlets-feel-warm",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Why Do Outlets Feel Warm?",
        "breadcrumb_name": "Why Outlets Feel Warm",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Troubleshooting",
        "keywords": "warm outlet, hot electrical outlet, outlet feels warm, electrical outlet repair Baltimore",
        "about": ["Electrical outlet", "Electrical overload", "Electrical safety", "Electrical troubleshooting"],
        "image_caption": "Hand checking the temperature of a residential electrical outlet",
        "howto": {
            "name": "What to Do About a Warm Outlet",
            "description": "How to check a warm outlet safely and decide whether it needs an electrician.",
            "totalTime": "PT15M",
            "tools": ["Non-contact voltage tester"],
            "steps": [
                {"name": "Unplug what is connected",
                 "text": "Remove everything from the outlet, including power strips. Note whether the plug itself or the device's power supply was the warm part - many chargers and adapters run warm by design."},
                {"name": "Wait and re-check",
                 "text": "Give the outlet 30 minutes with nothing plugged in and feel it again. An outlet that stays warm with no load is a wiring problem, not a load problem."},
                {"name": "Look for damage",
                 "text": "Check for discoloration, scorch marks, a melted or deformed faceplate, a burning smell or a loose-feeling receptacle. Any of these means stop and call an electrician."},
                {"name": "Shut off the circuit if the outlet is hot",
                 "text": "If the outlet is hot rather than mildly warm, or shows any damage, switch off its breaker and leave it off. Do not remove the faceplate or attempt a repair."},
                {"name": "Check what the circuit is carrying",
                 "text": "Add up the load on that circuit - space heaters, window units, hair dryers and toasters are the usual culprits. Consistent heat on a fully loaded circuit means the circuit is undersized for how the room is used."},
                {"name": "Call a licensed electrician",
                 "text": "Have the receptacle, the connections behind it and the circuit evaluated. The fix may be a new receptacle, a repaired connection, or an added circuit if the load is the real problem."},
            ],
        },
        "faqs": [
            ("Is it normal for an outlet to feel warm?",
             "No. Outlets and their faceplates should stay at room temperature. A dimmer switch plate that is slightly warm is normal, and a plug-in power adapter can run warm on its own, but the receptacle itself getting warm is a symptom of a problem."),
            ("What makes an outlet warm?",
             "An overloaded circuit, a loose connection at the receptacle's terminals - most often the push-in back-stab connections rather than the screws - a worn receptacle whose contacts no longer grip the plug, a damaged or undersized conductor, or aluminum branch wiring terminated on devices not rated for it."),
            ("Is a warm outlet dangerous?",
             "It can be. Heat at a connection means resistance, resistance means arcing is developing, and arcing inside a wall cavity is how electrical fires start. Treat a warm outlet as something to fix now rather than watch."),
            ("What should I do if an outlet is hot to the touch?",
             "Unplug everything, shut the circuit off at the breaker, and call an electrician. If you see scorch marks, smell burning or see smoke, leave the breaker off and treat it as an emergency."),
            ("Can a warm outlet fix itself?",
             "No. A loose terminal or a worn receptacle only gets worse as it heats and cools, because each cycle loosens the connection a little more."),
        ],
        "services": [
            {
                "name": "Outlet Repair and Circuit Troubleshooting",
                "serviceType": "Electrical repair and troubleshooting",
                "description": "Diagnosis and repair of warm, sparking or dead outlets, including receptacle replacement, connection repair, circuit load evaluation and added circuits.",
                "url": f"{SITE}/electrical-repair-troubleshooting/",
            }
        ],
    },
    {
        "slug": "electrical-load-calculation",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Electrical Load Calculation",
        "breadcrumb_name": "Electrical Load Calculation",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Panels",
        "keywords": "electrical load calculation, residential load calculation, service size calculation, panel capacity Baltimore",
        "about": ["Electrical load", "Electrical service", "National Electrical Code", "Electrical panel"],
        "image_caption": "Electrician performing a residential electrical load calculation at a panel",
        "howto": {
            "name": "How a Residential Electrical Load Calculation Works",
            "description": "The standard method from NEC Article 220 for determining how much electrical service a home needs.",
            "totalTime": "PT1H",
            "steps": [
                {"name": "Measure the conditioned floor area",
                 "text": "Take the square footage of the living space, excluding open porches, garages and unfinished areas not adaptable for future use."},
                {"name": "Add the general lighting and receptacle load",
                 "text": "The standard method assigns 3 volt-amperes per square foot for general lighting and general-use receptacles."},
                {"name": "Add the required branch circuits",
                 "text": "Add 1,500 VA for each of the two or more small-appliance branch circuits required in the kitchen, and 1,500 VA for the laundry circuit."},
                {"name": "Add the nameplate loads of fixed appliances",
                 "text": "Include the range, oven, dryer, water heater, dishwasher, disposal, well pump and any other fastened-in-place equipment at its nameplate rating."},
                {"name": "Apply the demand factors",
                 "text": "The general lighting, small-appliance and laundry loads are totaled, then the first 3,000 VA counts at 100 percent and the remainder at 35 percent under the standard method. Ranges and dryers have their own demand tables."},
                {"name": "Add the larger of heating or cooling",
                 "text": "Compare the air conditioning load against the electric heating load and include only the larger of the two, since they do not run at the same time."},
                {"name": "Convert to amps and compare to the service",
                 "text": "Divide the total volt-amperes by 240 to get the demand in amps, then compare that to the existing service. A result close to or above the service rating means the service needs to be upgraded before load is added."},
            ],
        },
        "faqs": [
            ("What is an electrical load calculation?",
             "It is the calculation that determines how much electrical capacity a home actually needs, based on square footage, required branch circuits, and the nameplate ratings of the appliances and equipment installed. It is what tells you whether a 100-amp service is still adequate or whether the home needs 200 amps."),
            ("When do I need a load calculation?",
             "Before adding significant load - an EV charger, a heat pump, central air, an electric range replacing gas, a hot tub, an addition or a finished basement - and before any service upgrade. Permit offices routinely require one with the application."),
            ("Can I do a load calculation myself?",
             "You can work through the standard method to get a rough idea of where your home stands. The calculation that goes on a permit application, and the decision about service size, should come from a licensed electrician who will also account for the existing panel, the service conductors and the code edition your jurisdiction has adopted."),
            ("Does adding an EV charger require a load calculation?",
             "Yes. An EV charger is a large continuous load, and the calculation determines whether the existing service can carry it, whether load management is needed, or whether the panel and service have to be upgraded first."),
            ("What size electrical service does a house need?",
             "It depends entirely on the calculation. A modest home with gas heat, gas cooking and no central air can still be fine on 100 amps; a home with electric heat, central air, an EV charger or a large addition generally needs 200 amps or more."),
        ],
        "services": [
            {
                "name": "Electrical Load Calculation and Service Sizing",
                "serviceType": "Electrical load calculation",
                "description": "Residential load calculations for permits, service upgrades and new equipment, including panel capacity evaluation and service sizing recommendations.",
                "url": f"{SITE}/electrical-panel-upgrades/",
            }
        ],
    },
])

PAGES.extend([
    {
        "slug": "aluminum-wiring-inspection",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Aluminum Wiring Inspection",
        "breadcrumb_name": "Aluminum Wiring Inspection",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Inspections",
        "keywords": "aluminum wiring inspection, aluminum wiring repair, COPALUM, AlumiConn, Baltimore electrician",
        "about": ["Aluminum wiring", "Electrical inspection", "Electrical safety", "Home wiring"],
        "image_caption": "Aluminum branch circuit conductors terminated in a residential junction box",
        "faqs": [
            ("How do I know if my house has aluminum wiring?",
             "Homes built or rewired roughly between 1965 and 1973 are the ones to check. The cable jacket is often printed with ALUMINUM or AL, and the conductors are silver rather than copper-colored. The check has to be done at the panel and at devices, so it is work for an electrician, not a visual guess from the basement."),
            ("Is aluminum wiring dangerous?",
             "The wire itself is not the problem - the terminations are. Aluminum expands, contracts and oxidizes differently than copper, so connections at outlets, switches and splices loosen over time and overheat. Homes with aluminum branch circuits have a documented history of connection failures at those points."),
            ("Does aluminum wiring have to be replaced?",
             "Not necessarily. The recognized remediation is to repair the connections rather than rip out the wiring - most commonly COPALUM crimp connectors or AlumiConn connectors that join the aluminum conductor to a copper pigtail at every device and splice. Full rewiring is the alternative when the wiring is damaged or the home is already being renovated."),
            ("Can I just install regular outlets and switches on aluminum wiring?",
             "No. Devices used with aluminum conductors must be listed for it - marked CO/ALR for receptacles and switches - and standard devices are a common cause of the overheating this wiring is known for. Even with listed devices, the connector-based repairs are the accepted fix."),
            ("What does an aluminum wiring inspection involve?",
             "An electrician confirms whether the branch circuits are aluminum, opens a representative sample of devices and junction boxes to check the terminations, looks for heat damage, discoloration and loose connections at the panel, and reports on which repair approach fits the home."),
            ("Will aluminum wiring affect my home insurance or sale?",
             "It can. Insurers frequently ask about aluminum branch circuits and may require documented remediation, and buyers' inspectors flag it during a sale. A documented repair by a licensed electrician is what resolves both."),
        ],
        "services": [
            {
                "name": "Aluminum Wiring Inspection and Repair",
                "serviceType": "Aluminum wiring inspection",
                "description": "Inspection of aluminum branch circuit wiring, evaluation of terminations and heat damage, and remediation with listed connectors and copper pigtails or full rewiring.",
                "url": f"{SITE}/home-rewire/",
            }
        ],
    },
    {
        "slug": "gfci-outlet-replacement",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "GFCI Outlet Replacement",
        "breadcrumb_name": "GFCI Outlet Replacement",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Repair",
        "keywords": "GFCI outlet replacement, replace GFCI, GFCI not resetting, GFCI installation Baltimore",
        "about": ["Ground fault circuit interrupter", "Electrical outlet", "Electrical safety", "Electrical repair"],
        "image_caption": "GFCI receptacle with test and reset buttons installed in a kitchen wall",
        "howto": {
            "name": "How a GFCI Outlet Is Replaced",
            "description": "The steps involved in replacing a failed GFCI receptacle, and the wiring details that decide whether downstream outlets stay protected.",
            "totalTime": "PT30M",
            "tools": ["Non-contact voltage tester", "Screwdriver", "Wire strippers", "GFCI outlet tester"],
            "supplies": ["Replacement GFCI receptacle", "Wire connectors", "Faceplate"],
            "steps": [
                {"name": "Confirm the GFCI has actually failed",
                 "text": "Press TEST - the receptacle should trip and cut power - then RESET. A unit that will not trip, will not reset, or does not restore power has failed. A unit that trips repeatedly is reporting a ground fault somewhere on the circuit, and replacing it will not fix that."},
                {"name": "Shut off the circuit and verify",
                 "text": "Switch off the breaker for the circuit and confirm the receptacle is dead with a non-contact voltage tester. Test both halves of the receptacle - some boxes carry more than one circuit."},
                {"name": "Note the LINE and LOAD wiring before removing anything",
                 "text": "Pull the receptacle out and label which cable feeds it. LINE is the incoming supply; LOAD feeds downstream outlets that the GFCI also protects. Reversing them leaves the downstream outlets unprotected and can leave the device unable to reset."},
                {"name": "Transfer the wiring to the new device",
                 "text": "Connect the incoming supply to the LINE terminals and the downstream cable to the LOAD terminals, matching hot, neutral and ground. Use the screw terminals rather than push-in connections, and do not remove the LOAD warning tape unless those terminals are being used."},
                {"name": "Seat the device and restore power",
                 "text": "Fold the conductors carefully into the box, secure the receptacle, install the faceplate and switch the breaker back on."},
                {"name": "Test the device and everything downstream",
                 "text": "Press TEST and RESET on the new device, then use a GFCI outlet tester on it and on every downstream outlet to confirm the protection follows the circuit as expected."},
            ],
        },
        "faqs": [
            ("How often do GFCI outlets need to be replaced?",
             "Plan on roughly ten years, sooner in wet or outdoor locations. The protective electronics degrade even when the outlet still delivers power, which is why the test button matters more than whether the outlet works."),
            ("How do I know if a GFCI outlet is bad?",
             "It will not trip when you press TEST, it will not reset, it resets but delivers no power, or it trips constantly with nothing plugged in. GFCIs made since 2015 self-test and many indicate a failure with a light or by refusing to reset."),
            ("Where are GFCI outlets required?",
             "Kitchens, bathrooms, garages, unfinished basements, crawlspaces, laundry areas, outdoors, and near sinks and wet locations generally. The list has grown with each code cycle, so an older home often needs GFCIs added in places that did not require them when it was built."),
            ("Why does my GFCI keep tripping?",
             "A tripping GFCI is usually reporting a real ground fault - moisture in an outdoor box, a failing appliance, a damaged cord, or a wiring fault downstream. Replacing the device without finding the fault just moves the problem. Unplug everything on the circuit and reset it; if it holds, add devices back one at a time."),
            ("Should I replace a GFCI outlet myself?",
             "Swapping a device on an existing circuit is within reach for a confident homeowner, but the LINE and LOAD terminals are easy to reverse, and doing so silently leaves downstream outlets unprotected. If the GFCI keeps tripping, if the box has multiple cables, or if the wiring is aluminum or ungrounded, have an electrician handle it."),
            ("Can a GFCI be installed on ungrounded wiring?",
             "Yes. A GFCI may replace an ungrounded two-prong receptacle and must be labeled No Equipment Ground. It protects people from shock, but it does not create a ground, so equipment needing a true ground still needs a grounded circuit."),
        ],
        "services": [
            {
                "name": "GFCI Outlet Installation and Replacement",
                "serviceType": "GFCI outlet replacement",
                "description": "Replacement of failed GFCI receptacles, addition of GFCI protection in kitchens, baths, garages and outdoor locations, and diagnosis of circuits that trip repeatedly.",
                "url": f"{SITE}/outlet-installation/",
            }
        ],
    },
    {
        "slug": "when-home-wiring-needs-replacement",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "When Home Wiring Needs Replacement",
        "breadcrumb_name": "When Home Wiring Needs Replacement",
        "description": "{{META_DESCRIPTION}}",
        "section": "Home Rewiring",
        "keywords": "when to replace home wiring, signs you need rewiring, old house wiring, rewiring Baltimore",
        "about": ["Home wiring", "Electrical rewiring", "Knob-and-tube wiring", "Electrical safety"],
        "image_caption": "Deteriorated cloth-insulated wiring in an older Baltimore home",
        "item_list": {
            "name": "Signs home wiring needs to be replaced",
            "items": [
                ("Knob-and-tube wiring", "Ungrounded, brittle with age, and unsafe to bury in insulation. Insurers often will not write a policy on it."),
                ("Cloth-insulated or deteriorating cable", "Mid-century cable whose insulation cracks and falls away at the terminations, leaving bare conductors in the box."),
                ("Aluminum branch circuits", "1965 to 1973 era wiring whose terminations loosen and overheat. It needs either connector-based remediation or replacement."),
                ("Two-prong ungrounded outlets throughout", "A house-wide sign that the branch circuits predate equipment grounding."),
                ("Repeated breaker trips and flickering", "Circuits that trip, dim when appliances start, or run warm are reporting that they are undersized or faulty."),
                ("Scorch marks, burning smells or warm devices", "Heat at outlets, switches or the panel means the connections are failing."),
                ("Too few circuits for how you live", "Extension cords and power strips as permanent wiring means the circuit layout no longer matches the house."),
                ("A major renovation with open walls", "The cheapest time to rewire is when the walls are already open. Waiting means paying twice for access."),
            ],
        },
        "faqs": [
            ("How long does home wiring last?",
             "Modern copper branch wiring in good condition can last the life of the house. What ages out first is everything around it - insulation that degrades, connections that loosen, devices that wear, and panels and circuit layouts that no longer match how the home is used."),
            ("What are the signs a house needs rewiring?",
             "Knob-and-tube, cloth-insulated or aluminum wiring; two-prong ungrounded outlets throughout; a fuse box or an undersized panel; breakers that trip repeatedly; lights that dim when appliances start; warm or discolored outlets and switches; burning smells; and reliance on extension cords because there are not enough circuits."),
            ("Does a whole house need rewiring, or just part of it?",
             "Often just part. Many older homes have had kitchens, baths and additions updated over the years, leaving only the original circuits to replace. An electrician's evaluation identifies which circuits are original and which have already been brought up to date."),
            ("How much does it cost to rewire a house?",
             "A useful estimate is $7.79 per linear foot of wall space plus $1,200 to $2,500 for the electrical panel. The size of the home, the number of circuits added and how much access has to be opened up drive the total."),
            ("Can I rewire a house without tearing out the walls?",
             "Mostly, yes. Electricians route new cable through attics, basements, closets and existing chases, and open small, patchable access points where a run cannot be fished. Some drywall repair is normal, but a whole-home rewire does not mean gutting the house."),
        ],
        "services": [
            {
                "name": "Home Rewiring",
                "serviceType": "Residential rewiring",
                "description": "Evaluation and replacement of outdated or unsafe branch circuit wiring, including partial rewiring, added circuits and panel replacement, permitted and inspected.",
                "url": f"{SITE}/home-rewire/",
                "unit_price": 7.79,
                "unit_text": "linear foot of wall space",
            }
        ],
    },
    {
        "slug": "how-to-test-smoke-alarms",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "How to Test Smoke Alarms",
        "breadcrumb_name": "How to Test Smoke Alarms",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Safety",
        "keywords": "how to test smoke alarms, smoke detector testing, smoke alarm maintenance, Baltimore electrician",
        "about": ["Smoke detector", "Fire safety", "Home maintenance", "Electrical safety"],
        "image_caption": "Pressing the test button on a ceiling-mounted smoke alarm",
        "howto": {
            "name": "How to Test Smoke Alarms",
            "description": "The monthly test that confirms every alarm in the home sounds, plus the interconnect check most people skip.",
            "totalTime": "PT10M",
            "steps": [
                {"name": "Tell everyone in the house first",
                 "text": "Alarms are loud enough to frighten children and pets, and a household that expects the test will not ignore the next real one."},
                {"name": "Press and hold the test button",
                 "text": "Hold the button until the alarm sounds - usually a few seconds. This checks the horn, the battery and the alarm's own electronics."},
                {"name": "Confirm every other alarm sounds",
                 "text": "On interconnected alarms, every alarm in the home should sound within seconds of the one you tested. If they do not, the interconnect is broken and needs attention even though each alarm still works on its own."},
                {"name": "Test each alarm in turn",
                 "text": "Walk the house and test every unit, including basement and hallway alarms. A single alarm that fails is the one covering the room it was installed for."},
                {"name": "Check the age of every unit",
                 "text": "Look for the manufacture date on the back or side of the alarm. Anything ten years past that date is replaced, not retested - the sensor degrades on a timeline the test button cannot see."},
                {"name": "Vacuum the alarms",
                 "text": "Dust and insects cause both missed detections and nuisance alarms. A vacuum brush around the vents once or twice a year is the whole maintenance routine."},
                {"name": "Replace batteries as specified",
                 "text": "Change the backup batteries in hardwired alarms on the manufacturer's schedule, or whenever an alarm chirps. Sealed ten-year units are replaced as a whole rather than re-batteried."},
            ],
        },
        "faqs": [
            ("How often should smoke alarms be tested?",
             "Once a month, and after any extended absence from the home. It takes about ten minutes for a whole house."),
            ("Should I use real smoke or a spray to test an alarm?",
             "The test button is what the manufacturers specify, and it checks the horn, power and electronics. Canned test aerosols are made for the purpose if you want to verify the sensor itself; open flame and smoke sources are not appropriate for a household test."),
            ("What does it mean when my smoke alarm chirps?",
             "A single periodic chirp is usually a low backup battery, or an end-of-life signal on a sealed ten-year unit. Chirping can also come from dust in the chamber or from a unit past its replacement date - check the manufacture date before assuming it is the battery."),
            ("When should smoke alarms be replaced?",
             "Ten years from the manufacture date printed on the unit, regardless of whether it still passes the test. Maryland also requires battery-only alarms over ten years old to be replaced with sealed ten-year lithium battery units."),
            ("Why do all my alarms go off at once?",
             "Because they are interconnected, which is how they are supposed to work - one alarm detecting smoke sounds every alarm in the house. If they sound with no cause, the trigger is usually steam, cooking, dust or a failing unit, and finding which alarm initiated is the first step."),
            ("Do hardwired smoke alarms still need batteries?",
             "Yes. The battery is the backup that keeps the alarm working during a power outage, which is exactly when candle and generator fires happen."),
        ],
        "services": [
            {
                "name": "Smoke Alarm Installation and Testing",
                "serviceType": "Smoke detector installation",
                "description": "Installation, replacement, interconnection and testing of hardwired smoke alarms with battery backup, including code compliance checks before a home sale.",
                "url": "{{SMOKE_DETECTOR_SERVICE_URL}}",
            }
        ],
    },
])

PAGES.extend([
    {
        "slug": "ev-charger-versus-standard-outlet",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "EV Charger vs. a Standard Outlet",
        "breadcrumb_name": "EV Charger vs. Standard Outlet",
        "description": "{{META_DESCRIPTION}}",
        "section": "EV Charging",
        "keywords": "EV charger vs standard outlet, level 1 vs level 2 charging, home EV charger installation, Baltimore electrician",
        "about": ["Electric vehicle charging", "Electrical installation", "Electrical panel", "Home electrification"],
        "image_caption": "Level 2 EV charger installed on a residential garage wall",
        "item_list": {
            "name": "Level 1 outlet charging compared with a Level 2 EV charger",
            "items": [
                ("Circuit", "Level 1 uses an existing 120-volt outlet, ideally a dedicated one. Level 2 needs a dedicated 240-volt circuit, commonly 40 to 60 amps."),
                ("Charging speed", "Level 1 adds only a few miles of range per hour. Level 2 adds several times that, which is the difference between a partial overnight charge and a full one."),
                ("Daily commuting", "Level 1 can keep up with a short commute if the car sits plugged in every night. Level 2 keeps up with almost any usage, including two vehicles."),
                ("Installation work", "Level 1 needs nothing beyond a sound dedicated outlet. Level 2 needs a new circuit, a load calculation, and sometimes a panel or service upgrade."),
                ("Panel capacity", "Level 1 rarely changes the picture. Level 2 is a large continuous load, which is why the calculation comes before the quote."),
                ("Cost", "Level 1 is essentially free if a suitable outlet exists. Level 2 carries equipment and installation cost, and more if the panel needs work."),
            ],
        },
        "faqs": [
            ("Can I charge an EV from a standard outlet?",
             "Yes. Every EV comes with a cordset for a standard 120-volt outlet, which is Level 1 charging. It works, but it adds only a few miles of range per hour, so it suits short commutes and cars that sit plugged in overnight, every night."),
            ("What is the difference between Level 1 and Level 2 charging?",
             "Level 1 uses a 120-volt household outlet. Level 2 uses a dedicated 240-volt circuit and delivers several times the charging speed, typically taking an EV from low to full overnight rather than over a couple of days."),
            ("What circuit does a Level 2 EV charger need?",
             "A dedicated 240-volt circuit sized to the charger, most often 40 to 60 amps, wired to the manufacturer's specification. Because the charger is a continuous load, the circuit is sized above the charger's continuous draw, and the equipment is installed per the code's EV charging requirements."),
            ("Do I need to upgrade my electrical panel for an EV charger?",
             "It depends on the load calculation and the panel's spare capacity. Homes on 200-amp service with gas heat often have room; homes on 100-amp service, or with electric heat and central air, frequently need a service upgrade or a load management device that shares capacity between the charger and other large loads."),
            ("Is it safe to charge an EV from a regular outlet all night?",
             "On a sound, dedicated 120-volt circuit, yes. It is not safe on an extension cord, a shared circuit carrying other loads, or an old outlet with loose connections - those are exactly the conditions that overheat under a continuous multi-hour draw. Have the outlet and circuit checked before relying on it nightly."),
            ("How much does it cost to install a Level 2 charger at home?",
             "{{EV_CHARGER_COST_ANSWER}}"),
        ],
        "services": [
            {
                "name": "EV Charger Installation",
                "serviceType": "EV charger installation",
                "description": "Installation of Level 2 EV charging equipment, including load calculations, dedicated 240-volt circuits, panel capacity evaluation and service upgrades where required.",
                "url": "{{EV_CHARGER_SERVICE_URL}}",
            }
        ],
    },
    {
        "slug": "home-electrical-maintenance",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Home Electrical Maintenance",
        "breadcrumb_name": "Home Electrical Maintenance",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Maintenance",
        "keywords": "home electrical maintenance, electrical maintenance checklist, annual electrical inspection, Baltimore electrician",
        "about": ["Home maintenance", "Electrical safety", "Electrical inspection", "Preventive maintenance"],
        "image_caption": "Electrician checking connections during a routine home electrical maintenance visit",
        "item_list": {
            "name": "Home electrical maintenance schedule",
            "items": [
                ("Monthly - test smoke and CO alarms", "Press the test button on every unit and confirm interconnected alarms all sound."),
                ("Monthly - test GFCI devices", "Press TEST and RESET on every GFCI receptacle and breaker. A device that will not trip has failed."),
                ("Quarterly - walk the outlets and cords", "Check for warm or discolored outlets, loose receptacles, damaged cords, and power strips doing the work of permanent circuits."),
                ("Twice a year - vacuum alarms and check bulbs", "Dust in an alarm chamber causes both missed detections and nuisance trips. Confirm fixtures are within their wattage rating."),
                ("Annually - check the panel and outdoor equipment", "Look for rust, moisture, burning smells or warmth at the panel, and check that outdoor covers, boxes and the service mast are intact."),
                ("Annually - exercise and inspect the generator", "Standby and portable generator equipment, transfer switches and their connections need a run and an inspection before storm season."),
                ("Every 10 years - replace smoke alarms and GFCIs", "Both age out on a schedule the test button cannot reveal. Replace by manufacture date, not by symptom."),
                ("Every few years - a professional inspection", "A licensed electrician checks terminations, torque, grounding, bonding and circuit loading - the things that cannot be seen from the living side of the wall."),
            ],
        },
        "faqs": [
            ("What does home electrical maintenance involve?",
             "Regular testing of smoke alarms and GFCI devices, a look at outlets, switches and cords for heat or damage, seasonal checks of the panel and outdoor equipment, and a periodic professional inspection of the connections, grounding and circuit loading behind the walls."),
            ("How often should I have my electrical system inspected?",
             "Every three to five years for a typical home, annually for homes with older wiring or heavy loads, and additionally when buying or selling, before a major renovation, and after any storm or water damage to electrical equipment."),
            ("What electrical maintenance can I do myself?",
             "Testing alarms and GFCIs, checking for warm or discolored devices, replacing bulbs within the fixture's rating, keeping the panel accessible and labeled, and keeping cords out from under rugs and furniture. Anything requiring the panel cover to come off belongs to an electrician."),
            ("Why does the panel need to be checked if nothing is wrong?",
             "Because connections loosen with thermal cycling, and a loose connection heats long before it trips a breaker. Torque checks, grounding and bonding verification and load balancing are preventive work - they find the failure while it is still a maintenance item."),
            ("Is an electrical maintenance plan worth it?",
             "It is worth it when it catches the loose connection, the failed GFCI or the aging alarm before they become an emergency call. The value is in the schedule being kept rather than in any single visit."),
        ],
        "services": [
            {
                "name": "Home Electrical Maintenance",
                "serviceType": "Electrical maintenance",
                "description": "Scheduled residential electrical maintenance covering panel inspection, connection checks, GFCI and alarm testing, grounding verification and circuit load evaluation.",
                "url": f"{SITE}/stella-simple-electrical-maintenance/",
            }
        ],
    },
    {
        "slug": "examples-hidden-electrical-hazards",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Examples of Hidden Electrical Hazards",
        "breadcrumb_name": "Hidden Electrical Hazards",
        "description": "{{META_DESCRIPTION}}",
        "section": "Electrical Safety",
        "keywords": "hidden electrical hazards, electrical safety hazards at home, unsafe wiring examples, Baltimore electrician",
        "about": ["Electrical hazard", "Electrical safety", "Home wiring", "Electrical inspection"],
        "image_caption": "Open junction box with unsecured splices found inside a residential attic",
        "item_list": {
            "name": "Hidden electrical hazards found in homes",
            "items": [
                ("Buried and open junction boxes", "Splices inside walls, ceilings or attics with no accessible box, or boxes left without covers, where a loose connection can arc unseen."),
                ("Back-stabbed device connections", "Receptacles wired through push-in holes instead of screw terminals. They loosen with load cycling and are a leading cause of warm outlets."),
                ("Double-tapped breakers", "Two conductors under one breaker terminal that is listed for one, which leaves at least one connection loose over time."),
                ("Undersized or unprotected extension wiring", "Lamp cord or undersized cable extending a circuit inside a wall, with no box and no protection from nails and screws."),
                ("Missing or bootleg grounds", "A jumper from neutral to ground at a receptacle so a three-prong tester reads correct. It hides an ungrounded circuit while creating a shock path."),
                ("Insulation contact with non-IC fixtures", "Blown-in insulation piled over recessed cans not rated for it, which cooks the fixture and the wiring above it."),
                ("Nicked or pierced cable", "Cable damaged by a drywall screw, a picture hook or a previous trade, arcing quietly inside the wall cavity."),
                ("Recalled and obsolete panels", "Federal Pacific Stab-Lok and Zinsco panels with a documented history of breakers that fail to trip on a fault."),
                ("Moisture in outdoor and basement boxes", "Water entering through failed covers, missing gaskets or unsealed penetrations, corroding terminations out of sight."),
            ],
        },
        "faqs": [
            ("What are hidden electrical hazards?",
             "Problems that give no symptom from the living side of the wall - buried splices, loose back-stabbed connections, double-tapped breakers, damaged cable, bootleg grounds, moisture in boxes and recalled panels. They are found by opening devices and panels, not by looking at a room."),
            ("How do I know if my home has hidden electrical problems?",
             "Some give warning signs: warm outlets, flickering lights, breakers that trip, buzzing, or a faint burning smell. Many give none at all until they fail, which is why an inspection by a licensed electrician is the only reliable way to find them."),
            ("Are DIY electrical repairs a common source of hazards?",
             "They are one of the most common. Buried splices, missing boxes, undersized wire, bootleg grounds and overloaded circuits are all typical of well-meaning work done without a permit or an inspection."),
            ("Do home inspections catch hidden electrical hazards?",
             "Partly. A general home inspection is visual and non-invasive - it catches what is exposed and reachable, and it will flag a recalled panel or a missing cover. It does not open devices, pull the panel dead front or trace circuits, which is where the hidden problems live."),
            ("What should I do if I find one of these hazards?",
             "Shut off the affected circuit and have a licensed electrician evaluate it. Where one is found, others usually follow, so an inspection of the whole system is more useful than a single repair."),
        ],
        "services": [
            {
                "name": "Electrical Hazard Inspection",
                "serviceType": "Electrical safety inspection",
                "description": "Inspection for concealed electrical hazards including buried splices, loose connections, damaged cable, improper grounding, recalled panels and moisture intrusion, with a written report.",
                "url": f"{SITE}/electrical-code-inspection/",
            }
        ],
    },
    {
        "slug": "how-to-plan-kitchen-outlets",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "How to Plan Kitchen Outlets",
        "breadcrumb_name": "How to Plan Kitchen Outlets",
        "description": "{{META_DESCRIPTION}}",
        "section": "Kitchen Electrical",
        "keywords": "how to plan kitchen outlets, kitchen outlet spacing, kitchen small appliance circuits, kitchen remodel wiring Baltimore",
        "about": ["Kitchen remodeling", "Electrical outlet", "National Electrical Code", "Electrical wiring"],
        "image_caption": "Kitchen countertop receptacles installed above a backsplash during a remodel",
        "howto": {
            "name": "How to Plan Kitchen Outlets",
            "description": "How to lay out kitchen receptacles and circuits so the finished kitchen meets code and matches how the room is actually used.",
            "totalTime": "PT2H",
            "steps": [
                {"name": "Draw the counters and appliances first",
                 "text": "Mark every countertop run, the sink, the range, the refrigerator, built-in appliances and any island or peninsula. Outlet planning follows the cabinet layout, not the other way around."},
                {"name": "Space the countertop receptacles to code",
                 "text": "Countertop receptacles are placed so that no point along the counter wall is more than 24 inches from one - which works out to roughly 4 feet apart - and any counter section 12 inches or wider gets a receptacle."},
                {"name": "Plan the small-appliance branch circuits",
                 "text": "At least two 20-amp small-appliance branch circuits serve the countertop and dining area receptacles, and they cannot feed lighting. Splitting the counter runs across both circuits is what keeps the toaster and the kettle from tripping each other."},
                {"name": "Give the fixed appliances their own circuits",
                 "text": "The range, wall oven, dishwasher, disposal, microwave and refrigerator are planned as dedicated circuits per their nameplate ratings, rather than sharing the counter circuits."},
                {"name": "Plan GFCI protection",
                 "text": "Kitchen receptacles serving the countertop require GFCI protection, and recent code editions extend that to the dishwasher and to other kitchen receptacles. Decide whether protection comes from GFCI breakers or GFCI receptacles at the head of each run."},
                {"name": "Handle islands and peninsulas deliberately",
                 "text": "Island and peninsula receptacle requirements changed between recent code editions, and the rules on placement below the countertop changed with them. Confirm which edition your jurisdiction has adopted before finalizing the layout."},
                {"name": "Add the outlets code does not require",
                 "text": "Charging spots, a coffee station, under-cabinet lighting, a pantry, a range hood and appliance garages are all easier to plan now than to add later. This is the step that separates a code-compliant kitchen from a comfortable one."},
                {"name": "Verify the panel can carry it",
                 "text": "A remodeled kitchen adds several dedicated circuits. Have a load calculation done to confirm the panel has both the capacity and the spaces before the walls close."},
            ],
        },
        "faqs": [
            ("How far apart should kitchen outlets be?",
             "Countertop receptacles are spaced so no point along the counter wall is more than 24 inches from a receptacle, which in practice means about every 4 feet. Any countertop section 12 inches or wider needs its own receptacle."),
            ("How many circuits does a kitchen need?",
             "At least two 20-amp small-appliance branch circuits for the countertop and dining receptacles, plus dedicated circuits for the range, dishwasher, disposal, microwave and refrigerator as their ratings require. A full kitchen commonly ends up with six or more circuits."),
            ("Do kitchen outlets need to be GFCI protected?",
             "Yes. Receptacles serving kitchen countertops require GFCI protection, and recent code editions have extended the requirement to the dishwasher and other kitchen receptacles. Your jurisdiction's adopted code edition determines the exact scope."),
            ("Does a kitchen island need an outlet?",
             "The island and peninsula requirements changed between recent code editions, including where a receptacle may be installed relative to the countertop. Plan the island with your electrician against the edition your jurisdiction enforces, and keep in mind that a usable island almost always wants a receptacle regardless of the minimum."),
            ("Can kitchen lighting share a circuit with the outlets?",
             "No. The small-appliance branch circuits serving the countertop receptacles cannot supply lighting. Kitchen lighting goes on its own circuit."),
            ("Do I need a permit to add kitchen outlets?",
             "Yes. Adding circuits or receptacles is permitted work in Maryland jurisdictions and requires an inspection, which is also what protects you at resale."),
        ],
        "services": [
            {
                "name": "Kitchen Electrical Wiring",
                "serviceType": "Kitchen remodel electrical",
                "description": "Kitchen circuit planning and installation including small-appliance branch circuits, dedicated appliance circuits, GFCI protection, under-cabinet lighting and panel capacity evaluation.",
                "url": f"{SITE}/remodeling/",
            }
        ],
    },
    {
        "slug": "renovation-electrical-upgrades",
        "kind": "article",
        "title": "{{PAGE_TITLE}}",
        "headline": "Electrical Upgrades to Make During a Renovation",
        "breadcrumb_name": "Renovation Electrical Upgrades",
        "description": "{{META_DESCRIPTION}}",
        "section": "Remodeling",
        "keywords": "renovation electrical upgrades, remodel wiring, electrical work during renovation, Baltimore electrician",
        "about": ["Home renovation", "Electrical upgrade", "Electrical wiring", "Remodeling"],
        "image_caption": "New circuits roughed in through open framing during a home renovation",
        "item_list": {
            "name": "Electrical upgrades worth doing while the walls are open",
            "items": [
                ("Panel or service upgrade", "Everything else depends on capacity. If the panel is full or the service is undersized, do this first rather than working around it."),
                ("Replace remaining original branch circuits", "Knob-and-tube, cloth-insulated and aluminum circuits are cheapest to replace when access is already open."),
                ("Add circuits for how the room will actually be used", "Home offices, media walls, workshops and kitchens all need more dedicated circuits than the original layout provided."),
                ("Rough in EV charging", "Even if the car comes later, running conduit or a circuit to the garage now costs a fraction of retrofitting it."),
                ("Whole-house surge protection", "A panel-mounted device is trivial to add while the panel is already being worked on - roughly $350 to $750."),
                ("AFCI and GFCI protection", "New and extended circuits require it, and the renovation is the moment to bring the rest of the home's protection current."),
                ("Recessed and layered lighting", "Ceiling access is what makes new lighting affordable. Plan switching, dimming and zones before the drywall goes up."),
                ("Hardwired interconnected smoke and CO alarms", "Renovations frequently trigger the requirement anyway, and the interconnect wiring is easy only while the walls are open."),
                ("Structured network wiring", "Cable to access points, cameras and equipment locations is the upgrade people most regret skipping."),
                ("Outlets where you will want them", "Under-cabinet, closet, garage, exterior and floor outlets are cheap now and disruptive later."),
            ],
        },
        "faqs": [
            ("What electrical work should I do during a renovation?",
             "Anything that needs access: replacing original wiring, adding circuits, upgrading the panel, roughing in EV charging, adding surge protection, running new lighting and switching, hardwiring interconnected alarms, and pulling network cable. Access is the expensive part of electrical work, and a renovation gives it to you for free."),
            ("Does a renovation trigger electrical code requirements?",
             "Often, yes. Work that extends or modifies circuits generally has to meet current code for the affected areas, and renovations frequently trigger requirements for AFCI and GFCI protection and for hardwired interconnected smoke alarms. The scope depends on the work and on your jurisdiction's adopted code."),
            ("Should I upgrade the electrical panel during a remodel?",
             "If the panel is full, undersized for the finished project, or a fuse box or recalled brand, do it as part of the project rather than after. Panel work during the renovation avoids a second round of scheduling, permitting and utility coordination."),
            ("When in the renovation should the electrician come in?",
             "Twice: at rough-in, after framing and before insulation and drywall, and again at trim-out once the walls and finishes are done. The planning conversation should happen before demolition, while the layout can still change."),
            ("Do I need a permit for electrical work during a renovation?",
             "Yes. New circuits, panel work and rewiring all require a permit and inspections in Maryland jurisdictions. The rough-in inspection has to happen before the walls are closed, which is why it belongs in the schedule from the start."),
        ],
        "services": [
            {
                "name": "Renovation and Remodeling Electrical Work",
                "serviceType": "Electrical remodeling",
                "description": "Electrical rough-in and trim-out for renovations, including added circuits, rewiring, panel upgrades, lighting design, alarm interconnection and EV charger provisions.",
                "url": f"{SITE}/remodeling/",
            }
        ],
    },
])


PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_/]+\}\}")


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
