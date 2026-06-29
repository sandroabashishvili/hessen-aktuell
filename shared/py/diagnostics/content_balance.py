from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def run_content_balance_diagnostics() -> dict[str, object]:
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    project_root = Path(__file__).resolve().parents[3]
    latest_news = _latest_news_path(project_root)
    items = _load_items(latest_news)
    city_counts = Counter(item.get("city", "") for item in items if item.get("city"))
    topic_counts = Counter(item.get("topic", "") for item in items if item.get("topic"))
    source_counts = Counter(item.get("source_name", "") for item in items if item.get("source_name"))
    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S Europe/Berlin"),
        "news_path": str(latest_news) if latest_news else "",
        "total_items": len(items),
        "city_counts": dict(sorted(city_counts.items())),
        "topic_counts": dict(sorted(topic_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "top_city": _top_item(city_counts),
        "top_source": _top_item(source_counts),
        "status": _status(len(items), city_counts, source_counts),
    }
    output_path = _report_path(project_root, now)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**report, "report_path": str(output_path)}


def _latest_news_path(project_root: Path) -> Path | None:
    news_dir = project_root / "shared" / "data" / "news"
    paths = sorted(news_dir.glob("news_items_*.json"))
    return paths[-1] if paths else None


def _load_items(path: Path | None) -> list[dict[str, object]]:
    if not path or not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    return items if isinstance(items, list) else []


def _top_item(counter: Counter[str]) -> dict[str, object]:
    if not counter:
        return {"name": "", "count": 0}
    name, count = counter.most_common(1)[0]
    return {"name": name, "count": count}


def _status(total_items: int, city_counts: Counter[str], source_counts: Counter[str]) -> str:
    if total_items == 0:
        return "empty"
    top_city = city_counts.most_common(1)[0][1] if city_counts else 0
    top_source = source_counts.most_common(1)[0][1] if source_counts else 0
    if top_city / total_items > 0.45 or top_source / total_items > 0.25:
        return "attention_required"
    return "ok"


def _report_path(project_root: Path, now: datetime) -> Path:
    return project_root / "shared" / "data" / "diagnostics" / f"content_balance_report_{now:%Y-%m-%d}.json"
