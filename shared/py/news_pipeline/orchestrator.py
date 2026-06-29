from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import shutil
from zoneinfo import ZoneInfo

from .archive_builder import ArchiveBuilder
from .city_builder import CityPageBuilder
from .collector import collect_news_items
from .config import HessenNewsPipelineConfig, load_config
from .index_builder import HomeIndexBuilder
from .models import NewsItem
from .service_builder import ServicePageBuilder
from .sitemap_builder import build_sitemap
from .sources import NEWS_SOURCES
from .topic_builder import TopicPageBuilder

ARCHIVE_RETENTION_DAYS = 10


def run_news_generation(config: HessenNewsPipelineConfig | None = None) -> dict[str, str | int]:
    resolved = config or load_config()
    local_now = datetime.now(ZoneInfo("Europe/Berlin"))
    day_iso = local_now.strftime("%Y-%m-%d")

    resolved.data_dir.mkdir(parents=True, exist_ok=True)
    items = collect_news_items(day_iso)

    daily_json_path = resolved.data_dir / f"news_items_{day_iso}.json"
    daily_json_path.write_text(
        json.dumps(
            {
                "day_iso": day_iso,
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "generated_at_local": local_now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
                "mode": "source_adapter_mvp",
                "count": len(items),
                "items": [asdict(item) for item in items],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _prune_archive_history(resolved, keep_days=ARCHIVE_RETENTION_DAYS)

    archive_builder = ArchiveBuilder()
    daily_archive_path = archive_builder.build_day(resolved.archive_dir, day_iso, items)
    _rebuild_stored_daily_archives(resolved, archive_builder, current_day=day_iso)
    archive_index_path = archive_builder.build_index(
        resolved.archive_dir,
        day_iso,
        items,
        archive_counts=_load_archive_counts(resolved, current_day=day_iso, current_count=len(items)),
    )
    history_items = _load_unique_news_items(resolved, current_items=items)
    home_index_path = HomeIndexBuilder().build(
        resolved.project_root,
        day_iso,
        items,
        resolved.max_home_items,
        count_items=history_items,
    )
    city_builder = CityPageBuilder()
    city_names = _known_city_names()
    city_paths = {
        city: str(city_builder.build(resolved.project_root, city, day_iso, items))
        for city in city_names
    }
    city_paths["index"] = str(city_builder.build_index(resolved.project_root, city_names, items))
    topic_paths = TopicPageBuilder().build_all(resolved.project_root, day_iso, items)
    service_path = ServicePageBuilder().build(resolved.project_root)
    sitemap_result = build_sitemap(resolved.project_root, base_url=resolved.site_base_url)

    return {
        "mode": "source_adapter_mvp",
        "count": len(items),
        "daily_json_path": str(daily_json_path),
        "daily_archive_path": str(daily_archive_path),
        "archive_index_path": str(archive_index_path),
        "home_index_path": str(home_index_path),
        "city_pages": city_paths,
        "topic_pages": topic_paths,
        "service_page": str(service_path),
        "sitemap_path": str(sitemap_result.sitemap_path),
        "robots_path": str(sitemap_result.robots_path),
        "sitemap_url_count": sitemap_result.url_count,
    }


def _known_city_names() -> list[str]:
    cities = {
        source.city
        for source in NEWS_SOURCES
        if source.city and source.city.lower() != "hessen"
    }
    return sorted(cities)


def _rebuild_stored_daily_archives(
    config: HessenNewsPipelineConfig,
    archive_builder: ArchiveBuilder,
    *,
    current_day: str,
) -> None:
    for json_path in sorted(config.data_dir.glob("news_items_*.json")):
        day_iso = json_path.stem.removeprefix("news_items_")
        if day_iso == current_day:
            continue
        items = _load_news_items(json_path)
        if items:
            archive_builder.build_day(config.archive_dir, day_iso, items)


def _load_news_items(json_path) -> list[NewsItem]:
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = []
    for raw_item in payload.get("items", []):
        try:
            items.append(NewsItem(**raw_item))
        except TypeError:
            continue
    return items


def _load_unique_news_items(
    config: HessenNewsPipelineConfig,
    *,
    current_items: list[NewsItem],
) -> list[NewsItem]:
    unique_items: dict[str, NewsItem] = {}
    for json_path in sorted(config.data_dir.glob("news_items_*.json")):
        for item in _load_news_items(json_path):
            unique_items[item.item_id] = item
    for item in current_items:
        unique_items[item.item_id] = item
    return list(unique_items.values())


def _load_archive_counts(
    config: HessenNewsPipelineConfig,
    *,
    current_day: str,
    current_count: int,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for json_path in sorted(config.data_dir.glob("news_items_*.json")):
        day_iso = json_path.stem.removeprefix("news_items_")
        items = _load_news_items(json_path)
        if items:
            counts[day_iso] = len(items)
    counts[current_day] = current_count
    return counts


def _prune_archive_history(config: HessenNewsPipelineConfig, *, keep_days: int) -> None:
    json_paths = sorted(config.data_dir.glob("news_items_*.json"), reverse=True)
    keep_stems = {path.stem.removeprefix("news_items_") for path in json_paths[:keep_days]}
    for old_json_path in json_paths[keep_days:]:
        old_json_path.unlink(missing_ok=True)

    if not config.archive_dir.exists():
        return
    for archive_day_dir in config.archive_dir.iterdir():
        if not archive_day_dir.is_dir():
            continue
        if not _is_archive_day_name(archive_day_dir.name):
            continue
        if archive_day_dir.name not in keep_stems:
            shutil.rmtree(archive_day_dir)


def _is_archive_day_name(value: str) -> bool:
    parts = value.split("-")
    return (
        len(parts) == 3
        and len(parts[0]) == 4
        and len(parts[1]) == 2
        and len(parts[2]) == 2
        and all(part.isdigit() for part in parts)
    )
