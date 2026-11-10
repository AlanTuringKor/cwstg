# 08 · Datei-Upload und Medienverwaltung

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Dateien werden nur im vorgesehenen Format angenommen, innerhalb ihrer Berechtigungsgrenzen verarbeitet und sicher ausgeliefert. Uploads dürfen weder ausführbaren Servercode noch unkontrollierte Browserinhalte oder unbegrenzte Verarbeitungsarbeit erzeugen.

## Voraussetzungen

- Erlaubte Dateitypen, Größen, Pixel-/Seitenlimits, Scanpflicht und Freigabezustände festhalten. Upload, Verarbeitung, Original, Vorschaubild und Download als getrennte Stationen erfassen.
- Konten A/B mit getrennten Dateien und gegebenenfalls Testmandanten vorbereiten; nur eigene Testobjekte überschreiben oder löschen.
- Kleine, harmlose Testdateien mit eindeutigen Markern verwenden. Parser-Exploitprüfungen und Ressourcenprüfungen in einer isolierten Umgebung mit festgelegten Budgets durchführen. Keine Webshells installieren.

## Testfälle

### CWSTG-08-01 — Dateityp und Inhalt unabhängig vom Client prüfen

**Referenzen:** [WSTG-v42-BUSL-08](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/08-Test_Upload_of_Unexpected_File_Types).

**Prüfschritte:**

1. Eine gültige kleine Datei als Kontrolle hochladen. Danach dieselbe Datei mit falschem `Content-Type` und abweichender Endung sowie eine kleine Textdatei mit Bildendung senden.
2. Doppelte Endungen wie `probe.php.jpg`, Groß-/Kleinschreibung und einen ungültigen Dateikörper mit lediglich passender Signatur prüfen; keine ausführbare Nutzlast verwenden.
3. Direkte API-, Mehrfach- und gegebenenfalls Chunk-Uploads auf identische serverseitige Regeln prüfen. Annahme, Verarbeitung und Veröffentlichung getrennt beobachten.

**Sicheres Ergebnis:** Die dokumentierte Dateipolitik greift auf allen Wegen. Endung, Client-MIME und Magic Bytes sind nur Hinweise; nicht interpretierbare oder unzulässige Inhalte werden nicht als vertrauenswürdige Datei veröffentlicht.

**Belege:** Dateihash, Name, deklarierter Typ, Größenangaben und Status jeder Verarbeitungsstation.

**Abhilfe:** Formate auf eine Positivliste beschränken, Inhalte mit geeigneten Parsern validieren und bei Bildern gegebenenfalls sicher neu kodieren. Sicherheitsregeln nach dem vollständigen Zusammenfügen erneut anwenden.

### CWSTG-08-02 — Dateinamen und Speicherpfade trennen

**Referenzen:** [WSTG-v42-ATHZ-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/01-Testing_Directory_Traversal_File_Include).

**Prüfschritte:**

1. Im eigenen Testbereich Dateinamen mit `../`, Backslash, kodierten Trennzeichen und kollidierenden Namen übertragen.
2. Rückgabe, gespeicherten Objektschlüssel und Downloadnamen vergleichen; kontrollieren, ob bestehende Testdateien unerwartet ersetzt werden.
3. Falls Dateisystemzugriff besteht, die tatsächliche Ablagegrenze prüfen. Ohne diese Sichtbarkeit keine sichere Pfadablage allein aus einer unveränderten URL ableiten.

**Sicheres Ergebnis:** Nutzernamen dienen höchstens als Anzeigename. Dateien bleiben im zugewiesenen Speicherbereich und überschreiben keine fremden Objekte oder Konfigurationen.

**Belege:** Multipart-Dateiname, serverseitiger Schlüssel und Zustand der vorbereiteten Testobjekte.

**Abhilfe:** Speicherpfade und Objekt-IDs serverseitig erzeugen, Pfadgrenzen nach Normalisierung prüfen und Downloadnamen sicher für HTTP-Header kodieren.

### CWSTG-08-03 — Ausführung über Uploadpfade verhindern

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files).

**Prüfschritte:**

1. Auslieferung einer harmlosen Markerdatei über Original-URL, Vorschau und Download beobachten. Auf Weiterleitungen zu App-Servern oder anderen Handlern achten.
2. Mit Konfigurationszugriff prüfen, ob Uploadpfade Skript-Handler, serverseitige Includes oder ausführbare Delegates erreichen können.
3. Eine Ausführungsprüfung nur bei gesondertem Bedarf in der isolierten Testumgebung mit einem wirkungslosen Marker durchführen; keine Befehlsausführung oder Persistenz hinzufügen.

**Sicheres Ergebnis:** Uploads werden als Daten behandelt und gelangen nicht an ausführende Handler. Das Ausbleiben einer sichtbaren Ausgabe ist kein Beweis für fehlende Serverausführung.

**Belege:** Routing-/Handlerkonfiguration, Antwortheader, Dateiinhalt und gegebenenfalls isolierte Verarbeitungstraces.

**Abhilfe:** Uploadablage außerhalb ausführbarer Webpfade oder auf separatem Speicher betreiben; Skriptausführung für alle Auslieferungsvarianten deaktivieren.

### CWSTG-08-04 — Dateinamen und Metadaten sicher darstellen

**Referenzen:** [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting).

**Prüfschritte:**

1. HTML-Sonderzeichen und einen eindeutigen Marker in Dateinamen, Beschreibung und unterstützte EXIF-Felder einer kleinen Datei eintragen.
2. Galerie, Tooltip, Detailansicht und Moderationsoberfläche aufrufen; tatsächlichen DOM-Kontext untersuchen.
3. In einem Testbrowser nur bei Bedarf einen passenden harmlosen Ausführungsmarker testen und Darstellung aus einem zweiten berechtigten Konto vergleichen.

**Sicheres Ergebnis:** Metadaten werden als Daten ausgegeben oder nach definierter HTML-Politik bereinigt. Kein ungeprüfter Inhalt erreicht Attribute, Skriptkontexte oder HTML-Sinks.

**Belege:** Ursprungsmetadaten, API-Ausgabe und resultierender DOM-Ausschnitt.

**Abhilfe:** Metadaten minimieren und kontextgerecht kodieren; für reine Textanzeige sichere Text-APIs verwenden.

### CWSTG-08-05 — SVG und aktive Dokumente je Renderkontext prüfen

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files); ergänzend [MDN: SVG als Bild](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image).

**Prüfschritte:**

1. Eine kleine SVG mit harmlosem lokalen Skriptmarker und eine Variante mit einer freigegebenen externen Testressource vorbereiten.
2. Die tatsächlich vorhandenen Kontexte getrennt prüfen: `<img>`, CSS-Bild, Inline-SVG, `<object>`, Vorschau und direkter Dokumentaufruf.
3. Browserkonsole und Netzwerk beobachten; bei Konvertierung zusätzlich prüfen, ob der Server externe Ressourcen nachlädt.

**Sicheres Ergebnis:** Kein unerlaubter aktiver Inhalt oder Ressourcenabruf entsteht. SVG im Bildkontext hat andere Einschränkungen als ein direkt geöffnetes SVG-Dokument; ein sicherer `<img>`-Test deckt andere Kontexte nicht ab.

**Belege:** SVG-Datei, Einbettungsart, Antwortheader, DOM und Browser-/Servernetzwerkprotokoll.

**Abhilfe:** Nicht benötigte aktive Formate ablehnen, gezielt bereinigen oder isoliert rasterisieren. Aktive Dokumente getrennt vom Anwendungsorigin und mit passender Download-/Sandbox-Politik ausliefern.

### CWSTG-08-06 — Parser und Konverter isolieren

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files); ergänzend [ImageMagick Security Policy](https://imagemagick.org/security-policy/).

**Prüfschritte:**

1. Eingesetzte Parser, Versionen, Konvertierungswerkzeuge und aktivierte Formate erfassen. Bekannte einschlägige Sicherheitsmeldungen mit der tatsächlichen Konfiguration abgleichen.
2. Kleine beschädigte Dateien im Testsystem verarbeiten; Behandlung von Parserfehlern und Jobabbrüchen beobachten.
3. Rechte, Netzwerkzugriff, Prozess-/Speicherlimits und erlaubte Delegates des Workers prüfen. Konkrete Exploitregressionen nur im isolierten Labor ausführen.

**Sicheres Ergebnis:** Fehler bleiben auf den Auftrag begrenzt; Verarbeitung läuft mit minimalen Rechten und wirksamen Ressourcen-/Netzwerkgrenzen. Ein erfolgreicher Scan ersetzt diesen Schutz nicht.

**Belege:** Versions-/Konfigurationsauszug, Workerrechte und zugehörige Jobprotokolle.

**Abhilfe:** Parser aktuell halten, unnötige Formate/Delegates sperren und Verarbeitung in beschränkte Worker auslagern.

### CWSTG-08-07 — Datei-, Verarbeitungs- und Kontingentlimits durchsetzen

**Referenzen:** [WSTG-v42-BUSL-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/07-Test_Defenses_Against_Application_Misuse).

**Prüfschritte:**

1. In einer Testkonfiguration kleine Limits setzen. Je eine Datei knapp unter, auf und knapp über der Grenze übertragen.
2. Pixelzahl, Seitenzahl, entpackte Größe und Chunk-Gesamtgröße getrennt prüfen; keine unbeschränkten Dekompressionsbomben verwenden.
3. Höchstens die vereinbarte Zahl gleichzeitiger kleiner Jobs starten. Bei Queue-, Speicher-, Latenz- oder Fehlergrenze stoppen und temporäre Testdateien entfernen.

**Sicheres Ergebnis:** Grenzen greifen vor kostspieliger Verarbeitung und gelten auch für zusammengesetzte Uploads. Abgebrochene Aufträge geben reservierten Speicher und Kontingente frei.

**Belege:** Konfigurierte Grenzen, gemessene Größen, Jobverlauf und Ressourcenmetriken.

**Abhilfe:** Byte-, Pixel-, Seiten-, Laufzeit- und Kontingentlimits über Proxy, Anwendung, Speicher und Worker hinweg konsistent durchsetzen.

### CWSTG-08-08 — Objektberechtigungen und signierte URLs prüfen

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References), [WSTG-v42-CLNT-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/07-Testing_Cross_Origin_Resource_Sharing); ergänzend [AWS: Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).

**Prüfschritte:**

1. Lesen, Ändern, Löschen und Vorschaubilder von A als B, anonym und aus einem anderen Testmandanten anfordern.
2. Bei signierten URLs Methode, Objektpfad und Ablaufzeit einzeln variieren. Wiederverwendung und Überschreiben nur am eigenen Testobjekt prüfen.
3. Bekannte Testobjekte auf öffentliche Lese-/Schreibrechte prüfen; CORS aus einem kontrollierten fremden Origin testen. Keine fremden Buckets oder Inhalte durchsuchen.

**Sicheres Ergebnis:** Nur beabsichtigte Rechte werden gewährt. Signierte URLs sind Bearer-Berechtigungen und bei S3 regulär bis zum Ablauf wiederverwendbar; zusätzliche Einmaligkeit muss die Anwendung umsetzen. CORS ersetzt keine Objektberechtigung.

**Belege:** Rechte-/Mandantenmatrix, redigierte URLparameter, Ablaufgrenzen und tatsächliche Objektzustände.

**Abhilfe:** Private Standards, passende IAM-/Objektrechte, kurze zweckgerechte Laufzeiten und gebundene Objektschlüssel nutzen. Freigabe erst nach Inhaltsprüfung; Überschreiben entsprechend der Produktanforderung verhindern.

### CWSTG-08-09 — Auslieferungsheader und private Caches prüfen

**Referenzen:** [WSTG-v42-ATHN-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/06-Testing_for_Browser_Cache_Weaknesses).

**Prüfschritte:**

1. Für Original, Vorschau und Download `Content-Type`, `Content-Disposition`, `X-Content-Type-Options` und Cachevorgaben aufzeichnen.
2. Nach Abruf als A dieselbe private Datei als B und anonym über denselben CDN-Pfad anfordern; tatsächliche Antwortinhalte vergleichen.
3. Direktaufruf und Download im unterstützten Browser testen. Dateiendung oder `nosniff` allein beweisen keine sichere Darstellung aller Dokumenttypen.

**Sicheres Ergebnis:** Inhalte werden mit passendem Typ und beabsichtigtem Darstellungsmodus geliefert; private Dateien gelangen nicht über gemeinsame Caches an andere Konten.

**Belege:** Header, Browserkontext, Cacheindikatoren und markierte Dateiinhalte aus beiden Konten.

**Abhilfe:** Sichere Typ-/Downloadvorgaben zentral setzen, aktive Inhalte isolieren und private Antworten mit geeigneter Cachepolitik schützen. `private` und `no-store` haben unterschiedliche Speicherwirkungen.

### CWSTG-08-10 — Quarantäne und Scanfehler behandeln

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files); ergänzend [EICAR-Testdatei](https://www.eicar.org/download-anti-malware-testfile/).

**Prüfschritte:**

1. Falls Malwareprüfung vorgesehen ist, einen vereinbarten EICAR-Testfall durch den tatsächlichen Uploadweg senden und Scanereignisse zuordnen.
2. Original und Vorschau vor Freigabe, nach Erkennung sowie bei simuliertem Scannerfehler im Testsystem abrufen.
3. Prüfen, ob Wiederholungen, Timeouts oder ein neuer Upload unter demselben Schlüssel eine bereits geprüfte Datei unbemerkt ersetzen können.

**Sicheres Ergebnis:** Ungeprüfte oder abgelehnte Dateien bleiben entsprechend der festgelegten Politik gesperrt. Ein erkannter EICAR-Test bestätigt die geprüfte Pipeline, keine vollständige Malwareerkennung.

**Belege:** Dateihash, Quarantäne-/Freigabeübergänge, Scanergebnis und Abrufversuche.

**Abhilfe:** Prüfung und Freigabe an eine unveränderliche Dateiversion binden, Fehlerzustände definieren und Zugriff bis zur erforderlichen Freigabe verhindern.

### CWSTG-08-11 — Import-URLs und externe Ressourcen begrenzen

**Referenzen:** Ergänzende Prüfung nach [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html); kein eigener Datei-Upload-Testbezeichner im WSTG 4.2.

**Prüfschritte:**

1. Falls „Von URL importieren“ oder serverseitiges Nachladen vorhanden ist, eine kontrollierte Test-URL mit eindeutiger Markierung angeben.
2. Mit dafür bereitgestellten Testendpunkten Weiterleitungen, erlaubte Protokolle, DNS-Auflösung und Zielgrenzen prüfen; keine produktiven internen Dienste oder Cloud-Metadaten abrufen.
3. Downloadgröße, Zeitlimit und Weitergabe von Authentifizierungsheadern über Weiterleitungen beobachten.

**Sicheres Ergebnis:** Der Server erreicht nur zulässige Ziele und gibt keine Anwendungsgeheimnisse weiter. Zielprüfung gilt erneut nach Auflösung und Weiterleitung.

**Belege:** Importanfrage, kontrollierte Zielprotokolle und Egress-/Timeoutkonfiguration.

**Abhilfe:** Ziele und Protokolle einschränken, Netzwerk-Egress begrenzen und Redirect-, Größen- sowie Zeitbudgets durchsetzen.

## Quellen

- Die Testfälle verlinken die jeweiligen OWASP-WSTG-Szenarien in Version 4.2.
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [AWS: Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- [MDN: SVG als Bild](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image)
- [ImageMagick Security Policy](https://imagemagick.org/security-policy/)
- [EICAR-Testdatei](https://www.eicar.org/download-anti-malware-testfile/)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
