# 06 · Listen, Detailseiten und CRUD

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Listen-, Detail-, Änderungs-, Lösch- und Exportfunktionen müssen dieselben Objekt-, Feld- und Mandantengrenzen einhalten. Filter, Massenoperationen und Caches dürfen diese Grenzen nicht umgehen.

## Voraussetzungen

- Testkonto A und B mit bekannten eigenen Objekten; gegebenenfalls ein weiterer Mandant und eine Verwaltungsrolle.
- Dokumentierte Lese-/Schreibrechte pro Feld, Regeln für Bulkverarbeitung, Exportformate und Paginggrenzen.
- Wiederherstellbare Testdaten sowie ein festes Anfrage- und Ressourcenbudget; für Cachetests eindeutige private Testmarker.

## Testfälle

### CWSTG-06-01 — Objektzugriff und Feldsichtbarkeit

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

**Prüfschritte:**

1. Rufe ein bekanntes eigenes Objekt als A über Liste und Detail-API ab. Notiere Sollsichtbarkeit und enthaltene Felder.
2. Ersetze die Objektkennung durch die bekannte Kennung eines Objekts von B beziehungsweise eines fremden Testmandanten. Prüfe Detailpfade, Listenfilter und verschachtelte Ressourcen.
3. Wiederhole anonym und vergleiche auch Zählwerte, Vorschauen und Metadaten. Nutze bekannte Test-IDs statt wahlloser Enumeration.

**Sicheres Ergebnis:** Die Antwort enthält nur autorisierte Objekte und Felder. Auch Filter, Zählwerte und Listenmetadaten respektieren den vorgesehenen Schutzbedarf; schwer erratbare IDs ersetzen diese Prüfung nicht.

**Belege:** Objekt-/Kontenzuordnung, Sollfelder und geschwärzte Antworten in jedem Zugriffskontext.

**Abhilfe:** Autorisierungs- und Mandantenfilter bereits in die Datenabfrage einbeziehen; Antwortfelder nach Berechtigung projizieren und verschachtelte Ressourcen ebenso prüfen.

### CWSTG-06-02 — Ändern und Löschen fremder Objekte

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) · [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation)

**Prüfschritte:**

1. Zeichne eine erlaubte Änderung am eigenen Testobjekt auf. Wiederhole mit der Kennung eines kontrollierten Objekts von B.
2. Prüfe getrennt PUT, PATCH, DELETE und unterstützte Aktionsendpunkte. Verändere zusätzliche Eigentümer-, Mandanten- oder privilegierte Felder nur in separaten Varianten.
3. Lies das Ziel als berechtigtes Konto erneut aus beziehungsweise prüfe den Wiederherstellungs-/Löschzustand und mögliche Nebenwirkungen.

**Sicheres Ergebnis:** Unzulässige Änderungen und Löschungen bleiben wirkungslos, einschließlich indirekter Nebenwirkungen. Bei erlaubten Änderungen akzeptiert der Server nur die freigegebenen Felder.

**Belege:** Kontrollrequest, Testvarianten und unabhängiger Vorher-/Nachher-Zustand.

**Abhilfe:** Objekt- und Aktionsberechtigung vor dem Schreiben prüfen, erlaubte Änderungsfelder begrenzen und Eigentümer-/Mandantenwechsel als eigene autorisierte Vorgänge behandeln.

### CWSTG-06-03 — Filter-, Such- und Sortierparameter

**Referenzen:** [WSTG-v42-INPV-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection) · [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation)

**Prüfschritte:**

1. Ermittle unterstützte Parameter und ihre Datentypen anhand normaler UI-/API-Nutzung. Halte einen erlaubten Kontrollfilter fest.
2. Prüfe wenige ungültige Typen, nicht freigegebene Sortierspalten und gepaarte harmlose Abfragevarianten. NoSQL-/Such-DSL-Operatoren nur testen, wenn die tatsächliche Schnittstelle solche Strukturen verarbeitet.
3. Vergleiche Resultatmenge, Mandanten-/Objektgrenzen und Fehlerverhalten. Prüfe bei Codezugriff Wertebindung, erlaubte Operatoren und Sortierfeldzuordnung.

**Sicheres Ergebnis:** Eingaben werden als Daten oder als ausdrücklich erlaubte Filter interpretiert und erweitern weder Abfragelogik noch Zugriffsumfang. Keine Fehlermeldung ist kein Nachweis gegen Injection.

**Belege:** Kontroll-/Testabfragen, erwartete Testobjekte und bei verfügbarem Code die Abfragekonstruktion.

**Abhilfe:** Werte parametrieren und dynamische Bezeichner wie Sortierspalten aus einer festen Zuordnung wählen. Unterstützte Operatoren, Typen und Filtertiefe serverseitig begrenzen.

### CWSTG-06-04 — CSV- und Tabellenexport: Formelinterpretation

**Referenzen:** [OWASP CSV Injection](https://owasp.org/www-community/attacks/CSV_Injection)

**Prüfschritte:**

1. Speichere in eigenen Testobjekten harmlose Werte wie `=1+1` und repräsentative führende Zeichen `+`, `-`, `@`, Tabulator sowie Felder mit Separatoren, Anführungszeichen und Zeilenumbrüchen.
2. Exportiere als CSV beziehungsweise XLSX. Prüfe Rohinhalt und öffne die Datei in den tatsächlich unterstützten Tabellenprogrammen ohne externe Verbindungen oder Makros.
3. Prüfe Zelltyp, Importoptionen und gegebenenfalls erneutes Speichern/Öffnen. Eine Formelzeichenfolge in einer CSV ist nicht automatisch in jedem Programm gleich wirksam; Zahlen wie `1+1` ohne Formelpräfix sind kein verlässlicher Test.

**Sicheres Ergebnis:** Unvertrauenswürdige Textfelder bleiben in den unterstützten Importabläufen Text. CSV-Quoting schützt die Feldstruktur, verhindert aber nicht allein Formelinterpretation. Dieser Spezialfall nutzt eine OWASP-Ergänzung ohne erfundene WSTG-ID.

**Belege:** Exportbytes, verwendetes Programm und Importmodus, tatsächlicher Zelltyp beziehungsweise Formelverhalten.

**Abhilfe:** Für XLSX explizite Textzellen erzeugen. Für CSV eine anhand der unterstützten Verbraucher getestete Neutralisierungsregel einsetzen; Apostroph oder Tabulator nicht pauschal als universellen Schutz behaupten.

### CWSTG-06-05 — Paging und begrenzte Ressourcenverwendung

**Referenzen:** [OWASP API4:2023](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/) · [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation) · [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

**Prüfschritte:**

1. Ermittle normale Seitengröße und dokumentierte Maximalwerte. Prüfe Grenzwert, Grenzwert plus eins, ungültige Typen und negative Werte mit wenigen Anfragen.
2. Prüfe tiefe Seiten nur in einer geeigneten Umgebung stufenweise innerhalb des vereinbarten Budgets. Beobachte Antwortgröße, Laufzeit und soweit verfügbar Datenbank-/Speicherkosten.
3. Prüfe Cursorwechsel zwischen eigenen Testkonten sowie Objekt-/Mandantengrenzen auf Folgeseiten. Laststeigerungen erst im ausdrücklich dafür festgelegten Test durchführen.

**Sicheres Ergebnis:** Antwortgrößen und Anfragekosten bleiben im vorgesehenen Budget; Folgeseiten halten dieselben Berechtigungsregeln ein. Cursorpagination ist eine mögliche Umsetzung, aber keine universelle Sicherheitsanforderung.

**Belege:** Getestete Grenzen, Antwortgrößen, Messwerte und kontrollierte Cursor-/Kontenvarianten.

**Abhilfe:** Seitengröße, Parametertypen, Abfragekosten und Laufzeit begrenzen; passende Indizes und bei Bedarf Seek-/Cursorpagination verwenden. Vertiefung in Kapitel 16.

### CWSTG-06-06 — Bulk-Änderung und Import pro Eintrag autorisieren

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) · [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation)

**Prüfschritte:**

1. Sende einen kleinen Bulkrequest mit einem Objekt von A und einem kontrollierten Objekt von B. Prüfe getrennt zusätzliche geschützte Felder und Mandantenwechsel.
2. Prüfe endgültige Zustände aller Einträge entsprechend der dokumentierten Transaktions- oder Teilfehlerregel.
3. Falls asynchron verarbeitet wird, prüfe Jobstart, Status, Ergebnisdownload und die Behandlung zwischenzeitlich entzogener Rechte.

**Sicheres Ergebnis:** Jeder Eintrag und jedes Feld wird autorisiert. Ein erlaubtes erstes Objekt legitimiert keine weiteren Einträge; eine angenommene Jobanfrage beweist noch keine korrekte Verarbeitung.

**Belege:** Kleines Eingabeset, Ergebnisse pro Eintrag, Jobartefakte und Vorher-/Nachher-Zustand.

**Abhilfe:** Autorisierung pro Objekt auch in Bulkpfaden durchführen, sichere Jobidentität und Berechtigungssemantik festlegen und Teiländerungen eindeutig dokumentieren.

### CWSTG-06-07 — Private Antworten in Browser- und Shared Caches

**Referenzen:** [WSTG-v42-ATHN-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/06-Testing_for_Browser_Cache_Weaknesses) · [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)

**Prüfschritte:**

1. Rufe eine private Testliste als A auf und notiere Cache-Control, Vary und verfügbare Cacheindikatoren. Verwende ausschließlich eindeutige private Testmarker.
2. Rufe dieselbe URL anschließend als B und anonym über den tatsächlich vorgesehenen Cachepfad auf. Prüfe Varianten von Cookie-/Authorization-Kontext und relevante Queryparameter.
3. Prüfe zusätzlich Browsernavigation nach Logout beziehungsweise Kontowechsel. Ordne private Datenausgabe, falsch getrennte Cachevarianten und bloße Headerauffälligkeiten getrennt ein.

**Sicheres Ergebnis:** Cacheeinträge werden nicht an unberechtigte Konten ausgeliefert. `private` verbietet Shared-Caching, erlaubt aber Browser-Caching; `no-store` ist für Inhalte ohne erlaubte Speicherung passend. Vary allein ersetzt keine sichere CDN-Konfiguration.

**Belege:** Kontenfolge, eindeutige Testmarker, Antworten und Cacheindikatoren beziehungsweise Cachekonfiguration.

**Abhilfe:** Shared-Caching privater Daten gezielt ausschließen oder korrekt autorisiert trennen. Cache-Control, Cachekeys und Edgekonfiguration gemeinsam prüfen; sensible Browserkopien entsprechend dem Schutzbedarf begrenzen.

### CWSTG-06-08 — Export-, Download- und Zählendpunkte

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

**Prüfschritte:**

1. Erzeuge als A einen Export eigener kontrollierter Objekte. Vergleiche Filter, Feldumfang und Gesamtzahlen mit der normalen Listenansicht.
2. Verändere beim Start und Ergebnisabruf bekannte Objekt-, Mandanten- und Jobkennungen auf die von B. Prüfe öffentliche beziehungsweise signierte Downloadlinks nach festgelegter Ablauf-/Widerrufsregel.
3. Entziehe bei einem Testauftrag die Berechtigung zwischen Erstellung und Abruf und prüfe das dokumentierte Verhalten.

**Sicheres Ergebnis:** Exports und Summen erweitern die erlaubte Datenmenge nicht. Auftrags- und Downloadberechtigung sowie die gültige Lebensdauer von Bearerlinks sind ausdrücklich festgelegt und eingehalten.

**Belege:** Vergleich von Liste und Export, Job-/Downloadfolge, Ablaufbelege und nachgewiesene Felder ausschließlich eigener Testdaten.

**Abhilfe:** Denselben Autorisierungsfilter für Listen, Zähler und Export anwenden; Auftragsartefakte schützen und Downloadlinks mit minimalem Umfang und geeigneter Laufzeit ausstellen.

## Ergänzende Hinweise

Vertiefung: [Suche und Filter](07-search-filter.md), [Pagination](16-pagination.md) sowie [Rollen](04-roles-permissions.md). Der tatsächliche Zugriff und die tatsächlich wirksame Zustandsänderung sind die maßgeblichen Prüfergebnisse; HTTP-Statuscodes dienen als ergänzende Beobachtung.

## Quellen

- [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation)
- [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [WSTG-v42-INPV-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection)
- [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation)
- [WSTG-v42-BUSL-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/05-Test_Number_of_Times_a_Function_Can_Be_Used_Limits)
- [WSTG-v42-ATHN-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/06-Testing_for_Browser_Cache_Weaknesses)
- [OWASP CSV Injection](https://owasp.org/www-community/attacks/CSV_Injection)
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)
