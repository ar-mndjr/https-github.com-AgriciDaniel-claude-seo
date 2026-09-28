import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Pages CMS may save empty fields as null; treat them as empty values.
const text = z.string().nullish().transform((v) => v ?? '');
const list = <T extends z.ZodTypeAny>(item: T) => z.array(item).nullish().transform((v) => v ?? []);

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: text,
    date: z.coerce.date(),
    category: z.enum(['seo', 'web', 'automation']),
    subcategory: text,
    read_time: z.coerce.number().nullish().transform((v) => v || 5),
    cover: z.string().nullish().transform((v) => v || 'migrate'),
    cover_image: text,
    metric: text,
    metric_label: text,
    featured: z.boolean().nullish().transform((v) => !!v),
    popular: z.boolean().nullish().transform((v) => !!v),
    draft: z.boolean().nullish().transform((v) => !!v),
    author: z.string().nullish().transform((v) => v || 'April'),
    tags: list(z.string()),
    tldr: list(z.string()),
    highlights: list(z.object({ value: z.string(), label: z.string() })),
  }),
});

const link = z.object({ label: text, url: text });
const cardItem = z.object({ title: z.string(), text: text, icon: z.string().nullish().transform((v) => v || 'i-check') });

// Industry SEO pages (/seo/<file name>/)
const industries = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/industries' }),
  schema: z.object({
    order: z.coerce.number().nullish().transform((v) => v ?? 99),
    draft: z.boolean().nullish().transform((v) => !!v),
    seo: z.object({ title: z.string(), description: text }),
    name: z.string(),
    label: text,
    title: z.string(),
    highlight: text,
    text: text,
    primary: link,
    secondary: link,
    answer: z.object({ question: z.string(), text: text }),
    why: z.object({ title: z.string(), text: text.optional(), cards: list(cardItem) }),
    services: z.object({ title: z.string(), text: text.optional(), cards: list(cardItem) }),
    ai: z.object({ title: z.string(), text: text, prompts: list(z.string()), list_title: text, items: list(z.string()) }),
    callout: z.object({ title: text, text: text }).nullish(),
    table: z.object({ title: text, columns: list(z.string()), rows: list(z.object({ cells: list(z.string()) })), note: text }).nullish(),
    faq: z.object({ title: z.string(), items: list(z.object({ question: z.string(), answer: z.string() })) }),
    cta: z.object({ title: z.string(), text: text, button: text }),
    related: list(link),
  }),
});

export const collections = { blog, industries };
