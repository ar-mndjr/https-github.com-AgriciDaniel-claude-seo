// Build an ATS-optimized .docx from the markdown master.
// Usage: node build-resume.js <input.md> <output.docx>
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  BorderStyle, LevelFormat, convertInchesToTwip,
} = require('docx');

const FONT = 'Calibri';
const BODY = 22;   // 11pt in half-points
const SMALL = 21;  // 10.5pt

// Split a line on ** markers into alternating normal/bold runs.
const inlineRuns = (text, opts = {}) =>
  text.split('**')
    .map((chunk, i) => ({ chunk, bold: i % 2 === 1 }))
    .filter(({ chunk }) => chunk !== '')
    .map(({ chunk, bold }) => new TextRun({
      text: chunk, font: FONT, size: opts.size ?? BODY,
      ...(bold ? { bold: true } : {}),
      ...(opts.italics ? { italics: true } : {}),
    }));

const para = (text, opts = {}) => new Paragraph({
  spacing: { after: opts.after ?? 60, line: 252 },
  alignment: opts.align,
  children: inlineRuns(text, opts),
});

const section = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 240, after: 100 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, space: 2, color: '000000' } },
  children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: '000000' })],
});

const jobTitle = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 180, after: 0 },
  children: [new TextRun({ text, font: FONT, size: BODY, bold: true, color: '000000' })],
});

const bullet = (text) => new Paragraph({
  numbering: { reference: 'resume-bullets', level: 0 },
  spacing: { after: 40, line: 252 },
  children: inlineRuns(text),
});

// ---- parse markdown ----
const lines = fs.readFileSync(process.argv[2], 'utf8').split('\n').map(l => l.trimEnd());
const children = [];
let inHeader = false;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  if (!line.trim() || line.trim() === '---') { if (line.trim() === '---') inHeader = false; continue; }

  if (line.startsWith('# ')) {                       // name
    children.push(new Paragraph({
      spacing: { after: 40 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: line.slice(2), font: FONT, size: 40, bold: true })],
    }));
    inHeader = true;
    continue;
  }
  if (line.startsWith('## ')) { children.push(section(line.slice(3))); continue; }
  if (line.startsWith('### ')) { children.push(jobTitle(line.slice(4))); continue; }
  if (line.startsWith('- ')) { children.push(bullet(line.slice(2))); continue; }

  // Tight spacing when the next line continues the same block (no blank line between).
  const next = lines[i + 1] || '';
  const tight = next.trim() && next.trim() !== '---' && !next.startsWith('#') && !next.startsWith('- ');
  const opts = { after: tight ? 0 : 60 };
  if (inHeader) { opts.align = AlignmentType.CENTER; opts.size = SMALL; if (!tight) opts.after = 40; }

  const italicLine = /^_.*_$/.test(line.trim());     // _dates_ / _graduated_
  if (italicLine) {
    children.push(para(line.trim().slice(1, -1), { ...opts, italics: true, size: SMALL, after: tight ? 0 : 80 }));
    continue;
  }
  children.push(para(line, opts));
}

const doc = new Document({
  creator: 'April Rose Mondejar',
  title: 'April Rose Mondejar - SEO Specialist Resume',
  description: 'ATS-optimized resume',
  numbering: {
    config: [{
      reference: 'resume-bullets',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: convertInchesToTwip(0.25), hanging: convertInchesToTwip(0.17) } } },
      }],
    }],
  },
  styles: { default: { document: { run: { font: FONT, size: BODY, color: '000000' } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },   // US Letter
        margin: {
          top: convertInchesToTwip(0.6), bottom: convertInchesToTwip(0.6),
          left: convertInchesToTwip(0.7), right: convertInchesToTwip(0.7),
        },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(process.argv[3], buf);
  console.log('written:', process.argv[3]);
});
