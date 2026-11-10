# 01 · Login

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Authentifizierung darf nur nach erfolgreicher Prüfung aller erforderlichen Faktoren erfolgen. Dieser Baustein prüft Login, Transport, Missbrauchsschutz und die Übergabe in eine authentifizierte Sitzung.

## Voraussetzungen

- Zwei Testkonten mit bekannten Passwörtern; ein Konto mit aktiviertem MFA sowie ein nicht existierender Testbezeichner.
- Getrennte Browserprofile, ein HTTP-Proxy und eine bekannte geschützte API für Kontrollaufrufe.
- Dokumentierte Regeln zu Fehlversuchen, Sperrzeiten, Sitzungsdauer und erlaubtem Anfragebudget; entsperrbarer Testaccount.

## Testfälle

### CWSTG-01-01 — SQL-Injection in Anmeldedaten

**Referenzen:** [WSTG-v42-INPV-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection)

**Prüfschritte:**

1. Zeichne eine erfolgreiche und eine fehlgeschlagene Anmeldung am Testkonto als Kontrollfälle auf. Verändere anschließend jeweils nur das Benutzername- oder Passwortfeld.
2. Prüfe wenige syntaktische und gepaarte boolesche Varianten, etwa ein einzelnes Apostroph und eine wahre/falsche Bedingung. Halte Konto und übrige Parameter konstant.
3. Vergleiche Antwortinhalt, Sitzungsrechte und den Zugriff auf die geschützte Kontroll-API. Zeitbasierte Varianten nur mit vereinbarter kurzer Verzögerung und wiederholten Kontrollmessungen einsetzen.

**Sicheres Ergebnis:** Eingaben werden als Werte verarbeitet und verändern nicht die Abfragestruktur; ohne gültige Zugangsdaten entsteht keine Anmeldung. Fehlende SQL-Fehler oder ein einzelner unveränderter Zeitwert schließen SQL-Injection nicht aus.

**Belege:** Kontroll- und Testanfragen, Antwortpaare, nachfolgender Autorisierungsstatus und bei Zeitmessungen Streuung sowie Messreihen. Im Quellcodezugriff die tatsächliche Parameterbindung prüfen.

**Abhilfe:** Werte durchgängig an parametrisierte Abfragen binden; dynamische Abfrageteile vermeiden oder erlaubte Werte explizit zuordnen. Ein ORM allein garantiert keine sichere Abfrage.

### CWSTG-01-02 — Authentifizierung umgehen

**Referenzen:** [WSTG-v42-ATHN-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/04-Testing_for_Bypassing_Authentication_Schema)

**Prüfschritte:**

1. Rufe die geschützte Kontroll-API ohne Anmeldung auf. Wiederhole mit fehlendem, leerem oder manipuliertem Sitzungstoken.
2. Wiederhole den Login mit entfernten Pflichtfeldern und veränderten Clientfeldern wie `authenticated=true`. Prüfe alternative Login-Endpunkte, Methoden und mobile API-Pfade im Scope.
3. Prüfe nach jedem Versuch serverseitig wirksame Identität und Rechte; eine Weiterleitung oder eine Erfolgsmeldung im UI reicht zur Bewertung nicht aus.

**Sicheres Ergebnis:** Jeder Anmeldeweg prüft die erforderlichen Zugangsdaten und Faktoren. Clientflags, ungültige Token oder übersprungene UI-Schritte verleihen keine Rechte.

**Belege:** Anfragen der Varianten sowie Identitäts- und Ressourcenantworten vor und nach dem Versuch.

**Abhilfe:** Authentifizierung serverseitig zentral prüfen, alternative Kanäle einbeziehen und Zugriffsentscheidungen an verifizierte Sitzungsinformationen binden.

### CWSTG-01-03 — Konten-Erkennung und Begrenzung von Fehlversuchen

**Referenzen:** [WSTG-v42-IDNT-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account) · [WSTG-v42-ATHN-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/03-Testing_for_Weak_Lock_Out_Mechanism)

**Prüfschritte:**

1. Vergleiche Anmeldefehler für ein bekanntes und ein nicht existierendes Testkonto: Nachricht, Status, Weiterleitung, Antwortlänge und wiederholte Zeitmessungen.
2. Führe am entsperrbaren Testkonto eine kleine, vorher festgelegte Anzahl falscher Anmeldungen bis zur vereinbarten Schwelle aus. Protokolliere Verzögerungen und die tatsächliche Annahme weiterer Versuche.
3. Prüfe mit einem zweiten Testkonto, ob Schutz und Entsperrung wie vorgesehen greifen und fremde Konten nicht dauerhaft durch Fehlversuche gesperrt werden können.

**Sicheres Ergebnis:** Es gibt keine verlässlich nutzbare Konten-Auskunft über den Login. Das vereinbarte Fehlversuchsbudget wird wirksam begrenzt; die Wiederherstellung bleibt möglich. Ein CAPTCHA oder ein HTTP-429 allein belegt keine wirksame Begrenzung.

**Belege:** Zeitreihen, Schwellen und Sperrdauer sowie zugeordnete Authentifizierungsereignisse ohne Passwörter oder vollständige Token.

**Abhilfe:** Gleichartige Fehlerpfade, kontobezogene Drosselung und ergänzende Netzwerk- beziehungsweise Risikosignale einsetzen. Sperren so gestalten, dass sie nicht selbst zum dauerhaften Kontenausfall führen.

### CWSTG-01-04 — Sitzungsfixierung und Wiederverwendung nach Logout

**Referenzen:** [WSTG-v42-SESS-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation) · [WSTG-v42-SESS-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/06-Testing_for_Logout_Functionality)

**Prüfschritte:**

1. Lasse den Server in Browserprofil A eine gültige anonyme Sitzung ausstellen. Übertrage diese bekannte Sitzungskennung vor dem Login in Browserprofil B.
2. Melde dich in B an und prüfe, ob A mit der alten Kennung Zugriff auf die authentifizierte Kontroll-API erhält. Dokumentiere Rotation beziehungsweise Trennung zwischen anonymem und authentifiziertem Kontext.
3. Sichere die nach dem Login gültige Testkennung, melde dich ab und wiederhole einen geschützten Aufruf mit dieser Kennung. Prüfe bei Tokenarchitekturen auch Refresh-Token und die dokumentierte Restlaufzeit.

**Sicheres Ergebnis:** Die vorbekannte Sitzung erhält durch den Login in B keine authentifizierten Rechte. Nach Logout ist die Sitzung entsprechend der dokumentierten Widerrufsregel unbrauchbar. Nur das Löschen des Browsercookies genügt nicht.

**Belege:** Zeitlich geordnete Sitzungswechsel, Kontrollaufrufe aus A/B sowie Replay nach Logout; Geheimnisse in Berichten schwärzen.

**Abhilfe:** Beim Authentifizierungswechsel eine frische authentifizierte Sitzung erzeugen und den vorherigen Kontext entwerten. Logout und Tokenwiderruf mit dem zugesagten Verhalten umsetzen.

### CWSTG-01-05 — Sitzungskennungen und Ablaufregeln

**Referenzen:** [WSTG-v42-SESS-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/01-Testing_for_Session_Management_Schema) · [WSTG-v42-SESS-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/07-Testing_Session_Timeout)

**Prüfschritte:**

1. Untersuche eine begrenzte Anzahl eigener Sitzungstoken auf konstante, fortlaufende oder personenbezogene Bestandteile. Teile anonymisierte Strukturbeispiele statt gültiger Kennungen.
2. Prüfe Leerlauf- und absolute Ablaufgrenzen mit kontrollierter Uhr oder abgewarteten Testfristen. Teste danach normale API-Aufrufe und gegebenenfalls Token-Erneuerung.
3. Prüfe bei Quellcode- oder Konfigurationszugriff den Zufallszahlengenerator, die nutzbare Zufallsbitzahl und die serverseitige Ablaufprüfung. Andernfalls diese Eigenschaften als nicht geprüft dokumentieren.

**Sicheres Ergebnis:** Sitzungsgeheimnisse entstehen aus einem kryptografisch sicheren Zufallsverfahren beziehungsweise einem überprüften Tokenprotokoll; Ablaufregeln werden serverseitig durchgesetzt. Unauffällige Stichproben beweisen weder Entropie noch Unvorhersagbarkeit.

**Belege:** Anonymisierte Formatbeobachtungen, Konfigurations- oder Codebelege und Zugriffsversuche vor/nach den festgelegten Ablaufgrenzen.

**Abhilfe:** Bewährte Sitzungsbibliotheken verwenden, Geheimnisse mit CSPRNG erzeugen und Leerlauf-, Gesamt- und Refresh-Laufzeiten konsistent begrenzen. IP- oder User-Agent-Bindung ersetzt keinen Sitzungsnachweis.

### CWSTG-01-06 — Cookies und persistente Anmeldung

**Referenzen:** [WSTG-v42-SESS-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/02-Testing_for_Cookies_Attributes)

**Prüfschritte:**

1. Erfasse `Set-Cookie` beim Login, bei Erneuerung und bei „angemeldet bleiben“. Prüfe tatsächlichen Cookiezweck, Domain, Path und Laufzeit.
2. Prüfe `Secure`, `HttpOnly` und die zum Anmeldeablauf passende `SameSite`-Regel an sitzungstragenden Cookies. Falls `SameSite=None` benötigt wird, prüfe zusätzlich `Secure` und den gesonderten CSRF-Schutz.
3. Prüfe in einem Browser, ob Cookies nur in den vorgesehenen Kontexten versendet werden. Vergleiche Logout und Widerruf persistenter Anmeldungen mit Kapitel 11.

**Sicheres Ergebnis:** Authentifizierungsgeheimnisse werden nur verschlüsselt übertragen und sind ohne fachliche Notwendigkeit nicht per JavaScript lesbar. Cookiebereich und Persistenz sind begrenzt; legitime Föderationsabläufe und CSRF-Schutz bleiben funktionsfähig.

**Belege:** Geschwärzte Cookieheader, Browserbeobachtungen und dokumentierter Zweck jedes relevanten Cookies.

**Abhilfe:** Cookieattribute explizit konfigurieren, einen möglichst engen Hostbereich wählen und persistente Anmeldetoken getrennt verwalten sowie widerrufbar machen.

### CWSTG-01-07 — MFA, Wiederherstellung und alternative Loginwege

**Referenzen:** [WSTG-v42-ATHN-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/04-Testing_for_Bypassing_Authentication_Schema) · [WSTG-v42-ATHN-10](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/10-Testing_for_Weaker_Authentication_in_Alternative_Channel) · [OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)

**Prüfschritte:**

1. Melde dich am MFA-Testkonto zunächst nur mit Passwort an. Rufe vor der zweiten Faktorprüfung direkt die geschützte API sowie alternative Loginwege auf.
2. Prüfe Bindung eines eigenen MFA-Vorgangs an Konto und Sitzung: tausche den Vorgangsbezeichner zwischen zwei Testanmeldungen, verwende einen verbrauchten Code erneut und prüfe Ablauf sowie begrenzte Fehlversuche.
3. Prüfe Faktorwechsel und Recovery mit eigenen Backupcodes: Wiederverwendung, Entfernen des Faktors ohne erneuten Nachweis und Verhalten bestehender Sitzungen. Supportwege nur einbeziehen, wenn sie zum vereinbarten Test gehören.

**Sicheres Ergebnis:** Eine Sitzung vor MFA besitzt keine vollwertigen Rechte. Faktorprüfung, Wiederherstellung und alternative Kanäle erfüllen den festgelegten Schutzbedarf; verbrauchte Backupcodes bleiben ungültig.

**Belege:** Vorgangsfolge, Kontrollaufrufe vor/nach MFA, Code-Replay und Auditereignisse; Codes und Recoverygeheimnisse schwärzen.

**Abhilfe:** MFA-Zustand serverseitig an den Anmeldevorgang binden, Versuche begrenzen und Faktoränderungen durch erneute Verifikation und Benachrichtigung absichern.

### CWSTG-01-08 — Transport und Weitergabe von Zugangsdaten

**Referenzen:** [WSTG-v42-ATHN-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/01-Testing_for_Credentials_Transported_over_an_Encrypted_Channel) · [WSTG-v42-SESS-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/04-Testing_for_Exposed_Session_Variables)

**Prüfschritte:**

1. Prüfe im Browser und Proxy, ob Login, MFA und Sitzungserneuerung durchgängig HTTPS verwenden. Untersuche Formularziel, Weiterleitungen und vorgeschaltete Infrastruktur.
2. Prüfe, ob Passwörter in URL, Browserhistorie, Analyseereignissen oder erlaubten Serverlogs auftauchen. Nutze dafür ausschließlich eigene Testgeheimnisse.
3. Prüfe direkte HTTP-Aufrufe ohne echte Zugangsdaten und kontrolliere, ob die Anwendung auf einen sicheren Einstieg verweist und keine unverschlüsselte Anmeldung annimmt.

**Sicheres Ergebnis:** Zugangsdaten und Sitzungstoken erscheinen nicht in unnötigen URLs oder Logs und werden nicht unverschlüsselt übertragen. Ein Redirect heilt eine bereits über HTTP gesendete Anmeldeanfrage nicht.

**Belege:** Formularziele, Transport- und Redirectfolge sowie geschwärzte Log- oder Historienbelege.

**Abhilfe:** HTTPS am gesamten Authentifizierungspfad erzwingen, HSTS passend ausrollen, Passwörter im Anfragekörper übertragen und Geheimnisse aus Protokollierung und Telemetrie entfernen.

## Ergänzende Hinweise

Für jeden negativen Befund den geprüften Pfad, die Konten und die Testgrenzen angeben. Eine einzelne abgewiesene Eingabe beweist keine vollständige Absicherung. Auswirkungen und Schweregrad anhand des tatsächlich erreichbaren Zugriffs bewerten. Vertiefung: [Registrierung und Recovery](02-registration-recovery.md), [Sitzungen](11-sessions.md).

## Quellen

- [WSTG-v42-ATHN-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/01-Testing_for_Credentials_Transported_over_an_Encrypted_Channel)
- [WSTG-v42-ATHN-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/03-Testing_for_Weak_Lock_Out_Mechanism)
- [WSTG-v42-ATHN-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/04-Testing_for_Bypassing_Authentication_Schema)
- [WSTG-v42-INPV-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection)
- [WSTG-v42-SESS-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/01-Testing_for_Session_Management_Schema)
- [WSTG-v42-SESS-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation)
- [WSTG-v42-SESS-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/06-Testing_for_Logout_Functionality)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)
