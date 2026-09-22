// Builds the formatted resume .docx, matching the layout of the reference PDF:
// Times New Roman 11pt, US Letter, 0.5" margins, two-column body via borderless
// tables, justified text, bold-caps section headings with a full-width rule.
// Usage: node build-formatted.js <output.docx>
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, LevelFormat, Tab, TabStopType,
} = require('docx');

const FONT = 'Times New Roman';
const S = 22;            // 11pt
const COL = 5070;        // column width in DXA
const GAP = 660;
const CONTENT_W = 10800;   // page width minus margins, in DXA
const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const NO_BORDERS = { top: NONE, bottom: NONE, left: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE };

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size ?? S, bold: o.bold, italics: o.italics });

const line = (text, o = {}) => new Paragraph({
  spacing: { after: o.after ?? 0, before: o.before ?? 0, line: 240 },
  alignment: o.align,
  children: [run(text, o)],
});

// Section heading: bold caps + full-width rule beneath.
const section = (text) => new Paragraph({
  spacing: { before: 240, after: 120 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, space: 3, color: '000000' } },
  children: [run(text, { bold: true })],
});

const bullet = (text, o = {}) => new Paragraph({
  numbering: { reference: 'r-bullets', level: 0 },
  spacing: { after: o.after ?? 0, line: 240 },
  alignment: o.align ?? AlignmentType.JUSTIFIED,
  children: [run(text)],
});

// Literal "• text" line used in the certifications block (matches the reference).
const certItem = (text) => new Paragraph({
  spacing: { after: 0, line: 240 },
  children: [run('• '), run(text, { italics: true })],
});

const cell = (children) => new TableCell({
  width: { size: COL, type: WidthType.DXA },
  borders: NO_BORDERS,
  margins: { top: 0, bottom: 0, left: 0, right: 0 },
  children,
});

const twoCol = (left, right) => new Table({
  columnWidths: [COL, GAP, COL],
  width: { size: COL * 2 + GAP, type: WidthType.DXA },
  borders: NO_BORDERS,
  rows: [new TableRow({
    children: [
      cell(left),
      new TableCell({ width: { size: GAP, type: WidthType.DXA }, borders: NO_BORDERS, children: [new Paragraph('')] }),
      cell(right),
    ],
  })],
});

// One work-experience entry: company (bold), role (italic), dates (italic), bullets.
const jobEntry = ({ company, role, dates, bullets }, first = false) => [
  line(company, { bold: true, before: first ? 0 : 200 }),
  ...(role ? [line(role, { italics: true })] : []),
  line(`(${dates})`, { italics: true, after: 40 }),
  ...bullets.map(b => bullet(b, { after: 20 })),
];

const certBlock = (title, left, right, first = false) => [
  line(title, { bold: true, italics: true, before: first ? 0 : 220, after: 40 }),
  twoCol(left.map(certItem), right.map(certItem)),
];

// ---------------------------------------------------------------- content ---
const SUMMARY = 'SEO Specialist with five years of experience in technical SEO, ecommerce SEO, on-page optimization, keyword research, content strategy, and website development. Experienced in managing portfolios of up to 25 clients across ecommerce, healthcare, real estate, construction, and service-based industries, delivering an average 35% increase in organic traffic. Applies Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO) alongside traditional SEO to build visibility in Google AI Overviews and AI assistants such as ChatGPT, Claude, Gemini, and Perplexity.';

const SKILLS_L = [
  'Technical SEO & Site Audits',
  'On-Page SEO & Content Optimization',
  'Off-Page SEO / Link Building',
  'Ecommerce SEO (Shopify, WooCommerce)',
  'Local SEO & Schema Markup',
  'Keyword Research & Search Intent Analysis',
];
const SKILLS_R = [
  'Generative Engine Optimization (GEO/AEO)',
  'AI Overviews & LLM Visibility Optimization',
  'AI Tools: Claude, ChatGPT, Gemini, Perplexity',
  'SEO Tools: GSC, GA4, Ahrefs, Screaming Frog',
  'WordPress Website Development',
  'HTML, CSS & Woo-Commerce Management',
];

const JOBS_L = [
  {
    company: 'Therapy Near Me', role: 'Web Developer & SEO Technician | Contract, Australia',
    dates: 'April 2026 – Present',
    bullets: [
      'Develop and maintain website content and functionality across service pages, location pages, practitioner profiles, and resource pages.',
      'Implement on-page and technical SEO improvements, contributing to a 20% increase in organic impressions across optimized pages.',
      'Structure content and schema markup so key pages are eligible for Google AI Overviews, featured snippets, and citation by AI assistants.',
      'Use Claude and AI-assisted workflows to accelerate technical audits, content QA, and bulk on-page optimization.',
      'Support technical issue resolution and website improvements in collaboration with SEO and content teams.',
    ],
  },
  {
    company: 'Building Inspections Near Me', role: 'Web Developer | Contract, Australia',
    dates: 'April 2026 – Present',
    bullets: [
      'Develop and maintain website pages and functionality while supporting SEO, user experience, and website performance.',
      'Implement website updates, content changes, and technical improvements based on business and SEO requirements.',
      'Apply local SEO and structured data best practices across service and location pages, supporting a 20% increase in local search visibility.',
    ],
  },
  {
    company: 'ZIB Digital', role: 'Mid-Level SEO Specialist',
    dates: 'November 2024 – April 2026',
    bullets: [
      'Managed a portfolio of up to 25 clients across multiple industries, executing data-driven SEO strategies that delivered an average 35% increase in organic traffic.',
      'Conducted keyword research, search intent analysis, on-page optimization, technical SEO audits, and content optimization.',
      'Developed SEO recommendations that lifted 30% of tracked keywords into the top 10 positions.',
      'Adopted AI tools, including Claude, to scale technical audits, keyword clustering, and content briefing across the portfolio.',
      'Mentored junior SEO team members and supported consistent implementation of SEO best practices.',
    ],
  },
  {
    company: 'Freelance', role: 'SEO Specialist',
    dates: 'April 2024 – October 2024',
    bullets: [
      'Delivered end-to-end SEO services for clients across ecommerce, digital marketing, healthcare, health and wellness, and real estate.',
      'Conducted keyword research, search intent analysis, on-page optimization, technical SEO, and link-building campaigns.',
      'Improved organic visibility and rankings, achieving up to 40% growth in organic traffic and Top 10 rankings for target keywords.',
    ],
  },
];

const JOBS_R = [
  {
    company: 'TechnologyAdvice', role: 'TechRepublic – SEO Research Specialist',
    dates: 'April 2023 – April 2024',
    bullets: [
      'Conducted keyword research and search intent analysis for upcoming content across multiple topic clusters.',
      'Developed SEO recommendations and content guidelines aligned with search intent and organic search opportunities.',
      'Managed weekly internal linking reports and maintained SEO tracking spreadsheets to identify and resolve discrepancies.',
      'Collaborated with SEO and content teams to improve content performance, contributing to a 25% increase in organic traffic across optimized topic clusters.',
    ],
  },
  {
    company: 'Freelance', role: 'Junior SEO Specialist',
    dates: 'June 2021 – March 2023',
    bullets: [
      'Supported keyword research, on-page optimization, technical SEO, and content optimization across client websites.',
      'Monitored organic performance using Google Analytics and Google Search Console to identify SEO opportunities.',
      'Assisted with content optimization and link-building initiatives, supporting up to 20% growth in organic traffic.',
    ],
  },
  {
    company: 'Ranga Digital', role: 'Assistant SEO Specialist',
    dates: 'March 2021 – June 2021',
    bullets: [
      'Assisted in conducting site audits, keyword research, content planning, and on-page optimization.',
      'Created content plan for 90 days.',
    ],
  },
  {
    company: 'ANT Digital', role: 'Assistant SEO Specialist',
    dates: 'September 2020 – March 2021',
    bullets: [
      'Assisted in conducting site audits, keyword research, content planning, and on-page optimization.',
      'Conducted guest post prospecting and supported link building outreach campaigns.',
    ],
  },
  {
    company: 'Freelance', role: 'Web Developer',
    dates: 'January 2019 – August 2020',
    bullets: [
      'Built and maintained responsive websites with a focus on usability, mobile optimization, and cross-browser compatibility.',
      'Translated client requirements into functional, user-friendly web solutions.',
      'Implemented front-end improvements that reduced page load times by 25% and enhanced website usability.',
    ],
  },
];

const CERTS = [
  ['Google Data Analytics Professional Certificate – Coursera',
    ['Data Analysis', 'SQL', 'Spreadsheet Software', 'Business Analysis'],
    ['Business Communication', 'Data Visualization', 'Data Management', 'General Statistics']],
  ['Advanced Google Analytics',
    ['Content Groupings', 'Advanced Marketing Tools', 'Custom Dimensions and Metrics', 'Google Tag Manager', 'Data Collection and Processing'],
    ['Assisted Conversions', 'Custom Reporting', 'Segments', 'User ID Tracking']],
  ['SEO Advance Master Class – All White Hat SEO',
    ['Local SEO Techniques and Strategy', 'Creating an Internal Link building Strategy', 'Off page SEO Tactic: Niche edits', 'Off page SEO Tactic: HARO'],
    ['Off page SEO Tactic: Roundup', 'Creating Off Page Link Building Strategy', 'Creating an SEO Strategy based on site audit.', 'Content Audit and Consolidation']],
  ['SEO Foundations – LinkedIn Learning',
    ['On-Page Optimization', 'Off-Page Optimization', 'Technical Optimization'],
    ['Keyword Strategy', 'International SEO', 'Link building']],
  ['WordPress Website Development – Udemy',
    ['Domain and Hosting Setup', 'Design and Development', 'Plugins'],
    ['Content Creation', 'SEO Fundamentals', 'Woo-Commerce']],
];

// ------------------------------------------------------------------ build ---
const children = [
  line('April Rose P. Mondejar', { bold: true, size: 28 }),
  line('SEO Specialist', { size: 24 }),
  line('+63 953 132 4768 | aprilrosemondejar0@gmail.com | https://www.linkedin.com/in/april-rose-mondejar/', { after: 240 }),
  new Paragraph({
    spacing: { after: 240, line: 240 }, alignment: AlignmentType.JUSTIFIED,
    children: [run(SUMMARY)],
  }),

  section('RELEVANT SKILLS'),
  twoCol(SKILLS_L.map(t => bullet(t, { align: AlignmentType.LEFT })), SKILLS_R.map(t => bullet(t, { align: AlignmentType.LEFT }))),

  new Paragraph({ spacing: { before: 240, after: 120 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, space: 3, color: '000000' } }, children: [run('WORK EXPERIENCE', { bold: true })] }),
  twoCol(
    JOBS_L.flatMap((j, i) => jobEntry(j, i === 0)),
    JOBS_R.flatMap((j, i) => jobEntry(j, i === 0)),
  ),

  new Paragraph({ spacing: { before: 360, after: 120 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, space: 3, color: '000000' } }, children: [run('EDUCATION AND CERTIFICATIONS', { bold: true })] }),
  line('Colegio de San Gabriel Arcangel', { bold: true }),
  new Paragraph({
    spacing: { after: 220, line: 240 },
    tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    children: [
      run('Bachelor of Science in Computer Engineering', { italics: true }),
      new TextRun({ font: FONT, size: S, italics: true, children: [new Tab()] }),
      run('San Jose Del Monte, Bulacan (June 2024)', { italics: true }),
    ],
  }),
  ...CERTS.flatMap(([t, l, r], i) => certBlock(t, l, r, i === 0)),
];

const doc = new Document({
  creator: 'April Rose P. Mondejar',
  title: 'April Rose P. Mondejar - SEO Specialist Resume',
  numbering: {
    config: [{
      reference: 'r-bullets',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 180 } } },
      }],
    }],
  },
  styles: { default: { document: { run: { font: FONT, size: S, color: '000000' } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    children,
  }],
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('written:', process.argv[2]); });
