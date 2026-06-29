from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path


DEFAULT_BASE_URL = "https://example.com"


@dataclass(frozen=True)
class SitemapResult:
    sitemap_path: Path
    robots_path: Path
    url_count: int


def build_sitemap(project_root: Path, *, base_url: str = DEFAULT_BASE_URL) -> SitemapResult:
    base = base_url.rstrip("/")
    html_pages = sorted(_public_html_pages(project_root))
    urls = [_public_url(project_root, page, base) for page in html_pages]
    sitemap_path = project_root / "sitemap.xml"
    robots_path = project_root / "robots.txt"
    sitemap_path.write_text(_render_sitemap(urls), encoding="utf-8")
    robots_path.write_text(_render_robots(base), encoding="utf-8")
    return SitemapResult(sitemap_path=sitemap_path, robots_path=robots_path, url_count=len(urls))


def _public_html_pages(project_root: Path) -> list[Path]:
    ignored_parts = {".git", "docs", "shared", "__pycache__"}
    pages: list[Path] = []
    for path in project_root.rglob("*.html"):
        if path.name == "404.html":
            continue
        relative_parts = set(path.relative_to(project_root).parts)
        if relative_parts.intersection(ignored_parts):
            continue
        pages.append(path)
    return pages


def _public_url(project_root: Path, page: Path, base: str) -> str:
    relative = page.relative_to(project_root)
    if relative.name == "index.html":
        route = "/".join(relative.parts[:-1])
    else:
        route = relative.as_posix()
    if not route:
        return f"{base}/"
    return f"{base}/{route.strip('/')}/" if relative.name == "index.html" else f"{base}/{route}"


def _render_sitemap(urls: list[str]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(url)}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def _render_robots(base: str) -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {base}/sitemap.xml
"""
