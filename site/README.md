# RankStruct website

Astro site edited with **Pages CMS** and published to cPanel hosting automatically.

## Editing (no code)
1. Go to https://app.pagescms.org and sign in with GitHub.
2. Open this repository (branch `main`).
3. Edit **Blog posts**, any **page**, or **Site settings**, then **Save**.
4. About a minute later the change is live on your domain.

**New blog post:** Blog posts → Add an entry → fill in title, date, category, summary and the article → Save.
Tick **Draft** to save without publishing; untick it to publish.

**Photo on the About page:** About page → Person → Photo → upload.

## One-time setup
1. **FTP login for auto-publish:** GitHub repo → Settings → Secrets and variables → Actions → New secret:
   - `FTP_SERVER` (e.g. `ftp.yourdomain.com`)
   - `FTP_USERNAME` and `FTP_PASSWORD` (cPanel → FTP Accounts)
   - optional `FTP_DIR` if your site isn't in `public_html/`
2. **Site settings in the CMS:** set your real contact email, form recipient, LinkedIn and booking links, and site URL.
3. **SSL:** cPanel → SSL/TLS Status or Let's Encrypt → enable for your domain.

## How it fits together
- `src/content/` — all text: `pages/*.json`, `blog/*.md`, `settings.json` (what the CMS edits)
- `src/pages/` — page templates; `src/components/` — shared sections; `src/styles/` — the design
- `public/` — files copied as-is (logo, images, `.htaccess`)
- `/contact.php` is generated at build time and emails form submissions via your hosting's PHP `mail()`
- `../.pages.yml` — the CMS field definitions; `../.github/workflows/deploy.yml` — build + FTP upload

## Working locally (optional)
```
cd site
npm install
npm run dev      # http://localhost:4321, shows drafts too
npm run build    # output in site/dist
```
