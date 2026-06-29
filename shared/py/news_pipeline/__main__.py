from __future__ import annotations

import json

from .orchestrator import run_news_generation


if __name__ == "__main__":
    result = run_news_generation()
    print(json.dumps(result, ensure_ascii=False, indent=2))
