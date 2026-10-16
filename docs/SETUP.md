# Local setup on Windows

Follow these steps once, in order, on your Windows PC. They take about 20 minutes.
At the end, WordPress runs locally, and this repository (theme, plugin, mockups and config)
sits inside the Local site folder with the theme and plugin active.

**Software you need:** Local, Git for Windows, VS Code and Claude Code.
**You don't need to install** PHP, MySQL, Apache/nginx, Node.js or WordPress itself. Local includes
the server software and installs WordPress for you.

---

## 1. Check what's already installed

Open **PowerShell** and run:

```powershell
git --version
code --version
claude --version
```

- Each one that prints a version number is installed.
- If `git` says "not recognized", do step 2. Otherwise skip to step 3.
- If XAMPP, WAMP or IIS is running, stop it. It holds ports 80/443, which Local needs.

## 2. Install Git (only if missing)

1. Either download Git from <https://git-scm.com> and install it with the default options, or run
   this in PowerShell:

   ```powershell
   winget install --id Git.Git -e --source winget
   ```

2. Close and reopen PowerShell.
3. Tell Git who you are. Every commit records this.

   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   git config --global init.defaultBranch main
   ```

## 3. Install Local

1. Download Local from <https://localwp.com> (free; choose Windows) and install it with the defaults.
2. On first launch, allow the **administrator** prompt and the **firewall** prompt. Local needs them
   so `seocampaign.local` points at your own PC.

## 4. Create the WordPress site in Local

Click **+** → **Create a new site**.

1. **Site name:** `seocampaign`. Under *Advanced options*, check:
   - Domain: `seocampaign.local`
   - Path: `C:\Users\<you>\Local Sites\seocampaign`
2. **Environment:** choose **Custom**:
   - PHP **8.3**, or the version your live host runs (8.2 or newer)
   - Web server **Apache**. Choose nginx only if you know your host uses it.
   - MySQL **8.x**
3. **WordPress:**
   - Use a username other than `admin`.
   - Use a strong password that you won't reuse on the live site.
   - Multisite: **No**.
4. When it finishes, click **Start site**, then **Trust** next to *SSL*.
5. Click **WP Admin** and log in to check that it works.

## 5. Connect this repository to the site folder

The repository root matches the site folder, so the theme and plugin land exactly where WordPress
looks for them. In **PowerShell**:

```powershell
cd "$env:USERPROFILE\Local Sites\seocampaign"
git init
git remote add origin https://github.com/ar-mndjr/https-github.com-AgriciDaniel-claude-seo.git
git fetch origin
git checkout --track origin/claude/serene-babbage-g96d3z
```

- If GitHub asks you to sign in, a browser window opens; approve it.
- `git status` should now say *"nothing to commit, working tree clean"*. That means WordPress
  core, `wp-config.php` and uploads are correctly ignored.
- These files and folders should now exist:
  - `app\public\wp-content\themes\seocampaign\`
  - `app\public\wp-content\plugins\seocampaign-tools\`
  - `design\mockups\`
  - `CLAUDE.md`

> If you changed Local's default sites folder, use that path in the `cd` line instead.

## 6. Turn on debugging and activate the theme and plugin

1. In Local, right-click the site → **Open site shell**.
2. Paste these commands. `wp config set` edits `wp-config.php` for you, so you don't touch the file
   by hand.

   ```
   wp config set WP_DEBUG true --raw
   wp config set WP_DEBUG_LOG true --raw
   wp config set WP_DEBUG_DISPLAY false --raw
   wp config set SCRIPT_DEBUG true --raw
   wp config set WP_ENVIRONMENT_TYPE local
   wp theme activate seocampaign
   wp plugin activate seocampaign-tools
   ```

What each setting does:

| Setting | Effect |
|---|---|
| `WP_DEBUG` | Report every PHP error and notice |
| `WP_DEBUG_LOG` | Write them to `app\public\wp-content\debug.log` |
| `WP_DEBUG_DISPLAY false` | Keep errors off the page itself |
| `SCRIPT_DEBUG` | Load WordPress's unminified JS/CSS, which makes debugging easier |
| `WP_ENVIRONMENT_TYPE local` | Lets code know it's running on your PC, not live |

Prefer clicking? You can activate the theme in **Appearance → Themes** and the plugin in **Plugins**.

## 7. Set clean URLs

In WP Admin, go to **Settings → Permalinks**, choose **Post name** and click **Save Changes**.
URLs then look like `/free-seo-tools/robots-txt-generator/` instead of `/?p=123`.

## 8. Open the project in VS Code

1. Use **File → Open Folder** to open `C:\Users\<you>\Local Sites\seocampaign`. Open this folder,
   **not** `app\public` or `wp-content`.
2. VS Code will suggest the recommended extensions. Install both:
   - **PHP Intelephense**: PHP autocomplete and error checking for WordPress
   - **EditorConfig**: keeps tabs and line endings consistent

## 9. Start Claude Code in the right place

Start Claude Code from the site folder:

```powershell
cd "$env:USERPROFILE\Local Sites\seocampaign"
claude
```

- To let Claude run WP-CLI (`wp ...`) and `php -l`, start `claude` from Local's **Open site shell**
  window instead. Only that window has them on the PATH.
- `.claude/settings.json` blocks Claude's file tools from editing WordPress core, `wp-config.php`,
  uploads, Local's config and the mockups. This is a guardrail, not a sandbox, so keep reviewing
  what Claude changes.

---

## You're done when

- [ ] `https://seocampaign.local` loads, with a dark header, the site name and a lime line above the footer
- [ ] **Appearance → Themes** shows *SEOcampaign* as active
- [ ] **Plugins** shows *SEOcampaign Tools* as active
- [ ] `app\public\wp-content\debug.log` doesn't exist or is empty
- [ ] `git status` in the site folder says the working tree is clean

## Good to know

- **Email:** forms on the local site never send real email. Local's **Mailpit** catches it
  (site → **Tools** → Mailpit).
- **Database:** Local's **Database** tab opens Adminer if you ever need to look inside.
- **Backups:** Git backs up the code. To back up the content (pages and settings), right-click the site
  in Local → **Export**.
- **Going live later:**
  - The live host gets its own fresh WordPress install.
  - You upload only the `seocampaign` theme and `seocampaign-tools` plugin folders.
  - Never upload the whole site folder or your local `wp-config.php`.
