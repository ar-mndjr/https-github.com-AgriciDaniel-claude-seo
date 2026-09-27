import { defineConfig } from 'astro/config';
import settings from './src/content/settings.json' with { type: 'json' };

// Static build. Each page is written as folder/index.html, so Apache on cPanel
// serves clean addresses like /services/seo/ with no extra configuration.
export default defineConfig({
  site: settings.site_url,
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  markdown: { shikiConfig: { theme: 'github-dark-dimmed' } },
});
