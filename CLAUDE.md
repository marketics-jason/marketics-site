# CLAUDE.md

Guidance for Claude when working in this repository.

## What this is
The Marketics marketing website — **static HTML/CSS/JS**, no build step and no
template engine. Each page is a hand-authored `index.html` (with inline CSS).
Deployed via Netlify on merge to `main`; PRs get a Netlify deploy preview.

## Important: "live" means merged + deployed
A branch push or open PR does **not** change `marketics.io`. Changes only go
live after the PR is **merged to `main`** and Netlify redeploys (~1–2 min).
When a task depends on the live site (e.g. Google's Rich Results Test, which
fetches the live URL), say so explicitly — don't report a fix as done until
it's merged and deployed.

## Adding or editing /intel/ pages
There's no shared template, so schema correctness is enforced by CI, not
inheritance. Before adding a page:

1. Copy the canonical Article JSON-LD block from **`intel/SCHEMA-CHECKLIST.md`**
   and fill in the values. Required: `datePublished` and `dateModified` as full
   ISO 8601 **with timezone** (Eastern: `-04:00` summer / `-05:00` winter),
   plus `image`, `author.url`, and `publisher.url` (all absolute URLs).
2. Self-check locally:
   `python3 scripts/validate-intel-schema.py intel/YOUR-PAGE/index.html`
3. The **"Validate intel schema"** CI check runs on changed intel pages in every
   PR and will fail the PR if the schema doesn't meet the standard.

Older intel pages still on date-only `datePublished` (e.g. `trust`, `money`,
`algorithm`) are intentionally left as-is and only need updating when next
edited — the CI check only inspects files a PR actually changes.

## Conventions
- `marketics.io` blocks non-browser fetchers (403), so verify rendered output
  via the Netlify deploy preview or a browser tool, not a plain fetch.
- Do not create a pull request unless explicitly asked.
