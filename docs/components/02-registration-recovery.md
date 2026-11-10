# 02 · Registrierung und Passwort-Wiederherstellung

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Neue Konten und Wiederherstellungsnachweise dürfen nur die vorgesehene Identität und Berechtigung erzeugen. Geprüft werden Registrierung, Passwortregeln, Verifizierung, Reset-Token und Missbrauchsschutz.

## Voraussetzungen

- Zwei eigene Testkonten und kontrollierte E-Mail-Postfächer beziehungsweise ein Mail-Testdienst.
- Dokumentierte Passwort-, Identifikator-, Verifizierungs- und Recoveryregeln sowie Ablaufzeiten.
- Kleines Anfragebudget einschließlich Mailversand; für Paralleltests bereinigbare Testkonten und Einsicht in den endgültigen Zustand.

## Testfälle

### CWSTG-02-01 — Konten-Erkennung bei Registrierung und Recovery

**Referenzen:** [WSTG-v42-IDNT-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account)

**Prüfschritte:**

1. Führe denselben Registrierungs- und Resetablauf mit einer bekannten und einer nicht registrierten Testadresse aus.
2. Vergleiche Nachricht, Status, Redirects, Antwortlänge, Fehlerschlüssel und wenige wiederholte Zeitmessungen unter gleichen Bedingungen.
3. Prüfe freigegebene Varianten bei Groß-/Kleinschreibung und Leerzeichen. Bewerte nur Informationen, die auch dem anfragenden Benutzer zugänglich sind; die interne Mailwarteschlange ist kein öffentlicher Seitenkanal.

**Sicheres Ergebnis:** Nicht öffentliche Konten lassen sich über diese Antworten nicht zuverlässig unterscheiden. Beabsichtigte Auskunft, etwa über öffentlich sichtbare Nutzernamen, wird mit Produktregel und Schutzbedarf dokumentiert.

**Belege:** Gepaarte Anfragen, Antwortvergleich und Messstreuung; beabsichtigte Ausnahmen mit Begründung.

**Abhilfe:** Gleichartige Antwortpfade und generische Recoverymeldungen einsetzen. Verarbeitung gegebenenfalls asynchron gestalten; zufällige Wartezeiten beheben einen systematischen Timingunterschied nicht zuverlässig.

### CWSTG-02-02 — Passwortregeln serverseitig durchsetzen

**Referenzen:** [WSTG-v42-ATHN-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/07-Testing_for_Weak_Password_Policy) · [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

**Prüfschritte:**

1. Ermittle die dokumentierte Passwortregel und prüfe sie durch direkte Registrierungs- und Reset-API-Aufrufe ohne UI-Validierung.
2. Prüfe wenige repräsentative Werte: zu kurz, bekannt häufig, lange Passphrase, Unicode und Leerzeichen. Teste maximale Längen innerhalb des vereinbarten Budgets.
3. Prüfe nach erfolgreicher Registrierung die Anmeldung mit exakt eingegebenem Passwort und einer Variante jenseits möglicher Abschneidegrenzen. Beziehe die Speicher- und Hashkonfiguration ein, falls zugänglich.

**Sicheres Ergebnis:** Alle Anmelde- und Resetwege setzen dieselbe serverseitige Regel um und kürzen Passwörter nicht stillschweigend. Die Regel berücksichtigt Länge, kompromittierte Passwörter und MFA; starre Zeichengruppen allein sind kein Gütenachweis.

**Belege:** Grenzwertfälle, Registrierungszustand und kontrollierte Loginversuche; keine echten Passwörter in den Bericht übernehmen.

**Abhilfe:** Passwortprüfung zentralisieren, lange Passphrasen ermöglichen und bekannte schwache beziehungsweise kompromittierte Werte blockieren. Passwörter mit geeigneter adaptiver Passwort-Hashfunktion und individuellen Salts speichern.

### CWSTG-02-03 — Reset-Token: Kontobindung, Ablauf und atomare Einmalverwendung

**Referenzen:** [WSTG-v42-ATHN-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Password_Change_or_Reset_Functionalities) · [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)

**Prüfschritte:**

1. Fordere für beide Testkonten einen Reset an. Tausche beim Einlösen nur die Konto- oder Vorgangskennung; prüfe, ob der Token ausschließlich das zugeordnete Konto beeinflusst.
2. Löse einen Token ein und verwende ihn erneut. Prüfe einen zweiten Token nach der festgelegten Frist mit kontrollierter Zeit oder nach Ablauf; Änderungen an Clientzeit oder einem nicht signierten Ablaufparameter ersetzen diesen Test nicht.
3. Sende in einer Testumgebung zwei kontrollierte Einlöseanfragen mit demselben Token und unterschiedlichen neuen Testpasswörtern nahezu gleichzeitig. Prüfe anhand korrelierter Auditereignisse oder Datenbankänderungen, wie viele tatsächlich wirksam wurden. Ein abschließender Login zeigt nur den letzten Passwortzustand und beweist den atomaren Einmalverbrauch nicht; ohne geeignete Einsicht diese Grenze ausdrücklich offenlassen.
4. Prüfe bei Codezugriff Zufallserzeugung, sichere Speicherung und atomaren Verbrauch. Prüfe offene Token und aktive Sitzungen nach einem erfolgreichen Reset gemäß Recoveryregel.

**Sicheres Ergebnis:** Nur das gebundene Konto wird geändert; abgelaufene und verbrauchte Token bleiben ungültig. Von konkurrierenden Einlöseversuchen kann höchstens einer wirksam werden. Unauffälliges Format allein belegt keine kryptografische Stärke.

**Belege:** Token-Vorgangsfolge, nachfolgende Loginprüfung und bei Paralleltests Zeitlinie, korrelierte Zustandsänderungen sowie tatsächlicher Endzustand; fehlende Einsicht kennzeichnen und Token vollständig schwärzen.

**Abhilfe:** Token an Konto und Resetvorgang binden, aus CSPRNG erzeugen beziehungsweise kryptografisch korrekt prüfen, kurz nach festgelegter Frist verfallen lassen und atomar verbrauchen. Gespeicherte Tokengeheimnisse durch einen geeigneten Hash schützen.

### CWSTG-02-04 — Reset-Links und Datenlecks

**Referenzen:** [WSTG-v42-ATHN-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Password_Change_or_Reset_Functionalities) · [WSTG-v42-SESS-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/04-Testing_for_Exposed_Session_Variables)

**Prüfschritte:**

1. Prüfe im eigenen Postfach die erzeugte Reset-URL: HTTPS, erwarteter Host, keine Passwörter oder unnötigen personenbezogenen Daten.
2. Wiederhole eine Resetanforderung mit einem kontrollierten abweichenden Host beziehungsweise freigegebenen Proxy-Header. Prüfe, ob die Mail weiterhin nur auf den vorgesehenen Host verweist.
3. Untersuche die Resetseite auf Drittinhalte, Referrerübertragung, Browserhistorie, Cache- und Logeinträge mit Token. Prüfe Linkvorschauen im Mail-Testdienst und den Ablauf beim ersten Aufruf.

**Sicheres Ergebnis:** Resetlinks führen zu einem vertrauenswürdigen Ziel. Token gelangen nicht an Drittanbieter oder allgemeine Logs; bloßer Linkabruf durch einen Vorschau-Scanner ändert das Passwort nicht. Ein URL-Token ist nicht grundsätzlich fehlerhaft, benötigt aber Schutz gegen Weitergabe.

**Belege:** Geschwärzte Mail, Linkziel, relevante Header und kontrollierte Beobachtung möglicher Tokenweitergabe.

**Abhilfe:** Vertrauenswürdige Basis-URL konfigurieren, Proxyvertrauen begrenzen, Resetseiten ohne Drittinhalte und mit passender Referrer- und Cachepolitik ausliefern. Passwortänderung erst durch ausdrückliches, geprüftes Absenden ausführen.

### CWSTG-02-05 — Parallele Registrierung und eindeutige Identitäten

**Referenzen:** [WSTG-v42-IDNT-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/02-Test_User_Registration_Process) · [WSTG-v42-BUSL-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/04-Test_for_Process_Timing)

**Prüfschritte:**

1. Registriere in der Testumgebung dieselbe neue Testadresse mit zwei nahezu gleichzeitigen Anfragen.
2. Prüfe nach Abschluss Kontenzahl, Identitätszuordnung, Verifizierungsmails und Anmeldemöglichkeiten. Wiederhole bei Bedarf mit fachlich gleichwertigen Schreibweisen entsprechend der dokumentierten Normalisierung.
3. Prüfe bei Codezugriff, ob Eindeutigkeit und Normalisierung auch bei paralleler Verarbeitung an der Datenbankgrenze garantiert sind.

**Sicheres Ergebnis:** Es entsteht nur die erlaubte Zahl eindeutiger Identitäten; konkurrierende Anfragen können keine Kontoverwechslung oder Übernahme verursachen. Statuscodes allein zeigen den tatsächlichen Zustand nicht.

**Belege:** Zeitlinie, Testidentifikatoren, Registrierungsergebnisse und nachgewiesene Kontenzuordnung.

**Abhilfe:** Eindeutigkeitsregeln in der Datenbank und atomare Anlage einsetzen. Identifikatoren vor konsistenter Prüfung fachgerecht normalisieren; E-Mail-Adressen nicht durch undokumentierte Providerannahmen zusammenfassen.

### CWSTG-02-06 — Registrierung, Verifizierung und Einladungen

**Referenzen:** [WSTG-v42-IDNT-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/02-Test_User_Registration_Process) · [WSTG-v42-IDNT-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/03-Test_Account_Provisioning_Process)

**Prüfschritte:**

1. Lege ein Konto an und rufe vor E-Mail-Verifizierung direkt Funktionen auf, die eine bestätigte Adresse voraussetzen.
2. Verändere in der Registrierungsanfrage Felder wie `verified`, `role` oder `tenantId`. Prüfe Einladungen mit einem zweiten eigenen Konto und nach Änderung der Zieladresse.
3. Prüfe Verifizierungs- und Einladungstoken auf Empfänger-/Vorgangsbindung, Ablauf und Wiederverwendung. Kontrolliere, welche Rechte nach jedem Schritt tatsächlich verfügbar sind.

**Sicheres Ergebnis:** Registrierung und Einladung verleihen nur die vorgesehenen Rechte. Unverifizierte Adressen gelten nicht als bestätigte Identität; Token können nicht auf andere Konten oder Mandanten übertragen werden.

**Belege:** Anlage- und Verifizierungsschritte, wirksame Kontoeigenschaften und Ressourcenaufrufe vor/nach Bestätigung.

**Abhilfe:** Verifizierungszustand und Rollen serverseitig verwalten, erlaubte Registrierungsfelder begrenzen und Einladungen an vorgesehenen Empfänger, Mandanten und Berechtigungsumfang binden.

### CWSTG-02-07 — Missbrauchsschutz, Benachrichtigung und Recoveryzustand

**Referenzen:** [WSTG-v42-BUSL-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/05-Test_Number_of_Times_a_Function_Can_Be_Used_Limits) · [WSTG-v42-ATHN-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Password_Change_or_Reset_Functionalities) · [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

**Prüfschritte:**

1. Führe eine begrenzte Serie von Register-/Resetanforderungen für eigene Adressen bis zur vereinbarten Schwelle aus. Prüfe angenommene Vorgänge und tatsächlich ausgelöste Mails.
2. Prüfe, ob schon eine Resetanforderung das Konto sperrt oder bestehende Anmeldung ohne Nachweis verändert. Schließe anschließend einen legitimen Reset ab und prüfe Passwortwechselbenachrichtigung sowie die dokumentierte Behandlung alter Sitzungen.
3. Ordne den Testereignissen Auditdaten und gegebenenfalls vorgesehene Alarme zu. Prüfe, dass Logs weder Passwörter noch gültige Resetgeheimnisse enthalten.

**Sicheres Ergebnis:** Die vorgesehenen Versand- und Versuchsgrenzen wirken; eine fremde Anfrage allein entzieht dem Kontoinhaber keinen Zugriff. Erfolgreiche Recovery wird nachvollziehbar gemeldet, und kompromittierte Sitzungen beziehungsweise Nachweise werden nach der vereinbarten Regel entwertet.

**Belege:** Anfrage- und Mailanzahl, Zeitlinie, Zustandsprüfung und geschwärzte Auditereignisse.

**Abhilfe:** Anforderungen und Einlösung getrennt begrenzen, Recoveryänderungen erst nach gültigem Nachweis ausführen und relevante Zustandswechsel geheimnisfrei protokollieren. Faktor-Recovery gesondert absichern.

## Ergänzende Hinweise

Magic Links sind ein eigener Authentifizierungsweg: zusätzlich [Login/MFA](01-login.md) und [Sitzungen](11-sessions.md) anwenden. Keine feste Tokenlaufzeit ohne den tatsächlichen Schutzbedarf als universelle Vorgabe behandeln. IP- oder Gerätebindung ist kein Ersatz für Kontobindung und Einmalverwendung.

## Quellen

- [WSTG-v42-IDNT-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/02-Test_User_Registration_Process)
- [WSTG-v42-IDNT-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/03-Test_Account_Provisioning_Process)
- [WSTG-v42-IDNT-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account)
- [WSTG-v42-ATHN-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/07-Testing_for_Weak_Password_Policy)
- [WSTG-v42-ATHN-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Password_Change_or_Reset_Functionalities)
- [WSTG-v42-BUSL-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/04-Test_for_Process_Timing)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
