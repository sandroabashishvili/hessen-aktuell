from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import json
import os
import re
from urllib.parse import urlparse
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class SitemapCheck:
    route: str
    status: str
    note: str


LOC_PATTERN = re.compile(r"<loc>(.*?)</loc>", re.S)


def run_sitemap_diagnostics() -> dict[str, object]:
    project_root = Path(__file__).resolve().parents[3]
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    sitemap_path = project_root / "sitemap.xml"
    robots_path = project_root / "robots.txt"
    base_path = _base_path()
    checks: list[SitemapCheck] = []

    if not sitemap_path.exists():
        checks.append(SitemapCheck("sitemap.xml", "missing", "sitemap.xml is missing"))
        sitemap_routes: set[str] = set()
    else:
        sitemap_routes = _sitemap_routes(sitemap_path)

    if not robots_path.exists():
        checks.append(SitemapCheck("robots.txt", "missing", "robots.txt is missing"))

    for page in _public_html_pages(project_root):
        route = _page_route(project_root, page, base_path)
        if route in sitemap_routes:
            checks.append(SitemapCheck(route, "ok", "covered by sitemap"))
        else:
            checks.append(SitemapCheck(route, "missing", "public HTML route is missing from sitemap"))

    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
        "total": len(checks),
        "ok": sum(1 for check in checks if check.status == "ok"),
        "missing": sum(1 for check in checks if check.status == "missing"),
        "sitemap_url_count": len(sitemap_routes),
        "robots_exists": robots_path.exists(),
        "checks": [asdict(check) for check in checks],
    }
    output_path = _report_path(project_root, now)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**report, "report_path": str(output_path)}


def _sitemap_routes(sitemap_path: Path) -> set[str]:
    text = sitemap_path.read_text(encoding="utf-8", errors="ignore")
    routes = set()
    for raw_url in LOC_PATTERN.findall(text):
        path = urlparse(raw_url.strip()).path or "/"
        routes.add(path if path.endswith("/") else f"{path}/")
    return routes


def _public_html_pages(project_root: Path) -> list[Path]:
    ignored_parts = {".git", "docs", "shared", "__pycache__"}
    pages = []
    for path in project_root.rglob("*.html"):
        relative_parts = set(path.relative_to(project_root).parts)
        if relative_parts.intersection(ignored_parts):
            continue
        pages.append(path)
    return sorted(pages)


def _page_route(project_root: Path, page: Path, base_path: str) -> str:
    relative = page.relative_to(project_root)
    if relative.name == "index.html":
        route = "/".join(relative.parts[:-1])
    else:
        route = relative.as_posix()
    local_route = "/" if not route else f"/{route.strip('/')}/"
    if not base_path:
        return local_route
    if local_route == "/":
        return f"/{base_path}/"
    return f"/{base_path}{local_route}"


def _base_path() -> str:
    base_url = os.environ.get("HESSEN_AKTUELL_BASE_URL", "")
    return urlparse(base_url).path.strip("/")


def _report_path(project_root: Path, now: datetime) -> Path:
    return project_root / "shared" / "data" / "diagnostics" / f"sitemap_report_{now:%Y-%m-%d}.json"
