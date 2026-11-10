# Komponentenmatrix

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [CSV-Testkatalog](../test-catalog.csv)

Je tatsächlicher UI-Funktion und Backend-Zugriffsweg eine Zeile anlegen. Dieselbe Komponente kann mehrere Endpunkte haben; jeder relevante Rollen- und Besitzkontext braucht einen eigenen Ergebnislauf. Die Zeile ist eine Planungszuordnung und noch kein Testergebnis.

| UI-Funktion | Endpunkt / Methode | Kapitel / Test-IDs | Rolle / Mandant | Testobjekt / Besitzer | Priorität | Lauf-ID / Status |
| --- | --- | --- | --- | --- | --- | --- |
| Profil bearbeiten | `PATCH /api/profile` | 03 / `<IDs aus Kapitel>` | Nutzer A / T1 | Profil A | `<Priorität>` | `<Lauf-ID, Status>` |
| Dokument öffnen | `GET /api/documents/{id}` | 06 / `<IDs aus Kapitel>` | Nutzer A / T1 | Dokument B, Besitzer B | `<Priorität>` | `<Lauf-ID, Status>` |
| `<Funktion>` | `<Methode / Pfad>` | `<Kapitel / Test-IDs>` | `<Kontext>` | `<Objekt / Besitzer>` | `<Priorität>` | `<Lauf-ID, Status>` |

## Ergänzender Testumfang

`<Infrastruktur, Deployment, externe Dienste und verwendete Protokolle erfassen, die nicht durch die ausgewählten Komponentenfälle abgedeckt sind. Verantwortliche und separate Testpläne verlinken.>`

## Grenzen und offene Voraussetzungen

`<Fehlende Rollen, ausgeschlossene Endpunkte, benötigte Testdaten, Ressourcenbudget und Folgeaktionen.>`
