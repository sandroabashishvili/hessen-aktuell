from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

from .html import brand_mark, head_meta, page_nav


@dataclass(frozen=True)
class ServiceLink:
    title: str
    description: str
    url: str


@dataclass(frozen=True)
class ServiceCategory:
    title: str
    description: str
    links: tuple[ServiceLink, ...]


SERVICE_CATEGORIES: tuple[ServiceCategory, ...] = (
    ServiceCategory(
        title="Warnungen & Notfälle",
        description="Offizielle Warnungen, Bevölkerungsschutz und digitale Sicherheit.",
        links=(
            ServiceLink("Warnportal des Bundes", "Aktuelle amtliche Warnungen für Deutschland.", "https://warnung.bund.de/"),
            ServiceLink("Bundesamt für Bevölkerungsschutz", "Vorsorge, Warnung und Kriseninformationen.", "https://www.bbk.bund.de/"),
            ServiceLink("Deutscher Wetterdienst", "Wetterwarnungen, Wetterlage und Unwetterinformationen.", "https://www.dwd.de/"),
            ServiceLink("BSI", "Informationen zu Cybersicherheit und sicherem digitalen Alltag.", "https://www.bsi.bund.de/"),
        ),
    ),
    ServiceCategory(
        title="Behörden & Verwaltung",
        description="Zentrale Portale für Bundes-, Landes- und Stadtverwaltung.",
        links=(
            ServiceLink("Verwaltung Bund", "Bundesweites Verwaltungsportal für Leistungen und Behörden.", "https://verwaltung.bund.de/"),
            ServiceLink("Hessen.de", "Offizielles Portal des Landes Hessen.", "https://www.hessen.de/"),
            ServiceLink("Verwaltungsportal Hessen", "Verwaltungsleistungen und Zuständigkeiten in Hessen.", "https://verwaltungsportal.hessen.de/"),
            ServiceLink("Stadt Kassel", "Offizielle Informationen und Dienstleistungen der Stadt Kassel.", "https://www.kassel.de/"),
            ServiceLink("Stadt Frankfurt", "Offizielles Stadtportal Frankfurt am Main.", "https://frankfurt.de/"),
            ServiceLink("Stadt Darmstadt", "Offizielles Portal der Wissenschaftsstadt Darmstadt.", "https://www.darmstadt.de/"),
            ServiceLink("Stadt Wiesbaden", "Offizielles Portal der Landeshauptstadt Wiesbaden.", "https://www.wiesbaden.de/"),
        ),
    ),
    ServiceCategory(
        title="Polizei & Sicherheit",
        description="Polizeiliche Informationen, Onlinewache und bundesweite Sicherheitsbehörden.",
        links=(
            ServiceLink("Polizei Hessen", "Offizielle Informationen der hessischen Polizei.", "https://www.polizei.hessen.de/"),
            ServiceLink("Onlinewache Hessen", "Digitale Kontaktstelle der hessischen Polizei.", "https://www.polizei.hessen.de/onlinewache/"),
            ServiceLink("BKA", "Bundeskriminalamt: Lagebilder, Prävention und Warnhinweise.", "https://www.bka.de/"),
            ServiceLink("Presseportal Blaulicht", "Pressemitteilungen von Polizei und Rettungsdiensten.", "https://www.presseportal.de/blaulicht/"),
        ),
    ),
    ServiceCategory(
        title="Gesundheit & Verbraucher",
        description="Gesundheitsinformationen, ärztlicher Bereitschaftsdienst und Verbraucherschutz.",
        links=(
            ServiceLink("116117", "Ärztlicher Bereitschaftsdienst und Patientenservice.", "https://www.116117.de/"),
            ServiceLink("Gesund.bund.de", "Gesundheitsinformationen des Bundesministeriums für Gesundheit.", "https://www.gesund.bund.de/"),
            ServiceLink("Gesundheit Hessen", "Gesundheitsthemen des Landes Hessen.", "https://soziales.hessen.de/gesundheit"),
            ServiceLink("Verbraucherzentrale Hessen", "Beratung und Informationen für Verbraucherinnen und Verbraucher.", "https://www.verbraucherzentrale-hessen.de/"),
        ),
    ),
    ServiceCategory(
        title="Verkehr & Mobilität",
        description="ÖPNV, Bahn, Straßenverkehr und Mobilitätsinformationen für Hessen.",
        links=(
            ServiceLink("RMV", "Rhein-Main-Verkehrsverbund: Verbindungen, Tickets und Störungen.", "https://www.rmv.de/"),
            ServiceLink("Deutsche Bahn", "Bahnverbindungen, Fahrpläne und Reiseinformationen.", "https://www.bahn.de/"),
            ServiceLink("Mobilität Hessen", "Mobilitätsportal des Landes Hessen.", "https://mobil.hessen.de/"),
            ServiceLink("Hessen Mobil", "Straßen, Baustellen und Verkehrsinfrastruktur in Hessen.", "https://www.hessenmobil.de/"),
            ServiceLink("VGF Frankfurt", "U-Bahn, Straßenbahn und Verkehrsmeldungen in Frankfurt.", "https://www.vgf-ffm.de/"),
        ),
    ),
    ServiceCategory(
        title="Arbeit, Familie & Integration",
        description="Arbeitssuche, Zuwanderung, Familie und Bildungsinformationen.",
        links=(
            ServiceLink("Bundesagentur für Arbeit", "Jobsuche, Arbeitslosmeldung, Ausbildung und Beratung.", "https://www.arbeitsagentur.de/"),
            ServiceLink("Make it in Germany", "Offizielles Portal für Fachkräfte aus dem Ausland.", "https://www.make-it-in-germany.com/"),
            ServiceLink("BAMF", "Migration, Aufenthalt, Integration und Sprachkurse.", "https://www.bamf.de/"),
            ServiceLink("Familienportal", "Leistungen und Informationen für Familien.", "https://www.familienportal.de/"),
            ServiceLink("Kultusministerium Hessen", "Schule, Bildung und Unterricht in Hessen.", "https://kultus.hessen.de/"),
            ServiceLink("Hochschulkompass", "Studiengänge und Hochschulen in Deutschland.", "https://www.hochschulkompass.de/"),
        ),
    ),
)

SERVICE_BANNERS: dict[str, str] = {
    "Warnungen & Notfälle": "safety-04.webp",
    "Behörden & Verwaltung": "politics-04.webp",
    "Polizei & Sicherheit": "police-03.webp",
    "Gesundheit & Verbraucher": "safety-03.webp",
    "Verkehr & Mobilität": "transport-04.webp",
    "Arbeit, Familie & Integration": "economy-03.webp",
}


class ServicePageBuilder:
    def build(self, project_root: Path) -> Path:
        target = project_root / "service" / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_render_service_page(), encoding="utf-8")
        return target


def service_teaser_links(prefix: str = "./") -> str:
    links = (
        ("Warnungen", "Notfälle", "Amtliche Warn- und Kriseninfos", f"{prefix}service/#warnungen-notfaelle"),
        ("Behörden", "Verwaltung", "Bund, Hessen und Stadtportale", f"{prefix}service/#behoerden-verwaltung"),
        ("Polizei", "Sicherheit", "Onlinewache und Prävention", f"{prefix}service/#polizei-sicherheit"),
        ("Gesundheit", "116117", "Ärztliche Hilfe und Beratung", f"{prefix}service/#gesundheit-verbraucher"),
        ("Verkehr", "RMV & Bahn", "Fahrplan, Störung und Straße", f"{prefix}service/#verkehr-mobilitaet"),
        ("Arbeit", "Jobs", "Agentur, Beratung und Suche", f"{prefix}service/#arbeit-familie-integration"),
        ("Familie", "Leistungen", "Familienportal und Bildung", f"{prefix}service/#arbeit-familie-integration"),
        ("Integration", "Sprache", "BAMF, Aufenthalt und Kurse", f"{prefix}service/#arbeit-familie-integration"),
    )
    return "\n".join(
        f'            <a class="quick-link" href="{escape(url, quote=True)}">'
        f"<span>{escape(label)}</span><strong>{escape(title)}</strong><em>{escape(description)}</em>"
        "</a>"
        for title, label, description, url in links
    )


def _render_service_page() -> str:
    category_sections = "\n".join(_render_category(category) for category in SERVICE_CATEGORIES)
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{head_meta(
    title="Service Links | Hessen Aktuell",
    description="Nützliche offizielle Links für Alltag, Behörden, Sicherheit, Gesundheit, Verkehr und Leben in Hessen.",
    prefix="../",
    canonical_path="/service/",
)}
  <link rel="stylesheet" href="../shared/css/styles.css">
</head>
<body data-page="service">
  <header class="site-header">
{brand_mark('../')}
    <p class="eyebrow">Hessen Aktuell</p>
    <h1><a class="hero-link" href="../service/">Service Links</a></h1>
    <p class="lede">Nützliche offizielle Links für Alltag, Behörden, Sicherheit, Gesundheit, Verkehr und Leben in Hessen.</p>
{page_nav('../')}
  </header>
  <main class="page-shell">
    <div class="service-directory-grid">
{category_sections}
    </div>
  </main>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <p class="site-footer__note">© 2026 Hessen Aktuell</p>
    </div>
  </footer>
  <script src="../shared/js/main.js"></script>
</body>
</html>
"""


def _render_category(category: ServiceCategory) -> str:
    category_id = _slug(category.title)
    links = "\n".join(_render_link_card(link) for link in category.links)
    banner = _render_category_banner(category)
    return f"""
    <section class="panel service-section" id="{escape(category_id)}">
{banner}
      <div class="panel-head service-panel-head">
        <div>
          <p class="section-label">Service</p>
          <h2>{escape(category.title)}</h2>
        </div>
      </div>
      <p class="story-summary">{escape(category.description)}</p>
      <div class="service-link-grid">
{links}
      </div>
    </section>"""


def _render_link_card(link: ServiceLink) -> str:
    return (
        f'        <a class="service-link-card" href="{escape(link.url, quote=True)}" rel="nofollow noopener" target="_blank">'
        f"<strong>{escape(link.title)}</strong>"
        f"<span>{escape(link.description)}</span>"
        "</a>"
    )


def _render_category_banner(category: ServiceCategory) -> str:
    image_name = SERVICE_BANNERS.get(category.title, "politics-01.webp")
    return (
        f'      <div class="service-banner">'
        f'<img src="../shared/assets/news/topics/{escape(image_name, quote=True)}" '
        f'alt="{escape(category.title)}" loading="lazy" decoding="async" width="1100" height="619">'
        "</div>"
    )


def _slug(value: str) -> str:
    normalized = value.lower()
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "&": "",
        ",": "",
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return "-".join(part for part in normalized.split() if part)
