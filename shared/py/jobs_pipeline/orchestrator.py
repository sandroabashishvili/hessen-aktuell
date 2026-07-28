from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from .builder import JobsPageBuilder
from .collector import collect_jobs


def run_jobs_generation(project_root: Path | None = None) -> dict[str, object]:
    root = project_root or Path(__file__).resolve().parents[3]
    local_now = datetime.now(ZoneInfo("Europe/Berlin"))
    jobs, source_counts = collect_jobs()
    data_dir = root / "shared" / "data" / "jobs"
    data_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "jobs_latest.json"
    data_path.write_text(
        json.dumps(
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "generated_at_local": local_now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
                "mode": "official_source_adapters",
                "count": len(jobs),
                "source_counts": source_counts,
                "items": [asdict(job) for job in jobs],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    page_path = JobsPageBuilder().build(
        root,
        jobs,
        source_counts,
        generated_at=local_now.strftime("%d.%m.%Y, %H:%M Uhr"),
    )
    return {
        "mode": "official_source_adapters",
        "count": len(jobs),
        "source_counts": source_counts,
        "data_path": str(data_path),
        "page_path": str(page_path),
    }
