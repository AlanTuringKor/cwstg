# 4. Role / Permission UI

# Kapitel: Role / Permission UI

**Ziel**

Sicherstellen, dass Rollen- und Berechtigungsänderungen nur durch berechtigte Akteure möglich sind, serverseitig geprüft werden und nicht durch Client-Tampering, JWT-Manipulation oder UI-Manipulation umgangen werden können.

**Scope / Prüfbereiche**

Role-assignment Endpoints (API + UI), client-side controls (hidden fields/DOM), Token-Claims (JWT), JWT tampering (alg/`kid`), CSRF auf Admin-Actions, Mass-Assignment / mass role changes, audit/alerting, separation of duties, delegation flows, race conditions bei Role-Changes.

**WSTG-Mapping (relevante Bereiche)**

- Authorization / Access Control tests (IDOR, Horizontal/Vertical Privilege Escalation).
- Session & Authentication tests (token handling, JWT verification).
- Business logic tests (role change flows, delegation).
- CSRF tests (admin actions).
- File / Input validation only indirectly (payloads in role names etc.).
    
    (Beim Report bitte die passenden WSTG-Sektionen als Referenz anführen.)
    

---

## Übersicht der Testfälle (mit TestID)

1. **ROLE-01** — Intercept role assignment → change `targetRole` / `targetUserId` (Tampering).
2. **ROLE-02** — Modify JWT / role claim client-side and reuse (JWT tampering / alg none / kid abuse).
3. **ROLE-03** — Check UI for hidden/disabled role controls (DOM toggle / mass-assignment via form fields).
4. **ROLE-04** — CSRF on role assignment endpoints (perform role change from foreign origin).
5. **ROLE-05** — Mass-assignment / Parameter pollution (extra parameters in request produce unintended changes).
6. **ROLE-06** — Race condition / concurrent role change leading to inconsistent ACL (double submit / conflicting writes).
7. **ROLE-07** — Delegation / approval workflow bypass (if app supports delegated role grant).
8. **ROLE-08** — Audit & alerting verification (changes logged, notifications for critical changes).

---

## Detaillierte Testfälle — Schritte, Hints, Erwartetes Ergebnis

### ROLE-01 — Intercept role assignment → change `targetRole` / `targetUserId`

**WSTG-Mapping:** Authorization / Access Control tests (privilege escalation).

**Kurz-Schritte**

1. Login als normaler (non-admin) User A.
2. Führe die Rolle-Änderung wie vom UI vorgesehen aus (oder verwende Burp/Proxy, falls UI nur angezeigt). Intercept den Request `POST/PUT /api/admin/users/{id}/roles` (oder äquivalente).
3. Manipuliere `targetUserId` auf einen anderen Benutzer B oder `role` auf `admin` / `ROLE_SUPERUSER`.
4. Replay the tampered request.
5. Prüfe Response + danach das Zielkonto (GET /api/users/{B}) ob die Rolle gesetzt wurde.

**Automation-Hint**

- Burp Repeater / Intruder für viele Permutationen; Python requests script zur Mass-Tamper-Ausführung.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server validiert, dass Caller die Rechte hat → Response 403/401 oder validation error. Keine Änderung in DB. Beweis: raw request/response, GET vor/nach.
    
    **Severity**
    
- Direkter Role Escalation = High / Critical (je nach Rolle).
    
    **Gegenmaßnahme (schnell)**
    
- Serverseitige checks: `if (!caller.hasRole('ADMIN')) reject;` – niemals client role flags übernehmen.
    
    **Tiefergehende Remediation**
    
- Zentralisierte Authorization-Middleware, RBAC/ABAC Policy Engine, least privilege, unit + integration tests für admin APIs.

---

### ROLE-02 — Modify JWT / role claim client-side and reuse

**WSTG-Mapping:** Session & Authentication tests (token verification).

**Kurz-Schritte**

1. Führe Login als User A durch, beobachte JWT (falls verwendet) in `Authorization: Bearer <jwt>` oder localStorage.
2. Dekodiere JWT (Base64) und ändere Claims (`"role":"admin"`). Reencode und ersetze Token im Client (localStorage / Authorization header).
3. Sende einen privilegierten Request (z. B. `POST /api/admin/...`) mit manipuliertem Token.
4. Teste typische JWT-Attacks: `alg: none`, Ersetze `kid` auf anderer key id, sign with weak key, swap signature.
5. Prüfe ob Token serverseitig validiert (sig verified, alg enforced, kid validated).

**Automation-Hint**

- jwt.io tools / simple script to change payload and re-sign using known keys (in misconfigured systems).
    
    **Erwartetes Ergebnis / Beweis**
    
- Server lehnt manipulierten Token ab (401) oder verifiziert Signatur; kein Zugriff. Evidence: manipulated JWT + server response.
    
    **Severity**
    
- High (vollständige Privilege Escalation möglich).
    
    **Gegenmaßnahme**
    
- Enforce signature verification, reject `alg: none`, validate `kid` mapping to known keys, use short token TTL or opaque tokens, rotate keys, verify claims (iss, aud, exp).
    
    **Tiefergehende Remediation**
    
- Use introspection endpoint for JWTs or use opaque reference tokens; enforce audience/issuer; pin accepted algorithms.

---

### ROLE-03 — Check UI for hidden/disabled role controls (DOM toggles / mass assignment)

**WSTG-Mapping:** Business logic + Authorization.

**Kurz-Schritte**

1. Open Admin UI, inspect role form fields; disable/hidden fields may be controlled by JS.
2. In DevTools toggle hidden fields or remove `disabled` attribute, modify form values and submit.
3. Inspect network request — replay with changed fields if UI normally prevents editing.
4. Also search for mass-assignment vectors: fields like `isAdmin` included in profile update payloads.

**Automation-Hint**

- Selenium / Puppeteer to toggle DOM attributes & submit forms. Burp to intercept final request.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server validiert serverseitig → rejects non-privileged changes. Evidence: raw req/res and UI before/after.
    
    **Gegenmaßnahme**
    
- Remove sensitive fields from client payloads or ignore them server-side; separate admin endpoints with strict auth.

---

### ROLE-04 — CSRF on role assignment endpoints

**WSTG-Mapping:** CSRF tests (session-based admin actions).

**Kurz-Schritte**

1. Logge dich als Admin in Browser A.
2. In Browser B (attacker page), host HTML form that submits to role assignment endpoint (e.g., `<form action="https://app.local/api/admin/users/42/role" method="POST">…</form>`).
3. Visit attacker page while admin still authenticated and submit form automatically; beobachte ob server die Änderung ausführt.
4. Variationen: JSON endpoints via `fetch` (CORS), check for `SameSite` cookie behavior.

**Automation-Hint**

- Simple HTML proof-of-concept page; test different Content-Types (form vs XHR) to find weak CSRF protections.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server verlangt CSRF-Token oder SameSite cookie prevents request; no role change performed. Evidence: PoC page + server response.
    
    **Gegenmaßnahme**
    
- CSRF tokens for state-changing requests; require double submit cookies, require custom header checked server-side; mark cookies `SameSite=Strict/Lax`.
    
    **Tiefergehende Remediation**
    
- Use CSRF protection libraries, require re-authentication / MFA for critical admin actions.

---

### ROLE-05 — Mass-assignment & Parameter pollution

**WSTG-Mapping:** Business logic / Input validation.

**Kurz-Schritte**

1. Intercept a harmless profile update request and add extra fields: `"isAdmin": true`, `"roles":["ADMIN"]`, or duplicate keys (`role=admin&role=user`).
2. Replay and check if server persists those fields.
3. Also try JSON with nested structures that the server might merge incorrectly.

**Erwartetes Ergebnis / Beweis**

- Server ignores unauthorized fields or returns validation error. Evidence: before/after state + raw req/res.
    
    **Gegenmaßnahme**
    
- Whitelist fields accepted by endpoint, strict model binding on server, validation schemas (e.g., JSON Schema), reject unknown properties.

---

### ROLE-06 — Race condition / concurrent role change

**WSTG-Mapping:** Logic/Concurrency tests.

**Kurz-Schritte**

1. Simuliere zwei nahezu zeitgleiche Requests: a) Admin1 setzt Role X, b) Admin2 entfernt Role X / setzt andere. Oder attacker sends forged request concurrently.
2. Prüfe DB Konsistenz und ob intermediate illegal state erlaubt war (momentary privilege escalation).
3. Teste create-or-update logic for non-atomic operations.

**Automation-Hint**

- Parallel threads/processes to fire requests with millisecond offsets; use DB snapshots to verify ordering.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server operations are atomic and consistent; no inconsistent privileges observed. Evidence: DB transaction logs, request timestamps.
    
    **Gegenmaßnahme**
    
- DB-level transactions, optimistic locking, serializable isolation or application-level mutex/locking for critical updates.

---

### ROLE-07 — Delegation / approval workflow bypass

**WSTG-Mapping:** Business logic / Authorization.

**Kurz-Schritte**

1. Wenn App Delegation (z. B. Team Leads can grant roles after approval) unterstützt: try to bypass approval by directly calling underlying endpoint or toggling `approved=true` field.
2. Test whether the approval is enforced server-side (requires reviewer id, timestamps).

**Erwartetes Ergebnis / Beweis**

- Approval logic enforced: direct attempts to set `approved` flag fail or require reviewer credentials. Evidence: raw req/res + audit trail.
    
    **Gegenmaßnahme**
    
- Implement server-enforced approval workflow, separate endpoints for request vs. approval, immutable audit trail.

---

### ROLE-08 — Audit & Alerting verification

**WSTG-Mapping:** Logging & Monitoring recommendations.

**Kurz-Schritte**

1. Führe eine berechtigte und eine unberechtigte Rolle-Änderung durch (oder simuliere) und verifiziere, ob beide Aktivitäten geloggt sind.
2. Prüfe ob kritische Änderungen (Admin role changes) Alarme/Notifications auslösen.
3. Prüfe Retention und Zugriffsschutz der Logs.

**Erwartetes Ergebnis / Beweis**

- Alle role changes logged with actor id, timestamp, previous/new state; alerts for critical changes. Evidence: log excerpts, alert messages.
    
    **Gegenmaßnahme**
    
- Centralized logging, SIEM alerts for suspicious role changes, immutable audit storage (write-once or signed logs).

---

## Tools & Beispiel-Payloads (autorisiert verwenden)

- Tools: Burp Suite (Proxy, Repeater, Intruder), Postman, curl, Python `requests`, `jwt` CLI tools, Selenium/Puppeteer (DOM manipulation), concurrency scripts (Python threading/asyncio).
- Beispiel-Payloads / Tests:
    - Tamper JSON: `{"userId": "42", "role": "ADMIN"}`
    - JWT alg none: modify header to `{"alg":"none",...}` and remove signature.
    - Duplicate params: `role=user&role=admin` or JSON with additional fields.
    - CSRF PoC: small HTML form auto-posting to admin endpoint.

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. ROLE-01)
- **WSTG-Ref** (z. B. Authorization / Auth bypass)
- **Beschreibung** (kurz)
- **Reproduktionsschritte** (raw request + payloads, auth context)
- **Beweis (raw req/res, JWT sample, logs)**
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation
- **Compensating controls** (z. B. temporary admin lock, monitor)

---

## Schnelle Gegenmaßnahmen (Kurz)

- Immer serverseitig autorisieren: `if (!hasRight(caller, action)) return 403`.
- Rollen nur über dedizierte Admin-APIs ändern; client darf keine role-Felder setzen.
- Verifiziere JWT Signatur & Claims; reject `alg:none` and unsupported algs; rotate keys.
- CSRF-Token / SameSite cookie protection / re-auth or MFA for role changes.
- Whitelist der erlaubten Felder (no mass assignment).
- Auditing + SIEM alerts für kritische role changes.
- Use opaque tokens or JWT introspection; deny token reuse if revoked.
- Rate-limit admin endpoints and detect anomalous change patterns.

## Tiefergehende Empfehlungen (Architektur / Process)

- Implementiere RBAC mit Policy Engine (e.g., OPA) oder ABAC für komplexe Regeln.
- Trenne duties: require two-person approval for highly-privileged roles.
- Implement test suites (unit + integration) that simulate tampering and validate policies automatically.
- Key management: rotate JWT signing keys and maintain key ID (kid) mapping securely.
- Periodic access reviews and automated scans to detect privilege creep.

---