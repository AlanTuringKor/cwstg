# 07 · Suche und Filter

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Suchbegriffe und Filter dürfen weder Abfragen verändern noch fremde Datensätze oder ausführbaren Inhalt offenlegen. Auch gültige Suchanfragen müssen innerhalb vereinbarter Ressourcenbudgets bleiben.

## Voraussetzungen

- Zwei Testkonten A/B mit getrennten Datensätzen; bei Mandantenbetrieb zusätzlich getrennte Testmandanten. Öffentliche, private und archivierte Treffer mit eindeutigen Markierungen vorbereiten.
- Eingabeformate, unterstützte Suchsyntax, Sortierfelder und Größenlimits dokumentieren. Backendtyp aus Architekturinformationen bestätigen, soweit zugänglich.
- Für Ressourcenprüfungen maximale Laufzeit, Anfragezahl, Parallelität und Abbruchschwellen mit dem Betrieb festlegen. Ohne Budget nur Konfiguration und einzelne kleine Grenzfälle prüfen.

## Testfälle

### CWSTG-07-01 — Suchbegriffe und Treffer sicher darstellen

**Referenzen:** [WSTG-v42-INPV-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/01-Testing_for_Reflected_Cross_Site_Scripting), [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting), [WSTG-v42-CLNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting).

**Prüfschritte:**

1. Einen eindeutigen Marker mit HTML-Sonderzeichen in Suchbegriff, Filterbezeichnung und eigenen durchsuchbaren Datensatz einfügen. Darstellung in Ergebnissen, Hervorhebungen, Autovervollständigung und Verlauf verfolgen.
2. Den tatsächlich erreichten HTML-, Attribut- oder DOM-Kontext untersuchen. In Testbrowsern einen darauf abgestimmten harmlosen Ausführungsmarker verwenden; keine externen Datenübertragungen.
3. Gespeicherte Suchbegriffe und Treffer als Konto B oder freigegebene Moderationsrolle öffnen; Dekodierung beim erneuten Rendern prüfen.

**Sicheres Ergebnis:** Text bleibt Text; erlaubtes Rich-Text-Markup wird für den jeweiligen Kontext bereinigt. Auch nach Hervorhebung oder späterem Abruf entsteht kein ausführbarer DOM-Inhalt. Ein ausbleibender Dialog allein reicht als Nachweis nicht aus.

**Belege:** Eingabe, HTTP-Antwort, resultierender DOM-Ausschnitt, Browserkontext und gegebenenfalls CSP-Meldungen.

**Abhilfe:** Kontextgerechte Ausgabe-Kodierung, sichere DOM-APIs wie `textContent` und geprüfte Bereinigung für bewusst erlaubtes HTML einsetzen. CSP ergänzt diese Maßnahmen.

### CWSTG-07-02 — Datenbank- und Suchabfragen gegen Injection absichern

**Referenzen:** [WSTG-v42-INPV-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection); ergänzend [OWASP NoSQL Security](https://cheatsheetseries.owasp.org/cheatsheets/NoSQL_Security_Cheat_Sheet.html) für NoSQL und strukturierte Suchabfragen.

**Prüfschritte:**

1. Für einen bekannten Testdatensatz eine gültige Abfrage mit erwarteter Treffermenge aufzeichnen. Suchtext, Filterwerte, Feldnamen und Sortierung getrennt untersuchen.
2. Pro Parameter einen passenden Sonderzeichen- oder Typwechsel testen, etwa String statt Objekt und umgekehrt. Nur vorhandene Backendfunktionen prüfen; keine beliebigen Datenänderungen oder systemweiten Zeitverzögerungen auslösen.
3. Gezielte Wahr/Falsch-Vergleiche gegen die vorbereiteten Datensätze durchführen. Für NoSQL prüfen, ob vom Client gelieferte Operatorobjekte die vorgesehene Gleichheitsprüfung ersetzen; bei Lucene/Elasticsearch zwischen dokumentierter Suchsyntax und unerlaubter DSL-Manipulation unterscheiden.
4. Wenn Quellcodezugriff besteht, die Trennung von Werten und Abfragestruktur überprüfen. Ein ORM kann ebenfalls unsichere Rohabfragen ausführen.

**Sicheres Ergebnis:** Eingaben beeinflussen nur die ausdrücklich vorgesehene Suche. Sie umgehen weder Filter noch Berechtigungen. Fehlende Fehlermeldungen oder unveränderte Laufzeiten beweisen keine Injection-Sicherheit.

**Belege:** Kontroll- und Variantenanfragen, erwartete/tatsächliche Treffer-IDs und gegebenenfalls Abfrageaufbau ohne Geheimnisse.

**Abhilfe:** Werte parametrisieren; Feldnamen, Sortierrichtung und Operatoren auf serverseitige Positivlisten abbilden. Keine frei gelieferten Abfrageobjekte oder Skripte übernehmen.

### CWSTG-07-03 — Teure Suchanfragen begrenzen

**Referenzen:** [WSTG-v42-BUSL-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/07-Test_Defenses_Against_Application_Misuse); ergänzend [Elasticsearch: Regexp query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-regexp-query).

**Prüfschritte:**

1. Unterstützte Wildcard-, Regex-, Sortier- und Aggregationsfunktionen auf einem kleinen Testbestand inventarisieren. Regex-Engine und Such-Engine unterscheiden; nicht jede Regex-Engine verwendet Backtracking.
2. Nacheinander eine normale Abfrage und vereinbarte Grenzfälle für Länge, Operatorzahl oder Komplexität senden. Anfragezahl, maximale Dauer und Timeout vorab begrenzen; Parallelität zunächst eins.
3. Antwortzeit und, falls verfügbar, CPU, Speicher und Query-Metriken vergleichen. Bei Timeout, Ressourcenwarnung oder vereinbarter Latenzschwelle abbrechen; Lastprüfungen separat planen.

**Sicheres Ergebnis:** Kosten werden durch geeignete Komplexitäts-, Laufzeit- und Ergebnislimits begrenzt. Eine langsame Einzelantwort ist ein Untersuchungshinweis; ein DoS-Nachweis braucht reproduzierbare Auswirkungen und Kontext.

**Belege:** Abfrageparameter, Datensatzgröße, Budgets, Messwerte und Abbruchgrund.

**Abhilfe:** Eingabelänge und teure Operatoren begrenzen, Query-Timeouts sowie Ressourcenlimits durchsetzen und geeignete Indizes nutzen. Limits müssen zur eingesetzten Engine passen.

### CWSTG-07-04 — Mehrdeutige Parameter und Operatoren behandeln

**Referenzen:** [WSTG-v42-INPV-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/04-Testing_for_HTTP_Parameter_Pollution), [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation).

**Prüfschritte:**

1. Doppelte Parameter wie `q=alpha&q=beta`, Arrays statt Einzelwerten und widersprüchliche Filter an Proxy und API senden.
2. Erlaubte Sonderzeichen, Wildcards und Boolesche Operatoren mit der dokumentierten Syntax vergleichen. Sortierfelder und Mandantenfilter gezielt variieren.
3. Prüfen, ob Gateway, Anwendung und Cache dieselbe Interpretation verwenden und Sicherheitsfilter unverändert bleiben.

**Sicheres Ergebnis:** Mehrdeutige Eingaben werden eindeutig verarbeitet oder abgelehnt. Unterstützte Suchoperatoren sind zulässig, solange sie weder Berechtigungen noch Kostenlimits umgehen.

**Belege:** Rohparameter einschließlich Reihenfolge und Typen, interpretierte Filter und Treffervergleich.

**Abhilfe:** Schema und Mehrfachwert-Regeln festlegen, Eingaben einmal eindeutig normalisieren und serverseitige Sicherheitsfilter unabhängig vom Suchausdruck anwenden.

### CWSTG-07-05 — Treffer, Metadaten und Fehler auf Offenlegung prüfen

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References), [WSTG-v42-ERRH-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/01-Testing_For_Improper_Error_Handling).

**Prüfschritte:**

1. Die Markierungen privater Datensätze von A als B, anonym und aus einem anderen Testmandanten suchen.
2. Trefferlisten, Vorschauen, Gesamtzahlen, Facetten, Vorschläge und Exporte prüfen; auch nicht sichtbare API-Felder berücksichtigen.
3. Einen ungültigen Filter senden und Fehler auf Stacktraces, Zugangsdaten oder interne Abfragen prüfen. Cacheantworten nach einem Kontowechsel vergleichen.

**Sicheres Ergebnis:** Nur freigegebene Datensätze und Felder erscheinen; Metadaten verraten keine geschützten Inhalte. Technische IDs oder Timing-Header sind für sich genommen kein Finding; die konkrete Offenlegung zählt.

**Belege:** Rollen- und Eigentümermatrix, markierte Treffer/Felder, Fehlerantwort und Cachekontext.

**Abhilfe:** Berechtigungen bereits in der Suchabfrage anwenden, auch Aggregationen und Vorschläge filtern, geschützte Antworten korrekt cachen und externe Fehlermeldungen begrenzen.

### CWSTG-07-06 — Such- und Pagingbudgets durchsetzen

**Referenzen:** [WSTG-v42-BUSL-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/05-Test_Number_of_Times_a_Function_Can_Be_Used_Limits), [Pagination](16-pagination.md).

**Prüfschritte:**

1. Konfigurierte Seiten-, Abfrage- und Ratenlimits für anonyme Nutzung, Konto und API-Schlüssel erfassen.
2. Mit einem Testkonto eine vorab begrenzte Folge normaler Abfragen senden und die vereinbarte Grenze knapp prüfen. Tiefe Seiten nur im festgelegten Datensatz und Budget abrufen.
3. Drosselung, Wiederaufnahme und Kosten pro Anfrage beobachten; bei Fehlerhäufung oder Betriebswarnung stoppen.

**Sicheres Ergebnis:** Vereinbarte Nutzungsgrenzen schützen die Ressourcen; Ablehnungen und Wiederaufnahme sind kontrolliert. `429` ist ein möglicher Mechanismus und kein universelles Muss.

**Belege:** Anfragefolge, Identitätskontext, Limitkonfiguration und Messwerte.

**Abhilfe:** Kostenabhängige Quoten, maximale Seitengrößen und begrenzte gleichzeitige Abfragen durchsetzen. Cacheeinträge nach Berechtigungskontext trennen.

## Quellen

- Die Testfälle verlinken die jeweiligen OWASP-WSTG-Szenarien in Version 4.2.
- [OWASP NoSQL Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/NoSQL_Security_Cheat_Sheet.html)
- [Elasticsearch: Regexp query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-regexp-query)
