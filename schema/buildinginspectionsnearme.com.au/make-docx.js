/**
 * Build one .docx per service page from the generated JSON-LD in output/.
 *
 * The Word files are a delivery format only: the code inside them is read
 * straight from output/*.html, so they cannot drift from the generated markup.
 * Re-run generate.py first, then this.
 *
 * Usage: node make-docx.js
 */

const fs = require("fs");
const path = require("path");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
  Table,
  TableRow,
  TableCell,
  WidthType,
  ShadingType,
  BorderStyle,
} = require("docx");

const BASE = __dirname;
const OUT = path.join(BASE, "output");
const DOCX_DIR = path.join(OUT, "docx");

const NAVY = "0B2C5A";
const GREY = "5A6472";
const CODE_BG = "F4F6F8";
const RULE = "D6DCE4";

const profile = JSON.parse(fs.readFileSync(path.join(BASE, "business-profile.json"), "utf8"));
const services = JSON.parse(fs.readFileSync(path.join(BASE, "services.json"), "utf8")).services;
const siteUrl = profile.site.url.replace(/\/$/, "");

function pageUrl(slug) {
  return `${siteUrl}/${slug}/`;
}

/** Body paragraph. */
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

/** One line of code. Kept as its own paragraph so indentation survives. */
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

function buildDoc(sections) {
  return new Document({
    styles: {
      default: {
        document: { run: { font: "Calibri", size: 21 } },
      },
    },
    sections: [
      {
        properties: {
          page: { margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } },
        },
        children: sections,
      },
    ],
  });
}

const IMPLEMENTATION = [
  "Paste the block above into the <head> of this page, server-side, so it is present in the initial HTML.",
  "The sitewide block (see _sitewide-business.docx) must also be present on this page. This page's Service node references it by @id, so the two work together.",
  "Rank Math: Page > Rank Math > Schema > Custom Schema (Code Validation tab). Disable its auto-generated WebPage schema for this page so nodes are not duplicated.",
  "Yoast: Yoast already emits WebPage, BreadcrumbList and an Organization at #organization. In that case delete the WebPage and BreadcrumbList nodes from this block and keep only the Service node; its provider already points at #organization.",
  "Do not ship two of the same node type on one page. If the theme or plugin already outputs BreadcrumbList, drop the one here.",
  "Validate at validator.schema.org and in Google's Rich Results Test after publishing.",
];

fs.mkdirSync(DOCX_DIR, { recursive: true });
const written = [];

// One document per service page.
for (const service of services) {
  const url = pageUrl(service.slug);
  const code = fs.readFileSync(path.join(OUT, `${service.slug}.html`), "utf8");
  const priceNote = service.priceFrom
    ? `Offer emitted: from $${service.priceFrom} ${service.priceCurrency} (minPrice, GST inclusive)`
    : "No Offer emitted (page quotes on request)";

  const children = [
    h1(service.name),
    subtitle("Service schema | Building Inspections Near Me"),
    factsTable([
      ["Page URL", url],
      ["Schema nodes", "WebPage, BreadcrumbList, Service"],
      ["Service type", service.serviceType],
      ["Primary keyword", service.primaryKeyword || "-"],
      ["Pricing", priceNote],
      ["Paste into", "<head> of this page"],
    ]),
    h2("JSON-LD"),
    body(
      "Copy everything between the script tags below, including the tags themselves.",
      { color: GREY }
    ),
    ...codeBlock(code),
    h2("What this markup says"),
    body(service.description),
    body(`Report delivered: ${service.serviceOutput}`),
    body(`Intended audience: ${service.audience}`),
    h2("Inclusions listed in the markup"),
    body(
      "These appear as the page's OfferCatalog. They should match the inclusions published on the page.",
      { color: GREY }
    ),
    ...bullets(service.items),
    h2("Implementation notes"),
    ...bullets(IMPLEMENTATION),
  ];

  const file = path.join(DOCX_DIR, `${service.slug}.docx`);
  written.push({ file, doc: buildDoc(children) });
}

// The sitewide business block.
{
  const code = fs.readFileSync(path.join(OUT, "_sitewide-business.html"), "utf8");
  const children = [
    h1("Sitewide Business Schema"),
    subtitle("Building Inspections Near Me | paste on every page"),
    factsTable([
      ["Applies to", "Every page on the site, including the 11 service pages"],
      ["Schema nodes", "HomeAndConstructionBusiness / ProfessionalService, WebSite"],
      ["Business @id", `${siteUrl}/#organization`],
      ["Paste into", "Global <head> (header template)"],
    ]),
    h2("JSON-LD"),
    body(
      "This block defines the business once. Every service page references it by @id rather than repeating it, so Google resolves one business entity across the site instead of eleven near-duplicates.",
      { color: GREY }
    ),
    ...codeBlock(code),
    h2("Implementation notes"),
    ...bullets([
      "Paste once into the global header so it appears on every page.",
      "If Yoast is active it already emits an Organization at this same @id. Do not add a second one; keep Yoast's and skip this block, since the Service nodes will attach to it automatically.",
      "logo, image, email, opening hours, sameAs, address and geo are intentionally absent: no published source records them. Add them to business-profile.json and regenerate once they exist.",
      "sameAs is the highest-value addition once the Google Business Profile is live, as it ties this entity to that listing.",
    ]),
  ];
  written.push({ file: path.join(DOCX_DIR, "_sitewide-business.docx"), doc: buildDoc(children) });
}

(async () => {
  for (const { file, doc } of written) {
    fs.writeFileSync(file, await Packer.toBuffer(doc));
    console.log(`wrote ${path.relative(BASE, file)}`);
  }
  console.log(`\n${written.length} documents in ${path.relative(BASE, DOCX_DIR)}/`);
})();
