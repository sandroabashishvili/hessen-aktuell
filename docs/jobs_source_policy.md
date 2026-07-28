# Jobs Source Policy

Stand: 28. Juli 2026

## Ziel

Die Jobs-Seite veröffentlicht kompakte Hinweise auf aktuelle
Stellenausschreibungen in Hessen. Sie ist kein Bewerbungsportal und speichert
keine Bewerberdaten.

## Zulässige Quellen

Bevorzugt werden:

- offizielle Karriereportale des Landes Hessen;
- offizielle Seiten hessischer Städte und Landkreise;
- offizielle Landesbetriebe und öffentliche Arbeitgeber;
- dokumentierte APIs oder RSS-Feeds mit geeigneten Nutzungsbedingungen.

Kommerzielle Jobbörsen werden nicht ohne ausdrückliche API- oder
Syndizierungsfreigabe automatisch kopiert.

## Aktive Quellen

- Stadt Kassel;
- Hessen Mobil;
- Stadt Frankfurt am Main;
- Landeshauptstadt Wiesbaden;
- Wissenschaftsstadt Darmstadt.

Die zentrale Stellendatenbank des Landes Hessen und die Jobsuche der
Bundesagentur für Arbeit bleiben als direkte Portal-Links verfügbar.

## Veröffentlichte Felder

- Stellenbezeichnung;
- Arbeitgeber;
- Arbeitsort;
- Arbeitszeit und Vertragsart, soweit vorhanden;
- Bereich oder Organisationseinheit, soweit vorhanden;
- Bewerbungsfrist;
- Kennziffer;
- direkter Link zur Originalausschreibung.

Vollständige Ausschreibungstexte, Ansprechpartnerdaten und Bewerbungsunterlagen
werden nicht übernommen.

## Technische Regeln

- Jeder Adapter muss bei Strukturänderungen leer und sicher ausfallen.
- Die Originalquelle bleibt die verbindliche Informationsquelle.
- Abgelaufene oder nicht mehr erreichbare Angebote werden beim nächsten Lauf
  entfernt.
- Bei leerer Quelle bleiben offizielle Portal-Links als Fallback sichtbar.
