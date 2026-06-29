from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from shared.py.news_pipeline.http_client import DEFAULT_USER_AGENT
from shared.py.news_pipeline.sources import NEWS_SOURCES


@dataclass(frozen=True)
class SourceLinkCheck:
    source_id: str
    name: str
    city: str
    url: str
    status: str
    http_status: int | None
    note: str


def run_source_link_diagnostics() -> dict[str, object]:
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    checks = [_check_source(source) for source in NEWS_SOURCES]
    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
        "total": len(checks),
        "ok": sum(1 for check in checks if check.status == "ok"),
        "warnings": sum(1 for check in checks if check.status == "warning"),
        "broken": sum(1 for check in checks if check.status == "broken"),
        "checks": [asdict(check) for check in checks],
    }
    output_path = _report_path(now)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**report, "report_path": str(output_path)}


def _check_source(source) -> SourceLinkCheck:
    request = Request(source.url, method="HEAD", headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urlopen(request, timeout=12) as response:
            code = response.status
    except HTTPError as exc:
        code = exc.code
    except (URLError, TimeoutError, OSError) as exc:
        return SourceLinkCheck(source.source_id, source.name, source.city, source.url, "broken", None, type(exc).__name__)

    if 200 <= code < 400:
        return SourceLinkCheck(source.source_id, source.name, source.city, source.url, "ok", code, "reachable")
    if code in {401, 403, 405, 429}:
        return SourceLinkCheck(source.source_id, source.name, source.city, source.url, "warning", code, "reachable but restricted")
    return SourceLinkCheck(source.source_id, source.name, source.city, source.url, "broken", code, "unexpected HTTP status")


def _report_path(now: datetime) -> Path:
    project_root = Path(__file__).resolve().parents[3]
    return project_root / "shared" / "data" / "diagnostics" / f"source_link_report_{now:%Y-%m-%d}.json"
