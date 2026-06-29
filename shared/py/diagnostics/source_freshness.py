from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from shared.py.news_pipeline.adapters import collect_source_items
from shared.py.news_pipeline.sources import NEWS_SOURCES


@dataclass(frozen=True)
class SourceFreshnessCheck:
    source_id: str
    name: str
    city: str
    access_method: str
    parsed_count: int
    latest_date: str
    age_days: int | None
    stale_notice: bool
    status: str
    note: str
    latest_titles: list[str]


def run_source_freshness_diagnostics() -> dict[str, object]:
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    day_iso = now.strftime("%Y-%m-%d")
    checks = [_check_source(source, day_iso) for source in NEWS_SOURCES]
    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
        "total": len(checks),
        "ok": sum(1 for check in checks if check.status == "ok"),
        "notices": sum(1 for check in checks if check.stale_notice),
        "warnings": sum(1 for check in checks if check.status == "warning"),
        "empty": sum(1 for check in checks if check.status == "empty"),
        "checks": [asdict(check) for check in checks],
    }
    output_path = _report_path(now)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**report, "report_path": str(output_path)}


def _check_source(source, day_iso: str) -> SourceFreshnessCheck:
    items = collect_source_items(source, day_iso)
    if not items:
        status = "empty" if source.access_method != "manual" else "warning"
        note = "no parsed items; pipeline will use fallback card"
        if source.access_method == "manual":
            note = "manual source; no adapter is configured"
        return SourceFreshnessCheck(
            source_id=source.source_id,
            name=source.name,
            city=source.city,
            access_method=source.access_method,
            parsed_count=0,
            latest_date="",
            age_days=None,
            stale_notice=False,
            status=status,
            note=note,
            latest_titles=[],
        )

    latest_date = max(item.published_date for item in items if item.published_date)
    age_days = _age_days(latest_date, day_iso)
    status = "ok"
    note = "adapter returned parsed items"
    stale_notice = False
    if age_days is not None and age_days >= 3:
        stale_notice = True
        note = f"latest parsed item is {age_days} days older than build day {day_iso}"

    return SourceFreshnessCheck(
        source_id=source.source_id,
        name=source.name,
        city=source.city,
        access_method=source.access_method,
        parsed_count=len(items),
        latest_date=latest_date,
        age_days=age_days,
        stale_notice=stale_notice,
        status=status,
        note=note,
        latest_titles=[item.title for item in items[:5]],
    )


def _report_path(now: datetime) -> Path:
    project_root = Path(__file__).resolve().parents[3]
    return project_root / "shared" / "data" / "diagnostics" / f"source_freshness_report_{now:%Y-%m-%d}.json"


def _age_days(latest_date: str, day_iso: str) -> int | None:
    try:
        latest = datetime.strptime(latest_date, "%Y-%m-%d").date()
        build_day = datetime.strptime(day_iso, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (build_day - latest).days
