# Testablauf

[Übersicht](../README.md) · [Komponentenmatrix](templates/component-matrix.md) · [Ergebnisvorlage](templates/test-result.md)

## 1. Anwendung und Grenzen erfassen

Im Testauftrag Zielsysteme, Umgebung und Build/Commit, Zeitraum, Rollen, Mandanten, erlaubte Aktionen sowie ausgeschlossene Systeme festhalten. Zu jedem UI-Baustein die tatsächlichen HTTP-/API-Endpunkte, Hintergrundjobs, Exporte und Speicherorte notieren. Eine versteckte Schaltfläche oder Client-Route bildet keine serverseitige Berechtigungsgrenze.

Die [Komponentenmatrix](templates/component-matrix.md) verknüpft diese Funktionen mit Kapiteln und Test-IDs. Wiederverwendete Backends gemeinsam erfassen, aber verschiedene Zugriffswege gesondert prüfen: Derselbe Datensatz kann in Detailansicht, Suche, Export und Vorschaubild unterschiedliche Filter durchlaufen.

## 2. Kontrollierte Testdaten vorbereiten

Soweit die Anwendung die Rollen anbietet, folgende Identitäten bereitstellen:

| Identität | Zweck |
| --- | --- |
| Anonym | Zugriff ohne Session oder Token |
| Nutzer A und B, gleiche Rolle | Fremde Objekte und horizontale Berechtigungen |
| Nutzer C, anderer Mandant | Mandantenübergreifende Isolation |
| Administrator oder Fachrolle | Vergleich mit zulässigen privilegierten Aktionen |

Eigene Testobjekte mit eindeutigen, nicht sensiblen Markern anlegen. Besitz, Rolle und Mandant jedes Objekts dokumentieren. Separierte Browserprofile oder Cookie-Speicher verwenden, damit Sitzungen nicht versehentlich vermischt werden. Ein Test mit fehlender erforderlicher Rolle ist `BLOCKIERT`; existiert das entsprechende Rollenmodell im System überhaupt nicht, kann er begründet `NICHT_ANWENDBAR` sein.

Für wiederholte Requests vorab eine maximale Requestzahl, Rate, Parallelität, Laufzeit und Abbruchschwelle festlegen. Kleine sequentielle Testmengen sind der Ausgangspunkt. Lastgrenzen, wiederholte Nachrichten und parallele Schreibvorgänge brauchen ein passendes Testfenster und Monitoring. Bei unerwarteten Änderungen, erhöhten Fehlerraten oder Erreichen des Budgets abbrechen und den Befund dokumentieren; Schutzmaßnahmen nicht durch neue Konten oder Quellen umgehen.

## 3. Hypothese mit Kontrollfall prüfen

1. **Sollverhalten festhalten:** Wer darf welche Daten lesen oder welche Aktion ausführen? Welche Grenze soll der Test überprüfen?
2. **Positiven Kontrollfall aufzeichnen:** Einen zulässigen Zugriff oder gültigen Ablauf ausführen und Request, Response sowie relevanten Zustand sichern.
3. **Eine Variable ändern:** Etwa die Objekt-ID, Rolle, Token-Bindung, einen Parameter oder die Reihenfolge ändern. Zum Vergleich dieselben übrigen Bedingungen beibehalten.
4. **Wirkung prüfen:** Antwortdaten und Zustandsänderung kontrollieren; bei asynchronen Vorgängen auch Jobstatus und erzeugte Artefakte. Ein Fehlerstatus kann trotzdem eine Änderung begleitet haben.
5. **Reproduzieren und eingrenzen:** Verdächtiges Verhalten mit einer kleinen Zahl von Wiederholungen bestätigen. Bei Timing-Fragen Baseline, Streuung und mögliche Cache-/Netzwerkeffekte erfassen.
6. **Bereinigen:** Testinhalte, Dateien, Jobs und Berechtigungsänderungen entfernen oder auf den Ausgangszustand zurücksetzen.

Für XSS den tatsächlichen DOM- und Ausgabekontext untersuchen; ein blockiertes Skript kann auf eine zusätzliche CSP-Barriere hinweisen, während unsicheres HTML weiterhin vorliegt. Für Injection sind Fehlerfreiheit und unauffällige Antwortzeiten allein kein Beweis für parametrisierte Abfragen. Für Zufallswerte liefert eine kleine Stichprobe Hinweise auf Muster, aber keinen Nachweis kryptographischer Entropie. Konfigurations- oder Codeeinsicht ergänzt solche Prüfungen, sofern verfügbar. Einschränkungen bleiben im Ergebnis sichtbar.

## 4. Ergebnisse getrennt von Findings führen

| Status | Bedeutung |
| --- | --- |
| `BESTANDEN` | Die festgelegten Prüfschritte liefern im dokumentierten Umfang das sichere Ergebnis; der Kontrollfall funktioniert. |
| `FEHLGESCHLAGEN` | Eine reproduzierbare Abweichung vom sicheren Ergebnis ist belegt. Ein Finding verweist auf den Testlauf. |
| `BLOCKIERT` | Der Test ist relevant, aber eine Voraussetzung fehlt oder eine technische Grenze verhindert die Durchführung. Grund und nächster Schritt angeben. |
| `NICHT_GETESTET` | Der relevante Test wurde noch nicht durchgeführt. |
| `NICHT_ANWENDBAR` | Die betreffende Funktion oder technische Voraussetzung existiert im geprüften System nicht. Begründung angeben. |

Pro Ausführung einen eigenen Datensatz mit Test-ID, Build, Endpunkt, Zeitpunkt, Identität und Ergebnis führen. Ein Test kann je nach Rolle oder Endpunkt mehrere Ausführungen haben. Ein Finding kann mehrere fehlgeschlagene Ausführungen zusammenführen. [Ergebnisvorlage](templates/test-result.md) und [Finding-Vorlage](templates/finding.md) trennen diese Zwecke.

Abdeckung als Anzahl der Ausführungen je Status und als Anteil geprüfter relevanter Test-/Endpunkt-/Rollen-Kombinationen berichten. `BLOCKIERT` und `NICHT_GETESTET` zählen nicht als bestanden. Nicht anwendbare Tests separat ausweisen. Ein hoher Abdeckungswert sagt ohne klaren Nenner und Testumfang wenig aus.

## 5. Nachweise und Priorität

Belege enthalten die kleinstmögliche reproduzierbare Request-/Response-Sequenz, Rollen-/Besitzverhältnisse und den relevanten Zustand vor und nach dem Test. Passwörter, aktive Sessions, Reset-Token und personenbezogene Daten in geteilten Berichten schwärzen. Vollständige Rohbelege nur im für das Projekt vorgesehenen geschützten Ablageort führen; im öffentlichen Repo bleiben synthetische Beispiele.

Den Schweregrad aus Voraussetzungen und belegter Auswirkung ableiten. Fehlendes Rate-Limiting, ein Cookie-Flag oder eine umgehbare UI-Sperre haben keinen universellen Schweregrad. Falls CVSS verwendet wird, Version, Score, vollständigen Vektor und die Begründung der Metriken angeben. Geschäftsauswirkung, erreichbare Daten, betroffene Mandanten und Behebungspriorität zusätzlich beschreiben. Grundlage ist die [FIRST CVSS v4.0-Spezifikation](https://www.first.org/cvss/v4.0/specification-document); bei einem vereinbarten v3.1-Verfahren dieses ausdrücklich kennzeichnen.

## 6. Behebung erneut prüfen

Den ursprünglichen Nachweis am behobenen Build wiederholen, den positiven Kontrollfall erneut ausführen und relevante verwandte Endpunkte prüfen. Im Ergebnis alten und neuen Build, Datum und neue Belege verknüpfen. Eine Änderung am Frontend schließt ein API-Berechtigungsproblem erst, wenn der Server den unerlaubten Zugriff tatsächlich verhindert.

## Quellen

- [OWASP WSTG v4.2: Testgrundsätze und Grenzen](https://owasp.org/www-project-web-security-testing-guide/v42/0-Foreword/)
- [OWASP WSTG v4.2: Web Application Security Testing](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/)
- [FIRST: CVSS v4.0](https://www.first.org/cvss/v4.0/specification-document)
