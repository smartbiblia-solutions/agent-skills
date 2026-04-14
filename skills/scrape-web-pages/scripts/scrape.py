#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ['requests', 'beautifulsoup4']
# ///
"""Scrape multi-page websites into clean Markdown.

Usage examples:

    uv run scripts/scrape.py \
        --sitemap https://example.com/sitemap.xml \
        --output-dir artifacts/example-site \
        --max-pages 60

    uv run scripts/scrape.py \
        --start-url https://example.com/blog \
        --max-depth 2 --max-pages 40 --delay 1.0

The script supports three input modes (sitemaps, crawl seeds, and explicit URL
lists). It removes layout/navigation blocks, saves clean Markdown files, and
writes an index manifest with provenance metadata.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency 'requests'. Install it with: pip install requests"
    ) from exc

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency 'beautifulsoup4'. Install it with: pip install beautifulsoup4"
    ) from exc

DEFAULT_HEADERS = {
    "User-Agent": (
        "scrape-web-pages/0.1 (+https://github.com/smartbiblia-solutions/agent-skills)"
    )
}
REMOVABLE_TAGS = {
    "script",
    "style",
    "noscript",
    "template",
    "iframe",
    "svg",
    "canvas",
    "picture",
    "source",
    "form",
    "button",
    "input",
}
STRUCTURAL_TAGS = {"header", "nav", "footer", "aside"}
LAYOUT_KEYWORDS = (
    "nav",
    "menu",
    "breadcrumb",
    "footer",
    "header",
    "sidebar",
    "hero",
    "banner",
    "promo",
    "subscribe",
    "comment",
    "share",
    "cookie",
    "signup",
    "login",
    "newsletter",
    "social",
)
BLOCK_SELECTOR = (
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "li",
    "pre",
    "blockquote",
    "table",
)
HEADING_PREFIX = {f"h{i}": "#" * i for i in range(1, 7)}


@dataclasses.dataclass
class QueueItem:
    url: str
    source: str  # "sitemap", "list", "crawl"
    depth: int = 0


@dataclasses.dataclass
class PageRecord:
    url: str
    title: str
    filepath: str
    word_count: int
    source: str
    hash: str


class MultiPageScraper:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.allowed_domains: Set[str] = set()
        self.queue: deque[QueueItem] = deque()
        self.visited: Set[str] = set()
        self.processed: list[PageRecord] = []
        self.output_dir = Path(args.output_dir).resolve()
        self.markdown_dir = self.output_dir / "markdown"
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "manifest.json"

    # ------------------------------------------------------------------
    def add_seed_url(self, url: str, source: str, depth: int = 0) -> None:
        normalized = self.normalize_url(url)
        if not normalized:
            return
        self.allowed_domains.add(self._netloc(normalized))
        self.queue.append(QueueItem(normalized, source, depth))

    # ------------------------------------------------------------------
    def add_url_file(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"URL list not found: {path}")
        for raw in path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            self.add_seed_url(raw, "list", depth=0)

    # ------------------------------------------------------------------
    def add_sitemap(self, url: str, max_urls: Optional[int] = None) -> None:
        urls = self._parse_sitemap(url, max_urls=max_urls)
        for item in urls:
            self.add_seed_url(item, "sitemap", depth=0)

    # ------------------------------------------------------------------
    def _parse_sitemap(
        self, url: str, *, max_urls: Optional[int] = None, _depth: int = 0
    ) -> List[str]:
        normalized = self.normalize_url(url)
        if not normalized:
            return []
        if _depth > 3:
            print(f"Skipping nested sitemap beyond depth 3: {normalized}")
            return []
        print(f"Fetching sitemap: {normalized}")
        try:
            resp = self.session.get(normalized, timeout=self.args.timeout)
            resp.raise_for_status()
        except Exception as exc:  # pragma: no cover - best-effort logging
            print(f"! Failed to fetch sitemap {normalized}: {exc}")
            return []
        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as exc:
            print(f"! Invalid sitemap XML at {normalized}: {exc}")
            return []
        tag = _strip_ns(root.tag)
        results: list[str] = []
        if tag == "sitemapindex":
            for node in root.findall(".//{*}loc"):
                loc = node.text.strip() if node.text else ""
                if loc:
                    results.extend(
                        self._parse_sitemap(
                            loc, max_urls=max_urls, _depth=_depth + 1
                        )
                    )
                    if max_urls and len(results) >= max_urls:
                        return results[:max_urls]
        elif tag == "urlset":
            for node in root.findall(".//{*}loc"):
                if node.text:
                    results.append(node.text.strip())
                    if max_urls and len(results) >= max_urls:
                        break
        else:
            print(f"! Unrecognized sitemap root: {root.tag}")
        return results[:max_urls] if max_urls else results

    # ------------------------------------------------------------------
    def run(self) -> dict:
        total_limit = self.args.max_pages
        if total_limit <= 0:
            raise SystemExit("max-pages must be > 0")
        print(
            f"Starting scrape with up to {total_limit} pages → {self.markdown_dir}"
        )
        while self.queue and len(self.processed) < total_limit:
            item = self.queue.popleft()
            if item.url in self.visited:
                continue
            self.visited.add(item.url)
            if not self._url_allowed(item.url):
                continue
            page_html = self._fetch(item.url)
            if page_html is None:
                continue
            soup = BeautifulSoup(page_html, "html.parser")
            links = self._collect_links(soup, item.url)
            self._strip_layout(soup)
            markdown_body, title, word_count = self._to_markdown(soup)
            if not markdown_body or word_count < self.args.min_words:
                print(
                    f"- Skipping {item.url} (insufficient text: {word_count} words)"
                )
                continue
            record = self._persist_page(
                url=item.url,
                title=title,
                markdown_body=markdown_body,
                source=item.source,
                word_count=word_count,
            )
            self.processed.append(record)
            print(
                f"✓ Saved {record.filepath} | {word_count} words | source={item.source}"
            )
            if (
                item.source == "crawl"
                and item.depth < self.args.max_depth
                and len(self.processed) < total_limit
            ):
                for link in links:
                    if link in self.visited:
                        continue
                    self.queue.append(
                        QueueItem(url=link, source="crawl", depth=item.depth + 1)
                    )
            if self.args.delay > 0:
                time.sleep(self.args.delay)
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_dir": str(self.output_dir),
            "markdown_dir": str(self.markdown_dir),
            "settings": {
                "max_pages": self.args.max_pages,
                "max_depth": self.args.max_depth,
                "same_domain_only": not self.args.allow_offsite,
                "min_words": self.args.min_words,
            },
            "pages": [dataclasses.asdict(p) for p in self.processed],
        }
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(
            f"Saved manifest with {len(self.processed)} pages → {self.manifest_path}"
        )
        return manifest

    # ------------------------------------------------------------------
    def _fetch(self, url: str) -> Optional[str]:
        try:
            resp = self.session.get(url, timeout=self.args.timeout)
            resp.raise_for_status()
            if "text" not in resp.headers.get("content-type", "text"):
                print(f"! Non-text content at {url}; skipping")
                return None
            return resp.text
        except Exception as exc:
            print(f"! Failed to fetch {url}: {exc}")
            return None

    # ------------------------------------------------------------------
    def _collect_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        results: list[str] = []
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "").strip()
            if not href or href.startswith("#"):
                continue
            if any(href.lower().startswith(prefix) for prefix in ("mailto:", "javascript:", "tel:")):
                continue
            absolute = urljoin(base_url, href)
            normalized = self.normalize_url(absolute)
            if not normalized:
                continue
            if not self._url_allowed(normalized):
                continue
            if normalized not in results:
                results.append(normalized)
        return results[: self.args.max_links_per_page]

    # ------------------------------------------------------------------
    def _strip_layout(self, soup: BeautifulSoup) -> None:
        for tag_name in REMOVABLE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        for tag in soup.find_all(True):
            if tag.name in STRUCTURAL_TAGS:
                tag.decompose()
                continue
            blob_parts = []
            classes = tag.get("class") or []
            if isinstance(classes, str):
                classes = [classes]
            blob_parts.extend(classes)
            blob_parts.append(tag.get("id", ""))
            blob_parts.append(tag.get("role", ""))
            blob = " ".join(blob_parts).lower()
            if tag.name in {"div", "section", "ul"} and any(
                keyword in blob for keyword in LAYOUT_KEYWORDS
            ):
                text_length = len(tag.get_text(" ", strip=True).split())
                if text_length <= 150:
                    tag.decompose()

    # ------------------------------------------------------------------
    def _to_markdown(self, soup: BeautifulSoup) -> Tuple[str, str, int]:
        content_root = self._pick_content_root(soup)
        if content_root is None:
            return "", "", 0
        lines: list[str] = []
        seen_nodes: Set[int] = set()
        for node in content_root.find_all(BLOCK_SELECTOR):
            if id(node) in seen_nodes:
                continue
            seen_nodes.add(id(node))
            text = self._extract_text(node)
            if not text:
                continue
            if node.name in HEADING_PREFIX:
                prefix = HEADING_PREFIX[node.name]
                lines.append(f"{prefix} {text}")
            elif node.name == "li":
                depth = self._list_depth(node)
                indent = "  " * depth
                lines.append(f"{indent}- {text}")
            elif node.name == "pre":
                lines.append("```")
                lines.append(node.get_text("\n", strip=False).rstrip())
                lines.append("```")
            elif node.name == "blockquote":
                lines.append("> " + text)
            elif node.name == "table":
                table_md = self._table_to_md(node)
                if table_md:
                    lines.extend(table_md)
            else:
                lines.append(text)
            lines.append("")
        markdown = "\n".join(_compact_blank_lines(lines)).strip()
        title = content_root.find("h1")
        page_title = self._extract_text(title) if title else ""
        if not page_title:
            page_title = soup.title.get_text(strip=True) if soup.title else ""
        word_count = len(markdown.split())
        return markdown, page_title, word_count

    # ------------------------------------------------------------------
    def _pick_content_root(self, soup: BeautifulSoup) -> Optional[Tag]:
        candidates = soup.select("main, article, section[role=main], div[role=main]")
        if not candidates and soup.body:
            candidates = [soup.body]
        best = None
        best_words = 0
        for candidate in candidates:
            words = len(candidate.get_text(" ", strip=True).split())
            if words > best_words:
                best_words = words
                best = candidate
        return best

    # ------------------------------------------------------------------
    def _extract_text(self, node: Tag | NavigableString | None) -> str:
        if not node:
            return ""
        text = node.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ------------------------------------------------------------------
    def _list_depth(self, node: Tag) -> int:
        depth = 0
        parent = node.parent
        while parent:
            if parent.name in {"ul", "ol"}:
                depth += 1
            parent = parent.parent
        return max(depth - 1, 0)

    # ------------------------------------------------------------------
    def _table_to_md(self, table: Tag) -> List[str]:
        rows = []
        for tr in table.find_all("tr"):
            cells = [self._extract_text(td) for td in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if not rows:
            return []
        col_count = max(len(r) for r in rows)
        header = rows[0]
        header += [""] * (col_count - len(header))
        divider = ["---"] * col_count
        body = [
            row + [""] * (col_count - len(row))
            for row in rows[1:]
        ]
        lines = [" | ".join(header), " | ".join(divider)]
        for row in body:
            lines.append(" | ".join(row))
        lines.append("")
        return lines

    # ------------------------------------------------------------------
    def _persist_page(
        self,
        *,
        url: str,
        title: str,
        markdown_body: str,
        source: str,
        word_count: int,
    ) -> PageRecord:
        slug = slugify(title or url)
        index = len(self.processed) + 1
        filename = f"{index:04d}-{slug}.md"
        filepath = self.markdown_dir / filename
        frontmatter = (
            "---\n"
            f"source_url: {url}\n"
            f"title: {title or ''}\n"
            f"fetched_at: {datetime.now(timezone.utc).isoformat()}\n"
            "---\n\n"
        )
        content = frontmatter + markdown_body + "\n"
        filepath.write_text(content, encoding="utf-8")
        sha = hashlib.sha256(markdown_body.encode("utf-8")).hexdigest()
        return PageRecord(
            url=url,
            title=title or slug,
            filepath=str(filepath),
            word_count=word_count,
            source=source,
            hash=sha,
        )

    # ------------------------------------------------------------------
    def normalize_url(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return None
        netloc = parsed.netloc.lower()
        if not netloc:
            return None
        path = parsed.path or "/"
        normalized = parsed._replace(
            scheme=parsed.scheme.lower(),
            netloc=netloc,
            path=path,
            params="",
            query=parsed.query,
            fragment="",
        )
        return normalized.geturl()

    # ------------------------------------------------------------------
    def _url_allowed(self, url: str) -> bool:
        if self.args.allow_offsite:
            return self._passes_filters(url)
        netloc = self._netloc(url)
        return netloc in self.allowed_domains and self._passes_filters(url)

    # ------------------------------------------------------------------
    def _passes_filters(self, url: str) -> bool:
        lowered = url.lower()
        if self.args.include and not any(p in lowered for p in self.args.include):
            return False
        if self.args.exclude and any(p in lowered for p in self.args.exclude):
            return False
        return True

    # ------------------------------------------------------------------
    def _netloc(self, url: str) -> str:
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "page"


def _compact_blank_lines(lines: Sequence[str]) -> List[str]:
    compact: list[str] = []
    for line in lines:
        if not line.strip() and compact and not compact[-1].strip():
            continue
        compact.append(line)
    return compact


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape multiple web pages into clean Markdown."
    )
    parser.add_argument(
        "--sitemap",
        action="append",
        default=[],
        help="Sitemap URL to expand into target pages (repeatable)",
    )
    parser.add_argument(
        "--start-url",
        action="append",
        default=[],
        help="Seed page to crawl via in-domain href links (repeatable)",
    )
    parser.add_argument(
        "--url-file",
        type=Path,
        help="Plain text file containing one URL per line",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=40,
        help="Maximum number of pages to save across all sources",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=1,
        help="Depth for crawl seeds (start-url). Depth 0 = seed page only",
    )
    parser.add_argument(
        "--max-links-per-page",
        type=int,
        default=30,
        help="Limit how many links are enqueued per crawled page",
    )
    parser.add_argument(
        "--min-words",
        type=int,
        default=80,
        help="Discard pages with fewer than this many words after cleaning",
    )
    parser.add_argument(
        "--include",
        action="append",
        help="Substring filter that URLs must include (case-insensitive)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Substring filter that URLs must NOT include",
    )
    parser.add_argument(
        "--allow-offsite",
        action="store_true",
        help="Allow following links to domains beyond the seeds",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay (seconds) between requests",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/webscrape"),
        help="Directory where Markdown files and manifest.json will be written",
    )
    args = parser.parse_args(argv)
    args.include = [s.lower() for s in (args.include or [])]
    args.exclude = [s.lower() for s in (args.exclude or [])]
    if not args.sitemap and not args.start_url and not args.url_file:
        parser.error("Provide at least one --sitemap, --start-url, or --url-file")
    return args


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    scraper = MultiPageScraper(args)
    for sitemap in args.sitemap:
        scraper.add_sitemap(sitemap, max_urls=args.max_pages)
    for seed in args.start_url:
        scraper.add_seed_url(seed, source="crawl", depth=0)
    if args.url_file:
        scraper.add_url_file(args.url_file)
    manifest = scraper.run()


if __name__ == "__main__":
    main()
