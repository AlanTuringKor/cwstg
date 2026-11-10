# 05 · Adminbereich und Dashboard

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Verwaltungsfunktionen müssen auch bei direkten API-Aufrufen, Massenänderungen und Fehlersituationen geschützt bleiben. Das Dashboard darf sensible Daten nur entsprechend der Verwaltungsrolle und dem Mandanten anzeigen.

## Voraussetzungen

- Niedrig privilegiertes Testkonto und ein Verwalter mit dokumentiertem Zuständigkeitsbereich; bei Bedarf zweiter Testmandant.
- Bekannte Verwaltungsrouten, dokumentierte API-Endpunkte, zulässige Testaktionen und rücksetzbare Testdaten.
- Für Bulk-, Audit- und Konsolentests festgelegte Ausführungsgrenzen und geeignete Einblicke in Ergebnisse.

## Testfälle

### CWSTG-05-01 — Verwaltungsrouten direkt aufrufen

**Referenzen:** [WSTG-v42-CONF-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/05-Enumerate_Infrastructure_and_Application_Admin_Interfaces) · [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema)

**Prüfschritte:**

1. Ermittle Verwaltungsrouten aus Produktdokumentation, freigegebenen API-Beschreibungen, UI-Links und wenigen bekannten Pfaden.
2. Rufe dieselben Seiten und dahinterliegenden Datenendpunkte als Verwalter, niedrig privilegiertes Konto und anonym auf.
3. Prüfe direkte URLs und alternative Methoden. Unterscheide eine öffentlich ausgelieferte leere SPA-Hülle von tatsächlich offengelegten Verwaltungsdaten.

**Sicheres Ergebnis:** Nur vorgesehene Verwaltungsrollen erhalten Daten und Funktionen. Ein versteckter Link oder ein bekannter Adminpfad ist allein keine Schwachstelle; unzulässiger Zugriff darf auch hinter der UI nicht möglich sein.

**Belege:** Routen-/Rollenmatrix, Datenantworten und gegebenenfalls geschützte Kontrollaktionen.

**Abhilfe:** Zentrale Autorisierung für jede Verwaltungs-API und Ressource erzwingen; Benutzeroberfläche und Backend aus derselben Berechtigungspolitik ableiten.

### CWSTG-05-02 — Privilegierte API-Aktionen und Mandantengrenzen

**Referenzen:** [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation) · [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

**Prüfschritte:**

1. Zeichne eine erlaubte Aktion des Testverwalters auf, etwa die Änderung eines kontrollierten Testbenutzers.
2. Wiederhole mit dem niedrig privilegierten Konto. Prüfe danach separat andere Zielkennungen, Mandantenzuordnungen und privilegierte Felder.
3. Prüfe das Zielobjekt nach jedem Versuch mit einem berechtigten Konto. Beziehe indirekte Verwaltungsaktionen wie Freigaben oder Erstattungen ein, wenn sie im Scope liegen.

**Sicheres Ergebnis:** Akteur, Aktion, Ziel und Mandant werden gemeinsam autorisiert. Eine Fehlermeldung nach bereits erfolgter Änderung gilt nicht als erfolgreiche Abwehr.

**Belege:** Zulässiger Kontrollfall, manipulierte Requests und unabhängiger Zustand des Testziels.

**Abhilfe:** Objekt- und Funktionsberechtigung vor Nebenwirkungen prüfen, privilegierte Felder begrenzen und kritische Aktionen gegebenenfalls an erneute Verifikation binden.

### CWSTG-05-03 — Fehlerausgaben und sensible Dashboarddaten

**Referenzen:** [WSTG-v42-ERRH-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/01-Testing_For_Improper_Error_Handling) · [WSTG-v42-ERRH-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/02-Testing_for_Stack_Traces)

**Prüfschritte:**

1. Prüfe mit einem berechtigten und einem niedrig privilegierten Testkonto fehlende Parameter, ungültige Kennungen und kleines fehlerhaftes JSON.
2. Untersuche Antworten, HTML, eingebettete Zustandsdaten und Dashboard-APIs auf Geheimnisse, Stacktraces, interne Verbindungsdaten und Felder außerhalb des Rollenbedarfs.
3. Prüfe, ob ein Fehler mit einer Korrelationskennung intern diagnostizierbar bleibt, ohne Details im Browser offenzulegen.

**Sicheres Ergebnis:** Der Browser erhält keine unnötigen Geheimnisse oder internen Fehlerdetails; privilegierte Daten sind auch in versteckten API-Feldern geschützt. Ein Serverfehler wird als Robustheitsproblem geprüft, ohne automatisch Datenabfluss zu behaupten.

**Belege:** Geschwärzte Antwortausschnitte, betroffener Kontext und zugeordnetes internes Diagnoseereignis.

**Abhilfe:** Produktionsdebugging deaktivieren, sichere Fehlerantworten verwenden und Antwortmodelle auf erforderliche Felder begrenzen. Diagnosedetails nur geschützt protokollieren.

### CWSTG-05-04 — CSRF auf Verwaltungsaktionen

**Referenzen:** [WSTG-v42-SESS-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery) · [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

**Prüfschritte:**

1. Wähle eine rücksetzbare Verwaltungsaktion und melde den Testverwalter im Browser an.
2. Öffne in derselben Sitzung eine kontrollierte Seite anderer Origin und versuche die Aktion ohne gültigen CSRF-Nachweis auszulösen. Prüfe akzeptierte Formular- und JSON-Content-Types.
3. Prüfe Netzwerkfolge, Preflight, automatisch angehängte Zugangsdaten und Zielzustand. Falls die Architektur es erfordert, beziehe fremde Origins derselben Site ein.

**Sicheres Ergebnis:** Eine fremde Browserseite kann keine Verwaltungsaktion bewirken. CORS muss im tatsächlichen Requestmodell bewertet werden: eine reine Sperre des Antwortlesens verhindert keine bereits ausgelöste Änderung.

**Belege:** Browserrequest mit Origin und Content-Type, Preflightentscheidung und Vorher-/Nachher-Zustand.

**Abhilfe:** Bewährten CSRF-Schutz beziehungsweise ein durchgängiges API-Konzept mit streng geprüften Headern, Content-Types und Origins einsetzen. SameSite als ergänzende Kontrolle behandeln.

### CWSTG-05-05 — Entwicklerkonsolen und Diagnoseendpunkte

**Referenzen:** [WSTG-v42-CONF-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/05-Enumerate_Infrastructure_and_Application_Admin_Interfaces)

**Prüfschritte:**

1. Prüfe dokumentierte oder aus der eigenen Anwendung bekannte Endpunkte für API-Dokumentation, GraphQL-Oberflächen, Datenbankkonsolen und Diagnosefunktionen.
2. Vergleiche Erreichbarkeit und Funktionsumfang als anonymes, normales und administratives Testkonto.
3. Prüfe mit einer harmlosen Leseabfrage auf eigenen Testdaten, ob eine Konsole weitergehende Daten- oder Schreibrechte vermittelt. Keine beliebigen Produktionsabfragen zur bloßen Erreichbarkeitsprüfung ausführen.

**Sicheres Ergebnis:** Entwicklerfunktionen sind entfernt oder passend zugangsbeschränkt. Bewusst öffentliche API-Dokumentation ist kein automatischer Befund; entscheidend sind offengelegte Geheimnisse und unzulässige Funktionen.

**Belege:** Endpunkt, vorgesehene Zielgruppe, erreichbarer Funktionsumfang und begrenzter Kontrollaufruf.

**Abhilfe:** Unnötige Konsolen aus Produktionsartefakten entfernen und verbleibende Funktionen durch starke Authentifizierung, Autorisierung und gegebenenfalls eine gesonderte Netzwerkgrenze absichern.

### CWSTG-05-06 — Standardzugänge und Adminbereitstellung

**Referenzen:** [WSTG-v42-ATHN-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/02-Testing_for_Default_Credentials) · [WSTG-v42-IDNT-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/03-Test_Account_Provisioning_Process)

**Prüfschritte:**

1. Prüfe Installations- und Bereitstellungsregeln auf Standardkonten, Bootstrapzugänge und Wiederherstellungskonten.
2. Teste ausschließlich bekannte Herstellerdefaults beziehungsweise vereinbarte Testwerte mit kleinem Versuchslimit an einem Testzugang.
3. Prüfe Selbstregistrierung und eigene Testeinladungen: Kann ein nicht berechtigter Akteur eine Verwaltungsrolle oder einen fremden Verwaltungsbereich auswählen? Prüfe Ablauf und Wiederverwendung des Bootstrapwegs.

**Sicheres Ergebnis:** Es gibt keinen wiederverwendbaren allgemeinen Standardzugang. Administrative Bereitstellung verlangt den vorgesehenen Nachweis und kann nach Abschluss nicht erneut übernommen werden.

**Belege:** Bereitstellungsregel, begrenzte Anmeldeversuche und Zustand des Testadministrators.

**Abhilfe:** Gemeinsame Defaultgeheimnisse vermeiden, Bootstrapzugänge kurzlebig und einmalig gestalten sowie Einladungsumfang serverseitig begrenzen. Passwortwechsel nach Erstlogin allein schützt einen vorher erreichbaren Standardzugang nicht.

### CWSTG-05-07 — Administratorsitzungen und erneuter Identitätsnachweis

**Referenzen:** [WSTG-v42-SESS-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/02-Testing_for_Cookies_Attributes) · [WSTG-v42-SESS-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation) · [WSTG-v42-SESS-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/06-Testing_for_Logout_Functionality) · [WSTG-v42-SESS-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/07-Testing_Session_Timeout)

**Prüfschritte:**

1. Prüfe Cookieattribute, Leerlauf-/Gesamtlaufzeit und persistente Anmeldung des Administrators anhand der dokumentierten Vorgaben.
2. Prüfe Sitzungsfixierung mit einer echten vorbekannten anonymen Serversitzung und Wiederverwendung nach Logout wie in Kapitel 01.
3. Prüfe eine kritische Testaktion vor und nach Ablauf der vorgesehenen erneuten Verifikation. Beziehe alternative Administrations-APIs und den Rechteentzug bestehender Sitzungen ein.

**Sicheres Ergebnis:** Die Administratorsitzung hält ihre festgelegten Grenzen ein; kritische Aktionen verlangen einen ausreichend aktuellen Nachweis. Ein gelöschtes Cookie oder ausgeblendetes UI genügt nicht zur Entwertung.

**Belege:** Geschwärzte Cookieheader, Zeitlinie und geschützte Kontrollaufrufe vor/nach Logout, Ablauf und Rechteentzug.

**Abhilfe:** Getrennte administrative Anforderungen definieren, Sitzungsrotation und Widerruf durchsetzen und erneute Verifikation serverseitig an die kritische Aktion binden.

### CWSTG-05-08 — Clickjacking und erlaubte Einbettung

**Referenzen:** [WSTG-v42-CLNT-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/09-Testing_for_Clickjacking)

**Prüfschritte:**

1. Bette eine geschützte Verwaltungsansicht von einer kontrollierten fremden Origin in ein iframe ein und prüfe im angemeldeten Testbrowser, ob die Ansicht geladen und bedienbar ist.
2. Prüfe Header wie CSP `frame-ancestors` und gegebenenfalls `X-Frame-Options`, einschließlich Fehler- und Unterseiten.
3. Falls Einbettung fachlich erlaubt ist, vergleiche erlaubte und nicht erlaubte Vorfahren. Teste eine harmlose Testaktion nur innerhalb des vereinbarten Umfangs.

**Sicheres Ergebnis:** Nicht erlaubte Einbettung wird vom Browser verhindert. Ein leeres iframe wegen fehlender Cookies ist kein Nachweis einer wirksamen Framingrichtlinie; tatsächliche Ausnutzbarkeit getrennt bewerten.

**Belege:** Antwortheader, Herkunfts-/Vorfahrenkontext und Browserentscheidung.

**Abhilfe:** Passende CSP-`frame-ancestors`-Richtlinie per HTTP-Header setzen, gegebenenfalls konsistentes X-Frame-Options für ältere Clients ergänzen. Eine Meta-CSP kann `frame-ancestors` nicht ersetzen.

### CWSTG-05-09 — Massenänderungen und Importaufträge

**Referenzen:** [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation) · [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) · [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation)

**Prüfschritte:**

1. Erstelle einen kleinen Bulkauftrag ausschließlich mit kontrollierten Testobjekten. Mische einen zulässigen und einen unzulässigen Ziel-/Mandanteneintrag.
2. Prüfe zusätzlich ein unzulässiges privilegiertes Feld pro Eintrag. Bei asynchronen Jobs prüfe Start, Fortschritt, Ergebnisdownload und erneut ausgewertete Berechtigungen.
3. Kontrolliere jedes Testobjekt sowie den dokumentierten Teilfehler- oder Alles-oder-nichts-Vertrag. Eine HTTP-202-Antwort ist noch kein Endergebnis.

**Sicheres Ergebnis:** Jeder verarbeitete Eintrag und jedes Feld ist autorisiert; Jobstatus und Ergebnisdateien bleiben geschützt. Fehlerhafte Teile verursachen keine undokumentierten Teiländerungen.

**Belege:** Kleine Eingabedatei beziehungsweise Request, Jobergebnis und Zustand aller betroffenen Testobjekte.

**Abhilfe:** Berechtigungen und Eingabeschema pro Eintrag prüfen, Transaktions-/Teilfehlermodell festlegen und Jobartefakte wie die Ausgangsdaten schützen.

### CWSTG-05-10 — Audit, Alarmierung und Schutz der Verwaltungsprotokolle

**Referenzen:** [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

**Prüfschritte:**

1. Führe eine erlaubte und eine verweigerte Verwaltungsaktion aus, etwa eine Rollenänderung an einem Testkonto.
2. Ordne die Ereignisse in der vorgesehenen Auditquelle zu. Prüfe Akteur, Mandant, Ziel, Zeitpunkt, Operation, Ergebnis und gegebenenfalls Änderungskontext.
3. Prüfe, ob vorgesehene Alarme erscheinen und ein gewöhnlicher Verwalter Auditdaten unberechtigt lesen, ändern oder löschen kann. Prüfe relevante Aufbewahrungs- und Integritätskonfiguration.

**Sicheres Ergebnis:** Die Aktionen sind nachvollziehbar, Logs enthalten keine wiederverwendbaren Geheimnisse und sind gegen unberechtigte Einsicht oder Manipulation geschützt. Alarmierung wird anhand definierter Regeln beurteilt.

**Belege:** Geschwärzte korrelierte Auditereignisse, Zugriffskontrollbeleg und vorgesehener Alarm.

**Abhilfe:** Auditpfad von den verwalteten Objekten trennen, Berechtigungen begrenzen und sicherheitsrelevante Ereignisse zuverlässig an eine geschützte Sammlung übertragen.

## Ergänzende Hinweise

Die [Rollenprüfung](04-roles-permissions.md) vertieft Delegation und Tokenvertrauen. Ein separates Adminnetz, MFA und zusätzliche Freigaben können den Schutzbedarf unterstützen; die erforderliche serverseitige Autorisierung jeder Aktion bleibt bestehen.

## Quellen

- [WSTG-v42-CONF-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/05-Enumerate_Infrastructure_and_Application_Admin_Interfaces)
- [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema)
- [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation)
- [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [WSTG-v42-ATHN-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/02-Testing_for_Default_Credentials)
- [WSTG-v42-IDNT-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/03-Test_Account_Provisioning_Process)
- [WSTG-v42-ERRH-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/01-Testing_For_Improper_Error_Handling)
- [WSTG-v42-ERRH-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/02-Testing_for_Stack_Traces)
- [WSTG-v42-SESS-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery)
- [WSTG-v42-CLNT-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/09-Testing_for_Clickjacking)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
