# Finding

[Übersicht](../../README.md) · [Testablauf](../methodology.md)

## Titel und Auswirkung

`<Konkrete unerlaubte Aktion und betroffene Daten/Funktion; z. B. Nutzer A kann das Testdokument von Nutzer B lesen.>`

| Feld | Eintrag |
| --- | --- |
| Finding-ID / Status | `<ID, offen / behoben / nachgeprüft>` |
| CWSTG-Tests / Lauf-IDs | `<Test-IDs und zugehörige Ergebnisdatensätze>` |
| Anwendung / Build / Endpunkte | `<betroffener Stand und Pfade>` |
| Voraussetzungen | `<Rolle, Kontobesitz, Mandant, Interaktion>` |
| Referenzen | `<konkrete versionierte WSTG-Links, ggf. weitere Primärquellen>` |
| Technischer Schweregrad | `<begründete Einstufung>` |
| CVSS, falls vereinbart | `<Version, Score, vollständiger Vektor, Begründung der Metriken>` |
| Geschäftsauswirkung / Priorität | `<erreichbare Daten, Reichweite, Folgen, Behebungstermin>` |
| Verantwortlich | `<Team / Ansprechperson>` |

## Reproduktion und Nachweis

1. `<Zulässigen Kontrollfall und Besitzverhältnisse belegen.>`
2. `<Geänderten Request mit synthetischen oder geschwärzten Testwerten angeben.>`
3. `<Unerlaubte Datenfreigabe oder Zustandsänderung nachweisen.>`

`<Minimale Request-/Response-Sequenz und relevante Zustandsbelege. Aktive Geheimnisse und personenbezogene Daten entfernen.>`

## Ursache und Abhilfe

`<Bestätigte Ursache oder ausdrücklich als Hypothese gekennzeichnete Erklärung. Konkrete serverseitige Korrektur, ggf. vorläufige Begrenzung und Regressionstest.>`

## Nachtest

`<Behobener Build, Datum, Ergebnislauf, erneuter Negativ- und Positivtest, verwandte Endpunkte, verbleibende Grenzen.>`
