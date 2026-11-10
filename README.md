# CWSTG — Component-based Web Security Testing Guide

Sicherheitstests entlang der Funktionen einer Webanwendung: vom Login über Dateiuploads bis zur Pagination. CWSTG verbindet sichtbare Komponenten mit den dahinterliegenden APIs, Berechtigungen und Datenflüssen. Die Kapitel unterstützen Pentests, Entwicklungsreviews und Regressionstests.

## Direkt loslegen

1. Im [Testablauf](docs/methodology.md) Anwendung, Rollen, Testdaten und Grenzen festhalten.
2. Passende Komponenten aus der Tabelle auswählen und ihre tatsächlichen API-Endpunkte erfassen.
3. Jeden Test mit berechtigtem Kontrollzugriff und gezielter Änderung durchführen. Ergebnis und Belege in der [Ergebnisvorlage](docs/templates/test-result.md) erfassen.
4. Bestätigte Schwachstellen mit der [Finding-Vorlage](docs/templates/finding.md) dokumentieren und nach der Behebung erneut prüfen.

Die [Komponentenmatrix](docs/templates/component-matrix.md) hilft bei der Planung. Der [CSV-Testkatalog](docs/test-catalog.csv) enthält Test-IDs, Titel, Quellenverweise und Kapitelpfade für Tabellenprogramme und eigene Werkzeuge.

## Komponenten

| Nr. | Komponente | Zentrale Prüfziele |
| --- | --- | --- |
| 01 | [Login](docs/components/01-login.md) | Authentifizierung, MFA, Session-Wechsel, begrenzte Anmeldeversuche |
| 02 | [Registrierung und Wiederherstellung](docs/components/02-registration-recovery.md) | Kontobindung, Reset-Token, Enumeration, atomare Zustandswechsel |
| 03 | [Profil und Einstellungen](docs/components/03-profile-settings.md) | Objektberechtigungen, sensible Änderungen, Mass Assignment, XSS |
| 04 | [Rollen und Berechtigungen](docs/components/04-roles-permissions.md) | Horizontale und vertikale Zugriffskontrolle, Mandantentrennung |
| 05 | [Adminbereich und Dashboard](docs/components/05-admin-dashboard.md) | Direkte API-Zugriffe, privilegierte Aktionen, Exporte und Protokolle |
| 06 | [Listen und Detailseiten / CRUD](docs/components/06-crud.md) | Lesen, Ändern, Löschen und Auflisten fremder Objekte |
| 07 | [Suche und Filter](docs/components/07-search-filter.md) | Query-Injection, Ausgabekontext, Berechtigungen, Abfragekosten |
| 08 | [Dateiupload und Medienverwaltung](docs/components/08-file-upload.md) | Dateityp, Speicherort, Auslieferung, Zugriff und Verarbeitung |
| 09 | [Formulare und mehrstufige Abläufe](docs/components/09-multi-step-forms.md) | CSRF, Reihenfolge, serverseitige Werte, Wiederholungen und Parallelität |
| 10 | [SPA und clientseitiges Routing](docs/components/10-spa-routing.md) | API-Autorisierung, DOM-XSS, Weiterleitungen und Nachrichten |
| 11 | [Cookies und Sessions](docs/components/11-sessions.md) | Cookie-Konfiguration, Logout, Zeitlimits und Remember-me |
| 12 | [Kommentare und Diskussionen](docs/components/12-comments.md) | Stored XSS, Moderation, Erwähnungen und Zugriffskontrolle |
| 13 | [Clientseitiger Speicher](docs/components/13-client-storage.md) | Vertrauensgrenzen, sensible Daten, Kontowechsel und Offline-Caches |
| 14 | [Galerie und Medienanzeige](docs/components/14-media-viewer.md) | Medienberechtigungen, Metadaten, SVG-Kontext und externe Quellen |
| 15 | [Rich-Text-Editor](docs/components/15-rich-text.md) | HTML-Bereinigung, URL-Schemata, Einbettungen und Renderpfade |
| 16 | [Pagination und Infinite Scroll](docs/components/16-pagination.md) | Grenzwerte, Cursor-Bindung, Datenfreigabe, Caches und Ressourcen |

## Ergebnisse richtig bewerten

Jeder Test besitzt eine stabile ID wie `CWSTG-01-01`, Voraussetzungen, Prüfschritte, ein sicheres Ergebnis, Belege und Abhilfe. Die ID bleibt bei Textkorrekturen erhalten; neue Tests bekommen neue IDs.

Ein Statuscode, ein ausgebliebenes Dialogfenster oder ein unauffälliger Scannerlauf reicht als Sicherheitsnachweis nicht aus. Entscheidend sind die tatsächlich ausgelieferten Daten, der serverseitige Zustand und ein funktionierender Kontrollfall. Nicht durchführbare Tests bleiben sichtbar: `BESTANDEN`, `FEHLGESCHLAGEN`, `BLOCKIERT`, `NICHT_GETESTET` und `NICHT_ANWENDBAR` haben im [Testablauf](docs/methodology.md) eigene Kriterien.

## Referenzen und Abdeckung

Die Testreferenzen sind auf [OWASP WSTG v4.2](https://owasp.org/www-project-web-security-testing-guide/v42/) festgelegt. Ein Label wie `WSTG-v42-SESS-03` bezeichnet die konkrete Version und den Abschnitt. Ergänzende Prüfungen ohne direkte Entsprechung verwenden eine passende Primärquelle statt einer erfundenen WSTG-ID. Technische Zuordnung und Versionsprüfung erläutert die [Referenzdokumentation](docs/references.md).

CWSTG deckt wiederkehrende Komponenten ab. Für das jeweilige System gehören zusätzliche Prüfungen zu Infrastruktur, Deployment, TLS, Lieferkette und weiteren Protokollen in den Testplan. Auch OAuth/OIDC, Passkeys, GraphQL, WebSockets oder Webhooks brauchen bei Verwendung eigene Protokolltests. Eine bestandene Komponentenliste belegt weder vollständige Sicherheit noch ASVS- oder ISO-Konformität.

## Mitwirken und prüfen

Fachliche Korrekturen, neue Tests und neue Komponenten sind willkommen. Der [Beitragsleitfaden](CONTRIBUTING.md) beschreibt Format, Quellen und die Regeln für Test-IDs. Für die lokale Prüfung genügt Python 3.11 oder neuer; zusätzliche Pakete und Netzwerkzugriff sind nicht erforderlich:

```sh
python3 scripts/check_docs.py
python3 -m unittest discover -s tests
```

Nach Änderungen an Testtiteln oder Referenzen den CSV-Katalog aktualisieren:

```sh
python3 scripts/check_docs.py --write-catalog
```

GitHub Actions führt dieselben Prüfungen bei Pushes und Pull Requests aus. Alte Notion-Exportpfade verweisen weiterhin auf die aktuellen Kapitel.

## Urheberschaft und Lizenz

Projektmaintainer und ursprünglicher Autor: **Mingi Hong**. Der Leitfaden steht wie bisher unter [Creative Commons Attribution-ShareAlike 4.0](LICENSE.md). CWSTG ist ein eigenständiges Projekt; die OWASP-Verweise kennzeichnen Quellen und Testzuordnungen.
