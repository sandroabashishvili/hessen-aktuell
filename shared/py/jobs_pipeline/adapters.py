from __future__ import annotations

from html import unescape
import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from ..news_pipeline.http_client import fetch_text
from .models import JobItem, JobSource


MAX_ITEMS_PER_SOURCE = 40


def collect_source_jobs(source: JobSource) -> list[JobItem]:
    html = fetch_text(source.url)
    if not html:
        return []
    if source.source_id == "stadt-kassel-jobs":
        return parse_stadt_kassel_jobs(html, source)
    if source.source_id == "hessen-mobil-jobs":
        return parse_hessen_mobil_jobs(html, source)
    if source.source_id == "stadt-frankfurt-jobs":
        return parse_rexx_jobs(
            html,
            source,
            deadline_column=4,
            department_column=2,
            employment_column=3,
        )
    if source.source_id == "stadt-wiesbaden-jobs":
        return parse_rexx_jobs(
            html,
            source,
            deadline_column=3,
            employment_column=2,
        )
    if source.source_id == "stadt-darmstadt-jobs":
        return parse_rexx_jobs(
            html,
            source,
            deadline_column=4,
        )
    return []


def parse_stadt_kassel_jobs(html: str, source: JobSource) -> list[JobItem]:
    jobs: list[JobItem] = []
    seen: set[str] = set()
    for raw_item in re.findall(
        r'<li class="SP-TeaserList__item">(.*?)</li>',
        html,
        flags=re.S,
    ):
        href_match = re.search(
            r'<a[^>]+class="SP-Teaser__link"[^>]+href="([^"]+)"',
            raw_item,
            flags=re.S,
        )
        title_match = re.search(
            r'<span class="SP-Teaser__headline__text">(.*?)</span>',
            raw_item,
            flags=re.S,
        )
        abstract_match = re.search(
            r'<div class="SP-Teaser__abstract">(.*?)</div>',
            raw_item,
            flags=re.S,
        )
        if not href_match or not title_match:
            continue

        url = urljoin(source.url, unescape(href_match.group(1)))
        if url in seen:
            continue
        seen.add(url)
        title = _clean_text(title_match.group(1))
        abstract = _clean_text(abstract_match.group(1) if abstract_match else "")
        parts = [part.strip() for part in abstract.split("|") if part.strip()]
        deadline = _field_value(abstract, "Bewerbungsfrist:")
        employment_type = next(
            (part for part in parts if "zeit" in part.lower()),
            "",
        )
        contract_type = next(
            (
                part
                for part in parts
                if any(token in part.lower() for token in ("befristet", "unbefristet"))
            ),
            "",
        )
        department = next(
            (
                part
                for part in parts
                if part not in {employment_type, contract_type}
                and "entgeltgruppe" not in part.lower()
                and "besoldungsgruppe" not in part.lower()
                and "bewerbungsfrist" not in part.lower()
            ),
            "",
        )
        jobs.append(
            JobItem(
                item_id=_job_id(source.source_id, url),
                title=title,
                employer=source.employer,
                location=source.default_location,
                employment_type=employment_type,
                contract_type=contract_type,
                department=department,
                deadline=deadline,
                reference="",
                source_name=source.name,
                source_url=url,
                source_id=source.source_id,
            )
        )
        if len(jobs) >= MAX_ITEMS_PER_SOURCE:
            break
    return jobs


def parse_hessen_mobil_jobs(html: str, source: JobSource) -> list[JobItem]:
    jobs: list[JobItem] = []
    seen: set[str] = set()
    pattern = re.compile(
        r'<button[^>]+aria-label="(?P<title>[^"]+)"'
        r'.{0,9000}?<p><strong>Standort:</strong>\s*(?P<location>.*?)'
        r'<br><strong>Bewerbungsfrist:</strong>\s*(?P<deadline>.*?)'
        r'<br><strong>Kennziffer:</strong>\s*(?P<reference>.*?)</p>'
        r'.{0,5000}?<a[^>]+href="(?P<href>[^"]+)"',
        flags=re.S,
    )
    for match in pattern.finditer(html):
        title = _clean_text(match.group("title"))
        if not title or "pdf" in title.lower():
            continue
        url = urljoin(source.url, unescape(match.group("href")))
        stable_key = f"{title}|{_clean_text(match.group('reference'))}"
        if stable_key in seen:
            continue
        seen.add(stable_key)
        jobs.append(
            JobItem(
                item_id=_job_id(source.source_id, stable_key),
                title=title,
                employer=source.employer,
                location=_clean_text(match.group("location")) or source.default_location,
                employment_type="",
                contract_type="",
                department="",
                deadline=_clean_text(match.group("deadline")),
                reference=_clean_text(match.group("reference")),
                source_name=source.name,
                source_url=url,
                source_id=source.source_id,
            )
        )
        if len(jobs) >= MAX_ITEMS_PER_SOURCE:
            break
    return jobs


def parse_rexx_jobs(
    html: str,
    source: JobSource,
    *,
    deadline_column: int,
    department_column: int | None = None,
    employment_column: int | None = None,
) -> list[JobItem]:
    jobs: list[JobItem] = []
    seen: set[str] = set()
    for raw_row in re.findall(
        r'<tr class="alternative_[01]">(.*?)</tr>',
        html,
        flags=re.S,
    ):
        columns = {
            int(column): value
            for column, value in re.findall(
                r'<td class="real_table_col(\d+)">(.*?)</td>',
                raw_row,
                flags=re.S,
            )
        }
        title_cell = columns.get(1, "")
        link_match = re.search(
            r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            title_cell,
            flags=re.S,
        )
        if not link_match:
            continue

        title = _clean_text(link_match.group(2))
        if not title or title.casefold().startswith("intern "):
            continue
        url = _canonical_job_url(urljoin(source.url, unescape(link_match.group(1))))
        if url in seen:
            continue
        seen.add(url)

        deadline = _clean_text(columns.get(deadline_column, ""))
        if deadline == "00.00.0000":
            deadline = ""
        department = (
            _clean_text(columns.get(department_column, ""))
            if department_column
            else _department_from_title(title)
        )
        employment_type = (
            _clean_text(columns.get(employment_column, ""))
            if employment_column
            else ""
        )
        jobs.append(
            JobItem(
                item_id=_job_id(source.source_id, url),
                title=title,
                employer=source.employer,
                location=source.default_location,
                employment_type=employment_type,
                contract_type="",
                department=department,
                deadline=deadline,
                reference="",
                source_name=source.name,
                source_url=url,
                source_id=source.source_id,
            )
        )
        if len(jobs) >= MAX_ITEMS_PER_SOURCE:
            break
    return jobs


def _field_value(text: str, label: str) -> str:
    match = re.search(
        rf"{re.escape(label)}\s*([^|]+)",
        text,
        flags=re.I,
    )
    return match.group(1).strip() if match else ""


def _clean_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(without_tags).split())


def _canonical_job_url(url: str) -> str:
    parsed = urlsplit(url)
    query = urlencode([
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.casefold() != "sid"
    ])
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, ""))


def _department_from_title(title: str) -> str:
    match = re.search(r"\bbeim\s+(.+)$", title, flags=re.I)
    return match.group(1).strip() if match else ""


def _job_id(source_id: str, stable_value: str) -> str:
    digest = hashlib.sha256(stable_value.encode("utf-8")).hexdigest()[:14]
    return f"{source_id}-{digest}"
