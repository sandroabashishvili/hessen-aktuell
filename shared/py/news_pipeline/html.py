from __future__ import annotations

import hashlib
from html import escape
import os
from pathlib import Path

from .models import NewsItem


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TOPIC_IMAGE_DIR = PROJECT_ROOT / "shared" / "assets" / "news" / "topics"
DEFAULT_SOCIAL_IMAGE = "/shared/assets/brand/social-card.png"


def head_meta(*, title: str, description: str, prefix: str, canonical_path: str) -> str:
    canonical = canonical_path if canonical_path.startswith("/") else f"/{canonical_path}"
    canonical_url = _absolute_site_url(canonical)
    social_image_url = _absolute_site_url(DEFAULT_SOCIAL_IMAGE)
    return f"""  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{escape(canonical_url, quote=True)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Hessen Aktuell">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{escape(canonical_url, quote=True)}">
  <meta property="og:image" content="{escape(social_image_url, quote=True)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title, quote=True)}">
  <meta name="twitter:description" content="{escape(description, quote=True)}">
  <meta name="twitter:image" content="{escape(social_image_url, quote=True)}">
{favicon_links(prefix)}"""


def _absolute_site_url(path: str) -> str:
    base_url = os.environ.get("HESSEN_AKTUELL_BASE_URL", "http://localhost:8090").rstrip("/")
    clean_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{clean_path}"


def favicon_links(prefix: str) -> str:
    return f"""
  <link rel="icon" type="image/svg+xml" href="{prefix}shared/assets/brand/favicon.svg">
  <link rel="shortcut icon" type="image/svg+xml" href="{prefix}shared/assets/brand/favicon.svg">"""


def brand_mark(prefix: str) -> str:
    return f"""
    <a class="site-brand-mark" href="{prefix}" aria-label="Hessen Aktuell Startseite">
      <img src="{prefix}shared/assets/brand/brand-mark.svg" alt="Hessen Aktuell">
    </a>"""


def page_nav(prefix: str) -> str:
    return f"""
    <nav class="site-nav" aria-label="Hauptnavigation">
      <a href="{prefix}">Start</a>
      <div class="nav-dropdown">
        <a href="{prefix}cities/">Städte</a>
        <div class="nav-menu">
          <a href="{prefix}cities/kassel/">Kassel</a>
          <a href="{prefix}cities/frankfurt/">Frankfurt</a>
          <a href="{prefix}cities/darmstadt/">Darmstadt</a>
          <a href="{prefix}cities/wiesbaden/">Wiesbaden</a>
        </div>
      </div>
      <div class="nav-dropdown">
        <a href="{prefix}topics/">Themen</a>
        <div class="nav-menu">
          <a href="{prefix}topics/politics/">Politik</a>
          <a href="{prefix}topics/transport/">Verkehr</a>
          <a href="{prefix}topics/police/">Polizei</a>
          <a href="{prefix}topics/economy/">Wirtschaft</a>
          <a href="{prefix}topics/events/">Veranstaltungen</a>
          <a href="{prefix}topics/safety/">Sicherheit</a>
        </div>
      </div>
      <a href="{prefix}archive/">Archiv</a>
      <a href="{prefix}service/">Service</a>
      <a href="{prefix}about/">Über uns</a>
    </nav>"""


def story_card(item: NewsItem, prefix: str = "./", visual_index: int | None = None) -> str:
    media_html = _story_media(item, prefix, visual_index)
    summary = _public_summary(item)
    summary_html = f"\n          <p>{escape(summary)}</p>" if summary else ""
    date_html = f"<span>{escape(item.published_date)}</span>" if item.published_date else ""
    return f"""
        <article class="story-card">
          {media_html}
          <p class="story-kicker">{escape(item.city)} · {escape(display_topic(item.topic))}</p>
          <h3><a href="{escape(item.source_url)}" rel="nofollow noopener" target="_blank">{escape(item.title)}</a></h3>{summary_html}
          <div class="meta-row">
            {date_html}
            <span>{escape(item.source_name)}</span>
          </div>
        </article>"""


def story_card_list(items: list[NewsItem], prefix: str = "./") -> list[str]:
    topic_counts: dict[str, int] = {}
    cards: list[str] = []
    for item in items:
        topic_key = item.topic.strip().lower()
        visual_index = topic_counts.get(topic_key, 0)
        topic_counts[topic_key] = visual_index + 1
        cards.append(story_card(item, prefix, visual_index))
    return cards


def route_media(topic: str, prefix: str, label: str) -> str:
    topic_image = _topic_image_name(topic, label)
    topic_class = _topic_class(topic)
    if topic_image:
        image_src = f"{prefix}shared/assets/news/topics/{topic_image}"
        return (
            f'<span class="route-card-media story-media-generated {topic_class}">'
            f'<img src="{escape(image_src, quote=True)}" alt="{escape(label, quote=True)} Bild" loading="lazy" decoding="async" width="1100" height="619" />'
            "</span>"
        )
    return (
        f'<span class="route-card-media story-media-placeholder {topic_class}">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(topic)}</strong>"
        "</span>"
    )


def route_media_asset(topic: str, prefix: str, label: str, image_name: str) -> str:
    topic_class = _topic_class(topic)
    image_path = TOPIC_IMAGE_DIR / image_name
    if image_name and image_path.exists():
        image_src = f"{prefix}shared/assets/news/topics/{image_name}"
        return (
            f'<span class="route-card-media story-media-generated {topic_class}">'
        f'<img src="{escape(image_src, quote=True)}" alt="{escape(label, quote=True)} Bild" loading="lazy" decoding="async" width="1100" height="619" />'
            "</span>"
        )
    return route_media(topic, prefix, label)


def grouped_counts(items: list[NewsItem], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        key = str(getattr(item, field))
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def display_topic(topic: str) -> str:
    return {
        "politics": "Politik",
        "transport": "Verkehr",
        "police": "Polizei",
        "economy": "Wirtschaft",
        "events": "Veranstaltungen",
        "safety": "Sicherheit",
    }.get(topic.strip().lower(), topic)


def _story_media(item: NewsItem, prefix: str, visual_index: int | None = None) -> str:
    topic_class = _topic_class(item.topic)
    if item.media_type == "youtube" and item.media_url:
        return (
            f'<div class="story-media story-media-youtube">'
            f'<iframe src="{escape(item.media_url, quote=True)}" title="{escape(item.title, quote=True)}" loading="lazy" allowfullscreen></iframe>'
            "</div>"
        )
    if item.media_type == "image" and item.media_url:
        return (
            f'<a class="story-media" href="{escape(item.source_url, quote=True)}" rel="nofollow noopener" target="_blank">'
            f'<img src="{escape(item.media_url, quote=True)}" alt="{escape(item.title, quote=True)}" loading="lazy" decoding="async" />'
            "</a>"
        )
    topic_image = _topic_image(item, visual_index)
    if topic_image:
        image_src = f"{prefix}shared/assets/news/topics/{topic_image}"
        return (
            f'<a class="story-media story-media-generated {topic_class}" href="{escape(item.source_url, quote=True)}" rel="nofollow noopener" target="_blank">'
            f'<img src="{escape(image_src, quote=True)}" alt="{escape(item.city)} {escape(display_topic(item.topic))} Bild" loading="lazy" decoding="async" width="1100" height="619" />'
            "</a>"
        )
    return (
        f'<div class="story-media story-media-placeholder {topic_class}">'
        f"<span>{escape(item.city)}</span>"
        f"<strong>{escape(display_topic(item.topic))}</strong>"
        "</div>"
    )


def _topic_class(topic: str) -> str:
    normalized = topic.strip().lower()
    if normalized in {"police", "transport", "events", "economy", "politics", "safety"}:
        return f"story-media-{normalized}"
    return "story-media-general"


def _topic_image(item: NewsItem, visual_index: int | None = None) -> str | None:
    if visual_index is not None:
        return _topic_image_name_by_index(item.topic, visual_index)
    return _topic_image_name(item.topic, item.item_id)


def _topic_image_name(topic: str, stable_key: str) -> str | None:
    normalized = topic.strip().lower()
    candidates = _topic_image_candidates(normalized)
    if not candidates:
        return None
    digest = hashlib.sha1(stable_key.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(candidates)
    return candidates[index]


def _topic_image_name_by_index(topic: str, visual_index: int) -> str | None:
    normalized = topic.strip().lower()
    candidates = _topic_image_candidates(normalized)
    if not candidates:
        return None
    return candidates[visual_index % len(candidates)]


def _topic_image_candidates(normalized_topic: str) -> tuple[str, ...]:
    webp = tuple(path.name for path in sorted(TOPIC_IMAGE_DIR.glob(f"{normalized_topic}-*.webp")))
    if webp:
        return webp
    return tuple(path.name for path in sorted(TOPIC_IMAGE_DIR.glob(f"{normalized_topic}-*.png")))


def _public_summary(item: NewsItem) -> str:
    if item.summary.startswith("Source watch entry for ") or "The MVP stores attribution" in item.summary:
        return (
            f"Aktuelle Meldungen zu {display_topic(item.topic)} in {item.city}. "
            "Die Karte verweist auf die vollständige Originalmeldung mit weiteren Details."
        )
    summary = item.summary.strip()
    if summary and len(summary) < 120:
        return (
            f"{summary} Weitere Details, Hintergründe und vollständige Angaben stehen "
            "in der verlinkten Originalmeldung."
        )
    return summary
