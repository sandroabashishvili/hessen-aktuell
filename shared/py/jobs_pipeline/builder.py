from __future__ import annotations

from collections import Counter
from html import escape
import json
import os
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
            "duales",
            "praktik",
            "studium",
            "student",
            "werkstudent",
        ),
    ),
    (
        "IT & Digitales",
        "economy",
        (
            "administrator",
            "client ",
            "datenanal",
            "digital",
            "dv-",
            "informat",
            "it-",
            "ki-",
            "m365",
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
            "bauunterhalt",
            "bauingenieur",
            "baumaß",
            "ingenieur",
            "projektsteuer",
            "stadtplan",
            "vermess",
            "verkehrstechnik",
        ),
    ),
    (
        "Natur & Handwerk",
        "economy",
        (
            "forst",
            "friedhof",
            "gärtner",
            "garten",
            "grünfläche",
            "handwerk",
            "landschaftspflege",
            "park",
            "pflaster",
            "tierpfleg",
        ),
    ),
    (
        "Technik & Betrieb",
        "transport",
        (
            "geräte",
            "kfz",
            "liegenschaft",
            "messgehilfe",
            "meister",
            "platzwart",
            "straßenwärter",
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
            "erzieher",
            "jugendhilfe",
            "kinderbetreuung",
            "kindertagesstätte",
            "kita",
            "pflege",
            "pädagog",
            "psycholog",
            "sozial",
        ),
    ),
    (
        "Kultur & Kommunikation",
        "events",
        (
            "akademie",
            "archiv",
            "ausstellung",
            "kommunikation",
            "kultur",
            "marketing",
            "museum",
            "protokoll",
            "publikation",
            "redaktion",
            "repräsentation",
            "tonkunst",
        ),
    ),
    (
        "Verwaltung & Organisation",
        "politics",
        (
            "leitung",
            "fachassist",
            "jobcenter",
            "projektmanager",
            "sachbearbeit",
            "sekretariat",
            "standesbeam",
            "steuer",
            "verwaltung",
        ),
    ),
)

DEFAULT_CATEGORY = "Weitere Bereiche"
DEFAULT_VISUAL_TOPIC = "economy"
PAGE_SIZE = 8
FEATURED_JOB_CITIES = (
    ("Kassel", "kassel"),
    ("Frankfurt", "frankfurt"),
    ("Wiesbaden", "wiesbaden"),
    ("Darmstadt", "darmstadt"),
    ("Offenbach", "offenbach"),
    ("Gießen", "giessen"),
)
JOB_IMAGE_POOLS = {
    "Studium & Einstieg": (
        "jobs-studium-einstieg.webp",
    ),
    "IT & Digitales": (
        "jobs-it-digital.webp",
    ),
    "Bau & Ingenieurwesen": (
        "jobs-bau-ingenieurwesen.webp",
    ),
    "Technik & Betrieb": (
        "jobs-technik-betrieb.webp",
    ),
    "Gesundheit & Soziales": (
        "jobs-gesundheit-soziales.webp",
    ),
    "Verwaltung & Organisation": (
        "jobs-verwaltung.webp",
    ),
    "Natur & Handwerk": (
        "jobs-natur-handwerk.webp",
    ),
    "Kultur & Kommunikation": (
        "jobs-kultur-kommunikation.webp",
    ),
    DEFAULT_CATEGORY: (
        "jobs-verwaltung.webp",
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
        decorated_jobs = _decorate_jobs(jobs)
        cards = "\n".join(
            _job_card(
                job,
                category,
                visual_topic,
                filter_city,
                index,
                prefix="../",
                initially_hidden=index >= PAGE_SIZE,
            )
            for job, category, visual_topic, filter_city, index in decorated_jobs
        )
        active_sources = [
            source for source in JOB_SOURCES
            if source_counts.get(source.source_id, 0)
        ]
        source_summary = (
            f"{len(active_sources)} offizielle Arbeitgeberportale"
        )
        source_names = ", ".join(source.name for source in active_sources)
        cities = sorted(
            {filter_city for _, _, _, filter_city, _ in decorated_jobs if filter_city},
            key=str.casefold,
        )
        category_counts = Counter(
            category for _, category, _, _, _ in decorated_jobs
        )
        categories = sorted(category_counts, key=str.casefold)
        city_counts = Counter(
            filter_city for _, _, _, filter_city, _ in decorated_jobs
        )
        featured_cities = [
            (city, slug, city_counts.get(city, 0))
            for city, slug in FEATURED_JOB_CITIES
            if city_counts.get(city, 0)
        ]
        output_path.write_text(
            _render_page(
                jobs_count=len(jobs),
                cards=cards,
                source_summary=source_summary,
                source_names=source_names,
                generated_at=generated_at,
                cities=cities,
                categories=categories,
                featured_cities=featured_cities,
                jobs=jobs,
            ),
            encoding="utf-8",
        )
        for city, slug in FEATURED_JOB_CITIES:
            city_jobs = [
                item for item in decorated_jobs
                if item[3] == city
            ]
            _write_city_page(
                output_dir=output_dir,
                city=city,
                slug=slug,
                decorated_jobs=city_jobs,
                generated_at=generated_at,
                featured_cities=featured_cities,
            )
        return output_path


def _render_page(
    *,
    jobs_count: int,
    cards: str,
    source_summary: str,
    source_names: str,
    generated_at: str,
    cities: list[str],
    categories: list[str],
    featured_cities: list[tuple[str, str, int]],
    jobs: list[JobItem],
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
    city_links = _city_links(featured_cities, prefix="./")
    structured_data = _jobs_structured_data(
        title="Jobs in Hessen | Hessen Aktuell",
        description=description,
        canonical_path="/jobs/",
        jobs=jobs,
    )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{head_meta(title="Jobs in Hessen | Hessen Aktuell", description=description, prefix="../", canonical_path="/jobs/")}
{structured_data}
  <link rel="stylesheet" href="../shared/css/styles.css?v=20260813">
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
        <p>{escape(source_summary)} · geprüft am {escape(generated_at)}</p>
      </div>
    </section>
{city_links}

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
        <span>Berufsfeld</span>
        <select id="job-category">
          <option value="">Alle Berufsfelder</option>
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
      <div class="story-stack story-grid jobs-grid" id="jobs-list" data-page-size="{PAGE_SIZE}">
{cards}
      </div>
      <p class="jobs-empty" id="jobs-empty" hidden>{empty_message}</p>
      <nav class="jobs-pagination" id="job-pagination" aria-label="Seitennavigation">
        <button id="job-page-prev" type="button">← Zurück</button>
        <span id="job-page-status">Seite 1</span>
        <button id="job-page-next" type="button">Weiter →</button>
      </nav>
    </section>

    <section class="jobs-more">
      <h2>Weitere offizielle Portale</h2>
      <p>{portal_links}</p>
      <p class="jobs-source-note">Automatisch ausgewertete Quellen: {escape(source_names)}.</p>
    </section>

    <p class="jobs-disclaimer">Hessen Aktuell speichert keine Bewerbungsdaten und übernimmt keine vollständigen Ausschreibungstexte. Verbindlich sind Angaben und Fristen beim jeweiligen Arbeitgeber.</p>
  </main>
{site_footer('../')}
  <script src="../shared/js/main.js"></script>
</body>
</html>
"""


def _decorate_jobs(
    jobs: list[JobItem],
) -> list[tuple[JobItem, str, str, str, int]]:
    return [
        (job, *_classify_job(job), _job_city_label(job.location), index)
        for index, job in enumerate(jobs)
    ]


def _write_city_page(
    *,
    output_dir: Path,
    city: str,
    slug: str,
    decorated_jobs: list[tuple[JobItem, str, str, str, int]],
    generated_at: str,
    featured_cities: list[tuple[str, str, int]],
) -> None:
    city_dir = output_dir / slug
    city_dir.mkdir(parents=True, exist_ok=True)
    cards = "\n".join(
        _job_card(
            job,
            category,
            visual_topic,
            filter_city,
            index,
            prefix="../../",
            initially_hidden=position >= PAGE_SIZE,
        )
        for position, (job, category, visual_topic, filter_city, index)
        in enumerate(decorated_jobs)
    )
    city_dir.joinpath("index.html").write_text(
        _render_city_page(
            city=city,
            slug=slug,
            cards=cards,
            jobs=[item[0] for item in decorated_jobs],
            generated_at=generated_at,
            featured_cities=featured_cities,
        ),
        encoding="utf-8",
    )


def _render_city_page(
    *,
    city: str,
    slug: str,
    cards: str,
    jobs: list[JobItem],
    generated_at: str,
    featured_cities: list[tuple[str, str, int]],
) -> str:
    title = f"Jobs in {city} | Hessen Aktuell"
    description = (
        f"Aktuelle Stellenangebote in {city} aus offiziellen Arbeitgeberportalen "
        "mit direktem Link zur Originalausschreibung."
    )
    city_links = _city_links(featured_cities, prefix="../", current_slug=slug)
    empty_message = (
        f"Zurzeit sind keine automatisch erfassten Stellen in {city} verfügbar. "
        "Bitte prüfen Sie später erneut die Übersicht."
    )
    structured_data = _jobs_structured_data(
        title=title,
        description=description,
        canonical_path=f"/jobs/{slug}/",
        jobs=jobs,
    )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{head_meta(title=title, description=description, prefix="../../", canonical_path=f"/jobs/{slug}/")}
{structured_data}
  <link rel="stylesheet" href="../../shared/css/styles.css?v=20260813">
</head>
<body data-page="jobs-city">
  <header class="site-header">
    <p class="eyebrow">Offizielle Quellen · Direkte Bewerbung</p>
    <h1><a class="hero-link" href="./">Jobs in {escape(city)}</a></h1>
    <p class="lede">Aktuelle kommunale und öffentliche Stellenangebote für {escape(city)} kompakt an einem Ort.</p>
{page_nav('../../')}
{brand_mark('../../')}
  </header>
  <main class="page-shell jobs-page" aria-label="Jobs in {escape(city)}">
    <section class="jobs-overview" aria-labelledby="jobs-heading">
      <div>
        <p class="section-label">Stellenangebote in {escape(city)}</p>
        <h2 id="jobs-heading">{len(jobs)} aktuelle Stellen</h2>
        <p>Automatisch geprüft am {escape(generated_at)} · Bewerbung beim Originalanbieter</p>
      </div>
      <a class="jobs-all-link" href="../">Alle Jobs in Hessen →</a>
    </section>
{city_links}

    <div class="jobs-result-line" aria-live="polite">
      <strong id="job-result-count">{len(jobs)}</strong>
      <span id="job-result-label">Stellen gefunden</span>
    </div>

    <section class="jobs-feed" aria-label="Stellenangebote in {escape(city)}">
      <div class="story-stack story-grid jobs-grid" id="jobs-list" data-page-size="{PAGE_SIZE}">
{cards}
      </div>
      <p class="jobs-empty" id="jobs-empty"{'' if not jobs else ' hidden'}>{escape(empty_message)}</p>
      <nav class="jobs-pagination" id="job-pagination" aria-label="Seitennavigation">
        <button id="job-page-prev" type="button">← Zurück</button>
        <span id="job-page-status">Seite 1</span>
        <button id="job-page-next" type="button">Weiter →</button>
      </nav>
    </section>

    <p class="jobs-disclaimer">Hessen Aktuell speichert keine Bewerbungsdaten. Verbindlich sind ausschließlich die Angaben und Fristen in der verlinkten Originalausschreibung.</p>
  </main>
{site_footer('../../')}
  <script src="../../shared/js/main.js"></script>
</body>
</html>
"""


def _city_links(
    featured_cities: list[tuple[str, str, int]],
    *,
    prefix: str,
    current_slug: str = "",
) -> str:
    if not featured_cities:
        return ""
    links = "\n".join(
        (
            f'      <span aria-current="page">{escape(city)} <b>{count}</b></span>'
            if slug == current_slug
            else f'      <a href="{prefix}{escape(slug, quote=True)}/">{escape(city)} <b>{count}</b></a>'
        )
        for city, slug, count in featured_cities
    )
    return f"""
    <nav class="jobs-city-links" aria-label="Jobs nach Stadt">
      <strong>Direkt nach Stadt:</strong>
{links}
    </nav>"""


def _jobs_structured_data(
    *,
    title: str,
    description: str,
    canonical_path: str,
    jobs: list[JobItem],
) -> str:
    base_url = os.environ.get(
        "HESSEN_AKTUELL_BASE_URL",
        "http://localhost:8090",
    ).rstrip("/")
    canonical_url = f"{base_url}/{canonical_path.strip('/')}/"
    payload = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": canonical_url,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(jobs),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": job.title,
                    "url": job.source_url,
                }
                for position, job in enumerate(jobs, start=1)
            ],
        },
    }
    serialized = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return f'  <script type="application/ld+json">{serialized}</script>'


def _job_card(
    job: JobItem,
    category: str,
    visual_topic: str,
    filter_city: str,
    index: int,
    *,
    prefix: str,
    initially_hidden: bool,
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
        job.pay_grade,
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
    hidden_attribute = " hidden" if initially_hidden else ""
    return f"""
        <article class="story-card job-card"{hidden_attribute}
          data-job-city="{escape(_filter_value(filter_city), quote=True)}"
          data-job-category="{escape(_filter_value(category), quote=True)}"
          data-job-search="{escape(_filter_value(search_text), quote=True)}">
          <a class="story-media story-media-generated job-media" href="{escape(job.source_url, quote=True)}" rel="nofollow noopener" target="_blank" aria-label="{escape(job.title, quote=True)} – Originalausschreibung">
            <img src="{prefix}shared/assets/jobs/{escape(image_name, quote=True)}" alt="" loading="lazy" decoding="async" width="1100" height="480">
          </a>
          <div class="job-card-content">
            <p class="story-kicker">{escape(category)} · {escape(job.employer)}</p>
            <h3><a href="{escape(job.source_url, quote=True)}" rel="nofollow noopener" target="_blank">{escape(job.title)}</a></h3>
{department}
            <p class="job-facts">{detail_line}</p>
            <a class="cta-link job-apply-link" href="{escape(job.source_url, quote=True)}" rel="nofollow noopener" target="_blank">Originalausschreibung öffnen ↗</a>
          </div>
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
    if lowered.startswith(("strassenmeisterei ", "straßenmeisterei ")):
        return re.sub(
            r"^stra(?:ß|ss)enmeisterei\s+",
            "",
            cleaned,
            flags=re.I,
        )
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
