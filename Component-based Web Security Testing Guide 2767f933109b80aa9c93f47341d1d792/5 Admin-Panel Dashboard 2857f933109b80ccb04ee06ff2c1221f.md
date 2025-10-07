# 5. Admin-Panel / Dashboard

# Kapitel: Admin-Panel / Dashboard

**Ziel**

Verhindern von unauthorized access, forced browsing, sensitive data leaks und privilege escalation im Admin-Bereich. Sicherstellen, dass administrative Aktionen sicher, auditiert, CSRF-geschützt und nur durch berechtigte Akteure ausführbar sind.

**Scope / Prüfbereiche**

URL-/Endpoint-Hardening, Forced-Browsing / hidden endpoints, Admin-APIs (read/write) und Bulk-Actions, CSRF auf Admin-Actions, Audit / Logging, verbose Fehlerinfos, Entwickler-/Debug-Endpunkte, default credentials, MFA/2FA für Admin, rate limiting, session timeouts, clickjacking / frame-busting.

**WSTG-Mapping (relevante Bereiche — benutze diese Referenzen im Report)**

- Authorization / Access Control (prüft fehlende/fehlerhafte Zugriffskontrollen, IDOR, privilege escalation).
- Authentication (Admin auth, 2FA/MFA, default credentials).
- Session Management (timeout, cookie flags, session invalidation).
- CSRF tests (state-changing admin requests).
- Error Handling & Information Leakage (stack traces, debug data).
- API Discovery / Hidden Endpoints (Swagger/GraphiQL/Devtools exposure).
- Logging & Monitoring (audit trail verification).

---

## Testübersicht (Kurzliste mit TestIDs)

- **ADM-01** Forced browsing: `/admin/*` ohne Admin-Cookie
- **ADM-02** Privilege escalation via API calls (change other users / escalate)
- **ADM-03** Verbose error messages / stack traces / secret leaks
- **ADM-04** CSRF on admin operations (mass changes)
- **ADM-05** Discovery: exposed dev endpoints (Swagger, GraphiQL, admin consoles)
- **ADM-06** Default/weak admin credentials / account provisioning misconfig
- **ADM-07** Session hardening: long sessions, missing cookie flags, session reuse
- **ADM-08** Clickjacking / framing of admin UI
- **ADM-09** Bulk action abuse: mass privilege changes / CSV imports without authorization
- **ADM-10** Audit & Alerting verification (are admin actions logged & alerted?)

---

## Detaillierte Testfälle

### ADM-01 — Forced browsing: Zugriff auf `/admin/*` ohne Admin-Cookie

**WSTG-Mapping:** Authorization / Forced Browsing.

**Kurz-Schritte**

1. Melde dich als Low-Privileged User (oder anonym).
2. Probiere direkte Aufrufe: `/admin`, `/admin/dashboard`, `/admin/users`, `/api/admin/*`, `/internal/admin/*`.
3. Teste Variationen: query strings, path traversal (`/admin%2e%2e/`), trailing slashes, case variations.
4. Teste `OPTIONS`, `TRACE`, `PUT` falls exposed.

**Automation-Hint**

- ffuf/dirbuster mit Wortlisten, Burp Intruder für parameter fuzzing.
    
    **Erwartetes Ergebnis / Beweis**
    
- 403/401/redirect to login; kein HTML mit sensitive data. Evidence: raw req/resp.
    
    **Severity**
    
- Hoch (wenn admin UI erreichbar oder sensitive Daten angezeigt).
    
    **Schnelle Gegenmaßnahme**
    
- Serverseitige AuthZ für alle `/admin` Routen; deny by default.

---

### ADM-02 — Privilege escalation via API calls (z. B. change other users)

**WSTG-Mapping:** Authorization / Privilege Escalation.

**Kurz-Schritte**

1. Login als Nicht-Admin → intercept admin API calls you can see (e.g., from UI or discovered endpoints).
2. Versuch, direkte API-Aufrufe gegen admin endpoints (PUT /api/users/{id}/role) mit manipulierten `targetId`/`role`.
3. Wenn API requires admin CSRF token, test missing/invalid token flows.
4. Prüfe auch business logic: z. B. promotion via payment/refund endpoints.

**Automation-Hint**

- Burp Repeater + scripted fuzzing across role values and target ids.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server prüft caller role; Response 403; DB unverändert. Evidence: raw req/res, GET user before/after.
    
    **Schnelle Gegenmaßnahme**
    
- Zentralisierte Authorization middleware, deny unless allow rule, require admin scope and MFA for role changes.

---

### ADM-03 — Verbose stack traces / sensitive data in responses

**WSTG-Mapping:** Error Handling & Information Leakage.

**Kurz-Schritte**

1. Führe fehlerhafte Requests aus (missing params, malformed JSON, unexpected input) auf admin endpoints.
2. Suche in Responses nach Stacktraces, SQL errors, connection strings, internal pathnames, AWS keys, SQL dumps.
3. Untersuche server headers, error pages and any HTML comments.

**Automation-Hint**

- Burp Scanner + manual malformed inputs; grep responses for keywords (`Exception`, `Stacktrace`, `SQLException`, `password`, `aws_secret`).
    
    **Erwartetes Ergebnis / Beweis**
    
- Keine stack traces / secrets; Responses are generic (500 Internal Server Error + friendly message). Evidence: response screenshots/snippets.
    
    **Schnelle Gegenmaßnahme**
    
- Disable debug in prod, generic error pages, remove verbose logging from responses, sanitize exceptions.

---

### ADM-04 — CSRF auf Admin-Operationen (mass changes)

**WSTG-Mapping:** CSRF tests.

**Kurz-Schritte**

1. Während Admin eingeloggt ist, besuche eine bösartige Seite die eine POST an admin endpoint absetzt (Form auto-submit).
2. Teste JSON endpoints (non-form) — viele APIs accept JSON and require custom headers (X-Requested-With).
3. Prüfe SameSite cookie effect und whether CSRF tokens enforced.

**Automation-Hint**

- PoC HTML + Burp to replay; test both form and fetch/XHR style requests.
    
    **Erwartetes Ergebnis / Beweis**
    
- Requests rejected without valid CSRF token or CORS denies request; no change performed. Evidence: PoC + server response.
    
    **Schnelle Gegenmaßnahme**
    
- CSRF tokens + require custom header + SameSite cookie; re-auth/MFA for critical admin operations.

---

### ADM-05 — Discovery: exposed Dev-Endpunkte (Swagger, GraphiQL, DB consoles)

**WSTG-Mapping:** API Discovery / Hidden Endpoints.

**Kurz-Schritte**

1. Suche nach `/swagger`, `/api/docs`, `/graphiql`, `/console`, `/adminer`, `/pgadmin`, `/h2-console`.
2. Prüfe ob diese Endpunkte erreichbar ohne auth or with weak auth.
3. Teste if they allow execution of queries or modifications.

**Automation-Hint**

- ffuf + common paths; check robots.txt, sitemap.xml, JS bundles for references.
    
    **Erwartetes Ergebnis / Beweis**
    
- Dev consoles not accessible in prod; if accessible, they require admin auth. Evidence: raw req/res and screenshots.
    
    **Schnelle Gegenmaßnahme**
    
- Remove or restrict dev consoles in prod, IP-whitelist, require mTLS or VPN.

---

### ADM-06 — Default / weak admin credentials & provisioning flaws

**WSTG-Mapping:** Authentication tests.

**Kurz-Schritte**

1. Check for default admin user creation during install (e.g., admin:admin).
2. Attempt common default credentials and weak passwords on admin endpoints.
3. Check provisioning flows (self-register as admin?) and invite links granting admin role.

**Automation-Hint**

- Use a small wordlist of common defaults; inspect installation docs/metadata.
    
    **Erwartetes Ergebnis / Beweis**
    
- No default creds; provisioning flows require validated approval. Evidence: auth attempts logged and denied.
    
    **Schnelle Gegenmaßnahme**
    
- Enforce forced password change at first login, disable default accounts, require admin onboarding via secure process.

---

### ADM-07 — Session hardening: long sessions, missing cookie flags, session reuse

**WSTG-Mapping:** Session Management.

**Kurz-Schritte**

1. Prüfe Set-Cookie headers for admin session cookies: `Secure`, `HttpOnly`, `SameSite`.
2. Teste session TTL: bleibt session sehr lange aktiv?
3. Test session fixation: set cookie before login, login → does id rotate? Test reuse after logout.

**Automation-Hint**

- curl to capture headers, scripted session reuse tests.
    
    **Erwartetes Ergebnis / Beweis**
    
- Cookies secure flags present, session rotates on auth, logout invalidates server session. Evidence: headers + replay attempts.
    
    **Schnelle Gegenmaßnahme**
    
- Set cookie flags, rotate session IDs on auth events, short admin session TTL, require re-auth for sensitive ops.

---

### ADM-08 — Clickjacking / framing of admin UI

**WSTG-Mapping:** UI security / clickjacking.

**Kurz-Schritte**

1. Host attacker page with `<iframe src="https://app/admin"></iframe>` and try actions via overlay.
2. Check if admin UI sets `X-Frame-Options: DENY` or CSP `frame-ancestors`.

**Erwartetes Ergebnis / Beweis**

- Framing blocked; header present. Evidence: missing frame renders or headers.
    
    **Schnelle Gegenmaßnahme**
    
- Set `X-Frame-Options: DENY` or Content Security Policy `frame-ancestors 'none'`.

---

### ADM-09 — Bulk action abuse (CSV import, mass role changes)

**WSTG-Mapping:** Business logic / Authorization.

**Kurz-Schritte**

1. Verwende bulk endpoints (CSV import, mass-update) und versuche Einträge zu manipulieren (z. B. set role field to ADMIN in CSV).
2. Prüfe ob import validiert und ob operation checks caller rights on each row.

**Erwartetes Ergebnis / Beweis**

- Server enforces per-row ACL & validation; rejects unauthorized privileged changes. Evidence: before/after records, import logs.
    
    **Schnelle Gegenmaßnahme**
    
- Validate and sanitize CSV content, require admin approvals, dry-run + review before apply.

---

### ADM-10 — Audit & Alerting verification

**WSTG-Mapping:** Logging & Monitoring.

**Kurz-Schritte**

1. Perform admin actions (change role, delete user) and verify logs contain actor, timestamp, target and old/new states.
2. Trigger suspicious activity and verify alerts (SIEM) or notifications.
3. Check retention, integrity and access control of logs.

**Erwartetes Ergebnis / Beweis**

- Action logged with sufficient context; alerts for abnormal patterns. Evidence: log excerpts, alert screenshots.
    
    **Schnelle Gegenmaßnahme**
    
- Ensure immutable logs, forward critical logs to SIEM, configure alerts for admin ops.

---

## Tools & Beispiel-Payloads (nur in autorisierten Testumgebungen)

- Tools: Burp Suite (Proxy/Repeater/Intruder/Scanner), ffuf/dirb, curl, Postman, Selenium (UI flows), sqlmap (only if injection suspected), SIEM/log access for audit checks.
- Beispiel-Requests / Payloads:
    - Forced browsing fuzz: wordlist `admin, admin/login, admin/users, internal, debug, console` with ffuf.
    - Tamper payload for escalation: `PUT /api/users/42` `{"roles":["ADMIN"]}`.
    - CSRF PoC HTML form that POSTs to `/api/admin/users/42/role`.
    - Error fuzz: malformed JSON, huge payloads, missing required fields to provoke stack traces.

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. ADM-02)
- **WSTG-Ref** (z. B. Authorization / Privilege Escalation)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw HTTP req/res + env)
- **Beweis (raw req/res, screenshots, log excerpts)**
- **Severity (CVSS + Business Impact)**
- **Remediation / Quickfix**
- **Detailled remediation / Design changes**
- **Mitigation / temporary controls** (e.g., restrict IPs, disable endpoint)

---

## Schnelle Gegenmaßnahmen (Kurz)

- Restrict all `/admin` endpoints with strong server-side AuthZ (deny by default).
- Require MFA/re-auth for admin actions and role changes.
- Enforce CSRF protection and SameSite cookie policies.
- Remove dev consoles from prod or protect via IP/VPN/mTLS.
- Disable verbose error output; sanitize exception messages.
- Set cookie flags (Secure, HttpOnly, SameSite), rotate session IDs on auth events.
- Audit logging + SIEM alerts for all admin actions; immutable storage.
- Use RBAC/ABAC policy engine for complex rules; require two-person approval for high-risk actions.

## Tiefergehende Empfehlungen (Architektur / Process)

- Bastion admin access (VPN + dedicated admin network), mTLS or client certs for admin consoles.
- Harden CI/CD to avoid shipping debug flags.
- Periodic privileged-account review and least-privilege enforcement.
- Automated smoke tests that verify admin endpoints require auth and are not publicly accessible.
- Penetration test runbook: include forced browsing discovery, CSRF PoC, bulk import abuse and audit verification.

---

Wenn du willst, erstelle ich daraus **sofort** eines der folgenden artefakte (wähle eine Option, ich generiere es direkt):

- **CSV** (TestID | Komponente | WSTG_Ref | Steps | Payload | Tool | Expected | Remediation) — für deine Checklist,
- **JSON** Test-Schema (für Test-Harness / CI),
- **Burp Repeater raw-requests + CSRF PoC HTML** (zum direkten Ausprobieren in einem autorisierten Lab),
- **kleines Python-Script** zum forced-browsing / endpoint discovery (nur für genehmigte Targets).

Welche dieser Ausgaben soll ich dir jetzt direkt erzeugen?