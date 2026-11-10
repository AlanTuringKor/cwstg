# 11 · Sitzungen, Logout und dauerhaftes Anmelden

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Sitzungen und dauerhafte Anmeldungen haben einen klaren Lebenszyklus: sichere Erzeugung, Schutz bei Übertragung und Speicherung, zweckgerechte Erneuerung, Ablauf und wirksamer Widerruf. Die sichtbare Logoutfunktion muss zum tatsächlichen Berechtigungszustand passen.

## Voraussetzungen

- Zwei getrennte Browserprofile und ein Testkonto mit optionalem MFA einrichten. Sitzungs-, Remember-me-, Access- und Refresh-Token nach Zweck unterscheiden.
- Vorgaben für Laufzeit, Rotation, Logout, Widerruf und erneute Authentifizierung dokumentieren. Bei SSO die lokale Sitzung und die Sitzung des Identitätsanbieters getrennt betrachten.
- Geschützte lesende Testendpunkte und harmlose Aktionen festlegen. Tokenwerte im Bericht redigieren; für Vergleich und Wiederverwendung nur geschützt verwahren.

## Testfälle

### CWSTG-11-01 — Session Fixation mit gültiger Vorsitzung prüfen

**Referenzen:** [WSTG-v42-SESS-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation).

**Prüfschritte:**

1. In Browser A eine vom Server ausgestellte anonyme Sitzung erzeugen und deren Kennung für den Test geschützt sichern.
2. Dieselbe Vorsitzung in Browser B verwenden und dort als Testnutzer anmelden. Alte und neue Kennung vergleichen.
3. Mit der in A bekannten alten Kennung einen geschützten Testendpunkt abrufen. Prüfen, ob dieser Zugriff plötzlich die Identität von B erhält.
4. Zusätzlich prüfen, ob nicht ausgestellte frei gewählte Kennungen akzeptiert werden. Das Ablehnen einer solchen Kennung allein deckt den ersten Fall nicht ab.

**Sicheres Ergebnis:** Eine vor der Anmeldung bekannte Kennung erhält keine authentifizierten Rechte; nach dem Sicherheitsübergang wird eine neue, nicht vorher bekannte Kennung verwendet.

**Belege:** Redigierte Vorher-/Nachherkennungen, Sitzungsübergang und Zugriffsergebnis aus A.

**Abhilfe:** Sitzungskennung bei Anmeldung erneuern und die alte Kennung für authentifizierten Zugriff entwerten; ausschließlich gültige serverseitig ausgestellte Kennungen akzeptieren.

### CWSTG-11-02 — Dauerhaftes Anmelden und sensible Aktionen prüfen

**Referenzen:** [WSTG-v42-ATHN-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/05-Testing_for_Vulnerable_Remember_Password).

**Prüfschritte:**

1. Mit und ohne „Angemeldet bleiben“ einloggen; gespeicherte Daten, Lebensdauer und erneutes Öffnen des Browsers vergleichen.
2. Den eigenen persistenten Testtoken kontrolliert in das zweite Browserprofil übertragen und die dadurch erreichbaren Rechte feststellen.
3. Prüfen, ob sensible Änderungen entsprechend der festgelegten Richtlinie eine frische Authentifizierung beziehungsweise MFA verlangen. Passwort oder wiederverwendbare Klartextzugangsdaten dürfen nicht im Client gespeichert sein.

**Sicheres Ergebnis:** Der Mechanismus verwendet begrenzte, widerrufbare Anmeldenachweise. Die Kopierbarkeit eines Bearer-Tokens ist eine Eigenschaft dieses Modells; der konkrete Schutz vor Diebstahl, die Laufzeit und erreichbare Aktionen bestimmen das Risiko.

**Belege:** Tokenart, Speicherort, Laufzeiten, erneute Anmeldung und Ergebnis einer sensiblen Testaktion.

**Abhilfe:** Dauerhafte Anmeldenachweise getrennt vom Passwort verwalten, Ablauf und Widerruf vorsehen und für risikoreiche Aktionen eine aktuelle Authentifizierung verlangen. IP oder User-Agent sind keine kryptografische Gerätebindung.

### CWSTG-11-03 — Logout über sämtliche Anmeldenachweise prüfen

**Referenzen:** [WSTG-v42-SESS-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/06-Testing_for_Logout_Functionality); ergänzend [RFC 7009: Token Revocation](https://www.rfc-editor.org/rfc/rfc7009.html).

**Prüfschritte:**

1. Vor Logout jeweils eine gültige Sitzung, einen dauerhaften Anmeldenachweis und gegebenenfalls Access-/Refresh-Token erfassen.
2. Über die UI abmelden und die gesicherten Nachweise getrennt an einem geschützten Endpunkt beziehungsweise am Refresh-Endpunkt wiederverwenden.
3. Prüfen, ob Cookies nur gelöscht oder auch serverseitige Sitzungen und persistente Nachweise entwertet werden. Bei selbstständigen Access-Tokens die tatsächliche verbleibende Gültigkeit messen und mit der Logoutanforderung vergleichen.
4. Zurücknavigation, Offlineansicht und erneutes Öffnen prüfen; gecachte Anzeige und neu autorisierten Datenabruf unterscheiden.

**Sicheres Ergebnis:** Die abgemeldete Sitzung und zugehörige Erneuerungsmöglichkeiten gelten nicht weiter. Eine technisch verbleibende Access-Token-Gültigkeit ist ausdrücklich begrenzt und muss mit den zugesagten Widerrufsfristen vereinbar sein; bloßes Cookie-Löschen erfüllt keinen serverseitigen Logout.

**Belege:** Logoutanfrage, Nachweistypen, Replay-/Refresh-Ergebnisse und gemessene Widerrufsfristen.

**Abhilfe:** Sitzung und persistente Erneuerungsrechte serverseitig entwerten. Für erforderlichen sofortigen Access-Entzug geeignete Sperrlisten, Introspektion oder Sitzungsprüfung einsetzen; Clientcaches passend bereinigen.

### CWSTG-11-04 — Cookieattribute und Geltungsbereich prüfen

**Referenzen:** [WSTG-v42-SESS-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/02-Testing_for_Cookies_Attributes).

**Prüfschritte:**

1. `Set-Cookie` bei Anmeldung, Erneuerung, Remember-me und Logout aufzeichnen; auch gleichnamige Cookies mit anderem Domain-/Pfadbereich berücksichtigen.
2. Für Authentifizierungscookies `Secure`, `HttpOnly`, `SameSite`, `Domain`, `Path` und Lebensdauer gegen die beabsichtigten SSO-/Cross-Site-Flows prüfen.
3. Prüfen, ob ein unnötig weiter Domainbereich weniger vertrauenswürdige Subdomains einbezieht und ob Logout alle relevanten Cookievarianten löscht.

**Sicheres Ergebnis:** Authentifizierungscookies sind nur über HTTPS nutzbar, nicht unnötig skriptzugänglich und haben einen zweckgerechten engen Geltungsbereich. `SameSite=None` kann für einen vorgesehenen Cross-Site-Ablauf korrekt sein und benötigt `Secure` sowie passenden CSRF-Schutz.

**Belege:** Redigierte vollständige Header und dokumentierte Einsatzgrenzen.

**Abhilfe:** Cookieattribute zentral setzen, Domainbereich minimieren und bei passenden hostgebundenen Cookies das `__Host-`-Präfix nutzen. `Path` ist keine verlässliche Zugriffssperre gegen gleichoriginige Skripte.

### CWSTG-11-05 — Sicherheitsniveau und Rechtewechsel an die Sitzung binden

**Referenzen:** [WSTG-v42-SESS-03](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation), [WSTG-v42-ATHZ-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema).

**Prüfschritte:**

1. Einen Nachweis vor MFA-Abschluss oder vor einer vorgesehenen temporären Rechteerhöhung sichern.
2. Den Übergang regulär durchführen und den alten Nachweis separat für eine nun erlaubte sensible Testaktion verwenden.
3. Nach Ende der Erhöhung oder Entzug einer Rolle den alten erhöhten Nachweis erneut testen; auch bestehende Verbindungen berücksichtigen.

**Sicheres Ergebnis:** Frühere Nachweise erhalten nicht nachträglich höhere Rechte. Ein Rollenentzug oder Ende der Erhöhung wirkt nach der festgelegten Frist auf alle betroffenen Zugriffspfade.

**Belege:** Authentifizierungsniveau, Übergangszeitpunkte, redigierte Kennungsänderung und Aktionsergebnisse.

**Abhilfe:** Sitzungen bei Sicherheitsübergängen erneuern, Authentifizierungsniveau explizit führen und Autorisierung mit dem aktuellen Berechtigungsstand abgleichen.

### CWSTG-11-06 — Refresh-Token gegen missbräuchliche Wiederverwendung schützen

**Referenzen:** Ergänzende OAuth-Prüfung nach [RFC 9700, Abschnitt 4.14](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.14).

**Prüfschritte:**

1. Clienttyp und Schutzmodell erfassen: rotierende Refresh-Token oder kryptografisch an einen Sender gebundene Token. Eine IP-/User-Agent-Prüfung erfüllt keine kryptografische Senderbindung.
2. Bei Rotation mit einem Testtoken erneuern und danach den verbrauchten Token einmal erneut senden. Schutzreaktion und gegebenenfalls Widerruf der Tokenfamilie beobachten; dokumentierte kurze Parallelitätsfenster berücksichtigen.
3. Bei Senderbindung im Testsystem einen Refresh ohne passenden Schlüsselnachweis prüfen. Danach einen widerrufenen oder abgelaufenen Token einsetzen.

**Sicheres Ergebnis:** Das für den Client erforderliche Schutzmodell verhindert unerkanntes dauerhaftes Erneuern durch kopierte Token. Bei öffentlichen OAuth-Clients wird Replay durch Rotation oder Senderbindung erkannt; ungültige Nachweise ermöglichen keine neue Anmeldung.

**Belege:** Clienttyp, Rotation-/Bindungsmodell, redigierte Tokenfolge und Serverentscheidung.

**Abhilfe:** OAuth-Refreshschutz nach RFC 9700 einsetzen; Rotation, Replayreaktion, Ablauf und Widerruf konsistent implementieren und Tokenfamilien nachvollziehbar verwalten.

### CWSTG-11-07 — Einzelne und sämtliche Geräte abmelden

**Referenzen:** [WSTG-v42-SESS-06](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/06-Testing_for_Logout_Functionality).

**Prüfschritte:**

1. Mit demselben Testkonto zwei unabhängige Sitzungen einschließlich persistenter Anmeldung erzeugen.
2. Falls vorhanden, zunächst nur die zweite Sitzung aus der Sitzungsübersicht widerrufen und beide getrennt prüfen.
3. Danach „Alle Geräte abmelden“ verwenden und alle alten Sitzungs-/Refreshnachweise prüfen. Ob die auslösende Sitzung bestehen bleibt, mit der dokumentierten Produktfunktion vergleichen.
4. Einen fremden Testkonto-Sitzungsbezeichner bei der Widerrufsfunktion einsetzen und die Berechtigungsentscheidung prüfen.

**Sicheres Ergebnis:** Genau der zugesagte Umfang wird innerhalb der vorgesehenen Frist entwertet; fremde Kontositzungen lassen sich nicht ohne Berechtigung verwalten.

**Belege:** Sitzungsmatrix vor/nach Widerruf, Funktionsbeschreibung und Wiederverwendungsversuche.

**Abhilfe:** Nachweise pro Konto und Sitzung verwalten, Widerruf an allen Zugriffspunkten anwenden und die Verwaltungsfunktion gegen unberechtigte Aufrufe schützen.

### CWSTG-11-08 — Sitzungsaktionen gegen CSRF schützen

**Referenzen:** [WSTG-v42-SESS-05](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery), [Formularprüfung](09-multi-step-forms.md).

**Prüfschritte:**

1. Logout, Gerätewiderruf und Erneuerung auf automatisch übertragene Cookies sowie zustandsändernde GET-Aufrufe prüfen.
2. Aus einem kontrollierten fremden Origin die tatsächlich unterstützten Browseranfragen mit fehlendem oder falschem CSRF-Nachweis auslösen.
3. Den betroffenen Sitzungszustand danach unabhängig prüfen; CORS-Lesebeschränkungen nicht mit dem Verhindern einer Aktion verwechseln.

**Sicheres Ergebnis:** Fremde Seiten veranlassen keine unbeabsichtigten Sitzungsaktionen. Die konkrete Auswirkung, etwa erzwungener Logout, wird anhand der Produktfunktion bewertet und nicht pauschal als Kontenübernahme bezeichnet.

**Belege:** Browseranfrage, Schutzentscheidung und tatsächlicher Sitzungszustand.

**Abhilfe:** Geeigneten Framework-CSRF-Schutz, sichere Zustandsänderungsmethoden und ergänzende Origin-/SameSite-Regeln einsetzen.

### CWSTG-11-09 — Inaktivitäts- und Gesamtlaufzeit serverseitig prüfen

**Referenzen:** [WSTG-v42-SESS-07](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/07-Testing_Session_Timeout).

**Prüfschritte:**

1. In einer Testkonfiguration kurze Inaktivitäts- und Gesamtlaufzeiten festlegen; Sitzung und Erstellungszeit erfassen.
2. Eine Sitzung ohne Hintergrundaktivität bis nach dem Inaktivitätslimit ruhen lassen und danach mit ihrem gesicherten Nachweis zugreifen.
3. Eine zweite Sitzung im erlaubten Intervall nutzen und nach der maximalen Gesamtlaufzeit prüfen. Remember-me und Refresh dürfen dokumentierte Sicherheitsgrenzen nicht unbeabsichtigt aufheben.
4. Clientseitige Timer ausschalten beziehungsweise den Endpunkt direkt aufrufen; die serverseitige Entscheidung prüfen.

**Sicheres Ergebnis:** Ablauf ist serverseitig durchgesetzt und benötigt keine funktionierende UI. Verbindliche Gesamtlaufzeiten werden nicht durch beliebiges Aktualisieren endlos verlängert.

**Belege:** Zeitachse, Testkonfiguration, Hintergrundanfragen und Zugriffsergebnisse nach Ablauf.

**Abhilfe:** Inaktivität, absolute Laufzeit und gegebenenfalls Authentifizierungsfrische im serverseitigen Sitzungsmodell prüfen; Erneuerungsregeln ausdrücklich definieren.

## Ergänzende Hinweise

Tokenkennungen, Browserfingerprints und Standortmerkmale können Risikoentscheidungen unterstützen, beweisen aber keine Geräteidentität. Eine allgemeine Pflicht zur Bindung an IP oder User-Agent würde legitime Netzwechsel stören und lässt sich häufig umgehen. Speicher- und XSS-Risiken behandelt außerdem [Client-Speicher](13-client-storage.md).

## Quellen

- Die Testfälle verlinken die jeweiligen OWASP-WSTG-Szenarien in Version 4.2.
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [RFC 9700: OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)
- [RFC 7009: OAuth 2.0 Token Revocation](https://www.rfc-editor.org/rfc/rfc7009.html)
