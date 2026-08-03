# Project-level Claude SEO install

The files under `.claude/skills/` and `.claude/agents/` are a **mirror** of the
plugin's top-level `skills/` and `agents/` directories. They exist so that any
Claude Code session working in this repository auto-discovers the SEO skills and
sub-agents without a separate install step.

## Priming the Python runtime

The skill markdown works immediately. The bundled Python tools need a one-time
runtime build:

```bash
.claude/skills/seo/bin/claude-seo setup
.claude/skills/seo/bin/claude-seo doctor    # expect: Runtime ready / Chromium ready
```

That creates `.claude/skills/seo/.venv/` (~800 MB, git-ignored). If you already
have a user-level install at `~/.claude/skills/seo`, point at its runtime instead
of building a second copy:

```bash
export CLAUDE_SEO_DATA_DIR="$HOME/.claude/skills/seo"
```

### Environments without access to cdn.playwright.dev

`claude-seo setup` exits 10 when Chromium cannot be downloaded. If the machine
already ships a Playwright Chromium (for example at `/opt/pw-browsers`), link it
into the runtime's browser directory instead of re-downloading, matching the
build number your installed Playwright expects (`python -m playwright --version`,
then check `driver/package/browsers.json`), and set `browser_ready` to `true` in
`runtime-state.json`.

## Keeping the mirror in sync

`.claude/skills/` and `skills/` are **duplicates, not links**. Edits to one do
not propagate to the other. When changing a skill, change the top-level
`skills/` copy (that is the one the plugin manifest and `install.sh` ship), then
re-mirror:

```bash
cp -a skills/. .claude/skills/
for d in extensions/*/skills/*/; do cp -a "$d" ".claude/skills/$(basename "$d")"; done
cp -a agents/*.md .claude/agents/
```

Note that the mirrored copies have `claude-seo run` rewritten to
`.claude/skills/seo/bin/claude-seo run`, since the plugin's `bin/` is not on
`PATH` for a plain checkout. Re-apply that rewrite after re-mirroring.
