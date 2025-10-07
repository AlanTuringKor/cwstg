# 10. Client-side Routing / SPA (hash/history)

# Kapitel: Client-side Routing / SPA (hash/history)

**Ziel**

Prüfen, ob Client-seitiges Routing (SPA mit `hash` / `history`) zu einer falschen Sicherheit führt — also ob „UI-Guards“ allein den Eindruck von Schutz erwecken, während die Backends routen-/endpunkt-basiert weiterhin sensible Daten liefern. Sicherstellen, dass alle sensiblen Daten und Aktionen serverseitig autorisiert sind und dass keine Geheimnisse in den gebündelten Assets landen.

**Scope / Prüfbereiche**

- Client-side guards (JS-only checks) vs. server-side Authorization
- Route-based data loading (server calls für jede Route)
- Preloaded initial payloads (SSR/SSG/initial state) im Bundle
- Exposure von Admin- oder Debug-Routen durch client config oder source maps
- Token / claim handling auf Client (localStorage / cookies)
- Caching / prefetching von sensiblen Daten

**WSTG-Mapping (relevante Bereiche — für Reports)**

- *WSTG Authorization Tests* — fehlende serverseitige Zugriffskontrolle.
- *WSTG Session & Authentication* — unsichere Token-Speicherung/Socket auth.
- *WSTG Information Leakage* — sensitive data in JS bundles / source maps.
- *WSTG API Endpoint/Discovery* — discoverable hidden/admin APIs.

---

## Testfälle (Kurzliste mit TestIDs)

- **SPA-01** — Direkter API-Aufruf an Route-Backend ohne UI-Guard (API access bypass).
- **SPA-02** — Manipuliere Client-State (z. B. `isAdmin = true`) und versuche privilegierte Aktionen.
- **SPA-03** — Sensible Daten sind im initialen Bundle / window.**INITIAL_STATE** oder als JSON eingebettet.
- **SPA-04** — Exponierte source maps / debug flags / hardcodierte Keys in JS.
- **SPA-05** — Prefetch / background fetch gibt sensible Inhalte an nicht berechtigte Nutzer.
- **SPA-06** — WebSocket / SSE Verbindungen, die ohne serverseitige Auth Daten pushen.

---

## Detaillierte Testfälle — Schritte, Automation-Hints, Erwartetes Ergebnis

### SPA-01 — Direkter API-Aufruf an Route-Backend ohne UI-Guard

**WSTG-Mapping:** Authorization / API Discovery.

**Kurz-Schritte**

1. Navigiere zur geschützten SPA-Route als nicht eingeloggter oder low-priv Nutzer (z. B. `/admin/users`).
2. Finde die API-Calls die die Route verwendet (DevTools → Network beim Laden der Route).
3. Kopiere einen typischen Request (z. B. `GET /api/admin/users?page=1`) und führe ihn in einem neuen Session-Kontext aus (curl/Postman) **ohne** UI-Auth-Token.
4. Variationen: remove `Authorization` header, set `X-Requested-With` falsified, call same endpoint from different origin.

**Automation-Hint**

- Burp Repeater / curl scripting; ffuf für many endpoints found in JS bundles.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server verlangt serverseitige Auth/Authorization (401/403); keine sensitive payload. Evidence: raw req/res, network trace showing UI request vs direct call.
    
    **Schnelle Gegenmaßnahme**
    
- Alle endpoints authorisieren serverseitig (role checks), never rely on client route guards.

---

### SPA-02 — Manipuliere Client-State um Admin-Route zu zeigen / Aktionen auszuführen

**WSTG-Mapping:** Authorization / Business Logic.

**Kurz-Schritte**

1. Öffne DevTools → Console und setze/ändere client state (z. B. `window.appState.user.isAdmin = true`) oder manipuliere localStorage / sessionStorage / cookies with `isAdmin` flag.
2. Beobachte, ob die UI nun Admin-Funktionen freischaltet.
3. Intercept die Requests die UI auslöst und re-play diese Requests ohne Admin credentials oder mit manipulated token.

**Automation-Hint**

- Puppeteer / Selenium zur scriptbasierten DOM/State-Manipulation; Burp zum Abfangen & Replays.
    
    **Erwartetes Ergebnis / Beweis**
    
- UI mag anzeigen, aber server verweigert die Aktionen; server responses 403/401. Evidence: console manip steps + raw req/res.
    
    **Schnelle Gegenmaßnahme**
    
- UI darf nur UX-Einschränkungen machen; alle Authorizs müssen serverseitig validiert werden; entfernen von sensitive flags aus client storage.

---

### SPA-03 — Sensible Daten im initialen Bundle / preloaded state

**WSTG-Mapping:** Information Leakage.

**Kurz-Schritte**

1. Lade die Seite und suche in HTML/JS nach `window.__INITIAL_STATE__`, `window.__DATA__`, inline JSON oder SSR payloads.
2. Suche nach Emails, tokens, internal IDs, API keys, oder PII in eingebettetem JSON.
3. Prüfe statische `index.html`, generated `.js` bundles oder `.json` vom Server.
4. Falls SSG/SSR genutzt wird: prüfe build pipeline ob private data eingeflossen sein kann.

**Automation-Hint**

- grep / ripgrep durch gebündelte Dateien; `curl` index.html + `jq` für JSON-Snippets.
    
    **Erwartetes Ergebnis / Beweis**
    
- Keine secrets/PII im Bundle; initial payload only contains public, non-sensitive view data. Evidence: snippets and file excerpts.
    
    **Schnelle Gegenmaßnahme**
    
- Remove secrets from server render; filter initial state; use APIs to fetch sensitive data on-demand with auth.

---

### SPA-04 — Exponierte source maps / hardcodierte Keys / debug flags

**WSTG-Mapping:** Information Leakage / Deployment hygiene.

**Kurz-Schritte**

1. Prüfe für `.map` files neben `app.js` (e.g., `app.js.map`) — lade sie herunter und inspect.
2. Suche nach `console.log` debug strings, hardcoded endpoints, credentials, dev-only flags.
3. Prüfe `process.env` replacements in bundle for leaked env values.

**Automation-Hint**

- ffuf /dirb for `.map`; `rg`/`grep` in downloaded maps.
    
    **Erwartetes Ergebnis / Beweis**
    
- No source maps in prod or maps sanitized; no secrets in maps. Evidence: map content excerpts.
    
    **Schnelle Gegenmaßnahme**
    
- Disable source map publishing to prod; strip/debug info at build; use env var management.

---

### SPA-05 — Prefetch / background fetch exposes data to unauthenticated flows

**WSTG-Mapping:** API design / Caching & Prefetch.

**Kurz-Schritte**

1. Check whether SPA prefetches data for routes the user cannot access (network tab: prefetch/fetch initiated on hover).
2. Simulate non-auth user and observe whether prefetch returns sensitive content (maybe cached).
3. Try clearing auth and re-trigger prefetch.

**Erwartetes Ergebnis / Beweis**

- Prefetch only returns public data or uses same auth checks; no sensitive data leaked. Evidence: prefetch requests/responses.
    
    **Schnelle Gegenmaßnahme**
    
- Prefetch only for public resources or require auth for prefetch; server should check auth on every request.

---

### SPA-06 — WebSocket / SSE data push without server auth

**WSTG-Mapping:** Session & Auth for persistent connections.

**Kurz-Schritte**

1. Observe WebSocket/SSE connection handshake (Network → WS) and check auth mechanism (cookie, Bearer token).
2. Attempt connecting without auth token or with revoked token; see if server sends privileged messages.
3. Try subscribing to privileged channels (admin notifications).

**Erwartetes Ergebnis / Beweis**

- Server requires valid auth at handshake and authorizes channel subscriptions. Evidence: WS handshake logs + unauthorized attempt responses.
    
    **Schnelle Gegenmaßnahme**
    
- Authenticate and authorize on handshake; check permission for each subscription message.

---

## Ergänzende Prüfungen / Edge-Cases

- **Client bundling leaks via CDN caching** (ensure private builds not cached publicly).
- **Route-based feature flags** stored in bundle that allow feature toggles; test toggling.
- **Service worker cache**: service worker precache may store sensitive responses — validate SW config.
- **Third-party libs** in bundle exposing secrets (analytics keys) — check allowed scope.
- **LocalStorage vs HttpOnly cookie**: ensure tokens that give long-term access are not in localStorage.

---

## Tools & Beispiele (nur autorisierte Tests)

- Tools: DevTools (Network, Sources), Burp Suite (Proxy/Repeater), curl/Postman, ffuf (discover endpoints in bundles), ripgrep/rg on downloaded JS, Puppeteer/Selenium for scripted state manipulation, WebSocket client (wscat).
- Beispieldirect calls: `curl -v 'https://app.example/api/admin/users'` (no auth), `curl -H 'Authorization: Bearer <manipulated token>' ...`
- Suche im bundle: `rg "window.__INITIAL_STATE__|process.env|apiKey|secret|sourceMappingURL"`.

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. SPA-03)
- **WSTG-Ref** (z. B. Authorization / Information Leakage)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw req/res, bundle excerpts)
- **Beweis (raw req/res, screenshots, code excerpts)**
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation

---

## Erwartetes Ergebnis / Acceptable Behaviour (Summary)

- Alle APIs, auch jene, die nur von geschützten SPA-Routen aufgerufen werden, validieren serverseitig Autorisierung → 401/403 wenn nicht berechtigt.
- Das Bundle enthält **keine** sensiblen Tokens, Secrets oder PII; source maps nicht in Prod.
- UI-State/Toggles dürfen UX verändern, aber nicht Authorisierungen erzeugen.
- Prefetch / SW / caching respektieren Auth und Cache-Control.

---

## Schnelle Gegenmaßnahmen (Kurz)

- Enforce server-side authorization for every request.
- Never embed secrets/PII in bundled JS or initial HTML.
- Don’t place long-lived tokens in localStorage; prefer HttpOnly cookies for auth where possible.
- Remove source maps from production builds.
- Validate and authorize WebSocket subscriptions on handshake.
- Limit prefetching of protected data; ensure SW caches are configured securely.

---