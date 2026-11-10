# 13 · Zustand und Speicher im Browser

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

In `localStorage`, `sessionStorage`, IndexedDB und Offline-Caches liegen nur die für die Funktion vorgesehenen Daten. Der Server vertraut keinem dort gespeicherten Berechtigungszustand. Kontowechsel, Ablauf und Abmeldung hinterlassen keine ungewollt nutzbaren Anmeldedaten oder fremden privaten Inhalte.

## Voraussetzungen

- Testkonten A und B und ein eigenes Browserprofil; Speicher nicht im Alltagsprofil verändern.
- Dokumentierte Sitzungsarchitektur, Offline-Anforderungen, Aufbewahrungsfristen und gewünschtes Verhalten beim Kontowechsel.
- DevTools, Netzwerkaufzeichnung und bei Implementierungszugriff die relevanten Speicher-/Workerfunktionen. In Belegen nur Schlüsselnamen, synthetische Werte oder gekürzte Tokenmerkmale festhalten.

## Testfälle

### CWSTG-13-01 — Speicherinventar und Geheimnisse

**Referenzen:** [WSTG-v42-CLNT-12](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/12-Testing_Browser_Storage).

**Prüfschritte:**

1. Vor und nach Anmeldung, Profilabruf und Offline-Nutzung `localStorage`, `sessionStorage`, IndexedDB und Cache Storage vergleichen.
2. Zweck, Lebensdauer und JavaScript-Zugriff jedes sicherheitsrelevanten Eintrags notieren. Auch in serialisiertem Anwendungszustand und API-Antwort-Caches suchen.
3. Gefundene Token anhand ihres tatsächlichen Einsatzes im Netzwerk einordnen. Ein JWT-Muster ist nur ein Suchhinweis; Base64 oder Verschlüsselung mit einem der Anwendung zugänglichen Schlüssel schafft keine Vertrauensgrenze gegenüber kompromittiertem Anwendungscode.

**Sicheres Ergebnis:** Keine Passwörter oder serverseitigen Geheimnisse; private Daten und persistente Anmeldetoken sind auf das dokumentierte Minimum begrenzt. Abweichungen von der vorgesehenen Sitzungsarchitektur werden anhand von Reichweite und Lebensdauer bewertet.

**Belege:** Inventartabelle mit Speicherart, Zweck, Zugriff und Aufbewahrung; Werte redigieren.

**Abhilfe:** Persistente Token vermeiden, Daten minimieren und eine serverseitige Sitzung oder andere zur Architektur passende Aufbewahrung wählen.

### CWSTG-13-02 — Reichweite eines Skriptzugriffs

**Referenzen:** [WSTG-v42-CLNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting); [HTML5-Sicherheit](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html).

**Prüfschritte:**

1. In einem eigenen Testprofil eine synthetische Markierung im betroffenen Speicher hinterlegen.
2. Bei einem separat nachgewiesenen XSS-Pfad ausschließlich diese Markierung lokal auslesen lassen; keine echten Token an einen Sammelserver übertragen.
3. Leserreichweite mit der Architektur abgleichen: Welche Anwendungen und eingebundenen Skripte laufen unter derselben Origin? Ist nur ein DevTools-Zugriff vorhanden, diesen nicht als XSS-Nachweis ausgeben.

**Sicheres Ergebnis:** Die bekannte JavaScript-Zugänglichkeit wird im Bedrohungsmodell berücksichtigt. `HttpOnly` verhindert das direkte Lesen eines Cookies durch JavaScript; XSS kann trotzdem Aktionen in der aktiven Sitzung auslösen.

**Belege:** Markierung, konkreter Ausführungspfad und betroffene Origin, getrennt vom eigentlichen XSS-Befund.

**Abhilfe:** XSS-Ursache beheben, Tokenexposition minimieren und fremden Anwendungscode bei Bedarf über getrennte Origins isolieren. Eine CSP ergänzt diese Maßnahmen.

### CWSTG-13-03 — Ablauf, Abmeldung und Kontowechsel

**Referenzen:** [WSTG-v42-SESS-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/06-Testing_for_Logout_Functionality); [WSTG-v42-CLNT-12](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/12-Testing_Browser_Storage).

**Prüfschritte:**

1. Als A private Testdaten laden, einen zweiten Tab öffnen und abmelden. Speicher, Offline-Ansicht und offenen Tab prüfen.
2. Im selben Profil als B anmelden und vorherige Ansichten einschließlich Offline-Daten öffnen. Einen Browserneustart gesondert testen; ein neues Inkognitofenster prüft nicht die Persistenz des alten Profils.
3. Ein vor Abmeldung erfasstes Testtoken innerhalb des vereinbarten Tests direkt gegen die API verwenden; Access- und Refresh-Token sowie das dokumentierte Ablauf-/Widerrufsfenster unterscheiden.

**Sicheres Ergebnis:** B erhält keine privaten Daten von A. Lokales Löschen und serverseitige Gültigkeit erfüllen jeweils die Sitzungsregeln. Ein lokales TTL-Feld erzwingt keinen serverseitigen Ablauf; ein gelöschtes Token allein ist kein Widerrufsnachweis.

**Belege:** Speicher-/Ansichtsvergleich und redigierte Wiederholungsanfragen mit Zeitpunkten.

**Abhilfe:** Kontogebundene Speicher und Caches beim Wechsel bereinigen; Logout zwischen Tabs synchronisieren und den vorgesehenen Widerruf serverseitig umsetzen.

### CWSTG-13-04 — Cookies und unbeabsichtigte Tokenkopien

**Referenzen:** [WSTG-v42-SESS-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/02-Testing_for_Cookies_Attributes).

**Prüfschritte:**

1. `Set-Cookie`, Cookiebereich und JavaScript-zugängliche Speicher gemeinsam untersuchen.
2. Prüfen, ob ein durch `HttpOnly` geschütztes Sitzungstoken zusätzlich in einer JSON-Antwort, URL, einem lesbaren Cookie oder Browserzustand erscheint.
3. Für Cookies Zweck und erforderliche Attribute bestimmen. Ein absichtlich JavaScript-lesbares CSRF-Token ist von einem Sitzungstoken zu unterscheiden.

**Sicheres Ergebnis:** Geschützte Anmeldedaten werden nicht unnötig kopiert. Authentifizierungscookies besitzen passende `Secure`-, `HttpOnly`-, `SameSite`- und Bereichseinstellungen; die Architektur enthält einen eigenen wirksamen CSRF-Schutz.

**Belege:** Redigierte Header und Herkunft einer etwaigen Kopie.

**Abhilfe:** Doppelte Tokenablage entfernen und Cookie-/CSRF-Regeln zusammen prüfen; Details unter [Sitzungen](11-sessions.md).

### CWSTG-13-05 — Nachrichtenkanäle und Service Worker

**Referenzen:** [WSTG-v42-CLNT-11](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/11-Testing_Web_Messaging).

**Prüfschritte:**

1. Nachrichten zwischen Fenstern, Tabs und Workern verfolgen; nur synthetische Daten verwenden.
2. Bei `postMessage` eine kontrollierte fremde Origin und ein unerwartetes Quellfenster prüfen. Vergleiche auf Teilzeichenfolgen und `targetOrigin: '*'` bei vertraulichen Nachrichten untersuchen.
3. Bei BroadcastChannel andere Testseiten derselben Origin/Speicherpartition einbeziehen. Worker-Nachrichten und Cacheantworten nach Kontowechsel prüfen.

**Sicheres Ergebnis:** Empfänger prüfen erwartete Origin, Quellfenster und Nachrichtenschema. BroadcastChannel ist kein Kanal für beliebige fremde Origins, aber auch keine eigene Vertrauensgrenze zwischen Anwendungen derselben Origin. Service Worker haben keinen direkten Zugriff auf `window.localStorage`; IndexedDB, Nachrichten und Caches bleiben prüfbar.

**Belege:** Sender/Empfänger, Markierung und akzeptierte/abgelehnte Nachrichten.

**Abhilfe:** Nachrichten auf erforderliche Daten begrenzen, Quellen exakt prüfen und Worker-/Cachezustand kontogebunden behandeln.

### CWSTG-13-06 — Speicherfehler und Größenbegrenzungen

**Referenzen:** [Browser-Speicherquoten](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria). CWSTG-Erweiterung zur Robustheit.

**Prüfschritte:**

1. Im isolierten Profil verweigerten Speicherzugriff oder eine Quotenexception durch einen Testhook simulieren. Keine fremden Nutzerdaten überschreiben und den Speicher nicht unkontrolliert füllen.
2. Die betroffene Funktion, einen Reload und Logout ausführen. Bei Teilzuständen kontrollieren, ob Anzeige und Serverstatus auseinanderlaufen.
3. Unterstützte Maximalgrößen an der Eingangsvalidierung mit kleinen Grenzwertfixtures prüfen; nach Fehlern und blockierter Oberfläche abbrechen.

**Sicheres Ergebnis:** Schreibfehler führen zu kontrolliertem Fallback oder einer verständlichen Fehlermeldung. Die Anwendung fällt nicht auf einen unsicheren Authentifizierungsweg zurück; Logout bleibt möglich.

**Belege:** Simulierter Fehler, Browserversion und sichtbarer/serverseitiger Zustand.

**Abhilfe:** Speicherzugriffe kapseln, Ausnahmen behandeln, Werte begrenzen und Teilzustände auflösen.

### CWSTG-13-07 — Manipulierter Clientzustand

**Referenzen:** [WSTG-v42-BUSL-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/01-Test_Business_Logic_Data_Validation).

**Prüfschritte:**

1. Im eigenen Profil lokale Felder wie `role`, `tenantId`, Preis oder Freigabestatus verändern und die Anwendung neu laden.
2. Eine zugehörige API-Operation mit dem manipulierten Zustand ausführen; Gegenprobe mit unverändertem Zustand festhalten.
3. Den tatsächlichen Serverzustand über einen unabhängigen berechtigten Abruf kontrollieren.

**Sicheres Ergebnis:** Lokaler Zustand beeinflusst höchstens vorgesehene Anzeigepräferenzen. Rechte, Mandant, Preise und Freigaben werden aus vertrauenswürdigen Serverdaten bestimmt; eine sichtbare Adminschaltfläche allein beweist keine Eskalation.

**Belege:** Verändertes Feld, resultierende Anfrage und unabhängig beobachtete Wirkung.

**Abhilfe:** Clientdaten als untrusted behandeln, sicherheitsrelevante Werte serverseitig bestimmen und jede Operation autorisieren.

## Quellen

- [OWASP Browser Storage, WSTG v4.2](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/12-Testing_Browser_Storage)
- [OWASP HTML5-Sicherheit](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [MDN BroadcastChannel](https://developer.mozilla.org/en-US/docs/Web/API/Broadcast_Channel_API)
- [MDN Service Worker](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [MDN Speicherquoten](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria)
