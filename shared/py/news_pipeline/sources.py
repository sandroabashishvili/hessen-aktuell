from __future__ import annotations

import json
from pathlib import Path

from .models import NewsSource


REGISTRY_PATH = Path(__file__).resolve().parents[3] / "shared" / "data" / "source_registry.json"


def load_sources() -> tuple[NewsSource, ...]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    sources = [NewsSource(**source) for source in payload.get("sources", [])]
    return tuple(sorted(sources, key=lambda source: source.priority))


NEWS_SOURCES: tuple[NewsSource, ...] = load_sources()
