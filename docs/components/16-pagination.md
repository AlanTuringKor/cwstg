# 16 · Pagination und Infinite Scroll

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Listen liefern ausschließlich berechtigte Datensätze und verursachen begrenzte Arbeit je Anfrage und Nutzer. Seitenparameter, Cursor, Cachevarianten und automatisches Nachladen dürfen weder Rechte umgehen noch unbegrenzte Datenbank-, Speicher- oder Netzwerkkosten auslösen.

## Voraussetzungen

- Kleine deterministische Testdaten mit öffentlichen, privaten, archivierten und gegebenenfalls mandantengebundenen Einträgen; Testkonten A und B.
- Bekannte Grenzwerte für Seitengröße, Suchbereich, Laufzeit und Anfragerate. In einer Testumgebung können Grenzwerte für die Prüfung vorübergehend niedrig eingestellt werden.
- Ein festes Messbudget, beispielsweise höchstens zehn einzelne Anfragen mit maximal einer Anfrage pro Sekunde für Grenzwertproben. Parallelität ist ein gesondert vereinbarter Test mit eigener Obergrenze; keine automatische Steigerung bis zum Ausfall.
- Abbruch bei unerwarteten 5xx, überschrittenem Latenz-/Ressourcengrenzwert oder wachsender Warteschlange. Ohne messbare Betriebsgrenzen nur Konfiguration und kleine funktionale Fälle prüfen; Lastverhalten als ungeprüft dokumentieren.

## Testfälle

### CWSTG-16-01 — Seitengröße und tiefe Offsets

**Referenzen:** [OWASP API4:2023](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/); [PostgreSQL LIMIT/OFFSET](https://www.postgresql.org/docs/18/queries-limit.html). CWSTG-Erweiterung für Ressourcenverbrauch.

**Prüfschritte:**

1. Eine normale Listenanfrage aufzeichnen und Anzahl, Größe und Laufzeit der Antwort erfassen.
2. Mit dem kleinen Testdatenbestand Werte unmittelbar unter, an und oberhalb der vereinbarten Seitengrößen-/Offsetgrenze prüfen. Keine willkürlich millionenfachen Werte oder unbeschränkten Exportanfragen verwenden.
3. Falls verfügbar Queryplan, gelesene Zeilen und Laufzeit beobachten. Derselbe kleine Antwortumfang kann unterschiedlich teure Datenbankarbeit verdecken.

**Sicheres Ergebnis:** Serverseitige Grenzen beschränken gelieferte Daten und Verarbeitungsaufwand; Überschreitungen werden kontrolliert abgewiesen oder dokumentiert begrenzt. Offsetpagination ist zulässig, wenn sie das festgelegte Budget einhält. Ein Cursor allein beweist keine effiziente Abfrage.

**Belege:** Grenzwertkonfiguration, wenige Kontroll-/Grenzwertanfragen und gegebenenfalls Queryplan.

**Abhilfe:** Seitengröße und Querykosten begrenzen, geeignete Indizes setzen und für tiefe Seiten bei Bedarf Seek-/Cursorverfahren verwenden.

### CWSTG-16-02 — Mehrfach ausgelöstes Nachladen

**Referenzen:** [OWASP DoS-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html). CWSTG-Erweiterung für Client- und Serverrobustheit.

**Prüfschritte:**

1. In der Testumgebung eine langsame einzelne Listenantwort simulieren und währenddessen mehrmals denselben Scroll-/Nachladen-Trigger auslösen.
2. Prüfen, ob der Client die gleiche Seite mehrfach anfordert und veraltete Antworten nach Filterwechsel noch anzeigt.
3. Eine kleine ausdrücklich vereinbarte Zahl paralleler Anfragen prüfen, sofern dieser Test vorgesehen ist. Antwortreihenfolge, Abbruch und Rückstau beobachten; danach normale Nutzung kontrollieren.

**Sicheres Ergebnis:** Der Client verhindert vermeidbare Duplikate und verwirft veraltete Ergebnisse. Servergrenzen wirken unabhängig vom Client; eine Warteschlange wächst nicht unbeschränkt. Fehlendes Client-Entprellen wird anhand der tatsächlichen serverseitigen Wirkung bewertet.

**Belege:** Browser-Netzwerkfolge, Filterzustand und Messwerte innerhalb des Budgets.

**Abhilfe:** Laufende Anfragen zusammenführen/abbrechen, Ergebnisse an den aktuellen Filter binden und serverseitige Parallelitäts-/Arbeitsgrenzen setzen.

### CWSTG-16-03 — Cachevarianten und private Listen

**Referenzen:** [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html); [WSTG-v42-ATHN-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/06-Testing_for_Browser_Cache_Weaknesses) für Browsercache. Gemeinsame Cachevarianten sind eine ergänzende Prüfung.

**Prüfschritte:**

1. Eine private markierte Seite als A über den echten Proxy-/CDN-Pfad abrufen; URL, Filter, Cookie-/Authentifizierungskontext und Cachetreffer erfassen.
2. Dieselbe Anfrage als B und ohne Sitzung wiederholen. Danach nur dokumentierte Darstellungsvarianten wie Sprache, Seitennummer und Sortierung einzeln verändern.
3. Prüfen, ob die Variante im tatsächlichen Cachekey berücksichtigt oder das Caching ausgeschlossen wird. Tests nur mit isolierten Testressourcen durchführen.

**Sicheres Ergebnis:** Konten und Mandanten erhalten ausschließlich ihre eigenen Daten; öffentliche Cachevarianten bleiben korrekt getrennt. `Vary: Authorization` allein ist keine allgemeine Lösung, insbesondere bei Cookieauthentifizierung oder abweichenden CDN-Regeln. `private` erlaubt Browsercache; `no-store` verbietet HTTP-Caches die Speicherung. Die tatsächliche Cachekonfiguration muss dazu passen.

**Belege:** Abruffolge mit Benutzerkontext, Markierung, Cacheheadern und tatsächlicher Antwort.

**Abhilfe:** Private Listen vom gemeinsamen Cache ausschließen oder eine geprüfte autorisierte Cachearchitektur verwenden; alle darstellungsrelevanten Varianten konsistent behandeln.

### CWSTG-16-04 — Ungültige Parameter und Cursor

**Referenzen:** [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation).

**Prüfschritte:**

1. Kleine ungültige Werte wie `limit=-1`, `offset=-1`, `limit=abc`, doppelte Parameter und einen abgeschnittenen Cursor einzeln senden.
2. Prüfen, ob unterschiedliche Parser widersprüchliche Werte akzeptieren. Fehlende Parameter mit den dokumentierten Defaults vergleichen.
3. Kontrollieren, dass Fehler keinen Rückfall auf eine unbegrenzte Liste auslösen und keine internen Querydetails offenlegen.

**Sicheres Ergebnis:** Der Server akzeptiert ausschließlich den dokumentierten Typ-/Wertebereich oder normalisiert ihn eindeutig. Ungültige Eingaben werden kontrolliert behandelt; Seitengrenzen gelten auch in Fehlerpfaden. Ein bestimmter Statuscode allein genügt nicht.

**Belege:** Parameterfall, effektiv verarbeiteter Wert und Umfang der Antwort.

**Abhilfe:** Ein eindeutiges Schema am Server erzwingen, doppelte/mehrdeutige Werte behandeln und Grenzen nach dem Parsing prüfen.

### CWSTG-16-05 — Rechte über Seiten, Cursor und Zähler

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References).

**Prüfschritte:**

1. Private Testeinträge von A zwischen sichtbaren Datensätzen anlegen; Listen als B auf erster, mittlerer und letzter Testseite vergleichen.
2. Einen bekannten Cursor von A mit B bzw. einem anderen Testmandanten verwenden; Filter und Sortierung ändern und einen zuvor gültigen Cursor nach Rechteentzug wiederholen.
3. Neben Zeilen auch `total`, `hasNextPage`, Facetten und Archive auf unerlaubte Hinweise prüfen.

**Sicheres Ergebnis:** Jede Anfrage wird anhand aktueller Rechte ausgewertet. Autorisierung begrenzt den Ergebnisraum vor Seitenauswahl und Aggregation; Seiten und Zähler verraten keine fremden Daten. Opaque oder signierte Cursor ersetzen keine Autorisierung.

**Belege:** Erwartete Sichtbarkeitsmatrix, bekannte Datensätze und Cursorverwendung mit redigierten Werten.

**Abhilfe:** Mandanten-/Objektfilter in die Abfrage und ihre Zähler übernehmen; Cursorkontext, Filter und Rechte konsistent prüfen.

### CWSTG-16-06 — Kontingente und Rücknahme der Sperre

**Referenzen:** [WSTG-v42-BUSL-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/05-Test_Number_of_Times_a_Function_Can_Be_Used_Limits).

**Prüfschritte:**

1. In einer Testkonfiguration ein kleines dokumentiertes Seiten-/Arbeitskontingent einstellen und innerhalb des Messbudgets erreichen.
2. Eine zusätzliche Anfrage senden. Mit einem weiteren Testkonto oder Testschlüssel prüfen, ob die dokumentierte Kontingentzuordnung tatsächlich gilt; keine IP-Rotation verwenden.
3. Rücksetzzeit abwarten und eine reguläre Anfrage wiederholen. Falls `Retry-After` vorhanden ist, Verhalten damit abgleichen.

**Sicheres Ergebnis:** Das vorgesehene Kontingent wird auch über alternative Listen-/Exportwege eingehalten. Ablehnung oder Drosselung begrenzen tatsächliche Arbeit; nach Freigabe ist normale Nutzung möglich. Ein fehlendes `429` ist allein kein Befund, wenn gleichwertige Grenzen greifen.

**Belege:** Testkontingent, Zeitfolge, akzeptierte/abgewiesene Arbeit und Erholung.

**Abhilfe:** Identitätsbezogene Kontingente mit übergreifenden Ressourcenlimits kombinieren und Rücksetzverhalten dokumentieren.

### CWSTG-16-07 — Datenbankarbeit, Speicher und stabile Reihenfolge

**Referenzen:** [PostgreSQL LIMIT/OFFSET](https://www.postgresql.org/docs/18/queries-limit.html); [OWASP API4:2023](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/). CWSTG-Erweiterung für Implementierungsprüfung.

**Prüfschritte:**

1. In Code/Queryplan prüfen, ob die Anwendung erst den gesamten Datenbestand lädt und danach lokal eine Seite auswählt. Auch teure Zähler und Joins einbeziehen.
2. Mit kleinen Fixtures und Monitoring den Aufwand normaler Seiten vergleichen; keine unbeschränkten Datensätze materialisieren lassen.
3. Gleiche Sortierwerte sowie eine einzelne Einfügung/Löschung zwischen zwei Seiten prüfen. Stabile Sortierung und dokumentierte Konsistenzregeln kontrollieren.

**Sicheres Ergebnis:** Arbeit und Speicher bleiben im vorgesehenen Budget; Datenbank und Autorisierung begrenzen die Auswahl frühzeitig. Eine kleine begrenzte Antwort muss nicht gestreamt werden. Doppelte oder übersprungene Zeilen sind zunächst ein Konsistenzproblem; Sicherheitswirkung und Ressourcenrisiko getrennt belegen.

**Belege:** Query-/Codeausschnitt, Messwerte und erwartete Reihenfolge des Testbestands.

**Abhilfe:** Frühzeitig filtern und paginieren, passende Indizes sowie Query-/Speicherlimits einsetzen und eine eindeutige Sortierung, etwa Zeitstempel plus ID, verwenden.

## Quellen

- [OWASP API4:2023 — Ressourcenverbrauch](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/)
- [OWASP DoS-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)
- [RFC 9111: HTTP-Caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [PostgreSQL 18: LIMIT und OFFSET](https://www.postgresql.org/docs/18/queries-limit.html)
