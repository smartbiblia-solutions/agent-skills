---
name: scrape_web_pages
description: >
  Scrape multi-page websites (sitemaps, hub pages, or URL lists), strip layout
  noise (headers, menus, footers), and store the extracted text as clean Markdown.
  Use when the user needs multi-page web content ingested into Markdown for
  downstream processing, text analysis, or knowledge extraction.
metadata:
  {
    "version": "0.1.0",
    "author": "smartbiblia",
    "maturity": "experimental",
    "preferred_output": "markdown",
    "openclaw":
      {
        "requires": { "bins": ["uv"] },
      },
  }

selection:
  use_when:
    - The task involves scraping multiple web pages into structured Markdown.
    - The user needs to convert website sections into a clean text corpus.
    - Layout noise removal (headers, footers, navigation) is required.
  avoid_when:
    - Only a single page needs to be scraped — use a simple fetch instead.
    - The site requires JavaScript rendering — use a headless browser tool instead.
  prefer_over:
    - generic-web-search

tags:
  - web-scraping
  - markdown
  - corpus
  - text-extraction
---

# Scrape Web Pages

## Overview
Use this skill to convert entire website sections into Markdown corpora. It
covers sitemap expansion, focused crawling, link filtering, markdown cleaning,
and manifest tracking.

- **Primary deliverable:** `markdown/*.md` files plus `manifest.json`
- **Trigger cues:** user mentions sitemap/web crawling, needs multi-page scrape,
  asks to avoid layout chrome, or wants clean text extraction from websites.

## Workflow Summary
1. **Collect inputs** — determine whether the user supplies sitemaps, hub URLs,
   or explicit URL lists. Ask for scope limits (sections, max pages, filters).
2. **Select playbook** — skim `references/scrape_playbooks.md` for the site
   archetype (sitemap-first, docs tree, blog, knowledge base, hub-and-spoke).
3. **Run scraper** — execute
   `skills/scrape-web-pages/scripts/scrape.py` with the chosen
   flags. Key arguments:
   - `--sitemap <url>` (repeatable) for sitemap-driven jobs
   - `--start-url <url>` and `--max-depth` for hub crawls
   - `--url-file urls.txt` for curated lists
   - Filtering: `--include keyword`, `--exclude pattern`, `--min-words 100`
   - Safety: `--max-pages`, `--max-links-per-page`, `--delay`, `--timeout`
   - Output location via `--output-dir artifacts/<project>`
4. **Inspect artifacts** — review `markdown/*.md` for noise and confirm
   `manifest.json` captures provenance (URL, title, word count, hash).
5. **Deliverables** — summarize coverage stats, mention filters used, provide
   path to Markdown corpus.

## Detailed Guidance

### Input Strategy
- Prefer sitemaps when coverage must be comprehensive or when navigation is
  JS-heavy.
- Use hub crawls for curated sections (product overview pages, doc entry points).
- Apply URL lists for compliance-driven work (user-provided canonical URLs).
- Always confirm scope: ask for keywords or sections to include/exclude.

### Cleaning & Noise Removal
`scrape.py` automatically:
- Drops scripts, styles, nav/headers/footers/aside blocks, CTA sections, and
  other layout-heavy nodes (see `REMOVABLE_TAGS`, `STRUCTURAL_TAGS`,
  `LAYOUT_KEYWORDS`).
- Prioritizes semantic blocks (`h1`-`h6`, `p`, `li`, `pre`, `blockquote`,
  `table`).
- Converts tables into Markdown, normalizes whitespace, and adds YAML frontmatter
  with source URL + fetch timestamp.
- Skips pages below `--min-words` threshold to avoid menus or placeholder text.

### Deliverable Checklist
- `artifacts/<project>/markdown/` — cleaned Markdown files, slugged filenames
  (with YAML metadata).
- `artifacts/<project>/manifest.json` — records URL, title, source type, word
  count, SHA256 hash, and run settings.
- Coverage summary — include number of pages saved, total words, filters used,
  and any pages skipped due to low text or blocked domains.

### References
- `references/scrape_playbooks.md` — scenario-specific guidance (sitemap-first,
  docs trees, blogs, knowledge bases, hub-and-spoke portals).
- `scripts/scrape.py` — main automation script (read for flag details
  or to modify cleaning heuristics).

## Scripts
- `scripts/scrape.py` — orchestrates scraping, cleaning, and manifesting.
- `scripts/example.py` — thin wrapper to run the scraper (imports `main`).

## References
- `references/api_reference.md` — pointer index for reference files.
- `references/scrape_playbooks.md` — choose the right scrape strategy.
