from __future__ import annotations

from .models import JobSource


JOB_SOURCES: tuple[JobSource, ...] = (
    JobSource(
        source_id="stadt-kassel-jobs",
        name="Stadt Kassel",
        url=(
            "https://www.kassel.de/buerger/rathaus_und_politik/"
            "arbeit-und-ausbildung-bei-der-stadt/stellenangebote/stellenangebote.php"
        ),
        employer="Stadt Kassel",
        default_location="Kassel",
        priority=10,
    ),
    JobSource(
        source_id="hessen-mobil-jobs",
        name="Hessen Mobil",
        url="https://mobil.hessen.de/karriere/stellenangebote",
        employer="Hessen Mobil",
        default_location="Hessen",
        priority=20,
    ),
)


FALLBACK_JOB_PORTALS: tuple[tuple[str, str, str], ...] = (
    (
        "Arbeitgeber Land Hessen",
        "Zentrale Stellendatenbank der hessischen Landesverwaltung.",
        "https://karriere.hessen.de/stellendatenbank-der-landesverwaltung/stellenangebote",
    ),
    (
        "Bundesagentur für Arbeit",
        "Offizielle Jobsuche für Beschäftigung und Ausbildung.",
        "https://www.arbeitsagentur.de/jobsuche/",
    ),
    (
        "Stadt Frankfurt",
        "Karriereportal und Stellenangebote der Stadtverwaltung Frankfurt.",
        "https://frankfurt.de/karriere",
    ),
)
