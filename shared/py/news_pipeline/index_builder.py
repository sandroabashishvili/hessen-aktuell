from __future__ import annotations

from pathlib import Path

from .html import brand_mark, display_topic, grouped_counts, head_meta, page_nav, site_footer, story_card_list
from .models import NewsItem
from .service_builder import service_teaser_links


class HomeIndexBuilder:
    def build(
        self,
        project_root: Path,
        day_iso: str,
        items: list[NewsItem],
        max_items: int,
        count_items: list[NewsItem] | None = None,
    ) -> Path:
        target = project_root / "index.html"
        target.write_text(
            _render_home(
                day_iso,
                count_items or items,
                _select_home_items(items, max_items),
            ),
            encoding="utf-8",
        )
        return target


def _select_home_items(items: list[NewsItem], max_items: int) -> list[NewsItem]:
    dated_items = sorted(
        items,
        key=lambda item: (item.published_date or "", item.city, item.source_name, item.title),
        reverse=True,
    )
    selected: list[NewsItem] = []
    selected_ids: set[str] = set()

    for city in ("Frankfurt", "Kassel", "Wiesbaden", "Darmstadt", "Hessen"):
        city_item = next((item for item in dated_items if item.city == city and item.item_id not in selected_ids), None)
        if not city_item:
            continue
        selected.append(city_item)
        selected_ids.add(city_item.item_id)
        if len(selected) >= max_items:
            return selected

    for item in dated_items:
        if item.item_id in selected_ids:
            continue
        selected.append(item)
        if len(selected) >= max_items:
            break
    return selected


def _render_home(day_iso: str, all_items: list[NewsItem], items: list[NewsItem]) -> str:
    lead = items[0] if items else None
    rendered_cards = story_card_list(items[:5], "./")
    lead_card = rendered_cards[0] if rendered_cards else ""
    latest_cards = "\n".join(rendered_cards[1:])
    city_links = _route_links(grouped_counts(all_items, "city"), "./cities", ("Kassel", "Frankfurt", "Darmstadt", "Wiesbaden"))
    topic_links = _route_links(
        grouped_counts(all_items, "topic"),
        "./topics",
        ("Politics", "Transport", "Police", "Economy", "Events", "Safety"),
    )
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title="Hessen Aktuell | Regionale Nachrichten",
    description="Hessen Aktuell bündelt regionale Meldungen aus Kassel, Frankfurt, Darmstadt, Wiesbaden und Hessen.",
    prefix="./",
    canonical_path="/",
)}
  <link rel="stylesheet" href="./shared/css/styles.css">
</head>
<body data-page="home">
  <header class="site-header">
{brand_mark('./')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="./">Hessen Nachrichten</a></h1>
    <p class="lede">Regionale Meldungen aus Kassel, Frankfurt, Darmstadt, Wiesbaden und Hessen, sortiert nach Stadt, Thema und Tagesarchiv.</p>
{page_nav('./')}
  </header>
  <main class="page-shell" aria-label="Startseite">
    <section class="home-layout">
      <article class="panel lead-panel home-lead-panel">
        <p class="section-label">Topmeldung</p>
        <h2>Aktuelle Meldung aus Hessen</h2>
        <div class="story-stack">
{lead_card}
        </div>
      </article>
      <aside class="panel home-dashboard-panel">
        <section class="dashboard-section">
          <div class="panel-head compact-head">
            <div>
              <p class="section-label">Städte</p>
              <h2>Nach Stadt lesen</h2>
            </div>
            <a href="./cities/">Alle</a>
          </div>
          <div class="quick-link-grid">
{city_links}
          </div>
        </section>
        <section class="dashboard-section">
          <div class="panel-head compact-head">
            <div>
              <p class="section-label">Themen</p>
              <h2>Nach Thema lesen</h2>
            </div>
            <a href="./topics/">Alle</a>
          </div>
          <div class="quick-link-grid">
{topic_links}
          </div>
        </section>
      </aside>
      <article class="panel latest-panel home-latest-panel">
        <div class="panel-head">
          <div>
            <p class="section-label">Aktuell</p>
            <h2>Weitere regionale Meldungen</h2>
          </div>
          <a href="./archive/">Archiv</a>
        </div>
        <div class="story-stack story-grid">
{latest_cards}
        </div>
      </article>
      <aside class="panel home-dashboard-panel">
        <div class="panel-head compact-head">
          <div>
            <p class="section-label">Service</p>
            <h2>Nützliche Links</h2>
          </div>
          <a href="./service/">Alle</a>
        </div>
        <p class="story-summary">Schnelle Zugänge zu offiziellen Quellen für Alltag, Warnungen, Gesundheit und Mobilität.</p>
        <div class="quick-link-grid service-teaser-grid">
{service_teaser_links('./')}
        </div>
      </aside>
    </section>
  </main>
{site_footer('./')}
  <script src="./shared/js/main.js"></script>
</body>
</html>
"""


def _route_links(counts: dict[str, int], route_root: str, ordered_names: tuple[str, ...]) -> str:
    links: list[str] = []
    for name in ordered_names:
        count = counts.get(name, 0)
        slug = name.lower().replace(" ", "-")
        label = display_topic(name) if route_root.endswith("topics") else name
        links.append(
            f'            <a class="quick-link" href="{route_root}/{slug}/">'
            f"<span>{label}</span><strong>{count}</strong>"
            "</a>"
        )
    return "\n".join(links)
