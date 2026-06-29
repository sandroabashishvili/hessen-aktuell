from __future__ import annotations

from html import escape
from pathlib import Path

from .html import brand_mark, display_topic, head_meta, page_nav, route_media, story_card_list
from .models import NewsItem


TOPIC_DESCRIPTIONS: dict[str, str] = {
    "Politics": "Entscheidungen, Verwaltung, kommunale Themen und öffentliche Debatten in Hessen.",
    "Transport": "Straßen, Bahn, ÖPNV, Baustellen, Verkehr und Mobilität.",
    "Police": "Polizei- und Sicherheitsmeldungen aus hessischen Städten und Regionen.",
    "Economy": "Wirtschaft, Infrastruktur, Energie und regionale Entwicklung.",
    "Events": "Kultur, Veranstaltungen, Stadtprogramme und öffentliche Termine.",
    "Safety": "Wetter, Gesundheit, Umwelt, Vorsorge und Sicherheit im Alltag.",
}


class TopicPageBuilder:
    def build_all(self, project_root: Path, day_iso: str, items: list[NewsItem]) -> dict[str, str]:
        topics = _known_topics(items)
        topic_paths = {
            topic: str(self.build(project_root, topic, day_iso, items))
            for topic in topics
        }
        topic_paths["index"] = str(self.build_index(project_root, topics, items))
        return topic_paths

    def build(self, project_root: Path, topic: str, day_iso: str, items: list[NewsItem]) -> Path:
        target = project_root / "topics" / _slug(topic) / "index.html"
        topic_items = [item for item in items if item.topic.lower() == topic.lower()]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_render_topic(topic, day_iso, topic_items), encoding="utf-8")
        return target

    def build_index(self, project_root: Path, topics: list[str], items: list[NewsItem]) -> Path:
        target = project_root / "topics" / "index.html"
        target.write_text(_render_index(topics, items), encoding="utf-8")
        return target


def _render_topic(topic: str, day_iso: str, items: list[NewsItem]) -> str:
    lead = items[0] if items else None
    rendered_cards = story_card_list(items, "../../")
    lead_card = rendered_cards[0] if lead else _empty_state(topic)
    feed_items = items[1:]
    feed_cards = "\n".join(rendered_cards[1:])
    feed_section = _render_feed_section(topic, feed_cards) if feed_cards else ""
    topic_label = display_topic(topic)
    description = TOPIC_DESCRIPTIONS.get(topic, "Regionale Meldungen zu diesem Thema.")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title=f"{topic_label} | Hessen Aktuell",
    description=description,
    prefix="../../",
    canonical_path=f"/topics/{_slug(topic)}/",
)}
  <link rel="stylesheet" href="../../shared/css/styles.css">
</head>
<body data-page="topic-{escape(_slug(topic))}">
  <header class="site-header">
{brand_mark('../../')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="../../topics/{escape(_slug(topic))}/">{escape(topic_label)}</a></h1>
    <p class="lede">{escape(description)}</p>
{page_nav('../../')}
  </header>
  <main class="page-shell" aria-label="{escape(topic_label)} Themenseite">
    <section class="panel lead-panel">
      <p class="section-label">Topmeldung</p>
      <h2>Aktuelle Meldung zu {escape(topic_label)}</h2>
      <div class="story-stack">
{lead_card}
      </div>
    </section>
{feed_section}
  </main>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__note">© 2026 Hessen Aktuell</p>
    </div>
  </footer>
  <script src="../../shared/js/main.js"></script>
</body>
</html>
"""


def _render_feed_section(topic: str, feed_cards: str) -> str:
    return f"""
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Meldungen</p>
          <h2>Weitere Meldungen zu {escape(display_topic(topic))}</h2>
        </div>
        <a href="../../archive/">Archiv</a>
      </div>
      <div class="story-stack story-grid">
{feed_cards}
      </div>
    </section>"""


def _render_index(topics: list[str], items: list[NewsItem]) -> str:
    cards = "\n".join(_topic_route(topic, _count_items(topic, items)) for topic in topics)
    description = "Themenübersicht für Hessen Aktuell mit Politik, Verkehr, Polizei, Wirtschaft, Veranstaltungen und Sicherheit."
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title="Themenmeldungen | Hessen Aktuell",
    description=description,
    prefix="../",
    canonical_path="/topics/",
)}
  <link rel="stylesheet" href="../shared/css/styles.css">
</head>
<body data-page="topics-index">
  <header class="site-header">
{brand_mark('../')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="../topics/">Themenmeldungen</a></h1>
    <p class="lede">Regionale Meldungen nach Thema lesen, von Politik und Verkehr bis Polizei, Wirtschaft, Veranstaltungen und Sicherheit.</p>
{page_nav('../')}
  </header>
  <main class="page-shell">
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="section-label">Themen</p>
          <h2>Nach Thema lesen</h2>
        </div>
      </div>
      <div class="mini-grid">
{cards}
      </div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__note">© 2026 Hessen Aktuell</p>
    </div>
  </footer>
  <script src="../shared/js/main.js"></script>
</body>
</html>
"""


def _topic_route(topic: str, count: int) -> str:
    description = TOPIC_DESCRIPTIONS.get(topic, "Regionale Meldungen.")
    topic_label = display_topic(topic)
    return (
        f'        <a class="route-card" href="./{escape(_slug(topic))}/">'
        f'{route_media(topic, "../", topic_label)}'
        f"<strong>{escape(topic_label)}</strong>"
        f"<span>{escape(description)} {count} Meldungen.</span>"
        "</a>"
    )


def _empty_state(topic: str) -> str:
    return f"""
        <article class="story-card">
          <p class="story-kicker">{escape(display_topic(topic))} · Nachrichten</p>
          <h3>Noch keine Meldungen</h3>
          <p>Zu diesem Thema sind aktuell keine Meldungen verfügbar.</p>
        </article>"""


def _known_topics(items: list[NewsItem]) -> list[str]:
    preferred = ["Politics", "Transport", "Police", "Economy", "Events", "Safety"]
    existing = {item.topic for item in items if item.topic}
    ordered = [topic for topic in preferred if topic in existing]
    ordered.extend(sorted(existing.difference(ordered)))
    return ordered


def _count_items(topic: str, items: list[NewsItem]) -> int:
    return sum(1 for item in items if item.topic.lower() == topic.lower())


def _slug(value: str) -> str:
    return value.strip().lower().replace(" ", "-")
