# Zu CWSTG beitragen

[Übersicht](README.md) · [Referenzen](docs/references.md)

## Fachliche Änderungen

Ein Beitrag sollte eine konkrete Sicherheitsgrenze prüfen und mit kontrollierten Testdaten reproduzierbar sein. Vorhandene Abdeckung erhalten; bei Ersatz oder Zusammenlegung die Änderung im Pull Request erklären. Begrenzte Requestmengen und beobachtbare Abbruchkriterien angeben, wenn Wiederholungen, Parallelität, teure Abfragen oder Benachrichtigungen Teil des Tests sind.

Pro Test Voraussetzungen, Schritte, sicheres Ergebnis, Belege und Abhilfe trennen. Ein Fehlerstatus allein beweist keine Zugriffskontrolle; eine ausbleibende Skriptausführung allein beweist keine sichere HTML-Verarbeitung. Fixes müssen zur Ursache und zum tatsächlichen Ausgabekontext passen.

## Kapitel und Test-IDs

Kapitel liegen unter `docs/components/NN-name.md`. Ein Kapitel hat genau eine H1 sowie `## Ziel`, `## Voraussetzungen`, `## Testfälle` und `## Quellen`. Nach der H1 folgt die Navigation zu Übersicht, Testablauf und Ergebnisvorlage.

Jeder Test beginnt mit einer H3 der Form `### CWSTG-NN-NN — Titel` und enthält diese Felder:

```text
**Referenzen:**
**Prüfschritte:**
**Sicheres Ergebnis:**
**Belege:**
**Abhilfe:**
```

`Referenzen` enthält direkte Links auf konkrete Quellen; `Prüfschritte` ist eine nummerierte Liste. Bestehende Test-IDs bei Textänderungen beibehalten und niemals für andere Sicherheitsziele wiederverwenden. Neue Tests erhalten eine neue freie Nummer im Kapitel. Lücken nach entfernten Tests sind zulässig; entfernte IDs und deren Ersatz im Pull Request festhalten.

## Quellen und Versionen

WSTG-Referenzen als verlinktes Label `WSTG-v42-SESS-03` auf die entsprechende v4.2-Seite schreiben. Keine `latest`-/`stable`-Testreferenzen, Trackingparameter, erfundenen Kategorien oder unbelegten Standardkonformitätsversprechen verwenden. Zu technischen Erweiterungen ohne direkten WSTG-Test eine passende Primärquelle angeben. Quellen in eigenen Worten zusammenfassen; übernommene Inhalte und Lizenzhinweise kenntlich machen.

Das [WSTG-Referenzregister](data/wstg-v42.json) stammt aus der offiziellen OWASP-Checkliste am dort vermerkten Commit. Bei Versionswechseln Quelle und Zuordnung fachlich prüfen, Kapitelreferenzen gemeinsam aktualisieren und die Prüfung anpassen. Ein automatisch existierender Link bestätigt die fachliche Zuordnung noch nicht.

## Prüfung vor einem Pull Request

```sh
python3 scripts/check_docs.py --write-catalog
python3 scripts/check_docs.py
python3 -m unittest discover -s tests
```

Der Prüfer kontrolliert lokale Links und Sprungmarken, Kapitelstruktur, eindeutige Test-IDs, Pflichtfelder, konkrete Referenzen und WSTG-ID-/Zielzuordnungen. Der generierte [CSV-Katalog](docs/test-catalog.csv) gehört bei Änderungen an Tests mit in den Beitrag. Die Offline-Prüfung ersetzt weder das fachliche Review noch die Erreichbarkeitsprüfung externer Quellen.

## Belege und Lizenz

Nur synthetische oder geschwärzte Beispiele einchecken. Aktive Tokens, Passwörter und vertrauliche Testberichte gehören in die dafür vorgesehene geschützte Projektablage. Beiträge erfolgen unter der bestehenden [CC-BY-SA-4.0-Lizenz](LICENSE.md); fremde Quellen behalten ihre jeweilige Lizenz und Urheberschaft.
