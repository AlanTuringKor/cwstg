# 04 · Rollen und Berechtigungen

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Berechtigungen müssen serverseitig pro Aktion, Zielobjekt und Mandant gelten. Geprüft werden Zuweisung, delegierte Freigaben, Tokenvertrauen, konkurrierende Änderungen und der Entzug bereits ausgegebener Rechte.

## Voraussetzungen

- Dokumentierte Rollen-/Aktionsmatrix einschließlich delegierbarer Rollen und Mandantengrenzen.
- Je ein niedrig privilegiertes Konto, Rollenverwalter und Testzielkonto; für Freigaben zwei getrennte Akteure.
- Bekannter zulässiger Verwaltungsrequest als Kontrollfall und ein rücksetzbarer Berechtigungszustand.

## Testfälle

### CWSTG-04-01 — Rolle, Zielkonto und Mandant manipulieren

**Referenzen:** [WSTG-v42-IDNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/01-Test_Role_Definitions) · [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation) · [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

**Prüfschritte:**

1. Führe eine erlaubte Rollenzuweisung durch den berechtigten Testverwalter aus und notiere Akteur, Ziel, Mandant und erlaubten Rollenbereich.
2. Wiederhole denselben Request mit der Sitzung des niedrig privilegierten Testkontos. Prüfe separat andere Zielkonten, einen fremden Testmandanten und eine Rolle außerhalb des delegierten Bereichs.
3. Prüfe anschließend mit dem Zielkonto die tatsächlichen Rechte und den gespeicherten Zustand. Beziehe direkte API-Aufrufe unabhängig von sichtbaren UI-Feldern ein.

**Sicheres Ergebnis:** Jede Zuweisung ist durch Akteur, Ziel und delegierbaren Umfang gedeckt. Weder UI-Sichtbarkeit noch der Besitz einer Objektkennung erlaubt eine Rollenänderung.

**Belege:** Rollenmatrix, Kontroll-/Testrequests und Vorher-/Nachher-Rechte des Zielkontos.

**Abhilfe:** Zentrale Autorisierungsregeln mit standardmäßiger Verweigerung nutzen, Mandant und Delegationsgrenzen prüfen und diese Prüfung vor der Änderung durchführen.

### CWSTG-04-02 — JWT-Prüfung und Claims-Vertrauen

**Referenzen:** [RFC 8725: JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725.html)

**Prüfschritte:**

1. Falls JWT verwendet werden: dekodiere ausschließlich eigene Token lokal. Ändere einen Berechtigungsclaim ohne gültige Neusignatur und rufe eine geschützte Testfunktion auf.
2. Prüfe kontrolliert nicht erlaubte Algorithmen, fehlende Signatur und unbekannte Schlüsselkennung. Falls mehrere Tokenarten oder Dienste existieren, verwende einen eigenen gültigen Token mit falschem Zweck, Aussteller oder Empfänger.
3. Prüfe Ablauf und gegebenenfalls `nbf`; kontrolliere bei Codezugriff feste Algorithmus-/Schlüsselzuordnung, Aussteller, Empfänger und Tokenart. Keine echten Token an öffentliche Onlinedecoder senden.

**Sicheres Ergebnis:** Unverifizierte oder kontextfremde Token verleihen keine Rechte. Die JWT-Signatur schützt Integrität, aber verschlüsselt lesbare Claims nicht. Dieser Fall hat in WSTG v4.2 keine eigene JWT-Test-ID; die RFC ergänzt das Mapping.

**Belege:** Tokenmetadaten ohne Geheimnis, abweichende Verifikationskontexte, Ressourcenantworten und freigegebene Prüflogik.

**Abhilfe:** Bewährte JWT-Bibliothek mit fest vorgegebenen Algorithmen und vertrauenswürdigen Schlüsseln verwenden; relevante Claims und Verwendungszweck prüfen. Schlüsselkennungen dürfen keine beliebigen Dateien oder Remoteziele auswählen.

### CWSTG-04-03 — Ausgeblendete UI-Felder und direkte Requests

**Referenzen:** [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema)

**Prüfschritte:**

1. Öffne die Rollenansicht als niedrig privilegiertes Konto. Blende ausgeblendete Felder lokal ein beziehungsweise entferne `disabled`.
2. Sende einen aus einem berechtigten Kontrollfall bekannten Rollenrequest direkt mit der niedrig privilegierten Sitzung.
3. Prüfe getrennt, ob UI, API und serverseitig wirksame Rechte auseinanderfallen.

**Sicheres Ergebnis:** Clientänderungen können Darstellung, aber keine serverseitigen Berechtigungen verändern. Auch alternative Endpunkte und Methoden verlangen dieselbe fachliche Freigabe.

**Belege:** UI-Zustand, tatsächlich gesendeter Request und unabhängige Rechteprüfung.

**Abhilfe:** UI-Sperren nur als Bedienhilfe einsetzen; Autorisierung bei jeder Verwaltungsoperation auf dem Server erzwingen.

### CWSTG-04-04 — CSRF auf Rollenzuweisungen

**Referenzen:** [WSTG-v42-SESS-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery) · [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

**Prüfschritte:**

1. Prüfe zunächst, ob die Anmeldung durch vom Browser automatisch angehängte Zugangsdaten erfolgt. Melde den berechtigten Testverwalter im Testbrowser an.
2. Öffne im selben Browser eine kontrollierte Seite anderer Origin, die einen Rollenrequest ohne gültigen CSRF-Nachweis auslöst. Prüfe zulässige Formular-Content-Types und bei JSON-Endpunkten die tatsächlichen Parserregeln.
3. Beobachte, ob ein Preflight den tatsächlichen Request verhindert, Cookies mitgesendet werden und die Änderung erfolgt. Prüfe bei relevanter Architektur auch einen anderen Origin derselben Site; SameSite ist keine Originprüfung.

**Sicheres Ergebnis:** Der fremde Browserkontext kann keine Rollenänderung auslösen. Eine CORS-Leseblockade nach versendetem Request belegt keinen CSRF-Schutz. Ein JSON-Endpunkt ist nur dann entsprechend geschützt, wenn einfache Content-Types nicht akzeptiert werden und notwendige Header/CORS-Regeln tatsächlich greifen.

**Belege:** Browser-Netzwerkfolge einschließlich Preflight, Cookie-/Originbeobachtung und endgültiger Rollenstatus.

**Abhilfe:** Framework-CSRF-Schutz, geeignete Origin-/Fetch-Metadata-Prüfung oder ein konsistentes API-Schutzkonzept einsetzen. SameSite ergänzend setzen; kritische Änderungen gegebenenfalls durch erneuten Identitätsnachweis schützen.

### CWSTG-04-05 — Mass Assignment und mehrdeutige Parameter

**Referenzen:** [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation) · [WSTG-v42-INPV-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/04-Testing_for_HTTP_Parameter_Pollution) · [OWASP Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)

**Prüfschritte:**

1. Ergänze eine normale Profil- oder Mitgliedschaftsänderung um ein einzelnes privilegiertes Feld wie `roles`, `isAdmin` oder einen verschachtelten Berechtigungswert.
2. Prüfe, sofern vom Format unterstützt, doppelte Formparameter beziehungsweise widersprüchliche Werte zwischen URL und Body. Trenne diese Fälle von normaler Rollenzuweisung.
3. Vergleiche die Interpretation von Gateway, Validierung und eigentlicher Verarbeitung; prüfe den Endzustand und die effektiven Rechte.

**Sicheres Ergebnis:** Unzulässige Zusatzfelder bleiben wirkungslos. Mehrdeutige Eingaben werden abgewiesen oder nach einer konsistent dokumentierten Regel verarbeitet, die keine Autorisierungsgrenze übergeht.

**Belege:** Genaue Bytefolge des Requests, interpretierte Werte soweit zugänglich und Kontozustand.

**Abhilfe:** Erlaubte Eingabefelder explizit modellieren, komplexe Modelle nicht ungeprüft binden und mehrdeutige Parameter an einer gemeinsamen Eingangsgrenze ablehnen.

### CWSTG-04-06 — Parallele Änderungen und widersprüchlicher Zustand

**Referenzen:** [WSTG-v42-BUSL-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/04-Test_for_Process_Timing)

**Prüfschritte:**

1. Definiere eine konkrete Invariante, etwa keine Selbstfreigabe oder keinen Erhalt einer Berechtigung nach bestätigtem Entzug.
2. Sende im Labor zwei freigegebene, widersprüchliche Rollenänderungen für dasselbe Testkonto nahezu gleichzeitig.
3. Prüfe Endzustand, Versionskonflikte, effektive Rechte und Auditfolge. Suche nach Verletzung der Invariante; zwei erlaubte Änderungen mit dokumentierter Reihenfolge sind allein kein Fehler.

**Sicheres Ergebnis:** Parallele Verarbeitung umgeht weder Freigabe noch Rollenregeln. Zustandsänderungen und ihre maßgeblichen Berechtigungsprüfungen sind konsistent.

**Belege:** Anfragereihenfolge, Zustandsversionen, Transaktions-/Auditbelege und die geprüfte Invariante.

**Abhilfe:** Änderungen mit Transaktionen, Versionsprüfung oder passenden Sperren absichern und die Autorisierungsentscheidung konsistent mit dem Schreibvorgang treffen.

### CWSTG-04-07 — Delegation und Freigabeprozess

**Referenzen:** [WSTG-v42-BUSL-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/06-Testing_for_the_Circumvention_of_Work_Flows) · [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation)

**Prüfschritte:**

1. Lege als berechtigter Antragsteller eine Rollenanfrage für das eigene Testziel an.
2. Rufe den abschließenden Zuweisungsendpunkt vor Freigabe direkt auf. Verändere Felder wie `approved`, `reviewerId`, Zielrolle oder Zielkonto und prüfe Selbstfreigabe.
3. Versuche nach einer echten Freigabe deren Wiederverwendung für eine geänderte Anfrage. Prüfe den tatsächlich zugewiesenen Umfang.

**Sicheres Ergebnis:** Freigabe stammt vom berechtigten, gegebenenfalls getrennten Akteur und gilt nur für den geprüften Antrag. Ein Clientflag kann fehlende oder veraltete Zustimmung nicht ersetzen.

**Belege:** Antragsversionen, Freigabeidentität, abgewiesene Varianten und endgültige Berechtigungen.

**Abhilfe:** Antrag und Freigabe serverseitig als Zustand verwalten, Freigabe an Ziel und Umfang binden und Änderungen nach Zustimmung erneut freigeben lassen.

### CWSTG-04-08 — Audit und Alarmierung

**Referenzen:** [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

**Prüfschritte:**

1. Führe eine berechtigte Änderung und einen unberechtigten Versuch an Testkonten aus.
2. Prüfe die zugeordneten Auditereignisse auf Akteur, Ziel, Zeitpunkt, Mandant, angeforderte Änderung und Ergebnis. Prüfe getrennt, ob für diese Ereignisse laut Konzept ein Alarm vorgesehen ist.
3. Prüfe Zugriffsrechte und Manipulationsschutz des Auditpfads sowie Schwärzung von Token und anderen Geheimnissen.

**Sicheres Ergebnis:** Berechtigungsänderungen und relevante Verweigerungen sind nachvollziehbar; definierte Alarme werden zugestellt. Ein Auditdatensatz enthält keine wiederverwendbaren Anmeldedaten. Eine allgemeine WSTG-Logging-ID wird nicht erfunden.

**Belege:** Geschwärzte Ereignisse mit Korrelationskennung, Zugriffskontrolltest und gegebenenfalls Alarmbeleg.

**Abhilfe:** Strukturierte Auditereignisse an eine getrennt geschützte Ablage senden, Zugriff begrenzen und Alarmregeln an konkrete risikoreiche Änderungen binden.

### CWSTG-04-09 — Rechteentzug bei bestehenden Sitzungen

**Referenzen:** [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema) · [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

**Prüfschritte:**

1. Melde das Testziel vor einer Rollenänderung in zwei Browserprofilen an und sichere einen eigenen API-Token, falls unterstützt.
2. Entziehe eine privilegierte Rolle beziehungsweise entferne die Testmitgliedschaft. Warte die dokumentierte maximale Wirksamkeitsfrist ab.
3. Wiederhole die zuvor erlaubte Aktion mit alten Sitzungen, Access-Token und einem möglichen Refreshvorgang. Prüfe auch serverseitige Berechtigungscaches.

**Sicheres Ergebnis:** Entzogene Rechte verschwinden in allen Pfaden innerhalb der vereinbarten Frist. Eine gültige Signatur oder erfolgreiche Token-Erneuerung hält eine widerrufene Rolle nicht über diese Frist hinaus wirksam.

**Belege:** Entzugszeitpunkt, zugesagte Frist und Ressourcenaufrufe mit alten und erneuerten Testanmeldungen.

**Abhilfe:** Autorisierungscaches und Tokenlaufzeiten auf den erforderlichen Entzug abstimmen; bei sofortigem Entzug etwa serverseitigen Sitzungs-/Berechtigungszustand oder eine Widerrufsversion auswerten.

## Ergänzende Hinweise

Wiederkehrende Autorisierungsfälle lassen sich aus der Rollen-/Aktionsmatrix automatisieren. Ein pauschaler Schweregrad pro Rollenfehler wäre irreführend: tatsächlichen delegierbaren Umfang, Mandantenwechsel und erreichbare Geschäftsaktionen belegen.

## Quellen

- [WSTG-v42-IDNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/01-Test_Role_Definitions)
- [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema)
- [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation)
- [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [WSTG-v42-INPV-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/04-Testing_for_HTTP_Parameter_Pollution)
- [WSTG-v42-SESS-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery)
- [WSTG-v42-BUSL-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/04-Test_for_Process_Timing)
- [WSTG-v42-BUSL-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/06-Testing_for_the_Circumvention_of_Work_Flows)
- [RFC 8725: JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725.html)
- [OWASP Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
