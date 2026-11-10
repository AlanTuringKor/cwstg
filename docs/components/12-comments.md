# 12 · Kommentare und Diskussionen

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Kommentare, Erwähnungen, Anhänge und Exporte bleiben an die Rechte des jeweiligen Threads gebunden. Fremde Inhalte dürfen beim Anzeigen, Moderieren oder Exportieren keinen ausführbaren Kontext erhalten. Veröffentlichungsregeln und Nutzungslimits gelten auch bei direkten API-Aufrufen.

## Voraussetzungen

- Zwei Testkonten A und B mit einem gemeinsamen Testthread, den beide lesen dürfen, sowie getrennten privaten Threads für Zugriffstests; ein Moderationskonto und bei Bedarf ein zweiter Mandant.
- Dokumentierte Regeln für HTML/Markdown, öffentliche Feeds, Bearbeitung, Freigabe und Benachrichtigungen.
- Ein isolierter Testthread und eigene Empfänger für Erwähnungen. Für Mengenprüfungen ein vereinbartes Limit und Abbruchkriterien; keine Benachrichtigungen an echte Nutzer.

## Testfälle

### CWSTG-12-01 — Gespeicherte Inhalte in allen Ansichten

**Referenzen:** [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting).

**Prüfschritte:**

1. Als A im gemeinsamen Testthread einen eindeutig markierten Kommentar mit HTML-Sonderzeichen und einer lokalen Ausführungsmarkierung wie `<img src=x onerror="console.log('CWSTG-12-01')">` speichern.
2. Als B und als Moderator Thread, Vorschau, Suchtreffer und Benachrichtigungsansicht öffnen. Nur Testempfänger verwenden.
3. Gespeicherten Wert, Antwort und endgültigen DOM vergleichen; auch eine Bearbeitung und erneute Anzeige prüfen.

**Sicheres Ergebnis:** Text bleibt Text; erlaubtes Rich-Text-HTML entspricht der festgelegten Bereinigungsregel. Keine unerlaubten Attribute, Elemente oder URL-Schemata erreichen einen ausführbaren Kontext. Ein ausgebliebener Konsoleneintrag allein genügt nicht: Auch blockierte Attribute im DOM und CSP-Meldungen untersuchen.

**Belege:** Kommentarkennung, bereinigte Eingabe/Ausgabe, DOM-Ausschnitt, Browserkontext und CSP-Befund.

**Abhilfe:** Für Text sichere Textausgabe verwenden; für HTML eine gepflegte, kontextgerechte Bereinigung nach der letzten Umwandlung einsetzen. Details: [Rich-Text](15-rich-text.md).

### CWSTG-12-02 — Anhänge und Verarbeitungsstatus

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files).

**Prüfschritte:**

1. Kleine Testdateien mit erlaubtem und unerwartetem Typ anhängen; Dateiname, deklarierten MIME-Typ und tatsächlichen Inhalt getrennt variieren.
2. Abruf von Original und Vorschau durch A, B und ohne Sitzung prüfen, auch während Scan/Freigabe noch ausstehen.
3. Eine Datei unmittelbar oberhalb der vereinbarten Größenobergrenze nur innerhalb des Uploadbudgets prüfen. Verarbeitung und Fehlerpfad beobachten, anschließend bereinigen.

**Sicheres Ergebnis:** Typ-, Größen- und Zugriffsregeln gelten für Anhänge und Ableitungen. Ausstehende oder abgelehnte Dateien werden nicht vorzeitig veröffentlicht. Ein erfolgreicher Virenscan ersetzt weder Typprüfung noch Isolation.

**Belege:** Upload/Abruf, Verarbeitungsstatus und bekannte Eigentümer der Dateien.

**Abhilfe:** Anhänge an Threadrechte koppeln, Verarbeitungsstatus serverseitig durchsetzen und [Uploadprüfungen](08-file-upload.md) übernehmen.

### CWSTG-12-03 — Kommentar- und Benachrichtigungslimits

**Referenzen:** [WSTG-v42-BUSL-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/05-Test_Number_of_Times_a_Function_Can_Be_Used_Limits).

**Prüfschritte:**

1. In einer Testkonfiguration das Nutzungslimit niedrig setzen lassen und die erlaubte Anzahl Kommentare einschließlich einer Wiederholung prüfen.
2. Innerhalb desselben Budgets eine Erwähnung und eine Bearbeitung einbeziehen: Werden neue Nachrichten oder weitere Moderationsjobs ausgelöst?
3. Nach dem vereinbarten Zeitfenster einen zulässigen Kommentar senden. Bei unerwarteten Benachrichtigungen, 5xx oder steigender Warteschlange abbrechen.

**Sicheres Ergebnis:** Das dokumentierte Budget begrenzt auch Folgewirkungen wie E-Mails und Verarbeitung. Abgelehnte Anfragen veröffentlichen keinen Kommentar. Reguläre Nutzung funktioniert nach Ablauf der Sperre wieder.

**Belege:** Zeitfolge, tatsächlich erzeugte Kommentare/Benachrichtigungen und Limitkonfiguration.

**Abhilfe:** Konten-, Thread- und Empfängerbudgets auf dem Server prüfen; Wiederholungen entprellen und Warteschlangen begrenzen.

### CWSTG-12-04 — Markdown, Erwähnungen und Linkvorschau

**Referenzen:** [WSTG-v42-CLNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting); [SSRF-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).

**Prüfschritte:**

1. Im gemeinsamen Testthread Erwähnungen mit Sonderzeichen, Markdownlinks mit unerlaubten Schemata und verschachtelte Formatierung speichern.
2. Den erzeugten Link, tatsächliche Zieldomain und HTML nach automatischer Linkerkennung prüfen. Auch abweichende Linkbeschriftung, Unicode-Domain und kontrollierte Weiterleitung mit den Produktregeln abgleichen. Als B erneut anzeigen.
3. Falls der Server Vorschauen abruft: eine eigene Test-URL mit protokolliertem Abruf und einer kontrollierten Weiterleitung verwenden. Nur vereinbarte Zieladressen testen.

**Sicheres Ergebnis:** Parserausgabe bleibt innerhalb der erlaubten HTML-/URL-Regeln; die Darstellung verschleiert das tatsächliche Linkziel nicht entgegen den Produktregeln. Eine Vorschau darf keine beliebigen Ziele abrufen oder vertrauliche Anmeldedaten mitsenden; Weiterleitungen unterliegen derselben Zielprüfung. HTML-Bereinigung allein bewertet nicht die Vertrauenswürdigkeit eines Linkziels.

**Belege:** Eingabe, endgültiger Link/DOM und Abrufprotokoll der eigenen Testadresse.

**Abhilfe:** Nach Markdown-/Erwähnungsumwandlung bereinigen, URL-Schemata erlaubnisbasiert prüfen und Vorschauabrufe isolieren.

### CWSTG-12-05 — Formeln in CSV-Exporten

**Referenzen:** [OWASP CSV Injection](https://owasp.org/www-community/attacks/CSV_Injection). CWSTG-Erweiterung ohne eigene WSTG-v4.2-Testkennung.

**Prüfschritte:**

1. Testkommentare mit harmlosen Formelmarkierungen wie `=1+1` sowie führenden Tabulatoren, Anführungszeichen und dem tatsächlichen Feldtrenner anlegen.
2. CSV exportieren; zunächst Rohdatei und Zellgrenzen prüfen. Anschließend in einer isolierten Umgebung mit den unterstützten Tabellenprogrammen importieren.
3. Speichern und erneut öffnen. Importoptionen und Programmversion notieren; keine Formeln mit Netzwerk- oder Befehlsaufrufen verwenden.

**Sicheres Ergebnis:** Nutzertext bleibt in den unterstützten Export-/Importwegen Text. CSV-Anführungszeichen allein verhindern keine Formelauswertung; ein Apostroph ist keine universelle Lösung für jedes Tabellenprogramm und jeden erneuten Export.

**Belege:** Minimale CSV, Importoptionen und tatsächlicher Zelltyp vor/nach erneutem Öffnen.

**Abhilfe:** Tabellenexport mit ausdrücklich als Text typisierten Zellen bevorzugen oder ein getestetes, dokumentiertes CSV-Schutzverfahren verwenden.

### CWSTG-12-06 — Zugriff auf Kommentare, Feeds und Exporte

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References).

**Prüfschritte:**

1. Einen privaten Kommentar von A mit bekannter Kennung erstellen. Als B und ohne Sitzung Lese-, Bearbeitungs-, Lösch- und Anhangsabrufe wiederholen.
2. Öffentliche Feeds, Suchtreffer, Exportjobs und deren Downloadlinks auf die Markierung des privaten Kommentars prüfen.
3. Rechte entziehen und die bekannten URLs erneut abrufen. Auch Zähler und Threadtitel auf unerlaubte Informationen prüfen.

**Sicheres Ergebnis:** Jede Operation respektiert Objekt-, Thread- und Mandantenrechte. Private Inhalte und Metadaten fehlen in unberechtigten Antworten; verweigerte Änderungen wirken sich nicht auf das Objekt aus.

**Belege:** Berechtigungsmatrix, direkte Anfragen und Zustandsvergleich des Kommentars.

**Abhilfe:** Gemeinsame Autorisierungsprüfung für UI, API, Feeds und Hintergrundexporte einsetzen; abgeleitete Downloadrechte mitprüfen.

### CWSTG-12-07 — Moderationsablauf und nachträgliche Bearbeitung

**Referenzen:** [WSTG-v42-BUSL-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/06-Testing_for_the_Circumvention_of_Work_Flows).

**Prüfschritte:**

1. Einen nach den dokumentierten Regeln prüfpflichtigen Testkommentar erstellen. Direktabruf, Feed und Benachrichtigungen vor Freigabe prüfen.
2. Einen freigegebenen Kommentar bearbeiten und die erforderliche erneute Prüfung beobachten. Statusfelder wie `approved` im eigenen API-Aufruf verändern.
3. Wenige vereinbarte Unicode-/Leerzeichenvarianten prüfen. Zwischen verbindlichen Veröffentlichungsregeln und statistischer Spamklassifikation unterscheiden.

**Sicheres Ergebnis:** Autoren können Freigabe und Rollen nicht selbst setzen; unveröffentlichte Inhalte bleiben gesperrt. Änderungen umgehen keine vorgeschriebene Prüfung. Eine übersehene Spamvariante wird anhand der tatsächlichen Schutzanforderung bewertet.

**Belege:** Statusübergänge, beteiligte Rollen und Sichtbarkeit jeder Version.

**Abhilfe:** Freigaben an eine Inhaltsversion binden, Moderationsaktionen autorisieren und Statusübergänge nachvollziehbar protokollieren.

## Quellen

- [OWASP XSS-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP Dateiupload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [OWASP CSV Injection](https://owasp.org/www-community/attacks/CSV_Injection)
- [OWASP SSRF-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
