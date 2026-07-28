"""Source-aware news generation pipeline for Hessen Aktuell."""


def run_news_generation(*args, **kwargs):
    from .orchestrator import run_news_generation as _run_news_generation

    return _run_news_generation(*args, **kwargs)


__all__ = ["run_news_generation"]
