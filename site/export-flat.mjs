// Turns the built site (dist/) into one flat folder of self-contained .html
// files — the same format as the original hand-made site. Every page opens by
// double-clicking, and the folder can also be uploaded to any hosting as is.
//
//   npm run export      →  ../rankstruct-export/
import fs from 'node:fs';
import path from 'node:path';

const DIST = new URL('./dist/', import.meta.url).pathname;
const OUT = new URL('../rankstruct-export/', import.meta.url).pathname;

// Clean addresses → flat file names
function fileFor(p) {
  const clean = p.replace(/index\.html$/, '').replace(/\/+$/, '');
  if (clean === '') return 'index.html';
  if (clean === '/404.html' || clean === '/404') return '404.html';
  const special = {
    '/services/seo': 'seo.html',
    '/services/web-development': 'web-development.html',
    '/services/ai-automation': 'automation.html',
  };
  if (special[clean]) return special[clean];
  return clean.replace(/^\//, '').replace(/\//g, '-') + '.html'; // /seo/saas → seo-saas.html, /blog/x → blog-x.html
}

const pages = [];
(function walk(dir) {
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, f.name);
    if (f.isDirectory()) walk(full);
    else if (f.name.endsWith('.html')) pages.push('/' + path.relative(DIST, full));
  }
})(DIST);

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const logo = 'data:image/svg+xml;base64,' + fs.readFileSync(path.join(DIST, 'logo.svg')).toString('base64');
const fileExists = (p) => fs.existsSync(path.join(DIST, p));

for (const page of pages) {
  let html = fs.readFileSync(path.join(DIST, page), 'utf8');

  // Inline stylesheets
  html = html.replace(/<link rel="stylesheet" href="(\/_astro\/[^"]+\.css)">/g,
    (_, href) => `<style>${fs.readFileSync(path.join(DIST, href), 'utf8')}</style>`);

  // Favicon travels with the page
  html = html.replace(/href="\/logo\.svg"/g, `href="${logo}"`);

  // Rewrite site-absolute links to the flat file names
  html = html.replace(/(href|src|data-endpoint|action)="\/([^"]*)"/g, (m, attr, rest) => {
    const [p, hash = ''] = ('/' + rest).split('#');
    const h = hash ? '#' + hash : '';
    if (/\.(php|svg|png|jpe?g|webp|gif|ico|txt|xml|pdf)$/i.test(p)) return `${attr}="${p.slice(1)}${h}"`;
    return `${attr}="${fileFor(p)}${h}"`;
  });

  fs.writeFileSync(path.join(OUT, fileFor(page)), html);
}

// Supporting files: form handler, images, logo, server config
for (const f of ['contact.php', 'logo.svg', '.htaccess']) if (fileExists(f)) fs.copyFileSync(path.join(DIST, f), path.join(OUT, f));
if (fileExists('images')) fs.cpSync(path.join(DIST, 'images'), path.join(OUT, 'images'), { recursive: true });

console.log(`Exported ${pages.length} pages to ${OUT}`);
