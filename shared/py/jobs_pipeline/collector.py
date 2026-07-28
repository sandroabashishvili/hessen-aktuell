from __future__ import annotations

from datetime import date, datetime

from .adapters import collect_source_jobs
from .models import JobItem
from .sources import JOB_SOURCES


GERMAN_MONTHS = {
    "januar": 1,
    "februar": 2,
    "märz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "dezember": 12,
}


def collect_jobs() -> tuple[list[JobItem], dict[str, int]]:
    jobs: list[JobItem] = []
    source_counts: dict[str, int] = {}
    for source in sorted(JOB_SOURCES, key=lambda item: item.priority):
        source_jobs = [
            job for job in collect_source_jobs(source)
            if not _is_expired(job.deadline)
        ]
        source_counts[source.source_id] = len(source_jobs)
        jobs.extend(source_jobs)
    return _deduplicate(jobs), source_counts


def _deduplicate(jobs: list[JobItem]) -> list[JobItem]:
    unique: dict[str, JobItem] = {}
    for job in jobs:
        unique[job.item_id] = job
    return sorted(
        unique.values(),
        key=lambda job: (_deadline_date(job.deadline) or date.max, job.location, job.title),
    )


def _is_expired(value: str) -> bool:
    parsed = _deadline_date(value)
    return parsed is not None and parsed < date.today()


def _deadline_date(value: str) -> date | None:
    numeric = " ".join(value.split())
    try:
        return datetime.strptime(numeric, "%d.%m.%Y").date()
    except ValueError:
        pass

    cleaned = " ".join(value.lower().replace(".", " ").split())
    parts = cleaned.split()
    if len(parts) < 3:
        return None
    try:
        day = int(parts[0])
        month = GERMAN_MONTHS[parts[1]]
        year = int(parts[2])
        return datetime(year, month, day).date()
    except (KeyError, ValueError):
        return None
