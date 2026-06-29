from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
from zoneinfo import ZoneInfo


REQUIRED_HEAD_KEYS = {
    "title",
    "description",
    "canonical",
    "og:title",
    "og:description",
    "og:url",
    "twitter:card",
}


@dataclass(frozen=True)
class SeoCheck:
    source_file: str
    key: str
    status: str
    note: str


class _HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""
        self.keys: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            name = attr_map.get("name")
            prop = attr_map.get("property")
            content = attr_map.get("content")
            if name == "description" and content:
                self.keys.add("description")
            if prop in {"og:title", "og:description", "og:url"} and content:
                self.keys.add(prop)
            if name == "twitter:card" and content:
                self.keys.add("twitter:card")
        if tag == "link" and attr_map.get("rel") == "canonical" and attr_map.get("href"):
            self.keys.add("canonical")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data.strip()


def run_seo_diagnostics() -> dict[str, object]:
    project_root = Path(__file__).resolve().parents[3]
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    checks: list[SeoCheck] = []
    for html_path in _public_html_pages(project_root):
        checks.extend(_check_html(project_root, html_path))

    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
        "total": len(checks),
        "ok": sum(1 for check in checks if check.status == "ok"),
        "missing": sum(1 for check in checks if check.status == "missing"),
        "checks": [asdict(check) for check in checks],
    }
    output_path = _report_path(project_root, now)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**report, "report_path": str(output_path)}


def _check_html(project_root: Path, html_path: Path) -> list[SeoCheck]:
    parser = _HeadParser()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    present = set(parser.keys)
    if parser.title:
        present.add("title")

    source_file = str(html_path.resolve().relative_to(project_root.resolve()))
    checks = []
    for key in sorted(REQUIRED_HEAD_KEYS):
        if key in present:
            checks.append(SeoCheck(source_file, key, "ok", "present"))
        else:
            checks.append(SeoCheck(source_file, key, "missing", "missing SEO head field"))
    return checks


def _public_html_pages(project_root: Path) -> list[Path]:
    ignored_parts = {".git", "docs", "shared", "__pycache__"}
    pages = []
    for path in project_root.rglob("*.html"):
        relative_parts = set(path.relative_to(project_root).parts)
        if relative_parts.intersection(ignored_parts):
            continue
        pages.append(path)
    return sorted(pages)


def _report_path(project_root: Path, now: datetime) -> Path:
    return project_root / "shared" / "data" / "diagnostics" / f"seo_report_{now:%Y-%m-%d}.json"
