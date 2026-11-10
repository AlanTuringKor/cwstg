# Referenzen und WSTG-Zuordnung

[Übersicht](../README.md) · [Beitragsleitfaden](../CONTRIBUTING.md)

## Festgelegte Referenzversion

CWSTG verwendet **OWASP WSTG v4.2** als feste Referenz für Testzuordnungen. Verlinkte Labels enthalten die Version, etwa `WSTG-v42-ATHZ-04`. Der Link führt direkt zum zugehörigen Test, in diesem Fall [Insecure Direct Object References](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References).

Diese Festlegung macht Berichte vergleichbar, wenn sich die Entwicklungsversion des WSTG ändert. Sie ist keine Aussage, dass ein einzelner Test sämtliche Anforderungen eines Standards abdeckt. Ergänzungen zu Cloud-Speicher, Browser-APIs oder bestimmten Protokollen verweisen auf die jeweils passende Primärquelle; nicht jeder CWSTG-Test hat eine direkte WSTG-Entsprechung.

## Offline-Referenzregister

[data/wstg-v42.json](../data/wstg-v42.json) enthält 97 Test-IDs mit Titeln und Linkzielen aus der [offiziellen OWASP-Checkliste am Commit dd33419](https://github.com/OWASP/wstg/blob/dd33419e10edb22b78d89325a6c2aad9f184e3a2/checklist/checklist.json). Quelldatum, SHA-256-Prüfsumme und Lizenz sind im Register vermerkt. Titel bleiben zur eindeutigen Zuordnung in der englischen Originalfassung.

Für die lokale Fassung wurden die IDs um `v42` ergänzt, `/stable/` in den ursprünglichen URLs durch `/v42/` ersetzt und die optionalen `.html`-Endungen entfernt. Alle Zielpfade wurden gegen die Dokumentdateien dieses OWASP-Commits abgeglichen. Die Daten stehen unter der in [LICENSE.md](../LICENSE.md) genannten OWASP-Attribution.

## Was die Prüfung leistet

```sh
python3 scripts/check_docs.py
```

Der Prüfer verwendet ausschließlich Dateien im Repository. Er kontrolliert lokale Linkziele und Markdown-Sprungmarken, die Kapitelstruktur, Test-IDs, Pflichtfelder, konkrete Quellenlinks und die Übereinstimmung von WSTG-ID und Zielpfad. Versionierte OWASP-URLs auf `owasp.org` und `wstg.owasp.org` werden dabei gleich behandelt. Er überprüft auch, ob der CSV-Katalog dem aktuellen Kapitelinhalt entspricht.

Die unterstützte Markdown-Konvention sind Inline-Links und ATX-Überschriften (`#`, `##`, `###`). Beispiele in Codeblöcken zählen nicht als echte Tests oder Verweise. Der Prüfer benötigt weder Drittanbieterpakete noch Netzverbindung. Erreichbarkeit externer Quellen und fachliche Eignung einer Zuordnung bleiben Aufgaben des Reviews.

## Quellen pflegen

Bei fachlichen Änderungen die Originalquelle lesen und die tatsächlich geprüfte Sicherheitsgrenze mit dem referenzierten Test vergleichen. Ein Rollenwechsel, ein Objektzugriff und eine Anmeldung können unterschiedliche Zuordnungen brauchen, obwohl sie auf derselben Seite vorkommen. Neue oder geänderte Standards getrennt und mit Version ausweisen; bestehende Bericht-IDs nicht stillschweigend auf andere Inhalte umdeuten.
