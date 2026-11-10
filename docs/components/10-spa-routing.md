# 10 · SPA-Routing und Hintergrundkommunikation

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Clientseitige Routen, versteckte Bedienelemente und lokale Zustände steuern die Oberfläche. Die dahinterliegenden Serverfunktionen müssen ihre eigenen Berechtigungen durchsetzen; Bundles, Vorabladen und dauerhafte Verbindungen dürfen keine geschützten Daten offenlegen.

## Voraussetzungen

- Testkonten mit verschiedenen Rollen und gegebenenfalls Mandanten sowie markierte Testdatensätze vorbereiten.
- Netzwerkprotokoll, Router, SSR-/Hydration-Daten, Service Worker und vorhandene WebSocket-/SSE-Verbindungen erfassen.
- Zwei Browserprofile und einen kontrollierten zweiten Origin für Browserprüfungen verwenden. Nur tatsächlich ermittelte, freigegebene Endpunkte prüfen.

## Testfälle

### CWSTG-10-01 — APIs unabhängig von Routen-Guards prüfen

**Referenzen:** [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema).

**Prüfschritte:**

1. Eine geschützte Route mit berechtigtem Testkonto öffnen und ihre Daten- und Aktionsanfragen aufzeichnen.
2. Dieselben Anfragen anonym, mit niedriger Rolle und gegebenenfalls anderem Testmandanten direkt wiederholen. Sitzungsdaten vollständig trennen.
3. Pfadparameter, alternative HTTP-Methoden und tatsächlich vorhandene API-Varianten vergleichen. Antwortinhalt und Zustand nach der Anfrage prüfen.

**Sicheres Ergebnis:** Der Server erzwingt Authentifizierung und passende Funktions-/Objektberechtigungen bei jedem Aufruf. Das Ausliefern einer öffentlichen SPA-Hülle für `/admin` ist allein kein Berechtigungsfehler.

**Belege:** Rollenmatrix, Original-/Variantenanfrage und tatsächliche Daten oder Seiteneffekte.

**Abhilfe:** Eine gemeinsame serverseitige Berechtigungsprüfung für sämtliche Transport- und Aufrufwege verwenden.

### CWSTG-10-02 — Clientzustand und Feature-Flags als unvertrauenswürdig behandeln

**Referenzen:** [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema), [Client-Speicher](13-client-storage.md).

**Prüfschritte:**

1. Im eigenen Browser Rollenanzeigen, Feature-Flags oder Zustandseinträge wie `isAdmin` ändern und neu freigeschaltete UI-Aktionen beobachten.
2. Die dazugehörigen Anfragen mit unverändert niedrig privilegierten Zugangsdaten senden.
3. Falls ein Token mit Rollenclaims verwendet wird, einen manipulierten Wert prüfen; Signatur und serverseitige Auswertung getrennt betrachten.

**Sicheres Ergebnis:** Veränderte Anzeigen oder Flags erzeugen keine zusätzlichen Serverrechte. Eine nur lokal sichtbare Schaltfläche ist ohne Datenzugriff oder erfolgreiche Aktion noch keine Privilegieneskalation.

**Belege:** Geänderter Clientzustand, verwendete Identität und unabhängige Kontrolle des Aktionsergebnisses.

**Abhilfe:** Berechtigungen aus vertrauenswürdiger serverseitiger Identität ableiten. Client-Flags dienen der Bedienung; Tokenintegrität und zulässige Claims strikt prüfen.

### CWSTG-10-03 — Initialdaten und statische Artefakte auf Offenlegung prüfen

**Referenzen:** [WSTG-v42-INFO-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/01-Information_Gathering/05-Review_Webpage_Content_for_Information_Leakage).

**Prüfschritte:**

1. HTML, Inline-JSON, Hydrationzustand, statische JSON-Dateien und geladene Bundles anonym und mit beiden Testkonten vergleichen.
2. Nach Markierungen fremder Datensätze und tatsächlichen Geheimnissen suchen. Öffentlich vorgesehene Client-IDs oder eingeschränkte veröffentlichbare Schlüssel davon unterscheiden.
3. Bei SSR/SSG und gemeinsamem CDN prüfen, ob für A erzeugte Daten an B oder anonym ausgeliefert werden.

**Sicheres Ergebnis:** Öffentlich ausgelieferte Artefakte enthalten ausschließlich dafür vorgesehene Daten. Authentifizierte Initialdaten dürfen berechtigte private Daten enthalten, müssen aber nach Identität getrennt ausgeliefert werden.

**Belege:** Fundstelle im Artefakt, Abrufkontext und belegte Sensitivität beziehungsweise fremder Datensatz.

**Abhilfe:** Geheimnisse im Backend halten, Initialdaten gezielt auswählen und personalisierte Antworten von öffentlichen Build-/Cacheartefakten trennen.

### CWSTG-10-04 — Source Maps und Debugausgaben bewerten

**Referenzen:** [WSTG-v42-INFO-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/01-Information_Gathering/05-Review_Webpage_Content_for_Information_Leakage).

**Prüfschritte:**

1. `sourceMappingURL` und dokumentierte Debugendpunkte der tatsächlich geladenen Dateien prüfen; keine unbeschränkte Pfadsuche starten.
2. Erreichbare Maps, eingebettete Quellen und Logs nach Zugangsdaten, privaten Daten oder vertraulichen Entwicklungsinformationen untersuchen.
3. Einen vermeintlichen Schlüssel anhand seiner vorgesehenen Veröffentlichbarkeit und Rechte einordnen; keine fremden Systeme damit aufrufen.

**Sicheres Ergebnis:** Veröffentlichte Artefakte geben keine schutzbedürftigen Daten preis. Eine erreichbare Source Map, ein Endpunktname oder ein `console.log` begründet für sich keinen Sicherheitsbefund.

**Belege:** Redigierte Fundstelle, Abrufbarkeit und konkrete missbräuchliche Fähigkeit oder Offenlegung.

**Abhilfe:** Geheimnisse aus dem Build entfernen und bei Offenlegung widerrufen; Maps entsprechend der Produktpolitik veröffentlichen oder nur an das geschützte Fehleranalysesystem übertragen.

### CWSTG-10-05 — Vorabladen und Service-Worker-Caches trennen

**Referenzen:** [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema), [WSTG-v42-ATHN-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/06-Testing_for_Browser_Cache_Weaknesses).

**Prüfschritte:**

1. Datenabrufe beim Hover, Navigieren, Vorabladen und Wiederverbinden erfassen. Prüfen, welche davon eine aktuelle Berechtigung benötigen.
2. Nach Logout und Wechsel von A zu B dieselben Routen einschließlich Offlineansicht öffnen; HTTP-Cache, Anwendungscache und Service-Worker-Cache getrennt beobachten.
3. Privaten Inhalt aus einem zuvor berechtigten Zustand mit frischen unberechtigten Netzwerkantworten vergleichen.

**Sicheres Ergebnis:** Hintergrundabrufe haben dieselben Serverprüfungen wie sichtbare Aufrufe. Clientcaches und Offlineansichten verraten nach dem vereinbarten Kontowechsel-/Logoutmodell keine Daten des vorherigen Kontos.

**Belege:** Initiator der Anfrage, Cachequelle, Kontowechsel und markierter Antwortinhalt.

**Abhilfe:** Personalisierte Cacheeinträge identitätsbezogen verwalten oder nicht speichern; bei Logout/Kontowechsel passende Anwendungs- und Service-Worker-Daten bereinigen.

### CWSTG-10-06 — WebSocket- und SSE-Berechtigungen über den Lebenszyklus prüfen

**Referenzen:** [WSTG-v42-CLNT-10](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/10-Testing_WebSockets); ergänzend [OWASP WebSocket Security](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html) und [OWASP HTML5 Security](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) für SSE.

**Prüfschritte:**

1. Verbindung anonym, mit gültigen und mit abgelaufenen oder widerrufenen Testzugangsdaten aufbauen.
2. Als A einen ausschließlich B zugewiesenen Testkanal abonnieren und einzelne Nachrichten-/Aktionsrechte prüfen. Bei cookieauthentifizierten WebSockets zusätzlich einen Verbindungsaufbau aus dem kontrollierten fremden Origin testen.
3. Eine bestehende Verbindung während Logout, Rollenentzug und Ablauf beobachten; danach neue geschützte Testereignisse auslösen. Auch erneute Verbindung und SSE-Fortsetzung prüfen.

**Sicheres Ergebnis:** Verbindung, Abonnement und Aktionen sind ihrem Zweck entsprechend autorisiert; Rechteverlust wirkt innerhalb der festgelegten Frist auch auf bestehende Verbindungen. Eine Origin-Prüfung ersetzt keine Authentifizierung.

**Belege:** Handshake, Origin, Abonnement, Ereigniszeitachse und tatsächlich empfangene Testnachrichten.

**Abhilfe:** Verbindungs- und Nachrichtenberechtigungen prüfen, erlaubte Browserorigins festlegen und Sitzungs-/Rechteänderungen an laufende Verbindungen propagieren.

### CWSTG-10-07 — Routenparameter und Weiterleitungen sicher verarbeiten

**Referenzen:** [WSTG-v42-CLNT-01](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting), [WSTG-v42-CLNT-04](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/04-Testing_for_Client-side_URL_Redirect).

**Prüfschritte:**

1. Eindeutige Marker mit Sonderzeichen in Pfad, Query, Fragment und gegebenenfalls Rücksprungparameter einsetzen.
2. Quelle und Verwendung im Router verfolgen: Textdarstellung, HTML-Sink, dynamischer Ressourcenabruf oder Weiterleitung.
3. Nur gegen kontrollierte Testziele externe oder schematische Weiterleitungen prüfen; normales und erneut dekodiertes Navigieren vergleichen.

**Sicheres Ergebnis:** Routenwerte gelangen nicht ungeprüft in ausführbare Kontexte oder unerlaubte Weiterleitungen. Ein URL-Fragment erreicht häufig nur den Client und braucht deshalb dort eigene Prüfung.

**Belege:** Ausgangs-URL, Dekodierungsschritte, DOM-Sink oder Ziel-URL und Browserbeobachtung.

**Abhilfe:** Sichere Router-/URL-APIs, passende Kodierung und ausdrücklich erlaubte Weiterleitungsziele nutzen; dynamische Skript-/Ressourcenpfade begrenzen.

### CWSTG-10-08 — Fensterkommunikation mit postMessage absichern

**Referenzen:** [WSTG-v42-CLNT-11](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/11-Testing_Web_Messaging); ergänzend [MDN: postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage).

**Prüfschritte:**

1. Vorhandene Popup-/Iframe-Kommunikation und erwartete Nachrichtenquellen erfassen; falls nicht vorhanden, den Fall als nicht anwendbar dokumentieren.
2. Aus einem kontrollierten fremden Fenster eine Nachricht mit passendem Typ und harmlosen Testdaten senden; auch die falsche Fensterquelle bei ansonsten passendem Origin prüfen, soweit der Ablauf dies erlaubt.
3. Empfängerverhalten bei unerwartetem Nachrichtenschema untersuchen. Beim Senden sensibler Daten prüfen, ob ein exakter `targetOrigin` verwendet wird.

**Sicheres Ergebnis:** Empfänger prüfen den vollständigen erwarteten Origin und, wenn ein bestimmtes Fenster erwartet wird, `event.source`; sie validieren das Nachrichtenschema vor jeder Aktion. Sensible Nachrichten gehen nicht mit `targetOrigin="*"` an unbekannte Empfänger.

**Belege:** Sender-/Empfängerorigin, Fensterbeziehung, Nachrichteninhalt und tatsächliche Reaktion.

**Abhilfe:** Exakte Originvergleiche statt Teilstringprüfungen, erwartete Fensterquelle und ein enges Nachrichtenschema verwenden; empfangene Werte als unvertrauenswürdige Daten behandeln.

## Quellen

- Die Testfälle verlinken die jeweiligen OWASP-WSTG-Szenarien in Version 4.2.
- [OWASP WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html)
- [OWASP HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [MDN: postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
