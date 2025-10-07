# 11. Cookie / Session UI (logout, remember me)

# Kapitel: Cookie / Session UI (logout, remember me)

**Ziel**

Absichern persistenter Sessions (z. B. „Remember me“), Verhindern von Session Fixation, sicherer Cookie-Handling und korrekte Invalidierung von Sessions beim Logout. Sicherstellen, dass langlebige Tokens an Gerät/Context gebunden sind und Session-IDs auf kritischen Events rotiert werden.

**Scope / Prüfbereiche**

- Implementation von „Remember me“ (persistent login) und Refresh/long-lived tokens
- Session fixation (vor Login gesetzte Session IDs)
- Session rotation bei Auth/Privilege-Changes
- Logout behavior (serverseitige Invalidation)
- Cookie Flags: `Secure`, `HttpOnly`, `SameSite`
- Token binding (device fingerprinting, IP/UA binding)
- Storage location (cookies vs localStorage)
- Revocation / revocation lists & logout from all devices flows
- CSRF impact on session endpoints

**WSTG-Mapping (relevante Bereiche)**

- **WSTG-SESS** — Session Management (creation, fixation, logout, cookie attributes).
- **WSTG-ATHN** — Authentication (remember-me, persistent credentials).
- **WSTG-CSRF** — CSRF tests (logout / session endpoints).
- **WSTG-INFO** — Cookie security & transport.

---

## Testfälle (Kurzliste mit TestIDs)

- **CSN-01** — Session fixation (set cookie before login → reused?)
- **CSN-02** — Persistent token theft (copy remember-me cookie to another device)
- **CSN-03** — Logout invalidation & session reuse after logout
- **CSN-04** — Cookie attributes presence / Secure + HttpOnly + SameSite
- **CSN-05** — Session rotation on login / privilege change (new session id)
- **CSN-06** — Long-lived token binding (device/IP/UA) & refresh token misuse
- **CSN-07** — Remember-me token revocation / logout all devices
- **CSN-08** — CSRF on session endpoints (logout / revoke)

---

## Detaillierte Tests — Schritte, Hints, Erwartetes Ergebnis

### CSN-01 — Session fixation (TestID CSN-01)

**WSTG-Mapping:** WSTG-SESS Session Fixation tests.

**Kurz-Schritte**

1. In Browser A (attacker or unauthenticated) set a cookie name matching session cookie (e.g. `session=attacker123`) for the app domain (via devtools).
2. Open login page, authenticate as victim user (perform normal login).
3. Observe `Set-Cookie` headers after login and the final session id in cookie.
4. Try to use the attacker session id to access the authenticated session (in attacker context) if possible.

**Automation-Hint**

- Burp or curl to set cookies and replay. Use browser devtools to manipulate document.cookie prior to login.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server **rotates**/replaces session id on login; attacker supplied id should **not** be accepted as authenticated session. Evidence: `Set-Cookie` before/after, raw request/responses showing new cookie value and that attacker session does not access victim resources.
    
    **Schnelle Gegenmaßnahme**
    
- Rotate session id on authentication events and generate new session server-side.

---

### CSN-02 — Persistent token theft (Remember-me cookie)

**WSTG-Mapping:** WSTG-ATHN persistent auth tests.

**Kurz-Schritte**

1. Login with „Remember me“ enabled on Browser A — note cookie(s) names (e.g., `remember_me`, `persistent_token`).
2. Copy cookie value(s) and paste into Browser B (different machine/profile) under same domain.
3. Load site in Browser B and check whether it is automatically authenticated as the user.
4. Try to use token after device change or after rotating UA/IP (simulate theft).

**Automation-Hint**

- Use devtools or Burp to export/import cookie header. For device binding, change user agent and IP via proxy.
    
    **Erwartetes Ergebnis / Beweis**
    
- If token alone grants auth (without additional binding) attacker gains access (bad). **Expect**: Remember-me token either tied to device (fingerprint), requires one-time verification, or is single-use and short TTL. Evidence: cookie values + access results.
    
    **Schnelle Gegenmaßnahme**
    
- Implement persistent tokens in server DB with device fingerprinting, short TTL, single-use refresh, and require re-auth for sensitive actions.

---

### CSN-03 — Logout invalidation & reuse after logout (CSN-03)

**WSTG-Mapping:** WSTG-SESS Logout / Session invalidation.

**Kurz-Schritte**

1. Login as User A → capture active session cookie.
2. Perform Logout (via UI). Record response and Set-Cookie (if cleared).
3. Try to reuse the old session cookie in a new request (same cookie header) to a protected endpoint.
4. Also test "logout all devices" flow if available.

**Erwartetes Ergebnis / Beweis**

- Server invalidates session server-side; subsequent requests with old cookie must be rejected (401/403). Evidence: raw req/res showing server rejects request despite old cookie. If logout route sets `Set-Cookie: session=; Max-Age=0`, still must ensure server-side session invalidation.
    
    **Schnelle Gegenmaßnahme**
    
- Invalidate session server-side on logout; store session states in server store and mark as revoked.

---

### CSN-04 — Cookie attributes presence (Secure, HttpOnly, SameSite) (CSN-04)

**WSTG-Mapping:** WSTG-SESS Cookie attributes tests.

**Kurz-Schritte**

1. Inspect `Set-Cookie` headers for auth cookies (login response) using curl or devtools network.
2. Verify flags: `Secure` (for HTTPS only), `HttpOnly` (not accessible via JS), `SameSite` (Lax/Strict as appropriate).
3. If `remember_me` uses persistent cookie, ensure attributes set too.

**Erwartetes Ergebnis / Beweis**

- All auth cookies set `Secure; HttpOnly; SameSite=Lax or Strict` as appropriate. Evidence: captured headers.
    
    **Schnelle Gegenmaßnahme**
    
- Enforce Secure + HttpOnly + SameSite for auth/persistent cookies.

---

### CSN-05 — Session rotation on login / privilege change (CSN-05)

**WSTG-Mapping:** WSTG-SESS session rotation tests.

**Kurz-Schritte**

1. Authenticate as User A; capture session id.
2. Trigger privilege change (e.g., login with MFA, or role elevation) or logout/login event.
3. Confirm server issues new session id and invalidates old one.

**Erwartetes Ergebnis / Beweis**

- Session id rotated on sensitive events; old id invalidated. Evidence: session id before/after and server responses rejecting old id.
    
    **Schnelle Gegenmaßnahme**
    
- Always rotate session id on authentication and privilege elevation.

---

### CSN-06 — Long-lived token binding & refresh misuse (CSN-06)

**WSTG-Mapping:** WSTG-ATHN persistent tokens & refresh tokens.

**Kurz-Schritte**

1. Inspect remember/refresh token flow: where tokens stored server-side, are refresh tokens single-use, what is TTL?
2. Attempt to reuse a refresh token after using it once (should be rotated).
3. Try to use refresh token from different device/UA/IP.

**Erwartetes Ergebnis / Beweis**

- Refresh tokens are single-use or bound to device; stale refresh tokens rejected; evidence: request/response and token rotation logs.
    
    **Schnelle Gegenmaßnahme**
    
- Implement refresh token rotation, store tokens server-side with device metadata, revoke on suspicious reuse.

---

### CSN-07 — Remember-me revocation / logout all devices (CSN-07)

**Kurz-Schritte**

1. Create remember tokens on multiple devices. Use “logout all devices” or revoke feature.
2. Confirm all tokens invalidated and devices require re-login.

**Erwartetes Ergebnis**

- All devices require re-auth; evidence: attempts using old cookies fail.
    
    **Schnelle Gegenmaßnahme**
    
- Provide server endpoint to revoke all persistent tokens and enforce immediate invalidation.

---

### CSN-08 — CSRF on session endpoints (logout / revoke) (CSN-08)

**WSTG-Mapping:** WSTG-CSRF.

**Kurz-Schritte**

1. While authenticated, visit an attacker page that issues `POST /logout` or `POST /revoke` without CSRF token (auto-submit form).
2. Observe if the server performs state-changing action without CSRF protection.

**Erwartetes Ergebnis**

- State-changing session endpoints require CSRF tokens or custom header; requests from foreign origin rejected. Evidence: PoC page + server response.
    
    **Schnelle Gegenmaßnahme**
    
- Require CSRF tokens or double-submit cookies for session-affecting endpoints; enforce `SameSite` where applicable.

---

## Automation & Tools (only in authorised tests)

- Tools: Burp Suite (Proxy/Repeater), curl, Postman, Selenium/Puppeteer (for cookie manipulation), browser DevTools (Application → Cookies), proxy for IP/UA changes, scripts to copy/import cookies.
- Useful commands:
    - `curl -i -c cookies.txt -b cookies.txt https://app.example/...` (capture headers)
    - Use Burp to intercept Set-Cookie and inspect flags.
- Patterns to look for: JWT format in cookie/localStorage, names like `remember`, `persistent`, `refresh_token`.

---

## Reporting Template (Minimalfelder pro Finding)

- **TestID** (e.g., CSN-02)
- **WSTG-Ref** (e.g., WSTG-SESS, WSTG-ATHN)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw requests, cookie values obfuscated)
- **Beweis** (Set-Cookie headers, replay results, screenshots)
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation
- **Mitigation / temporary controls**

---

## Erwartetes Ergebnis / Akzeptanzkriterien

- Auth and persistent cookies must have `Secure; HttpOnly; SameSite` set.
- Session IDs are rotated on login and privilege elevation; attacker-supplied session IDs are rejected.
- Logout invalidates session server-side (not only client cookie deletion).
- Remember-me tokens are server-tracked, bound to device/UA/IP → single-use or require re-verification, short TTL, can be revoked centrally.
- CSRF tokens or equivalent protections on logout and revoke endpoints.

---

## Schnelle Gegenmaßnahmen (Kurz)

- Rotate session ID on all authentication/privilege events.
- Store persistent tokens server-side (DB) with device metadata; mark tokens single-use or rotate on refresh.
- Enforce `Secure; HttpOnly; SameSite` cookie attributes.
- On logout, server-side session invalidation and persistent token revocation.
- Implement “logout all devices” and ability to revoke persistent tokens.
- Use CSRF tokens (synchronizer or double-submit) for state-changing session endpoints.
- Avoid storing tokens in JS-accessible storage (localStorage) for critical auth tokens.

---

## Tiefergehende Empfehlungen (Architektur / Process)

- Use short-lived access tokens and refresh tokens with rotation + revocation lists.
- Tie persistent tokens to device fingerprints and IP heuristics; alert on token reuse from new geolocation or UA.
- Provide administrative view for active sessions + ability to revoke.
- Add automated tests that simulate fixation and token theft as part of CI/CD security checks.
- Consider using secure, audited session stores (Redis with encryption) and strict session lifecycle policies.

---