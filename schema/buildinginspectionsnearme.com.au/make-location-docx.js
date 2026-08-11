/**
 * Build one .docx per location page from output/locations/.
 *
 * The code inside each document is read straight from the generated .html, so
 * it cannot drift. Run generate-locations.py first.
 *
 * Usage: node make-location-docx.js
 */

const fs = require("fs");
const path = require("path");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  Table,
  TableRow,
  TableCell,
  WidthType,
  ShadingType,
  BorderStyle,
} = require("docx");

const BASE = __dirname;
const SRC = path.join(BASE, "output", "locations");
const DOCX_DIR = path.join(SRC, "docx");

const NAVY = "0B2C5A";
const GREY = "5A6472";
const CODE_BG = "F4F6F8";
const WARN_BG = "FFF4E5";
const RULE = "D6DCE4";

const profile = JSON.parse(fs.readFileSync(path.join(BASE, "business-profile.json"), "utf8"));
const services = JSON.parse(fs.readFileSync(path.join(BASE, "services.json"), "utf8")).services;
const config = JSON.parse(fs.readFileSync(path.join(BASE, "locations.json"), "utf8"));
const siteUrl = profile.site.url.replace(/\/$/, "");

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after === undefined ? 160 : opts.after },
    children: [
      new TextRun({
        text,
        font: "Calibri",
        size: 21,
        color: opts.color || "222222",
        bold: !!opts.bold,
        italics: !!opts.italics,
      }),
    ],
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { after: 80 },
    children: [new TextRun({ text, font: "Calibri", size: 34, bold: true, color: NAVY })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 320, after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 6 } },
    children: [new TextRun({ text, font: "Calibri", size: 25, bold: true, color: NAVY })],
  });
}

function subtitle(text) {
  return new Paragraph({
    spacing: { after: 260 },
    children: [new TextRun({ text, font: "Calibri", size: 20, color: GREY })],
  });
}

/** Callout box for the things that must be checked before publishing. */
function callout(lines) {
  return lines.map(
    (line, i) =>
      new Paragraph({
        spacing: { before: i === 0 ? 120 : 0, after: i === lines.length - 1 ? 200 : 60 },
        shading: { type: ShadingType.CLEAR, fill: WARN_BG, color: "auto" },
        indent: { left: 140, right: 140 },
        children: [
          new TextRun({ text: line, font: "Calibri", size: 20, color: "6B4A12", bold: i === 0 }),
        ],
      })
  );
}

function codeLine(line, isFirst, isLast) {
  return new Paragraph({
    spacing: { before: isFirst ? 40 : 0, after: isLast ? 40 : 0, line: 240 },
    shading: { type: ShadingType.CLEAR, fill: CODE_BG, color: "auto" },
    indent: { left: 120, right: 120 },
    children: [
      new TextRun({
        text: line.length ? line : " ",
        font: "Consolas",
        size: 14,
        color: "1B2733",
      }),
    ],
  });
}

function codeBlock(text) {
  const lines = text.replace(/\s+$/, "").split("\n");
  return lines.map((line, i) => codeLine(line, i === 0, i === lines.length - 1));
}

function factsTable(rows) {
  const LABEL = 2600;
  const VALUE = 6700;
  return new Table({
    columnWidths: [LABEL, VALUE],
    rows: rows.map(
      ([label, value]) =>
        new TableRow({
          children: [
            new TableCell({
              width: { size: LABEL, type: WidthType.DXA },
              shading: { type: ShadingType.CLEAR, fill: CODE_BG, color: "auto" },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [
                new Paragraph({
                  children: [
                    new TextRun({ text: label, font: "Calibri", size: 19, bold: true, color: NAVY }),
                  ],
                }),
              ],
            }),
            new TableCell({
              width: { size: VALUE, type: WidthType.DXA },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [
                new Paragraph({
                  children: [
                    new TextRun({ text: value, font: "Calibri", size: 19, color: "222222" }),
                  ],
                }),
              ],
            }),
          ],
        })
    ),
  });
}

function bullets(items) {
  return items.map(
    (text) =>
      new Paragraph({
        bullet: { level: 0 },
        spacing: { after: 90 },
        children: [new TextRun({ text, font: "Calibri", size: 21, color: "222222" })],
      })
  );
}

/** The FAQ as readable copy, so it can be published on the page. */
function faqBlock(questions) {
  const out = [];
  questions.forEach((q, i) => {
    out.push(
      new Paragraph({
        spacing: { before: i === 0 ? 40 : 200, after: 70 },
        children: [
          new TextRun({ text: q.name, font: "Calibri", size: 21, bold: true, color: NAVY }),
        ],
      })
    );
    out.push(body(q.acceptedAnswer.text, { after: 0 }));
  });
  return out;
}

function buildDoc(children) {
  return new Document({
    styles: { default: { document: { run: { font: "Calibri", size: 21 } } } },
    sections: [
      {
        properties: { page: { margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } } },
        children,
      },
    ],
  });
}

const IMPLEMENTATION = [
  "Paste the block above into the <head> of this page, server-side, so it is present in the initial HTML.",
  "This block is self-contained. It carries the local business details itself, so nothing else needs to be added to the page.",
  "The business @id is identical on every page across the site, so all copies resolve to one business entity. Do not change it per page.",
  "The Service node's OfferCatalog links the eleven service pages by @id, which connects this location page into the service cluster.",
  "Rank Math: Page > Rank Math > Schema > Custom Schema (Code Validation tab). Disable its auto-generated WebPage schema for this page so nodes are not duplicated.",
  "Yoast: Yoast already emits WebPage, WebSite, BreadcrumbList and an Organization at #organization. In that case delete those four nodes and keep only the Service node.",
  "Validate at validator.schema.org and in Google's Rich Results Test after publishing.",
];

fs.mkdirSync(DOCX_DIR, { recursive: true });
const written = [];

for (const raw of config.locations) {
  const loc = { ...config.defaults, ...raw };
  const url = `${siteUrl}/${loc.slug}/`;
  const code = fs.readFileSync(path.join(SRC, `${loc.slug}.html`), "utf8");
  const graph = JSON.parse(fs.readFileSync(path.join(SRC, `${loc.slug}.json`), "utf8"))["@graph"];
  const page = graph[2];
  const faq = page.mainEntity || [];

  const nodeList = faq.length
    ? "LocalBusiness (HomeAndConstructionBusiness / ProfessionalService), WebSite, WebPage + FAQPage, BreadcrumbList, Service"
    : "LocalBusiness (HomeAndConstructionBusiness / ProfessionalService), WebSite, WebPage, BreadcrumbList, Service";

  const faqSection = faq.length
    ? [
        h2("FAQ in this markup"),
        body(
          "Transcribed from the live page. If the page copy changes, update locations.json and regenerate so the two stay identical.",
          { color: GREY }
        ),
        ...faqBlock(faq),
      ]
    : [
        h2("FAQ — not included"),
        ...callout([
          "No FAQ schema is included for this page, and that is deliberate.",
          "FAQPage markup must mirror Q&A that a visitor can actually see on the page. The live page could not be read when this was generated, so no questions were written. Inventing plausible questions would put text in the markup that does not exist on the page, which breaches Google's structured data guidelines.",
          "To add it: copy the page's published questions and answers word for word into the `faq` array for this location in locations.json, then re-run generate-locations.py and node make-location-docx.js. The page node becomes WebPage + FAQPage automatically.",
          "Note: Google retired FAQ rich results for all sites on 7 May 2026, so FAQ markup earns no SERP snippet either way. Its value is entity clarity and extraction by AI answer engines.",
        ]),
      ];

  const children = [
    h1(`Building Inspections in ${loc.city}`),
    subtitle("Location page schema | Building Inspections Near Me"),
    factsTable([
      ["Page URL", url],
      ["Schema nodes", nodeList],
      ["Area served", `${loc.city}, ${loc.state}`],
      ["FAQ questions", faq.length ? String(faq.length) : "none — see below"],
      [
        "Pricing",
        loc.priceFrom
          ? `from $${loc.priceFrom} ${loc.priceCurrency} (minPrice, GST inclusive)`
          : "no Offer emitted — no price confirmed for this page",
      ],
      ["Paste into", "<head> of this page"],
    ]),

    h2("Check before publishing"),
    ...callout([
      "Two things in this markup were generated rather than read off the page.",
      "The WebPage and Service descriptions are built from the city, the state and BINM's verified positioning. Check them against the copy actually published on this page and edit generate-locations.py if they differ.",
      `Confirm BINM services ${loc.city}, ${loc.state} with practitioners registered in that jurisdiction. The markup asserts coverage here.`,
    ]),

    ...faqSection,

    h2("JSON-LD"),
    body("Copy everything between the script tags below, including the tags themselves.", {
      color: GREY,
    }),
    ...codeBlock(code),

    h2("Services catalogued on this page"),
    body(
      "The Service node links these eleven service pages by @id, so the location page joins the service cluster rather than sitting on its own.",
      { color: GREY }
    ),
    ...bullets(services.map((s) => s.name)),

    h2("Implementation notes"),
    ...bullets(IMPLEMENTATION),
  ];

  written.push({ file: path.join(DOCX_DIR, `${loc.slug}.docx`), doc: buildDoc(children) });
}

(async () => {
  for (const { file, doc } of written) {
    fs.writeFileSync(file, await Packer.toBuffer(doc));
    console.log(`wrote ${path.relative(BASE, file)}`);
  }
  console.log(`\n${written.length} documents in ${path.relative(BASE, DOCX_DIR)}/`);
})();
