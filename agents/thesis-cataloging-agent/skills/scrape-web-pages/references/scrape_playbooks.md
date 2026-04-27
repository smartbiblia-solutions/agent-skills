# Scrape Playbooks for Multi-Page Webscraper

Use these patterns to configure scraping jobs based on the website structure the user provides.

## Table of Contents
- [Sitemap-first Sites](#sitemap-first-sites)
- [Hub-and-Spoke Portals](#hub-and-spoke-portals)
- [Documentation Trees](#documentation-trees)
- [Blog Archives](#blog-archives)
- [Knowledge-Base Cleanups](#knowledge-base-cleanups)

## Sitemap-first Sites
Many marketing sites expose a comprehensive `sitemap.xml`. Prefer `--sitemap` inputs when:
- The user provides the sitemap URL.
- The site’s navigation is heavily AJAX-based (sitemap gives reliable canonical URLs).
- You only need specific sections (combine with `--include` filters).

**Workflow**
1. Collect targeted sitemap URLs.
2. Run `scrape_to_graph.py --sitemap <URL> --max-pages <N> --include section-keyword`.
3. Inspect `manifest.json` to confirm coverage.

## Hub-and-Spoke Portals
When the user points to a central hub page with many sub-pages (e.g., product overview linking to detail pages).

**Workflow**
1. Use `--start-url https://example.com/hub` and set `--max-depth 1` or `2`.
2. Keep `--max-links-per-page` conservative (10–20) to avoid chasing nav clutter.
3. Combine with `--include` to ensure only relevant spokes are crawled.

## Documentation Trees
Docs portals often have consistent sidebars and anchor-heavy layouts.

**Workflow**
1. Start with sitemap if available. Otherwise, crawl from `/docs/` root.
2. Set `--min-words 100` to skip UI stubs.
3. Use `--exclude` for `/search`, `/api-explorer`, or parameterized examples to avoid duplicates.

## Blog Archives
Blogs include tag pages and date archives with repetitive content.

**Workflow**
1. If RSS feeds exist, convert feed URLs to canonical posts first (avoid feed entries themselves).
2. Use `--max-pages` to limit volume; blogs can be large.
3. Add `--include /blog/` and `--exclude /tag/` to skip taxonomy pages.

## Knowledge-Base Cleanups
Help centers and FAQ portals mix articles with login/signup prompts.

**Workflow**
1. Provide the root category sitemap or start URL.
2. Use higher `--min-words` (120+) so tiny notices are dropped.
3. Consider `--allow-offsite` if articles live on subdomains.

## After Scraping
- Review `markdown/` for noise; adjust filters and rerun if needed.
- Use the cleaned Markdown corpus for downstream processing, analysis, or knowledge extraction.
