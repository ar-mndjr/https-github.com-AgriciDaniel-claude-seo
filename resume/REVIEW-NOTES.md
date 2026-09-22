# Review notes

## 1. There are now two resumes - use the right one for the right channel

| File | Use for |
|---|---|
| `April-Rose-Mondejar-Resume.docx` | Matches your reference layout. Send to humans - recruiters, referrals, email applications. |
| `April-Rose-Mondejar-Resume.pdf` | Same document as PDF, for job ads that ask for PDF. |
| `April-Rose-Mondejar-SEO-Resume-ATS.docx` | Automated application forms (Workday, Greenhouse, Lever, Taleo, SEEK, LinkedIn Easy Apply). |
| `April-Rose-Mondejar-SEO-Resume.txt` | Plain-text paste fields. |
| `April-Rose-Mondejar-SEO-Resume.md` | Editable master for the ATS version. |

**Why two.** Your reference layout puts skills and work experience in two side-by-side
columns. That is built with tables, and tables are the single most common reason an ATS
misreads a resume - parsers often read straight across the page, interleaving the left and
right columns into nonsense. The layout you asked for is reproduced faithfully, but it
carries that risk, so the single-column version exists for the forms that parse
automatically. Send the formatted one to people, the ATS one to machines.

## 2. Format match against the reference PDF
Measured from your PDF and reproduced: Times New Roman 11pt, US Letter, 0.5" margins,
name at 14pt bold, title at 12pt, two columns at 255pt each with a 33pt gap, justified body
text, bold-caps section headings with a full-width rule beneath, company in bold, role and
dates in italics, and the certifications block in bold-italic headings with two-column
italic topic lists. Output is 2 pages, same as the reference.

## 3. Two roles from your old resume are NOT in these versions
Your reference PDF lists two jobs that were not in the details you sent me:

- **Universal Brands LLC** - Wholesale Account Manager (August 2022 - March 2023)
- **Sneaker Arena** - Product Researcher (June 2021 - July 2022)

I left them out because your written details did not include them. Tell me if you want them
back in - worth considering, since dropping them opens an employment gap between
March 2021 and April 2023 that a recruiter will ask about.

## 4. The percentages are estimates - confirm each one
You asked for safe numbers, so these are deliberately conservative. None came from your
actual reporting. Confirm each before sending, and be ready to name the tool (GSC, GA4,
Ahrefs) and timeframe.

| Role | Claim |
|---|---|
| Summary | average 35% increase in organic traffic across managed accounts |
| Therapy Near Me | 20% increase in organic impressions across optimized pages |
| Building Inspections Near Me | 20% increase in local search visibility |
| ZIB Digital | average 35% increase in organic traffic (same result as the summary figure) |
| ZIB Digital | 30% of tracked keywords lifted into the top 10 |
| Freelance SEO Specialist | up to 40% growth in organic traffic |
| TechnologyAdvice | 25% increase in organic traffic across optimized topic clusters |
| Junior SEO Specialist | up to 20% growth in organic traffic |
| Web Developer (Freelance) | 25% reduction in page load times |

Ranga Digital and ANT Digital were left without percentages on purpose - short assistant
roles where metrics invite questions that are hard to answer.

## 5. Bullets that were added, not supplied - verify before sending
Written to cover GEO and AI tooling as requested. Everything else is your own wording.

- Therapy Near Me: AI Overviews / schema eligibility bullet.
- Therapy Near Me: Claude and AI-assisted workflows bullet.
- Building Inspections Near Me: local SEO and structured data bullet.
- ZIB Digital: AI tools for audits, keyword clustering, and content briefing.
- Relevant Skills: the GEO/AEO, AI Overviews, and AI tools entries.

Trim anything you have not actually used - interviewers ask about these.

## 6. Contact details
Email `aprilrosemondejar0@gmail.com`, phone `+63 953 132 4768`, LinkedIn
`https://www.linkedin.com/in/april-rose-mondejar/` (taken from your reference PDF).
Your reference wrote the phone as `0953-132-4768`; the international form is used here
since you are applying to Australian and remote roles. Say the word if you prefer the
local format.

## 7. Spelling
US English throughout ("optimization"). For Australian or UK applications, find-and-replace
`optimiz` -> `optimis` and `organiz` -> `organis`.

## 8. Regenerating after an edit

```bash
npm install docx

# Formatted version (content lives inside the script)
node resume/build-formatted.js resume/April-Rose-Mondejar-Resume.docx
soffice --headless --convert-to pdf --outdir resume resume/April-Rose-Mondejar-Resume.docx

# ATS version (content lives in the .md)
node resume/build-resume.js resume/April-Rose-Mondejar-SEO-Resume.md \
  resume/April-Rose-Mondejar-SEO-Resume-ATS.docx
sed -e 's/^#\{1,3\} //' -e 's/\*\*//g' -e 's/^_\(.*\)_$/\1/' -e 's/^---$//' \
  resume/April-Rose-Mondejar-SEO-Resume.md | cat -s \
  > resume/April-Rose-Mondejar-SEO-Resume.txt
```

Note the two documents have separate content sources: the formatted resume holds its text
inside `build-formatted.js` (the left/right column split cannot be expressed in the
markdown), and the ATS resume is generated from the `.md`. **Edit both when you change
wording**, or the two will drift apart.
