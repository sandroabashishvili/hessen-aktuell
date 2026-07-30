from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from shared.py.jobs_pipeline.sources import JOB_SOURCES


def run_jobs_diagnostics() -> dict[str, object]:
    project_root = Path(__file__).resolve().parents[3]
    data_path = project_root / "shared" / "data" / "jobs" / "jobs_latest.json"
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    warnings: list[str] = []
    notices: list[str] = []

    try:
        payload = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        payload = {}
        warnings.append(f"jobs_latest.json unavailable: {type(exc).__name__}")

    items = payload.get("items", [])
    source_counts = payload.get("source_counts", {})
    if not isinstance(items, list):
        items = []
        warnings.append("items is not a list")
    if not isinstance(source_counts, dict):
        source_counts = {}
        warnings.append("source_counts is not an object")

    expected_source_ids = {source.source_id for source in JOB_SOURCES}
    empty_sources = sorted(
        source_id
        for source_id in expected_source_ids
        if int(source_counts.get(source_id, 0) or 0) == 0
    )
    if empty_sources:
        notices.append(f"empty sources: {', '.join(empty_sources)}")

    item_ids = [
        str(item.get("item_id", ""))
        for item in items
        if isinstance(item, dict)
    ]
    duplicate_ids = len(item_ids) - len(set(item_ids))
    if duplicate_ids:
        warnings.append(f"duplicate item ids: {duplicate_ids}")

    invalid_links = sum(
        1
        for item in items
        if not isinstance(item, dict)
        or urlparse(str(item.get("source_url", ""))).scheme not in {"http", "https"}
    )
    if invalid_links:
        warnings.append(f"invalid source links: {invalid_links}")

    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
        "jobs_count": len(items),
        "configured_sources": len(expected_source_ids),
        "active_sources": len(expected_source_ids) - len(empty_sources),
        "empty_sources": empty_sources,
        "notices": notices,
        "warnings": warnings,
        "status": "ok" if not warnings else "attention_required",
    }
    output_path = (
        project_root
        / "shared"
        / "data"
        / "diagnostics"
        / f"jobs_report_{now:%Y-%m-%d}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {**report, "report_path": str(output_path)}
