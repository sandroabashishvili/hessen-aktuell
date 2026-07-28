from __future__ import annotations

from html import escape
from pathlib import Path

from ..news_pipeline.html import brand_mark, head_meta, page_nav, site_footer
from .models import JobItem
from .sources import FALLBACK_JOB_PORTALS, JOB_SOURCES


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
        cards = "\n".join(_job_card(job) for job in jobs)
        if not cards:
            cards = """
        <div class="jobs-empty">
          <strong>Zurzeit konnten keine Stellen automatisch geladen werden.</strong>
          <p>Nutzen Sie die unten verlinkten offiziellen Karriereportale.</p>
        </div>"""
        source_summary = " · ".join(
            f"{escape(source.name)}: {source_counts.get(source.source_id, 0)}"
            for source in JOB_SOURCES
        )
        output_path.write_text(
            _render_page(
                jobs_count=len(jobs),
                cards=cards,
                source_summary=source_summary,
                generated_at=generated_at,
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
) -> str:
    description = (
        "Aktuelle Stellenangebote aus offiziellen hessischen Quellen mit "
        "Arbeitsort, Bewerbungsfrist und direktem Link zum Arbeitgeber."
    )
    fallback_cards = "\n".join(
        _portal_card(name, description_text, url)
        for name, description_text, url in FALLBACK_JOB_PORTALS
    )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{head_meta(title="Jobs in Hessen | Hessen Aktuell", description=description, prefix="../", canonical_path="/jobs/")}
  <link rel="stylesheet" href="../shared/css/styles.css">
</head>
<body>
  <header class="site-header">
    <p class="eyebrow">Offizielle Quellen · Direkte Bewerbung</p>
    <h1><a class="hero-link" href="../jobs/">Jobs in Hessen</a></h1>
    <p class="lede">Ausgewählte aktuelle Stellenangebote aus offiziellen Karriereportalen. Die Bewerbung erfolgt immer direkt beim jeweiligen Arbeitgeber.</p>
{page_nav('../')}
{brand_mark('../')}
  </header>
  <main class="page-shell" aria-label="Jobs in Hessen">
    <section class="panel lead-panel jobs-intro">
      <div>
        <p class="section-label">Aktueller Stand</p>
        <h2>{jobs_count} Stellen aus offiziellen Quellen</h2>
        <p class="story-summary">{source_summary}</p>
      </div>
      <div class="jobs-update">
        <span>Zuletzt geprüft</span>
        <strong>{escape(generated_at)}</strong>
      </div>
    </section>
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Stellenangebote</p>
          <h2>Direkt zur Originalausschreibung</h2>
        </div>
      </div>
      <div class="jobs-grid">
{cards}
      </div>
    </section>
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Weitere offizielle Portale</p>
          <h2>Selbst weitersuchen</h2>
        </div>
      </div>
      <div class="jobs-portals">
{fallback_cards}
      </div>
    </section>
    <section class="panel status-panel">
      <p class="section-label">Transparenz</p>
      <p>Hessen Aktuell speichert keine Bewerbungsdaten und übernimmt keine vollständigen Ausschreibungstexte. Angezeigt werden nur kompakte Kerndaten mit Link zur offiziellen Quelle. Angaben und Fristen sind beim Arbeitgeber zu prüfen.</p>
    </section>
  </main>
{site_footer('../')}
  <script src="../shared/js/main.js"></script>
</body>
</html>
"""


def _job_card(job: JobItem) -> str:
    metadata = [
        ("Ort", job.location),
        ("Arbeitszeit", job.employment_type),
        ("Vertrag", job.contract_type),
        ("Bereich", job.department),
        ("Frist", job.deadline),
        ("Kennziffer", job.reference),
    ]
    details = "\n".join(
        f'<span><small>{escape(label)}</small>{escape(value)}</span>'
        for label, value in metadata
        if value
    )
    return f"""
        <article class="job-card">
          <p class="story-kicker">{escape(job.employer)}</p>
          <h3>{escape(job.title)}</h3>
          <div class="job-meta">
            {details}
          </div>
          <a class="cta-link" href="{escape(job.source_url, quote=True)}" rel="nofollow noopener" target="_blank">Originalausschreibung öffnen ↗</a>
        </article>"""


def _portal_card(name: str, description: str, url: str) -> str:
    return f"""
        <a class="job-portal-card" href="{escape(url, quote=True)}" rel="nofollow noopener" target="_blank">
          <strong>{escape(name)}</strong>
          <span>{escape(description)}</span>
          <em>Portal öffnen ↗</em>
        </a>"""
