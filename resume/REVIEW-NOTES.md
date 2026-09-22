# Review notes before sending this resume out

## 1. Still placeholders
Contact details are filled in except these two. Replace them or delete the line:

- `[add your LinkedIn URL]`
- `[add your portfolio URL]`

Email and phone are set to aprilrosemondejar0@gmail.com and +63 953 132 4768.
The phone is spaced as `+63 953 132 4768` for readability; the +63 country code is kept
so overseas recruiters can dial it directly.

## 2. The percentages are estimates - confirm each one
You asked for safe numbers, so these are deliberately conservative and in the range
recruiters see most often. None of them came from your actual reporting. Confirm each is
true for you before sending, or adjust to your real figures. Interviewers do ask
"how did you measure that?", so be ready to name the tool (GSC, GA4, Ahrefs) and timeframe.

| Role | Claim |
|---|---|
| Professional Summary | average 35% increase in organic traffic across managed accounts |
| Therapy Near Me | 20% increase in organic impressions across optimized pages |
| Building Inspections Near Me | 20% increase in local search visibility |
| ZIB Digital | average 35% increase in organic traffic (matches the summary figure) |
| ZIB Digital | 30% of tracked keywords lifted into the top 10 |
| Freelance SEO Specialist | up to 40% growth in organic traffic |
| TechnologyAdvice | 25% increase in organic traffic across optimized topic clusters |
| Junior SEO Specialist | up to 20% growth in organic traffic |
| Web Developer (Freelance) | 25% reduction in page load times |

Ranga Digital and ANT Digital were left without percentages on purpose - they were short
assistant roles, and metrics there tend to invite questions you cannot answer.

The 35% figure appears twice (summary and ZIB Digital) by design; they refer to the same
result. If you change one, change both.

## 3. Bullets that were added, not supplied - verify before sending
These lines are new, written to cover GEO and AI tooling as requested. Everything else is
your original wording. Keep them only if they are accurate for you.

- Therapy Near Me: "Structure content and schema markup so key pages are eligible for Google
  AI Overviews, featured snippets, and citation by AI assistants."
- Therapy Near Me: "Use Claude and AI-assisted workflows to accelerate technical audits,
  content QA, and bulk on-page optimization across a large page inventory."
- Building Inspections Near Me: "Apply local SEO and structured data best practices across
  service and location pages..."
- ZIB Digital: "Adopted AI tools, including Claude and large language model assistants, to
  scale technical audits, keyword clustering, and content briefing across the client portfolio."
- Technical Skills: the AI tools line names Claude Code, Claude Projects, custom Skills, MCP
  integrations, ChatGPT, Gemini, Perplexity, and Ahrefs Brand Radar. Trim anything you have
  not actually used.

## 4. Spelling variant
Spelling is US English throughout ("optimization"). For Australian or UK applications,
find-and-replace `optimiz` -> `optimis` and `organiz` -> `organis` so the wording matches
how those job ads are written.

## 5. Which file to send
- `.docx` - ATS applications (Workday, Greenhouse, Lever, Taleo, SEEK, LinkedIn Easy Apply).
- `.txt` - plain-text paste fields and older ATS forms.
- `.md` - the master copy. Edit here, then regenerate the other two (see below).
- Export a PDF from the `.docx` only when a job ad explicitly asks for PDF.

## 6. Regenerating after an edit
`April-Rose-Mondejar-SEO-Resume.md` is the single source of truth. After editing it:

```bash
npm install docx
node resume/build-resume.js resume/April-Rose-Mondejar-SEO-Resume.md \
  resume/April-Rose-Mondejar-SEO-Specialist-Resume.docx

sed -e 's/^#\{1,3\} //' -e 's/\*\*//g' -e 's/^_\(.*\)_$/\1/' -e 's/^---$//' \
  resume/April-Rose-Mondejar-SEO-Resume.md | cat -s \
  > resume/April-Rose-Mondejar-SEO-Resume.txt
```

## 7. ATS formatting choices made here
Single column, no tables, no text boxes, no headers or footers, no images or icons, no
multi-column layout. Calibri throughout, US Letter page size, standard section headings,
real bulleted list items, contact details in the document body rather than a header, and
dates as "Month YYYY - Month YYYY" with a plain hyphen.
