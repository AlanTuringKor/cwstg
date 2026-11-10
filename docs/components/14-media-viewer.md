# 14 · Galerie und Medienanzeige

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Originale, Vorschaubilder und Metadaten werden nur im vorgesehenen Kontext und für berechtigte Nutzer ausgeliefert. Die Verarbeitung von Medien bleibt isoliert; öffentliche Ansichten geben keine unerwünschten Standort- oder Personendaten preis.

## Voraussetzungen

- Testkonten A und B, private und öffentliche Testmedien sowie eine Liste aller Ableitungen: Original, Thumbnail, Download, Transkodierung und Metadaten-API.
- Kleine selbst erstellte Dateien mit synthetischen Metadaten; Browser und gegebenenfalls Metadatenwerkzeug.
- Dokumentierte Regeln für Freigabe, signierte URLs, Metadaten und Cacheverhalten. Für Verarbeitungstests ein festes Datei-/Pixel-/Zeitbudget und Zugriff auf Testumgebungslogs.

## Testfälle

### CWSTG-14-01 — Metadaten als HTML-Eingabe

**Referenzen:** [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting).

**Prüfschritte:**

1. In einem kleinen Testbild Kommentar, Titel und Dateiname mit eindeutiger Markierung und HTML-Sonderzeichen setzen; zusätzlich einen lokalen XSS-Marker verwenden.
2. Galerie, Detailseite, Tooltip, Verwaltungsansicht und Metadaten-API mit A und einem berechtigten zweiten Testkonto öffnen.
3. Metadatenwert, Antwort und DOM vergleichen. Exiftool oder ein vergleichbares Werkzeug dient zur Prüfung der Datei, der Browser zur Prüfung der HTML-Ausgabe.

**Sicheres Ergebnis:** Metadaten werden als Text ausgegeben oder nach einer ausdrücklich erlaubten HTML-Regel bereinigt. Der bloße Besitz eines EXIF-Felds mit HTML bedeutet keine XSS-Schwachstelle; entscheidend ist dessen Weg in einen ausführbaren Kontext.

**Belege:** Testdatei, betroffenes Metadatenfeld, Ansichtsroute und DOM-Ausschnitt.

**Abhilfe:** Metadaten kontextgerecht ausgeben, unnötige Felder entfernen und dieselbe Ausgaberegel auch in der Verwaltung anwenden.

### CWSTG-14-02 — Rechte auf Originale und Ableitungen

**Referenzen:** [WSTG-v42-ATHZ-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References).

**Prüfschritte:**

1. Als A ein privates Medium erstellen und die bekannten URLs aller Ableitungen erfassen.
2. Mit B, ohne Sitzung und gegebenenfalls aus einem anderen Testmandanten dieselben Ressourcen abrufen; auch alternative Download-/Range-Endpunkte einbeziehen.
3. Freigabe entziehen und erneut prüfen. Bei signierten URLs Ablauf, erlaubtes Objekt und dokumentierte Widerrufsregeln prüfen; gültige Freigabelinks sind selbst Zugriffsberechtigungen.

**Sicheres Ergebnis:** Unberechtigte erhalten weder Bytes noch sensible Metadaten. Ableitungen erben die geltenden Rechte. Zufällige Dateinamen ersetzen keine Autorisierung; ein noch gültiger signierter Link wird entsprechend seiner vorgesehenen Freigabefunktion bewertet.

**Belege:** Eigentümer-/Freigabematrix, direkte Abrufe und redigierte URL-Eigenschaften.

**Abhilfe:** Objekt- und Mandantenrechte zentral durchsetzen; signierte URLs eng an Objekt, Nutzung und Laufzeit binden.

### CWSTG-14-03 — MIME-Typ und tatsächlicher Browserkontext

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files); [X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options).

**Prüfschritte:**

1. Eine gültige Rastergrafik sowie kleine Dateien mit widersprüchlicher Endung, MIME-Deklaration und Inhalt im Testupload prüfen.
2. Header und reale Auslieferung für Original und Vorschau erfassen. Direktnavigation und Einbettung separat prüfen.
3. Falls SVG erlaubt ist, `<img>`, direkte Dokumentnavigation und erlaubte `<object>`-/Iframe-Ansichten unterscheiden.

**Sicheres Ergebnis:** Der Server bestimmt einen konkreten geprüften Medientyp und setzt passende Header. `nosniff` ergänzt diese Regeln, macht aktive SVG-/HTML-Dokumente jedoch nicht passiv. Ein an eine JPEG-Datei angehängtes Skript beweist keine Browserausführung.

**Belege:** Dateityp, tatsächlicher Inhalt, Response-Header, Browserversion und Einbettungsart.

**Abhilfe:** Erlaubte Formate tatsächlich dekodieren/prüfen, Ableitungen kontrolliert neu erzeugen und aktive Formate gesondert behandeln.

### CWSTG-14-04 — Inlineanzeige, Download und isolierte Origin

**Referenzen:** [SVG als Bild](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image); [Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition). CWSTG-Erweiterung zur Auslieferungsarchitektur.

**Prüfschritte:**

1. Für jedes erlaubte Format dokumentieren, ob es als Bild, eigenständiges Dokument oder Download angeboten wird.
2. Einen kleinen SVG-Marker in den tatsächlich angebotenen Kontexten prüfen. In SVG-Bildkontexten ist JavaScript eingeschränkt; direkte Dokumentansichten besitzen andere Möglichkeiten.
3. Downloadnamen mit Sonderzeichen prüfen und die Origin aktiver Inhalte mit der Anwendungsorigin vergleichen.

**Sicheres Ergebnis:** Unvertrauenswürdige aktive Inhalte erhalten keinen unbeabsichtigten Zugriff auf die Anwendungsorigin. `attachment` steuert die Downloadbehandlung, ist aber weder eine Berechtigungsprüfung noch eine Garantie für sicheres späteres Öffnen. Zulässige Inlineansichten besitzen eine passende Isolation.

**Belege:** Auslieferungskontext, Origin, Header und beobachtete Markerwirkung.

**Abhilfe:** Aktive Formate ablehnen, kontrolliert umwandeln oder auf separater Origin mit eigener restriktiver Dokumentrichtlinie bereitstellen.

### CWSTG-14-05 — Standort- und Personenmetadaten

**Referenzen:** [OWASP Datenschutz](https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html). CWSTG-Erweiterung zur Datenminimierung.

**Prüfschritte:**

1. Ein eigenes Testfoto mit synthetischen GPS-, Autor-, Geräte- und Kommentarfeldern hochladen.
2. Öffentliche Vorschau, Downloadoriginal, Metadaten-API und Export separat untersuchen. Mit berechtigten und öffentlichen Ansichten vergleichen.
3. Falls die Anwendung Metadaten bewusst erhält, Zweck und sichtbare Freigaberegel mit dem Produktverhalten abgleichen.

**Sicheres Ergebnis:** Nur die für den jeweiligen Empfänger vorgesehenen Metadaten werden veröffentlicht. Ein bereinigtes Thumbnail reicht nicht, wenn der öffentliche Originaldownload weiterhin ungewollte GPS-Daten enthält.

**Belege:** Synthetische Felder vor Upload und in jeder ausgelieferten Variante.

**Abhilfe:** Nicht benötigte Metadaten in allen öffentlichen Ableitungen entfernen; erforderliche Originale separat schützen.

### CWSTG-14-06 — Sichere Medienverarbeitung

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files); [ImageMagick-Sicherheitsrichtlinie](https://imagemagick.org/security-policy/).

**Prüfschritte:**

1. In der Testumgebung Verarbeitungsbibliotheken, erlaubte Decoder, Delegates, Netzwerkzugriff und Rechte des Workerprozesses erfassen.
2. Kleine abgeschnittene Dateien und begrenzte Grenzwertfixtures für Pixelzahl, Seitenzahl oder Dauer einzeln verarbeiten. Keine Exploitdateien zur Befehlsausführung verwenden.
3. Fehler, temporäre Dateien, Queue und Ressourcen beobachten; beim vereinbarten Zeit-/Speichergrenzwert, 5xx oder wachsendem Rückstau abbrechen.

**Sicheres Ergebnis:** Ungültige Dateien scheitern kontrolliert; Jobs besitzen harte Grenzen und geringe Rechte. Nicht benötigte Dateisystem-/Netzwerkzugriffe sind unterbunden. Ausbleibende Abstürze allein belegen keine Abwesenheit von Codeausführungsfehlern.

**Belege:** Versions-/Konfigurationsbefund, Dateihash und begrenzter Jobverlauf.

**Abhilfe:** Decoder und Delegates reduzieren, Bibliotheken pflegen und Verarbeitung mit Ressourcenlimits isolieren.

### CWSTG-14-07 — Private Medien in Browser- und CDN-Caches

**Referenzen:** [WSTG-v42-ATHN-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/06-Testing_for_Browser_Cache_Weaknesses); [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html).

**Prüfschritte:**

1. Ein privates, eindeutig markiertes Testmedium über den tatsächlichen CDN-Pfad als A abrufen; Cacheheader und Cachetreffer erfassen.
2. Dieselbe URL als B und ohne Sitzung abrufen. Rechteentzug, Ablauf und bedingte Anfragen gemäß Freigabemodell prüfen.
3. Im bisherigen Browserprofil nach Logout zurücknavigieren; HTTP-Cache, Verlaufssnapshot und Service-Worker-Cache getrennt erfassen.

**Sicheres Ergebnis:** Gemeinsame Caches liefern keine fremden privaten Medien. `private` erlaubt Browsercache, verhindert aber gemeinsame Speicherung; `no-store` untersagt neue Speicherung durch HTTP-Caches. Bereits gespeicherte Kopien werden dadurch nicht nachträglich gelöscht. Das vereinbarte Anzeigeverhalten nach Logout wird eingehalten.

**Belege:** Abruffolge, Cachetreffer, Kontokontext und tatsächlich empfangene Bytes.

**Abhilfe:** Private Antworten vom gemeinsamen Cache ausschließen, sensible Inhalte entsprechend der Aufbewahrungsregel behandeln und vorhandene unzulässige CDN-Kopien entfernen.

## Quellen

- [OWASP Dateiupload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [MDN SVG-Bildkontexte](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image)
- [ImageMagick-Sicherheitsrichtlinie](https://imagemagick.org/security-policy/)
- [RFC 9111: HTTP-Caching](https://www.rfc-editor.org/rfc/rfc9111.html)
