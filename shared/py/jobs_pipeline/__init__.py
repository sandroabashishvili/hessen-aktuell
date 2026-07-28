"""Official-source jobs pipeline for Hessen Aktuell."""


def run_jobs_generation(*args, **kwargs):
    from .orchestrator import run_jobs_generation as _run_jobs_generation

    return _run_jobs_generation(*args, **kwargs)


__all__ = ["run_jobs_generation"]
