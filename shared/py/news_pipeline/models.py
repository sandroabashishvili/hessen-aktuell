from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsSource:
    source_id: str
    name: str
    url: str
    city: str
    topic: str
    family: str
    priority: int
    trust_level: str
    access_method: str
    copy_policy: str
    image_policy: str
    image_download_allowed: bool
    youtube_embed_allowed: bool


@dataclass(frozen=True)
class NewsItem:
    item_id: str
    title: str
    summary: str
    source_name: str
    source_url: str
    source_family: str
    city: str
    topic: str
    published_date: str
    summary_status: str
    image_rights_status: str
    media_type: str
    media_url: str | None
    media_source: str
    media_rights_status: str
    image_download_allowed: bool
    youtube_embed_allowed: bool
