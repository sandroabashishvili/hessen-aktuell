from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo


LOCAL_ATTRS = {
    "a": ("href",),
    "link": ("href",),
    "script": ("src",),
    "img": ("src",),
}


@dataclass(frozen=True)
class InternalLinkCheck:
    source_file: str
    tag: str
    attr: str
    url: str
    resolved_path: str
    status: str
    note: str


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        wanted_attrs = LOCAL_ATTRS.get(tag)
        if not wanted_attrs:
            return
        attr_map = {name: value for name, value in attrs}
        for attr in wanted_attrs:
            value = attr_map.get(attr)
            if value:
                self.links.append((tag, attr, value))


def run_internal_link_diagnostics() -> dict[str, object]:
    project_root = Path(__file__).resolve().parents[3]
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    checks: list[InternalLinkCheck] = []
    for html_path in sorted(project_root.rglob("*.html")):
        if _is_generated_cache(html_path):
            continue
        checks.extend(_check_html_file(project_root, html_path))

    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
        "total": len(checks),
        "ok": sum(1 for check in checks if check.status == "ok"),
        "skipped": sum(1 for check in checks if check.status == "skipped"),
        "broken": sum(1 for check in checks if check.status == "broken"),
        "checks": [asdict(check) for check in checks],
    }
    output_path = _report_path(project_root, now)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**report, "report_path": str(output_path)}


def _check_html_file(project_root: Path, html_path: Path) -> list[InternalLinkCheck]:
    parser = _LinkParser()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    checks = []
    for tag, attr, raw_url in parser.links:
        checks.append(_check_link(project_root, html_path, tag, attr, raw_url))
    return checks


def _check_link(project_root: Path, html_path: Path, tag: str, attr: str, raw_url: str) -> InternalLinkCheck:
    clean_url = raw_url.strip()
    source_file = _relative(project_root, html_path)
    if _should_skip(clean_url):
        return InternalLinkCheck(source_file, tag, attr, clean_url, "", "skipped", "external or non-file URL")

    parsed = urlparse(clean_url)
    local_path = unquote(parsed.path)
    if not local_path:
        return InternalLinkCheck(source_file, tag, attr, clean_url, "", "skipped", "empty local path")

    if local_path.startswith("/"):
        resolved = project_root / local_path.lstrip("/")
    else:
        resolved = html_path.parent / local_path

    resolved = resolved.resolve()
    if not _is_inside(project_root, resolved):
        return InternalLinkCheck(source_file, tag, attr, clean_url, str(resolved), "broken", "resolves outside project")

    target = resolved / "index.html" if clean_url.rstrip().endswith("/") else resolved
    if target.is_dir():
        target = target / "index.html"
    if target.exists():
        return InternalLinkCheck(source_file, tag, attr, clean_url, _relative(project_root, target), "ok", "reachable")
    return InternalLinkCheck(source_file, tag, attr, clean_url, _relative(project_root, target), "broken", "missing local target")


def _should_skip(url: str) -> bool:
    parsed = urlparse(url)
    return (
        not url
        or url.startswith("#")
        or parsed.scheme in {"http", "https", "mailto", "tel", "data", "javascript"}
    )


def _is_inside(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_generated_cache(path: Path) -> bool:
    return "__pycache__" in path.parts


def _relative(project_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(project_root.resolve()))


def _report_path(project_root: Path, now: datetime) -> Path:
    return project_root / "shared" / "data" / "diagnostics" / f"internal_link_report_{now:%Y-%m-%d}.json"
