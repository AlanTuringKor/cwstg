# 15 · Rich-Text und WYSIWYG-Editor

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Formatierte Nutzereingaben bleiben auf erlaubte Inhalte begrenzt. Editor, API, Vorschau, spätere Bearbeitung und alle weiteren Ausgaben verwenden eine konsistente Regel für HTML, URLs, eingebettete Medien und Formatierung.

## Voraussetzungen

- Testkonten für Autor, Leser und gegebenenfalls Moderator; eigene Testdokumente und -medien.
- Festgelegte erlaubte Elemente, Attribute, URL-Schemata, Embeds und Inhaltsgrößen. Unterstützte Browser sowie Parser-/Sanitizerversionen notieren.
- Zugriff auf API-Rohdaten und endgültigen DOM. Marker schreiben nur lokal in die Konsole oder verändern ein eigenes Testelement; keine fremden Sitzungsdaten auslesen.

## Testfälle

### CWSTG-15-01 — HTML und Attribute nach direktem API-Aufruf

**Referenzen:** [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting).

**Prüfschritte:**

1. Erlaubten formatierten Text speichern und daraus eine unveränderte Kontrollanfrage erstellen.
2. Über UI und direkt über die API ein unerlaubtes Attribut mit lokalem Marker einspeisen, etwa `<img src=x onerror="console.log('CWSTG-15-01')">`. Bei strukturiertem Editorformat auch ungültige Knoten/Attribute prüfen.
3. Als Leser Vorschau, gespeicherte Ansicht, erneute Bearbeitung und vorhandene Exporte öffnen. Rohwert und endgültigen DOM vergleichen.

**Sicheres Ergebnis:** Erlaubte Formatierung funktioniert; unerlaubte Elemente und Attribute erreichen keinen ausführbaren Kontext. Die API umgeht die Inhaltsregeln nicht. Ein ausgebliebener Dialog oder eine CSP-Blockierung allein beweist keine korrekte Bereinigung.

**Belege:** Kontroll-/Testanfrage, gespeicherte Ausgabe, DOM und Browser-/CSP-Kontext.

**Abhilfe:** Eingabeformat verbindlich validieren und erzeugtes HTML vor jeder relevanten HTML-Ausgabe nach einer gepflegten erlaubnisbasierten Regel bereinigen; reinen Text kontextgerecht kodieren.

### CWSTG-15-02 — URLs, Bildquellen und Attribute

**Referenzen:** [WSTG-v42-CLNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting); [OWASP XSS-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html).

**Prüfschritte:**

1. In Linkdialog und API erlaubte `https:`-Ziele sowie unerlaubte Schemata wie `javascript:` vergleichen. Auch Entities und Groß-/Kleinschreibung im tatsächlich dekodierten URL-Wert prüfen.
2. `href`, `src`, `srcset`, Poster und eingebettete Vorschau separat untersuchen; jede Liste und jedes URL-Feld erhält eine eigene Prüfung.
3. Links im eigenen Testdokument aktivieren und die tatsächliche Navigation bzw. Ressourcenanforderung beobachten.

**Sicheres Ergebnis:** Die erlaubten Schemata und Zielregeln gelten nach dem relevanten Parsing. `data:text/html` in einem `<img>` ist kein belastbarer JavaScript-PoC: Der Browser behandelt das Element als Bildkontext. Andere Dokument-/Navigationskontexte müssen separat geprüft werden.

**Belege:** Ursprungseingabe, endgültiger Attributwert, Elementkontext und beobachtete Anfrage.

**Abhilfe:** URLs mit einem passenden Parser prüfen, erlaubte Schemata/Ziele beschränken und Werte für das konkrete Attribut sicher ausgeben.

### CWSTG-15-03 — Dekodierung, Parserwechsel und nachträgliche Mutation

**Referenzen:** [WSTG-v42-CLNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting); [DOMPurify-Dokumentation](https://github.com/cure53/DOMPurify).

**Prüfschritte:**

1. Eine kleine Sammlung aus HTML-Entities, verschachtelten Elementen und erlaubter/nicht erlaubter Formatierung speichern.
2. Die Stufen Editorformat → API → HTML → DOM → erneute Bearbeitung vergleichen. JSON-Escapes wie `\u003c` nur dort als Dekodierungstest bewerten, wo tatsächlich JSON geparst wird.
3. Nachgelagerte Linkerkennung, Syntaxhervorhebung und Vorschau prüfen: Verändern sie bereits bereinigtes Markup und führen es erneut einem HTML-Parser zu?

**Sicheres Ergebnis:** Keine nachträgliche Umwandlung erzeugt einen zuvor entfernten gefährlichen Kontext. Mehrfaches Dekodieren ist kein pauschaler Fix; reine Text-Entities bleiben Text, solange sie nicht erneut als Markup geparst werden.

**Belege:** Minimale Eingabe und Wert/DOM an der ersten fehlerhaften Verarbeitungsstufe.

**Abhilfe:** Umwandlungsfolge festlegen, unnötiges erneutes HTML-Parsing vermeiden und die endgültige Ausgabe kontextgerecht bereinigen. Sanitizer samt DOM-Laufzeit aktuell halten.

### CWSTG-15-04 — SVG, MathML und Medienimporte

**Referenzen:** [WSTG-v42-BUSL-09](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files); [SVG als Bild](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image).

**Prüfschritte:**

1. Kleine SVG-/MathML-Fixtures mit erlaubten Elementen und lokalen Markern einfügen, sofern diese Formate unterstützt werden.
2. Inline-Markup, `<img>`, Medienbibliothek und eigenständige Dokumentansicht getrennt prüfen. Auch nach Copy-and-paste und erneuter Bearbeitung kontrollieren.
3. Externe Referenzen nur auf eigene vereinbarte Testadressen setzen; dokumentieren, ob Browser oder Server sie abrufen.

**Sicheres Ergebnis:** Erlaubte Formate behalten ihre festgelegten Grenzen. Die Einschränkungen von SVG als Bild gelten nicht automatisch für Inline-SVG oder ein SVG-Dokument. Ein sicherer Thumbnail beweist nichts über die öffentlich erreichbare Originaldatei.

**Belege:** Fixture, Einbettungsart, DOM und Protokoll der eigenen Testadresse.

**Abhilfe:** Nicht benötigte Namensräume/Formate sperren; nötige Inhalte kontextgerecht bereinigen oder isoliert in ein passives Zielformat umwandeln. Siehe [Medienanzeige](14-media-viewer.md).

### CWSTG-15-05 — CSS und Beeinflussung der Oberfläche

**Referenzen:** [WSTG-v42-CLNT-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/05-Testing_for_CSS_Injection).

**Prüfschritte:**

1. Erlaubte Textformatierung mit unerlaubten `style`-Eigenschaften, globalen Selektoren und `position: fixed` vergleichen.
2. Im Testdokument prüfen, ob Inhalte Anwendungsnavigation überdecken, fremde Bedienelemente nachbilden oder Ressourcen von einer eigenen Testadresse nachladen können.
3. Legacybeispiele wie `expression()` oder `background:url(javascript:...)` nur bei tatsächlich unterstützten alten Browsern als JavaScript-Test verwenden; Browserversion und konkrete Wirkung angeben.

**Sicheres Ergebnis:** Nutzereigene Gestaltung bleibt im vorgesehenen Bereich und innerhalb der erlaubten CSS-Eigenschaften/Werte. Moderne Browser müssen alte CSS-JavaScript-Beispiele nicht ausführen; deren Wirkungslosigkeit belegt keinen sicheren CSS-Parser.

**Belege:** Akzeptierte Eigenschaften, tatsächlicher Sichtbereich und kontrollierte Ressourcenanforderungen.

**Abhilfe:** Unnötige Inline-Styles sperren, Formatierung auf definierte Optionen begrenzen und beliebiges CSS bei Bedarf in ein isoliertes Dokument verlagern.

### CWSTG-15-06 — Eingefügte Office-Inhalte und Größenlimits

**Referenzen:** [WSTG-v42-INPV-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting); [DOMPurify-Dokumentation](https://github.com/cure53/DOMPurify).

**Prüfschritte:**

1. Kleine eigene Inhalte aus den unterstützten Office-/HTML-Quellen mit Kommentaren, eingebetteten Bildern und Links einfügen.
2. Zwischen Zwischenablage-HTML, gespeichertem Editorformat und späterer Ausgabe vergleichen. Dieselben Daten direkt an die API senden.
3. Mit begrenzten Fixtures unmittelbar an den vereinbarten Text-/Knoten-/Mediengrenzen prüfen. Bei blockierter Oberfläche oder ausufernder Verarbeitung abbrechen und Testinhalte entfernen.

**Sicheres Ergebnis:** Importierte Formatierung unterliegt denselben Regeln wie direkte Eingabe; versteckte Elemente und Metadaten schaffen keine neue Ausführungsmöglichkeit. Inhaltsgrenzen gelten auch ohne UI und Fehler hinterlassen keinen unkontrollierten Teilzustand.

**Belege:** Quelle/Importweg, minimales Fixture, bereinigte Ausgabe und Grenzwertreaktion.

**Abhilfe:** Importfunktionen in die gemeinsame Validierungs-/Bereinigungskette einbinden, Inhalte begrenzen und Parserregressionen mit kleinen Fixtures prüfen.

### CWSTG-15-07 — Embeds und Dokumentisolation

**Referenzen:** [Iframe-Sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe); [OWASP CSP](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html). CWSTG-Erweiterung für erlaubte Embeds.

**Prüfschritte:**

1. Erlaubte Embedprovider und Ziel-Origins erfassen. In UI und API eine eigene unerlaubte Test-URL sowie kontrollierte Weiterleitungen prüfen.
2. Origin, Sandbox- und Berechtigungsattribute des erzeugten Frames untersuchen. Mit Testmarkierungen Navigation, Popups und zulässige Kommunikation zum Elternfenster prüfen.
3. Direktaufruf des eingebetteten Inhalts gesondert testen: Die Sandbox des Elternfensters schützt diesen Aufruf nicht automatisch.

**Sicheres Ergebnis:** Nicht vertrauenswürdige Embeds erhalten keine unbeabsichtigten Rechte in der Anwendung. Bei gleicher Origin ist die Kombination `allow-scripts` und `allow-same-origin` als Sandboxschutz ungeeignet. Eine CSP gilt für ein Dokument; sie lässt sich nicht als `script-src 'none'` auf einen einzelnen Editorbereich beschränken.

**Belege:** Embed-URL/Origin, Attribute, Dokumentheader und beobachtete Interaktion.

**Abhilfe:** Provider und Fähigkeiten begrenzen, untrusted Inhalte auf separater Origin rendern und eine eigene CSP für das isolierte Dokument setzen. Nachrichten zusätzlich anhand von Origin, Quelle und Schema prüfen.

## Ergänzende Hinweise

Eine gepflegte Bibliothek ist nur mit geeigneter Konfiguration und Laufzeit wirksam. Bei serverseitigem DOMPurify müssen auch die verwendete DOM-Implementierung und deren Version geprüft werden. Reines Text-Escaping ist für Textausgaben richtig; bei ausdrücklich erlaubtem HTML ist eine passende HTML-Bereinigung erforderlich. Regressionstests sollten den tatsächlichen Parser-/Renderweg abdecken.

## Quellen

- [OWASP XSS-Prävention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [DOMPurify: Konfiguration, Laufzeit und nachträgliche Änderungen](https://github.com/cure53/DOMPurify)
- [MDN SVG-Bildkontexte](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image)
- [MDN Iframe-Sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)
- [OWASP Content Security Policy](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
