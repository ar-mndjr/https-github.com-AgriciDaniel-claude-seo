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

export const collections = { blog };
