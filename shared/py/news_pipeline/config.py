from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class HessenNewsPipelineConfig:
    project_root: Path
    data_dir: Path
    archive_dir: Path
    site_base_url: str = "https://example.com"
    max_home_items: int = 6


def load_config() -> HessenNewsPipelineConfig:
    project_root = Path(__file__).resolve().parents[3]
    return HessenNewsPipelineConfig(
        project_root=project_root,
        data_dir=project_root / "shared" / "data" / "news",
        archive_dir=project_root / "archive",
        site_base_url=os.environ.get("HESSEN_AKTUELL_BASE_URL", "http://localhost:8090"),
    )
