# Hessen Aktuell

![Hessen Aktuell – regionales Nachrichtenportal](shared/assets/brand/social-card.png)

Ein deutschsprachiges regionales Informationsportal für Hessen, das
Nachrichten und Stellenangebote aus freigegebenen öffentlichen Quellen
automatisiert erfasst, strukturiert und als statische Website veröffentlicht.
Das Projekt verbindet Quellenverarbeitung, lokale Suche und Filter,
SEO-optimierte Themenseiten und einen wiederholbaren Publish-Prozess.

**Live:** [sandroabashishvili.github.io/hessen-aktuell](https://sandroabashishvili.github.io/hessen-aktuell/)

- automatische Hell-/Dunkeldarstellung nach Systemeinstellung
- gültiges PWA-Manifest mit projektspezifischen Installations-Icons

## Vom Quellensystem zur Website

1. **Quellen erfassen:** Freigegebene Adapter lesen Metadaten aus offiziellen
   und etablierten Nachrichten- und Arbeitgeberportalen.
2. **Daten verarbeiten:** Die Python-Pipeline normalisiert, prüft, kategorisiert
   und ergänzt die Datensätze um eigene kurze Zusammenfassungen.
3. **Statisch veröffentlichen:** Aus den geprüften Daten entstehen
   indexierbare Nachrichten-, Stadt-, Themen-, Archiv- und Jobseiten.

## Was bereits funktioniert

- regionale Nachrichten für Kassel, Frankfurt, Darmstadt und Wiesbaden
- Themenbereiche für Politik, Verkehr, Polizei, Wirtschaft, Veranstaltungen
  und Sicherheit
- Adapter für freigegebene offizielle oder etablierte Quellen
- Quellenangabe und direkter Link zum Original bei jeder Meldung
- tägliche Archive sowie Stadt- und Themenseiten
- automatisch gepflegte Stellenangebote aus offiziellen Arbeitgeberportalen
  mit Suche, Orts- und Berufsfeldfiltern sowie Seitennavigation
- eigene indexierbare Jobs-Seiten für Kassel, Frankfurt, Wiesbaden, Darmstadt,
  Offenbach und Gießen
- sieben aktive offizielle Arbeitgeberquellen
- eigene lokale Jobs-Banner für berufliche Bereiche
- lokal erzeugte, thematisch passende Kartenbilder
- automatisierte Sitemap, `robots.txt`, Canonicals und Social-Media-Metadaten
- Diagnosen für Quellen, interne Links, SEO-Felder und Inhaltsverteilung
- statische Veröffentlichung ohne eigenes Produktions-Backend

## Inhaltliche Leitlinie

Hessen Aktuell kopiert keine vollständigen Fremdartikel. Die Pipeline übernimmt
nur notwendige Metadaten, erstellt kurze eigene Zusammenfassungen und verweist
für den vollständigen Inhalt auf die Originalquelle.

## Technik

- Python 3
- eigene Source-Adapter und Build-Pipeline
- statisches HTML, CSS und JavaScript
- JSON-Dateien für generierte Nachrichtendaten und Archive
- GitHub Pages als Veröffentlichungsziel

## Lokal erzeugen

```bash
git clone https://github.com/sandroabashishvili/hessen-aktuell.git
cd hessen-aktuell
python3 -m shared.py.news_pipeline
python3 -m shared.py.diagnostics
```

Für eine veröffentlichungsfähige Version mit korrekter Basis-URL:

```bash
HESSEN_AKTUELL_BASE_URL="https://sandroabashishvili.github.io/hessen-aktuell" \
  bash scripts/build_publish.sh
```

Die generierte Website kann anschließend lokal bereitgestellt werden:

```bash
python3 -m http.server 8000
```

## Wichtige Bereiche

```text
.
├── shared/
│   ├── py/                 # Pipeline, Adapter und Diagnosen
│   ├── data/               # Registry, Nachrichten und Berichte
│   └── assets/             # gemeinsame Bilder und Styles
├── cities/                 # generierte Stadtseiten
├── topics/                 # generierte Themenseiten
├── archive/                # tägliche Archive
├── jobs/                   # generierte aktuelle Stellenangebote
├── service/                # nützliche offizielle Dienste
├── docs/                   # Architektur und Projektregeln
├── scripts/                # Build- und Automatisierungsskripte
└── index.html
```

## Status und nächste Ausbaustufe

Der aktuelle Stand ist ein funktionsfähiger Portfolio-MVP und noch kein
vollständiges redaktionelles Produkt. Nachrichten und Stellenangebote werden
aus freigegebenen Quellen erzeugt. Als Nächstes folgen weitere offizielle
Jobquellen, zusätzliche SEO-/Indexierungsarbeit und eine stabilere
langfristige Automatisierung.

Details stehen in [docs/current_status.md](docs/current_status.md).

## Autor

Sandro Abashishvili

[Portfolio](https://sandroabashishvili.github.io/) ·
[GitHub](https://github.com/sandroabashishvili)
