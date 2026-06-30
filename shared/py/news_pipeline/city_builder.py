from __future__ import annotations

from html import escape
from pathlib import Path

from .html import brand_mark, head_meta, page_nav, route_media_asset, site_footer, story_card_list
from .models import NewsItem


CITY_DESCRIPTIONS: dict[str, str] = {
    "Kassel": "Meldungen aus Stadt, Landkreis, Polizei, Verkehr und öffentlichem Leben in Nordhessen.",
    "Frankfurt": "Meldungen zu Polizei, Verkehr, Wirtschaft, Infrastruktur und öffentlichem Leben.",
    "Darmstadt": "Meldungen aus Verwaltung, Polizei, Mobilität und Stadtgesellschaft.",
    "Wiesbaden": "Meldungen aus Landeshauptstadt, Polizei, Stadtleben und öffentlichen Diensten.",
}

CITY_TOPICS: dict[str, str] = {
    "Kassel": "Transport",
    "Frankfurt": "Economy",
    "Darmstadt": "Politics",
    "Wiesbaden": "Events",
}

CITY_VISUALS: dict[str, tuple[str, str]] = {
    "Kassel": ("Transport", "transport-03.png"),
    "Frankfurt": ("Economy", "economy-03.png"),
    "Darmstadt": ("Politics", "politics-01.png"),
    "Wiesbaden": ("Events", "events-04.png"),
}


class CityPageBuilder:
    def build(self, project_root: Path, city: str, day_iso: str, items: list[NewsItem]) -> Path:
        target = project_root / "cities" / city.lower() / "index.html"
        city_items = [item for item in items if item.city.lower() == city.lower()]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_render_city(city, day_iso, city_items), encoding="utf-8")
        return target

    def build_index(self, project_root: Path, cities: list[str], items: list[NewsItem]) -> Path:
        target = project_root / "cities" / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_render_index(cities, items), encoding="utf-8")
        return target


def _render_city(city: str, day_iso: str, items: list[NewsItem]) -> str:
    lead = items[0] if items else None
    rendered_cards = story_card_list(items[:9], "../../")
    lead_card = rendered_cards[0] if lead else _empty_state(city)
    feed_items = items[1:9]
    feed_section = _render_feed_section(city, rendered_cards[1:]) if feed_items else ""
    description = f"Regionale Nachrichten aus {city} mit lokalen Meldungen, Themen und Archiv."
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title=f"{city} Nachrichten | Hessen Aktuell",
    description=description,
    prefix="../../",
    canonical_path=f"/cities/{city.lower()}/",
)}
  <link rel="stylesheet" href="../../shared/css/styles.css">
</head>
<body data-page="city-{escape(city.lower())}">
  <header class="site-header">
{brand_mark('../../')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="../../cities/{escape(city.lower())}/">{escape(city)}</a></h1>
    <p class="lede">Regionale Meldungen für {escape(city)}, mit lokalen Quellen, Themenüberblick und Tagesarchiv an einem Ort.</p>
{page_nav('../../')}
  </header>
  <main class="page-shell" aria-label="{escape(city)} Stadtseite">
    <section class="panel lead-panel">
        <p class="section-label">Topmeldung</p>
        <h2>Aktuelle Meldung aus {escape(city)}</h2>
        <div class="story-stack">
{lead_card}
        </div>
    </section>
{feed_section}
  </main>
{site_footer('../../')}
  <script src="../../shared/js/main.js"></script>
</body>
</html>
"""


def _render_feed_section(city: str, feed_cards_list: list[str]) -> str:
    feed_cards = "\n".join(feed_cards_list)
    return f"""
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Meldungen</p>
          <h2>Weitere Meldungen aus {escape(city)}</h2>
        </div>
        <a href="../../archive/">Archiv</a>
      </div>
      <div class="story-stack story-grid">
{feed_cards}
      </div>
    </section>"""


def _empty_state(city: str) -> str:
    return f"""
        <article class="story-card">
          <p class="story-kicker">{escape(city)} · Nachrichten</p>
          <h3>Noch keine Meldungen</h3>
          <p>Für diese Stadt sind aktuell keine Meldungen verfügbar.</p>
        </article>"""


def _render_index(cities: list[str], items: list[NewsItem]) -> str:
    cards = "\n".join(_city_route(city, _count_items(city, items)) for city in cities)
    description = "Städteübersicht für Hessen Aktuell mit Kassel, Frankfurt, Darmstadt und Wiesbaden."
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title="Stadtmeldungen | Hessen Aktuell",
    description=description,
    prefix="../",
    canonical_path="/cities/",
)}
  <link rel="stylesheet" href="../shared/css/styles.css">
</head>
<body data-page="cities-index">
  <header class="site-header">
{brand_mark('../')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="../cities/">Stadtmeldungen</a></h1>
    <p class="lede">Regionale Meldungen nach Stadt lesen, mit eigener Übersicht für Kassel, Frankfurt, Darmstadt und Wiesbaden.</p>
{page_nav('../')}
  </header>
  <main class="page-shell">
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Städte</p>
          <h2>Nach Stadt lesen</h2>
        </div>
      </div>
      <div class="mini-grid">
{cards}
      </div>
    </section>
  </main>
{site_footer('../')}
  <script src="../shared/js/main.js"></script>
</body>
</html>
"""


def _city_route(city: str, count: int) -> str:
    description = CITY_DESCRIPTIONS.get(city, "Regionale Meldungen.")
    visual_topic, image_name = CITY_VISUALS.get(city, (CITY_TOPICS.get(city, "Politics"), "politics-01.png"))
    return (
        f'        <a class="route-card" href="./{escape(city.lower())}/">'
        f'{route_media_asset(visual_topic, "../", city, image_name)}'
        f"<strong>{escape(city)}</strong>"
        f"<span>{escape(description)} {count} Meldungen.</span>"
        "</a>"
    )


def _count_items(city: str, items: list[NewsItem]) -> int:
    return sum(1 for item in items if item.city.lower() == city.lower())
