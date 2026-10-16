# SEOcampaign website

A professional WordPress site for SEOcampaign: SEO services, web development and free SEO tools.
It is built as a custom lightweight theme plus a custom plugin, developed locally in
[Local](https://localwp.com) on Windows, and deployed to a live host later.

## Where things are

This repository's root **is** the Local site folder: `C:\Users\<you>\Local Sites\seocampaign\`.
Always start Claude Code from this folder. `.claude/settings.json` only loads from here.

| Path | What it is | May Claude edit it? |
|---|---|---|
| `app/public/wp-content/themes/seocampaign/` | **SEOcampaign** theme: layout, templates, CSS | Yes |
| `app/public/wp-content/plugins/seocampaign-tools/` | **SEOcampaign Tools** plugin: the free SEO tools | Yes |
| `design/mockups/` | Approved HTML mockups, the design source of truth | No (read only) |
| `docs/` | Setup guide and project notes | Yes |
| Everything else in `app/public/` | WordPress core, `wp-config.php`, uploads, other plugins | **Never** |
| `conf/`, `logs/`, `app/sql/` | Local's server config, logs and database dumps | **Never** (reading logs is fine) |

## Hard rules

- **Stack:** PHP, HTML, CSS and vanilla JavaScript. No Elementor or other page builders, no React,
  Next.js or headless CMS, no jQuery on the front end, no paid plugins, and no npm build step
  unless the owner agrees first.
- **Never** edit WordPress core, `wp-config.php` or third-party plugins and themes. Config changes go
  through `wp config set` in Local's Site Shell, and only after asking the owner.
- **Never** commit secrets (API keys, passwords). Each environment keeps them as constants in its
  own `wp-config.php`.
- **Ask before** installing software or running destructive commands.
- **Theme = presentation, plugin = functionality.** The plugin must work with any theme. The theme
  must not break when the plugin is inactive: check `function_exists()` or `shortcode_exists()`
  before calling plugin code.

## Naming

| | Theme | Plugin |
|---|---|---|
| Display name | SEOcampaign | SEOcampaign Tools |
| Folder / slug | `seocampaign` | `seocampaign-tools` |
| Text domain | `seocampaign` | `seocampaign-tools` |
| PHP function prefix | `seocampaign_` | `seocampaign_tools_` |
| Constant prefix | `SEOCAMPAIGN_` | `SEOCAMPAIGN_TOOLS_` |
| Script/style handles | `seocampaign-*` | `seocampaign-tools-*` |
| CSS classes | plain names (`.site-header`) | prefixed `.sct-` so they can't clash with any theme |

## Code standards

- Follow the [WordPress Coding Standards](https://developer.wordpress.org/coding-standards/): tabs,
  `array()` syntax, Yoda conditions, and docblocks on functions.
- Minimum versions: **PHP 8.2** and **WordPress 6.8**. Don't use newer PHP features.
- Every PHP file starts with `defined( 'ABSPATH' ) || exit;`, except `index.php` "silence" files.
- **Security**
  - Sanitize input early (`sanitize_text_field`, `absint`, `esc_url_raw` and so on).
  - Escape output late (`esc_html`, `esc_attr`, `esc_url`, `wp_kses_post`).
  - Use a nonce plus `current_user_can()` on every form, admin and AJAX action.
  - Use `$wpdb->prepare()` for any SQL.
  - Give every REST route a real `permission_callback`.
- **Server-side fetching of other sites** (sitemap checker, sitemap import):
  - Use `wp_safe_remote_get()` only, which blocks local and private IPs.
  - Allow http/https only, and set short timeouts and a response size cap.
  - Rate-limit per IP with transients.
  - Never print fetched HTML unescaped.
- **Tools run in the browser where possible**, and visitor input is never stored. The Free Tools
  page promises "nothing stored".

## Front end: performance and accessibility

- Load scripts and styles only where they are used. A tool's JS loads on its own page only.
  Load scripts with `'strategy' => 'defer'`.
- Self-host fonts (woff2, `font-display: swap`). No Google Fonts CDN, for speed and GDPR.
- Images: set `width` and `height`, add `loading="lazy"` below the fold, and prefer WebP/AVIF.
- Meet WCAG 2.2 AA:
  - semantic HTML, the skip link and visible focus styles
  - a label on every form field
  - tap targets at least 44px and body text at least 16px
  - text contrast of 4.5:1 or more
- Design mobile-first. No horizontal scrolling at 320px wide.

## Design

- The mockups in `design/mockups/` are the reference. Open `index.html` in a browser; the pages link
  to each other.
- They use inline styles. Rebuild them with theme classes and the CSS custom properties in
  `themes/seocampaign/assets/css/main.css`. Don't copy the inline styles across.
- Fonts: **Unbounded** (headings, 500/700/800) and **Manrope** (body, 400–700).
- Colours:

| Role | Colour |
|---|---|
| Dark background | `#1C1C1C` |
| Dark cards | `#2A2A28` |
| Page background | `#F5F5F2` |
| Text | `#18181B` |
| Lime accent | `#A8F02E` (hover `#97DF1F`, text on lime `#14210A`) |
| Links | `#14532D` (hover `#0B3B1F`) |

- Layout: max width 1200px with 24px gutters. Buttons are pills (999px radius); cards use 18–24px radii.
- Bracketed placeholders in the mockups (`[3]`, `[hello@seocampaign.co]`, `[number]`, `[city, country]`)
  are content the owner still has to supply. Never invent those values.

## Testing locally

- The site is at `https://seocampaign.local` and the admin at `https://seocampaign.local/wp-admin`.
- PHP errors go to `app/public/wp-content/debug.log`. Check it after every change.
- Outgoing email is caught by Mailpit (Local → site → **Tools** → Mailpit).
- `wp` (WP-CLI) and `php` are only on the PATH inside Local's **Site Shell**. Start `claude` from the
  Site Shell if Claude needs to run them.
- **Before committing:**
  - run `php -l` on changed PHP files
  - confirm `debug.log` has no new entries
  - check the pages at 320px, 768px and 1280px widths

## Git

- Git tracks only the theme, the plugin, `design/`, `docs/` and the root config files (see `.gitignore`).
- Make small commits with clear messages, one feature per branch.

## Decisions still open

- How tools are placed on pages: shortcode or block.
- Alt Text Generator: which AI vision API to use, and how to cap its cost.
- AVIF output: in the browser or on the server (depends on the host's GD/Imagick support).
- Live host and deploy method.
- Brand spelling in content: the mockups write "SEOCampaign". The theme and plugin names use
  "SEOcampaign", as the owner specified.
