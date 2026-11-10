# 03 · Profil und Kontoeinstellungen

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Profilfunktionen müssen private Daten, Kontoeigenschaften und zugehörige Dateien entsprechend der tatsächlichen Berechtigung schützen. Sichtbarkeit im UI und schwer erratbare IDs ersetzen keine Zugriffskontrolle.

## Voraussetzungen

- Testkonto A und B mit jeweils eigenen Profildaten; bei Mehrmandantenbetrieb ein weiterer Testmandant.
- Festgelegte Sichtbarkeit öffentlicher und privater Profilfelder, erlaubte Änderungen sowie Regeln für sensible Einstellungen.
- Kontrollierte Avatar-Dateien, zwei Browserprofile und bekannte Profil-/API-Endpunkte.

## Testfälle

### CWSTG-03-01 — Fremde Profile und private Felder lesen

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

**Prüfschritte:**

1. Rufe das eigene Profil als Konto A auf und notiere sämtliche zurückgegebenen Felder, inklusive eingebetteter API-Daten.
2. Ersetze die Profilkennung durch die bekannte Kennung von Testkonto B. Prüfe UI, direkte API, alternative Detailpfade und falls vorhanden einen anderen Testmandanten.
3. Wiederhole ohne Anmeldung. Vergleiche die Antwort mit der festgelegten Feldsichtbarkeit, einschließlich Avatar-URLs, Metadaten und Änderungsverlauf.

**Sicheres Ergebnis:** Jeder Kontext liefert ausschließlich freigegebene Profilfelder und zugehörige Ressourcen. Öffentlich sichtbarer Name und privater Kontaktdatensatz werden getrennt behandelt; ein HTTP-200 für ein öffentliches Profil ist für sich kein Befund.

**Belege:** Konten-/Mandantenmatrix, freigegebene Sollfelder und geschwärzte Antwortvergleiche.

**Abhilfe:** Autorisierung und Feldprojektion serverseitig für jede Ressource durchsetzen. Nicht erratbare IDs nur ergänzend verwenden; Mandantenzuordnung aus dem verifizierten Kontext ableiten.

### CWSTG-03-02 — Profiländerung und zusätzliche Berechtigungsfelder

**Referenzen:** [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation) · [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) · [OWASP Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)

**Prüfschritte:**

1. Zeichne eine zulässige Profiländerung von A auf. Ersetze in einer getrennten Variante die Zielkennung durch die von B und kontrolliere dessen Profil anschließend als B.
2. Füge bei einer Änderung des eigenen Profils wenige zusätzliche Felder wie `role`, `isAdmin`, `verified` oder `tenantId` hinzu, soweit diese im Datenmodell vorkommen.
3. Prüfe Antwort, endgültige Kontoeigenschaften und Zugriff auf eine privilegierte Kontrollfunktion. Prüfe auch verschachtelte Änderungsobjekte und PATCH-Endpunkte.

**Sicheres Ergebnis:** Nur berechtigte Felder des berechtigten Zielkontos ändern sich. Ignorierte Zusatzfelder sind akzeptabel, wenn sie keine Nebenwirkung haben; ein Fehlerstatus allein beweist dies nicht.

**Belege:** Geschwärzte Änderungsanfragen, Vorher-/Nachher-Zustand beider Konten und Kontrollaufruf.

**Abhilfe:** Erlaubte Felder je Vorgang explizit binden, Ziel und Akteur autorisieren und privilegierte Kontoeigenschaften ausschließlich durch passende Verwaltungsfunktionen ändern lassen.

### CWSTG-03-03 — Gespeichertes XSS in Profilfeldern

**Referenzen:** [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting) · [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

**Prüfschritte:**

1. Speichere einen eindeutigen Textmarker und anschließend einen harmlosen lokalen Ausführungsmarker in Anzeigename, Beschreibung und weiteren gerenderten Profilfeldern.
2. Öffne das Profil als B und anonym, sofern erlaubt. Prüfe zusätzlich Navigation, Suchtreffer, Verwaltungsansicht und gegebenenfalls gerenderte Avatar-Metadaten.
3. Vergleiche gespeicherten Wert, Serverantwort und den resultierenden DOM-Kontext. Prüfe unterstützte HTML-/Linkfelder mit wenigen kontextspezifischen Varianten.

**Sicheres Ergebnis:** Reiner Text bleibt Text; erlaubtes Rich Text wird für den tatsächlichen Ausgabekontext bereinigt. Ausbleibende Dialoge reichen nicht als Beweis, da CSP, Browserregeln oder fehlende Interaktion die Ausführung verdecken können.

**Belege:** Gespeicherter Testwert, konkrete Ausgabestellen, DOM-Ausschnitt und Browserbeobachtung mit Renderkontext.

**Abhilfe:** Text kontextgerecht kodieren und sichere DOM-Schnittstellen verwenden. Nur für tatsächlich erlaubtes HTML einen gepflegten Sanitizer einsetzen; CSP ergänzt diese Maßnahmen.

### CWSTG-03-04 — Avatar-Upload und Dateizugriff

**Referenzen:** [WSTG-v42-BUSL-08](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/08-Test_Upload_of_Unexpected_File_Types) · [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files) · [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)

**Prüfschritte:**

1. Lade kleine kontrollierte Testdateien hoch: erlaubtes Bild, widersprüchlicher Dateityp, mehrfache Endung und gegebenenfalls SVG mit lokalem Marker. Prüfe Erweiterung, deklarierten Typ und tatsächlichen Inhalt unabhängig voneinander.
2. Rufe Original und Vorschaubild direkt ab. Prüfe Browserkontext, Content-Type, Auslieferungsdomain und bei privaten Avataren den Zugriff als B und anonym.
3. Prüfe einen begrenzten Pfadsegment-Marker im Dateinamen und kontrolliere über freigegebene Speicherbelege, ob der Speicherort fest vorgegeben bleibt. Für Serverausführung ausschließlich eine gesondert vereinbarte Testdatei im Labor verwenden.

**Sicheres Ergebnis:** Ungeeignete Inhalte werden abgelehnt oder sicher in das erlaubte Bildformat überführt. Originale werden nicht serverseitig ausgeführt; private Dateien und Vorschaubilder bleiben geschützt. Magic Bytes oder ein Bild-Content-Type allein beweisen dies nicht.

**Belege:** Uploadantwort, tatsächlicher Dateityp, Abrufheader und Rechtevergleich für Original sowie abgeleitete Bilder.

**Abhilfe:** Erlaubte Formate dekodieren und gegebenenfalls neu kodieren, Dateinamen serverseitig erzeugen, Ausführung deaktivieren und Speicher-/Abrufberechtigung konsistent prüfen. Detailtests in Kapitel 08 anwenden.

### CWSTG-03-05 — Sensible Einstellungen: E-Mail, Passwort und Faktoren

**Referenzen:** [WSTG-v42-ATHN-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Password_Change_or_Reset_Functionalities) · [WSTG-v42-SESS-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery) · [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

**Prüfschritte:**

1. Zeichne einen zulässigen Wechsel einer sensiblen Einstellung am eigenen Testkonto auf. Wiederhole ohne den vorgesehenen erneuten Identitätsnachweis sowie mit fehlendem oder fremdem CSRF-Nachweis bei cookiegestützter Anmeldung.
2. Prüfe einen E-Mail-Wechsel mit kontrollierten alten und neuen Postfächern: Bestätigung, Ablauf offener Vorgänge, neue Anmeldung und Benachrichtigung nach der festgelegten Regel.
3. Prüfe nach Passwort-/Faktorwechsel den Zustand bestehender Testanmeldungen und Wiederherstellungsnachweise. Verifiziere die Änderung unabhängig vom UI.

**Sicheres Ergebnis:** Sensible Änderungen verlangen den vorgesehenen erneuten Nachweis und können nicht durch eine fremde Browserseite ausgelöst werden. Eine unbestätigte Zieladresse übernimmt keine Rechte, die eine bestätigte Adresse voraussetzen.

**Belege:** Änderungsfolge, erforderliche Nachweise, geschwärzte Benachrichtigungen und unabhängiger Kontozustand.

**Abhilfe:** Sensible Vorgänge serverseitig gesondert absichern, CSRF-Schutz passend zum Anmeldeverfahren einsetzen und Änderungen an Wiederherstellungskanälen mit überprüfbarer Bestätigung und Benachrichtigung versehen.

### CWSTG-03-06 — Profilsuche, Verlauf und Datenexport

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) · [WSTG-v42-BUSL-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/05-Test_Number_of_Times_a_Function_Can_Be_Used_Limits)

**Prüfschritte:**

1. Suche als A über die vorgesehenen Autocomplete- und Profilendpunkte nach bekannten Testkonten. Prüfe, welche Felder bei Treffer, Vorschau und Detailaufruf sichtbar werden.
2. Rufe vorhandene Änderungsverläufe, Datenexporte und zugehörige Downloadlinks mit A, B und anonym auf.
3. Prüfe mit wenigen Anfragen die vereinbarten Such-/Exportgrenzen und die Bereinigung privater Profildaten im Browser nach Logout beziehungsweise Kontowechsel.

**Sicheres Ergebnis:** Suche, Verlauf und Export halten dieselben Feld- und Mandantengrenzen wie das Profil ein. Private Daten werden nicht durch Nebenfunktionen oder ein nachfolgendes Browserkonto offengelegt.

**Belege:** Sollsichtbarkeit, Antwortfelder, Exportinhalt und Kontowechselbeobachtung mit ausschließlich eigenen Testdaten.

**Abhilfe:** Feldfreigaben auch für Suche und Export zentral anwenden, Downloadzugriff absichern und persistente Browserkopien privater Daten gezielt vermeiden beziehungsweise beim Kontextwechsel bereinigen.

## Ergänzende Hinweise

Weitere Tests: [Dateiupload](08-file-upload.md), [Rich Text](15-rich-text.md) und [Clientspeicher](13-client-storage.md). Datenexportfunktionen auf die technische Zugriffskontrolle prüfen; eine vollständige rechtliche Bewertung ist damit nicht verbunden.

## Quellen

- [WSTG-v42-ATHZ-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/03-Testing_for_Privilege_Escalation)
- [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting)
- [WSTG-v42-BUSL-08](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/08-Test_Upload_of_Unexpected_File_Types)
- [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
