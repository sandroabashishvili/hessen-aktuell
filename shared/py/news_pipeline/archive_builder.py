from __future__ import annotations

from pathlib import Path

from .html import brand_mark, display_topic, grouped_counts, head_meta, page_nav, route_media_asset, site_footer, story_card_list
from .models import NewsItem

ARCHIVE_CARD_VISUALS: tuple[tuple[str, str], ...] = (
    ("Politics", "politics-03.png"),
    ("Transport", "transport-04.png"),
    ("Police", "police-02.png"),
    ("Economy", "economy-03.png"),
    ("Events", "events-04.png"),
    ("Safety", "safety-02.png"),
)


class ArchiveBuilder:
    def build_day(self, archive_dir: Path, day_iso: str, items: list[NewsItem]) -> Path:
        target_dir = archive_dir / day_iso
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "index.html"
        target.write_text(_render_day(day_iso, items), encoding="utf-8")
        return target

    def build_index(self, archive_dir: Path, day_iso: str, items: list[NewsItem], archive_counts: dict[str, int] | None = None) -> Path:
        archive_dir.mkdir(parents=True, exist_ok=True)
        target = archive_dir / "index.html"
        target.write_text(_render_index(day_iso, items, archive_counts or {day_iso: len(items)}), encoding="utf-8")
        return target


def _render_day(day_iso: str, items: list[NewsItem]) -> str:
    cards = "\n".join(story_card_list(items, "../../"))
    city_counts = grouped_counts(items, "city")
    topic_counts = grouped_counts(items, "topic")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title=f"Archiv {day_iso} | Hessen Aktuell",
    description=f"Regionale Nachrichten im Hessen Aktuell Archiv für {day_iso}.",
    prefix="../../",
    canonical_path=f"/archive/{day_iso}/",
)}
  <link rel="stylesheet" href="../../shared/css/styles.css">
</head>
<body data-page="archive-day">
  <header class="site-header">
{brand_mark('../../')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="./">Archiv {day_iso}</a></h1>
    <p class="lede">Regionale Meldungen dieses Tages, gesammelt aus den aktiven Quellen und nach Stadt sowie Thema lesbar.</p>
{page_nav('../../')}
  </header>
  <main class="page-shell">
    <section class="hero-grid">
      <article class="panel lead-panel">
        <p class="section-label">Tagesarchiv</p>
        <h2>{len(items)} regionale Meldungen</h2>
        <p class="story-summary">Alle Karten öffnen die jeweilige Originalmeldung.</p>
      </article>
      <aside class="panel urgent-panel">
        <p class="section-label">Überblick</p>
        <p class="story-summary">Städte: {_format_counts(city_counts)}</p>
        <p class="story-summary">Themen: {_format_counts(topic_counts, translate_topics=True)}</p>
      </aside>
    </section>
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Meldungen</p>
          <h2>Alle Einträge</h2>
        </div>
      </div>
      <div class="story-stack story-grid">
{cards}
      </div>
    </section>
  </main>
{site_footer('../../')}
  <script src="../../shared/js/main.js"></script>
</body>
</html>
"""


def _render_index(day_iso: str, items: list[NewsItem], archive_counts: dict[str, int]) -> str:
    description = "Archivübersicht für regionale Nachrichten von Hessen Aktuell."
    archive_cards = _archive_cards(archive_counts)
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title="Archiv | Hessen Aktuell",
    description=description,
    prefix="../",
    canonical_path="/archive/",
)}
  <link rel="stylesheet" href="../shared/css/styles.css">
</head>
<body data-page="archive-index">
  <header class="site-header">
{brand_mark('../')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="../archive/">Archiv</a></h1>
    <p class="lede">Regionale Nachrichten nach Datum lesen, mit den letzten archivierten Tagesseiten und direktem Zugriff auf ältere Meldungen.</p>
{page_nav('../')}
  </header>
  <main class="page-shell">
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Tagesarchiv</p>
          <h2>Letzte Tage</h2>
        </div>
        <a href="./{day_iso}/">Neueste</a>
      </div>
      <div class="mini-grid">
{archive_cards}
      </div>
    </section>
  </main>
{site_footer('../')}
  <script src="../shared/js/main.js"></script>
</body>
</html>
"""


def _format_counts(counts: dict[str, int], *, translate_topics: bool = False) -> str:
    rendered: list[str] = []
    for key, value in counts.items():
        label = display_topic(key) if translate_topics else key
        rendered.append(f"{label} {value}")
    return ", ".join(rendered) or "keine"


def _archive_cards(archive_counts: dict[str, int]) -> str:
    cards: list[str] = []
    for index, (day, count) in enumerate(sorted(archive_counts.items(), reverse=True)):
        topic, image_name = ARCHIVE_CARD_VISUALS[index % len(ARCHIVE_CARD_VISUALS)]
        cards.append(
            f'        <a class="route-card archive-route-card" href="./{day}/">'
            f'{route_media_asset(topic, "../", day, image_name)}'
            f"<strong>{day}</strong>"
            f"<span>{count} regionale Meldungen</span>"
            "</a>"
        )
    return "\n".join(cards)
