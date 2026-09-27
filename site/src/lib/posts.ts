import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'blog'>;

export const CATEGORY = {
  seo: { name: 'SEO', domain: 'rank', color: 'var(--mint)', icon: 'i-trend' },
  web: { name: 'Web', domain: 'struct', color: 'var(--lav)', icon: 'i-window' },
  automation: { name: 'Automation', domain: 'automate', color: 'var(--violet-l)', icon: 'i-flow' },
} as const;

/** Published posts, newest first. Drafts are included only in `npm run dev`. */
export async function getPosts(): Promise<Post[]> {
  const posts = await getCollection('blog', ({ data }) => import.meta.env.DEV || !data.draft);
  return posts.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export const postUrl = (p: Post) => `/blog/${p.id}/`;

export const formatDate = (d: Date) =>
  d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
