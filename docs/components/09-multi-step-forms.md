# 09 · Formulare und mehrstufige Abläufe

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Der Server setzt Geschäftsregeln, Berechtigungen und zulässige Zustandsübergänge bei jedem Schritt durch. Manipulierte, wiederholte oder gleichzeitig eintreffende Anfragen dürfen keine unzulässigen Nebenwirkungen erzeugen.

## Voraussetzungen

- Einen vollständigen gültigen Ablauf, erlaubte Übergänge, Abbruchregeln und unveränderliche Geschäftsbedingungen dokumentieren, etwa Gesamtbetrag, Empfänger oder erforderliche Freigabe.
- Konten A/B, getrennte Vorgänge und gegebenenfalls Testmandanten vorbereiten. Zahlungs- und Versandaktionen über Sandboxsysteme oder Test-Doubles abwickeln.
- Zustand und Nebenwirkungen vor/nach einer Anfrage lesbar machen. Für Paralleltests zunächst genau zwei Anfragen und einen Testvorgang vereinbaren.

## Testfälle

### CWSTG-09-01 — Zustandsänderungen gegen CSRF schützen

**Referenzen:** [WSTG-v42-SESS-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery); ergänzend [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

**Prüfschritte:**

1. Für Zwischen- und Abschlussschritte feststellen, ob der Browser Authentifizierungsdaten automatisch mitsendet. Bei expliziten Bearer-Headern den tatsächlichen Übergabeweg untersuchen.
2. Fehlendes, falsches und aus einer anderen Testsitzung stammendes CSRF-Token getrennt prüfen.
3. Aus einem kontrollierten fremden Origin die vom Browser tatsächlich erlaubten Formularanfragen auslösen. Unterstützte einfache Content-Types, Origin-/Referer-Prüfung und CORS-Preflight berücksichtigen.
4. Vorgangszustand anschließend über einen unabhängigen Abruf prüfen. Ein blockiertes Lesen der Antwort beweist nicht, dass die Aktion verhindert wurde.

**Sicheres Ergebnis:** Eine fremde Seite kann keine unbeabsichtigte Zustandsänderung veranlassen. JSON, `SameSite` oder ein benutzerdefinierter Header sind nur mit passenden serverseitigen Regeln wirksame Schutzmaßnahmen.

**Belege:** Browser-PoC, übertragene Header/Cookies, Schutzmechanismus und Vorher-/Nachherzustand.

**Abhilfe:** Bewährten Frameworkschutz einsetzen; Token oder streng geprüfte Origin-/Header-Regeln zum Authentifizierungsmodell passend umsetzen. CORS und akzeptierte Content-Types konsistent beschränken.

### CWSTG-09-02 — Versteckte und abgeleitete Felder prüfen

**Referenzen:** [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation), [WSTG-v42-BUSL-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/03-Test_Integrity_Checks).

**Prüfschritte:**

1. Eine gültige Anfrage aufzeichnen und Felder nach nutzereditierbaren und serverseitig abgeleiteten Werten trennen.
2. Jeweils ein Feld ändern, etwa `total`, `discount`, `recipientId`, `role` oder einen deaktivierten Formulareintrag. Zulässige und unzulässige Änderungen vergleichen.
3. Validierung über direkte API-Anfragen umgehen und berechnete Endwerte sowie tatsächliche Nebenwirkungen abrufen.

**Sicheres Ergebnis:** Der Server berechnet verbindliche Werte selbst und prüft editierbare Werte gegen Geschäftsregeln und Berechtigungen. Ein deaktiviertes Feld ist keine Sicherheitsgrenze.

**Belege:** Original-/Variantenanfrage, geltende Regel und gespeicherte Endwerte.

**Abhilfe:** Eingabeschemas auf erlaubte Felder beschränken und Preise, Rollen, Eigentümer sowie andere verbindliche Werte aus vertrauenswürdigen Daten ableiten.

### CWSTG-09-03 — Reihenfolge und Freigaben erzwingen

**Referenzen:** [WSTG-v42-BUSL-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/06-Testing_for_the_Circumvention_of_Work_Flows).

**Prüfschritte:**

1. Mit einem frischen Testvorgang direkt einen späteren Schritt oder den Abschluss aufrufen, ohne notwendige Vorbedingungen zu erfüllen.
2. Einen erledigten Schritt nachträglich verändern und prüfen, ob davon abhängige Bestätigungen ihre Gültigkeit verlieren.
3. Abbruch und Wiederaufnahme testen; prüfen, ob Reservierungen, Gutschriften oder andere vorläufige Effekte korrekt zurückgenommen werden.

**Sicheres Ergebnis:** Ausschließlich erlaubte Übergänge und gültige Freigaben ermöglichen den Abschluss. Änderungen an Betrag oder Empfänger entwerten dazugehörige Bestätigungen entsprechend der Fachregel.

**Belege:** Anfragefolge, Zustandsübergänge, Freigabestatus und Nebenwirkungen.

**Abhilfe:** Einen serverseitig verbindlichen Zustandsautomaten und atomare Übergangsprüfungen verwenden; abhängige Freigaben an die bestätigten Vorgangsdaten binden.

### CWSTG-09-04 — Wiederholung und Idempotenz prüfen

**Referenzen:** [WSTG-v42-BUSL-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/05-Test_Number_of_Times_a_Function_Can_Be_Used_Limits).

**Prüfschritte:**

1. Einen Testvorgang abschließen und dieselbe Abschlussanfrage einmal wiederholen. Aufträge, Buchungen und externe Sandboxaufrufe zählen.
2. Falls ein Idempotenzschlüssel vorgesehen ist, denselben Schlüssel mit identischem und danach verändertem Inhalt prüfen.
3. Einen bereits abgeschlossenen Vorgang mit neuem Schlüssel erneut adressieren; zusätzlich die Trennung der Schlüssel zwischen Konten/Vorgängen prüfen.

**Sicheres Ergebnis:** Eine fachlich einmalige Aktion wirkt genau einmal. Wiederholungen dürfen dasselbe Ergebnis zurückgeben oder kontrolliert abgelehnt werden; ein weiterer erfolgreicher HTTP-Status ist für sich kein Duplikat.

**Belege:** Vorgangs-/Schlüsselzuordnung, Antwortfolge und Anzahl tatsächlicher Nebenwirkungen.

**Abhilfe:** Idempotenzschlüssel an Akteur, Zweck und Anfrageinhalt binden; zusätzlich fachliche Eindeutigkeit und dauerhafte Deduplizierung im Transaktionsmodell durchsetzen.

### CWSTG-09-05 — Gleichzeitigen Abschluss atomar verarbeiten

**Referenzen:** [WSTG-v42-BUSL-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/04-Test_for_Process_Timing).

**Prüfschritte:**

1. Einen Testvorgang unmittelbar vor einer einmaligen Aktion vorbereiten. Genau zwei Abschlussanfragen mit demselben Vorgang nahezu gleichzeitig senden.
2. Endzustand, Buchungen, Bestand und externe Sandboxaktionen prüfen; ein Duplikat kann auch bei einer abgelehnten HTTP-Antwort entstanden sein.
3. Nach dem vereinbarten Versuch stoppen und Testeffekte bereinigen. Weitere Wiederholungen nur innerhalb des festgelegten Budgets durchführen.

**Sicheres Ergebnis:** Gleichzeitige Anfragen verletzen weder Eindeutigkeit noch Bestands-/Betragsgrenzen. Zustandsprüfung und Änderung bilden eine atomare Operation; externe Effekte sind ebenfalls dedupliziert oder kompensiert.

**Belege:** Zeitachse beider Anfragen und zugehörige Transaktions-/Auftrags-IDs.

**Abhilfe:** Datenbank-Constraints, geeignete Transaktionen oder Versionsprüfungen einsetzen; externe Effekte über ein robustes Outbox-/Deduplizierungsverfahren absichern.

### CWSTG-09-06 — Vorgangsbesitz und verbindlichen Zwischenzustand prüfen

**Referenzen:** [WSTG-v42-BUSL-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/03-Test_Integrity_Checks), [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References).

**Prüfschritte:**

1. Vorgänge für A und B öffnen. Vorgangs-ID oder clientseitigen Zustand zwischen beiden Sitzungen austauschen und jeden Schritt getrennt aufrufen.
2. Im eigenen Vorgang ein veraltetes oder manipuliertes Zustandspaket einreichen; prüfen, ob bereits bestätigte Daten überschrieben werden.
3. Eine Integritätssignatur, falls vorhanden, mit einem unveränderten alten Paket und im falschen Vorgang prüfen. Eine gültige Signatur beweist weder Aktualität noch Berechtigung.

**Sicheres Ergebnis:** Jeder Zugriff prüft Akteur, Mandant, Vorgang und aktuellen Zustand. Signierte Clientdaten unterliegen denselben Besitz-, Ablauf- und Wiederholungsregeln wie serverseitige Daten.

**Belege:** Akteur-/Vorgangsmatrix, Paketversionen und nachfolgender Zustand.

**Abhilfe:** Verbindlichen Zustand serverseitig führen oder signierte Zustände vollständig an Kontext und Version binden; Berechtigungen bei jedem Übergang prüfen.

### CWSTG-09-07 — Ablauf und Entwertung von Schrittnachweisen prüfen

**Referenzen:** [WSTG-v42-BUSL-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/06-Testing_for_the_Circumvention_of_Work_Flows).

**Prüfschritte:**

1. Gültigkeitsdauer und Zweck von Schritttoken beziehungsweise Freigaben dokumentieren. In einer Testkonfiguration einen kurzen Ablauf verwenden.
2. Verwendung vor und nach Ablauf, nach Abschluss/Abbruch und in einem anderen Testvorgang prüfen.
3. Bei verlangter Einmaligkeit einen bereits konsumierten Nachweis erneut senden. Wiederverwendbare CSRF-Token davon unterscheiden.

**Sicheres Ergebnis:** Nachweise gelten nur für den vorgesehenen Akteur, Vorgang, Zweck und Zeitraum. Einmaligkeit wird dort durchgesetzt, wo sie fachlich erforderlich ist; nicht jedes Formular- oder CSRF-Token muss pro Anfrage wechseln.

**Belege:** Gültigkeitsregeln, Zeitstempel, Lebenszyklus und geprüfte Zustandsänderung.

**Abhilfe:** Ablauf und Verbrauch serverseitig prüfen, notwendige Einmaligkeit atomar umsetzen und Nachweise bei relevanten Vorgangsänderungen entwerten.

### CWSTG-09-08 — Fachliche Ereignisse nachvollziehbar protokollieren

**Referenzen:** Ergänzende Prüfung nach [OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).

**Prüfschritte:**

1. Einen erlaubten Übergang, eine abgelehnte Manipulation und eine Wiederholung ausführen.
2. Mit freigegebenem Logzugriff Akteur, Vorgang, Zeit, Entscheidung und Korrelations-ID den Anfragen zuordnen.
3. Prüfen, ob Passwörter, vollständige Token oder unnötige personenbezogene Inhalte in Logs landen und ob Meldungen die vereinbarte Überwachung erreichen.

**Sicheres Ergebnis:** Sicherheitsrelevante Entscheidungen sind nachvollziehbar, sensible Werte werden angemessen ausgelassen oder redigiert. Fehlender Logzugriff wird als Einschränkung dokumentiert.

**Belege:** Redigierte, korrelierte Protokollauszüge und gegebenenfalls Monitoringereignis.

**Abhilfe:** Strukturierte Ereignisse mit konsistenter Korrelation, Zugriffsschutz und passenden Aufbewahrungsregeln einführen; vollständige Geheimnisse nicht protokollieren.

## Quellen

- Die Testfälle verlinken die jeweiligen OWASP-WSTG-Szenarien in Version 4.2.
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
