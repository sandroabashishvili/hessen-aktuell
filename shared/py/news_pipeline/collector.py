from __future__ import annotations

from datetime import date

from .adapters import collect_source_items
from .html import display_topic
from .models import NewsItem, NewsSource
from .sources import NEWS_SOURCES


def collect_news_items(day_iso: str | None = None) -> list[NewsItem]:
    """Collect the current regional news items from configured sources."""

    resolved_day = day_iso or date.today().isoformat()
    items: list[NewsItem] = []
    for source in sorted(NEWS_SOURCES, key=lambda item: item.priority):
        source_items = collect_source_items(source, resolved_day)
        if source_items:
            items.extend(source_items)
        else:
            items.append(_source_to_item(source, resolved_day))
    return items


def _source_to_item(source: NewsSource, day_iso: str) -> NewsItem:
    topic_label = display_topic(source.topic)
    city_label = source.city
    return NewsItem(
        item_id=f"{day_iso}-{source.source_id}",
        title=f"{city_label}: {source.name}",
        summary=f"Aktuelle Meldungen zu {topic_label} in {city_label}. Details stehen auf der Originalseite.",
        source_name=source.name,
        source_url=source.url,
        source_family=source.family,
        city=source.city,
        topic=source.topic,
        published_date=day_iso,
        summary_status="source_watch_fallback",
        image_rights_status=source.image_policy,
        media_type="placeholder",
        media_url=None,
        media_source="local_placeholder",
        media_rights_status=source.image_policy,
        image_download_allowed=source.image_download_allowed,
        youtube_embed_allowed=source.youtube_embed_allowed,
    )
