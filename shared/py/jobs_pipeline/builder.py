from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path
import re
import unicodedata

from ..news_pipeline.html import brand_mark, head_meta, page_nav, site_footer
from .models import JobItem
from .sources import FALLBACK_JOB_PORTALS, JOB_SOURCES


CATEGORY_RULES = (
    (
        "Studium & Einstieg",
        "events",
        (
            "ausbildung",
            "praktik",
            "student",
            "werkstudent",
        ),
    ),
    (
        "IT & Digitales",
        "economy",
        (
            "administrator",
            "digital",
            "informat",
            "it-",
            "netzwerk",
            "software",
            "system",
        ),
    ),
    (
        "Bau & Ingenieurwesen",
        "transport",
        (
            "architekt",
            "bauingenieur",
            "baumaß",
            "ingenieur",
            "projektsteuer",
            "verkehrstechnik",
        ),
    ),
    (
        "Technik & Betrieb",
        "transport",
        (
            "geräte",
            "kfz",
            "liegenschaft",
            "meister",
            "straßenbetriebsdienst",
            "straßenmeister",
            "techniker",
        ),
    ),
    (
        "Gesundheit & Soziales",
        "safety",
        (
            "arzt",
            "ärzt",
            "facharzt",
            "gesundheit",
            "hygiene",
            "pflege",
            "pädagog",
            "psycholog",
            "sozial",
        ),
    ),
    (
        "Verwaltung & Organisation",
        "politics",
        (
            "leitung",
            "sachbearbeit",
            "verwaltung",
        ),
    ),
)

DEFAULT_CATEGORY = "Weitere Bereiche"
DEFAULT_VISUAL_TOPIC = "economy"
JOB_IMAGE_POOLS = {
    "Studium & Einstieg": (
        "events-03.webp",
        "politics-04.webp",
        "economy-03.webp",
        "events-02.webp",
    ),
    "IT & Digitales": (
        "economy-03.webp",
        "economy-04.webp",
        "politics-04.webp",
        "economy-01.webp",
    ),
    "Bau & Ingenieurwesen": (
        "transport-03.webp",
        "economy-02.webp",
        "economy-01.webp",
        "transport-04.webp",
    ),
    "Technik & Betrieb": (
        "transport-01.webp",
        "transport-02.webp",
        "transport-04.webp",
        "safety-01.webp",
    ),
    "Gesundheit & Soziales": (
        "safety-03.webp",
        "politics-04.webp",
        "economy-03.webp",
        "events-03.webp",
    ),
    "Verwaltung & Organisation": (
        "politics-01.webp",
        "politics-02.webp",
        "politics-03.webp",
        "politics-04.webp",
    ),
    DEFAULT_CATEGORY: (
        "economy-01.webp",
        "economy-02.webp",
        "economy-03.webp",
        "economy-04.webp",
    ),
}


class JobsPageBuilder:
    def build(
        self,
        project_root: Path,
        jobs: list[JobItem],
        source_counts: dict[str, int],
        generated_at: str,
    ) -> Path:
        output_dir = project_root / "jobs"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "index.html"
        decorated_jobs = [
            (job, *_classify_job(job), _job_city_label(job.location), index)
            for index, job in enumerate(jobs)
        ]
        cards = "\n".join(
            _job_card(job, category, visual_topic, filter_city, index)
            for job, category, visual_topic, filter_city, index in decorated_jobs
        )
        source_summary = " · ".join(
            f"{escape(source.name)}: {source_counts.get(source.source_id, 0)}"
            for source in JOB_SOURCES
        )
        cities = sorted(
            {filter_city for _, _, _, filter_city, _ in decorated_jobs if filter_city},
            key=str.casefold,
        )
        category_counts = Counter(
            category for _, category, _, _, _ in decorated_jobs
        )
        categories = sorted(category_counts, key=str.casefold)
        output_path.write_text(
            _render_page(
                jobs_count=len(jobs),
                cards=cards,
                source_summary=source_summary,
                generated_at=generated_at,
                cities=cities,
                categories=categories,
            ),
            encoding="utf-8",
        )
        return output_path


def _render_page(
    *,
    jobs_count: int,
    cards: str,
    source_summary: str,
    generated_at: str,
    cities: list[str],
    categories: list[str],
) -> str:
    description = (
        "Aktuelle Stellenangebote aus offiziellen hessischen Quellen – "
        "durchsuchbar nach Ort und beruflichem Bereich."
    )
    city_options = "\n".join(
        f'          <option value="{escape(_filter_value(city), quote=True)}">{escape(city)}</option>'
        for city in cities
    )
    category_options = "\n".join(
        f'          <option value="{escape(_filter_value(category), quote=True)}">{escape(category)}</option>'
        for category in categories
    )
    portal_links = " · ".join(
        _portal_link(name, url)
        for name, _, url in FALLBACK_JOB_PORTALS
    )
    empty_message = (
        "Aktuell passen keine Stellen zu dieser Auswahl."
        if cards
        else "Zurzeit konnten keine Stellen automatisch geladen werden."
    )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{head_meta(title="Jobs in Hessen | Hessen Aktuell", description=description, prefix="../", canonical_path="/jobs/")}
  <link rel="stylesheet" href="../shared/css/styles.css">
</head>
<body data-page="jobs">
  <header class="site-header">
    <p class="eyebrow">Offizielle Quellen · Direkte Bewerbung</p>
    <h1><a class="hero-link" href="../jobs/">Jobs in Hessen</a></h1>
    <p class="lede">Aktuelle Stellenangebote nach Ort und beruflichem Bereich filtern. Die Bewerbung erfolgt direkt beim jeweiligen Arbeitgeber.</p>
{page_nav('../')}
{brand_mark('../')}
  </header>
  <main class="page-shell jobs-page" aria-label="Jobs in Hessen">
    <section class="jobs-overview" aria-labelledby="jobs-heading">
      <div>
        <p class="section-label">Aktuelle Stellenangebote</p>
        <h2 id="jobs-heading">{jobs_count} Stellen aus offiziellen Quellen</h2>
        <p>{source_summary} · geprüft am {escape(generated_at)}</p>
      </div>
    </section>

    <section class="jobs-filter-bar" aria-label="Stellenangebote filtern">
      <label class="jobs-search">
        <span>Suche</span>
        <input id="job-search" type="search" placeholder="Beruf, Arbeitgeber oder Kennziffer" autocomplete="off">
      </label>
      <label>
        <span>Ort</span>
        <select id="job-city">
          <option value="">Alle Orte</option>
{city_options}
        </select>
      </label>
      <label>
        <span>Bereich</span>
        <select id="job-category">
          <option value="">Alle Bereiche</option>
{category_options}
        </select>
      </label>
      <button id="job-filter-reset" class="jobs-filter-reset" type="button">Zurücksetzen</button>
    </section>

    <div class="jobs-result-line" aria-live="polite">
      <strong id="job-result-count">{jobs_count}</strong>
      <span id="job-result-label">Stellen gefunden</span>
    </div>

    <section class="jobs-feed" aria-label="Gefundene Stellenangebote">
      <div class="story-stack story-grid jobs-grid" id="jobs-list">
{cards}
      </div>
      <p class="jobs-empty" id="jobs-empty" hidden>{empty_message}</p>
    </section>

    <section class="jobs-more">
      <h2>Weitere offizielle Portale</h2>
      <p>{portal_links}</p>
    </section>

    <p class="jobs-disclaimer">Hessen Aktuell speichert keine Bewerbungsdaten und übernimmt keine vollständigen Ausschreibungstexte. Verbindlich sind Angaben und Fristen beim jeweiligen Arbeitgeber.</p>
  </main>
{site_footer('../')}
  <script src="../shared/js/main.js"></script>
</body>
</html>
"""


def _job_card(
    job: JobItem,
    category: str,
    visual_topic: str,
    filter_city: str,
    index: int,
) -> str:
    search_text = " ".join(
        (
            job.title,
            job.employer,
            job.location,
            job.department,
            job.reference,
            category,
        )
    )
    details = [
        job.location,
        job.employment_type,
        job.contract_type,
        f"Frist: {job.deadline}" if job.deadline else "",
        f"Kennziffer: {job.reference}" if job.reference else "",
    ]
    detail_line = " · ".join(escape(value) for value in details if value)
    department = (
        f'<p class="job-department">{escape(job.department)}</p>'
        if job.department
        else ""
    )
    image_name = _job_image_name(job, category, visual_topic, index)
    image_topic = image_name.split("-", 1)[0]
    return f"""
        <article class="story-card job-card"
          data-job-city="{escape(_filter_value(filter_city), quote=True)}"
          data-job-category="{escape(_filter_value(category), quote=True)}"
          data-job-search="{escape(_filter_value(search_text), quote=True)}">
          <a class="story-media story-media-generated story-media-{escape(image_topic)}" href="{escape(job.source_url, quote=True)}" rel="nofollow noopener" target="_blank" aria-label="{escape(job.title, quote=True)} – Originalausschreibung">
            <img src="../shared/assets/news/topics/{escape(image_name, quote=True)}" alt="" loading="lazy" decoding="async" width="1100" height="619">
          </a>
          <p class="story-kicker">{escape(category)} · {escape(job.employer)}</p>
          <h3><a href="{escape(job.source_url, quote=True)}" rel="nofollow noopener" target="_blank">{escape(job.title)}</a></h3>
{department}
          <p class="job-facts">{detail_line}</p>
          <a class="cta-link job-apply-link" href="{escape(job.source_url, quote=True)}" rel="nofollow noopener" target="_blank">Originalausschreibung öffnen ↗</a>
        </article>"""


def _classify_job(job: JobItem) -> tuple[str, str]:
    haystack = _filter_value(
        " ".join((job.title, job.department, job.reference))
    )
    for category, visual_topic, keywords in CATEGORY_RULES:
        if any(_filter_value(keyword) in haystack for keyword in keywords):
            return category, visual_topic
    return DEFAULT_CATEGORY, DEFAULT_VISUAL_TOPIC


def _job_image_name(
    job: JobItem,
    category: str,
    visual_topic: str,
    fallback_index: int,
) -> str:
    candidates = JOB_IMAGE_POOLS.get(category)
    if not candidates:
        return f"{visual_topic}-{(fallback_index % 4) + 1:02d}.webp"
    stable_index = sum(job.item_id.encode("utf-8")) % len(candidates)
    return candidates[stable_index]


def _job_city_label(location: str) -> str:
    cleaned = " ".join(location.split())
    lowered = cleaned.casefold()
    if lowered.startswith("straßenmeisterei "):
        return cleaned[len("Straßenmeisterei "):]
    if lowered.startswith("sm "):
        return cleaned[3:]
    if lowered.startswith("wahlweise "):
        choices = cleaned[len("wahlweise "):].replace(" oder ", " / ")
        return choices[:1].upper() + choices[1:]
    return cleaned


def _filter_value(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    without_marks = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", " ", without_marks).strip()


def _portal_link(name: str, url: str) -> str:
    return (
        f'<a href="{escape(url, quote=True)}" rel="nofollow noopener" '
        f'target="_blank">{escape(name)} ↗</a>'
    )
