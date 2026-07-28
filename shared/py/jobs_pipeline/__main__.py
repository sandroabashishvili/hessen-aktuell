from __future__ import annotations

import json

from .orchestrator import run_jobs_generation


if __name__ == "__main__":
    print(json.dumps(run_jobs_generation(), ensure_ascii=False, indent=2))
