# 2. Register / Forgot-Password

# Kapitel: Register / Forgot-Password

**Ziel**

Schutz vor Account-Enumeration, Schwachstellen im Registrierungs-/Passwort-Wiederherstellungs-Flow (weak passwords, token-Abuse), Race-Conditions beim Anlegen von Accounts und Missbrauch von Recovery-Mechanismen.

**Scope / Prüfbereiche**

Error-Message-Uniformität (Account-Enumeration), server-side validation (Passwortrichtlinie), Token-Leben/Single-Use (Reset/“Magic Link”), E-Mail-Inhalt (Leaking), CAPTCHA/Rate-Limiting, Race-conditions / uniqueness checks, logging & monitoring der Flows.

**WSTG-Mapping (relevant section names)**

- *Identity Management / Account Creation* → Tests zur Registrierung und Input-Validation.
- *Identity Management / Account Enumeration* → Testing for account enumeration and guessing.
- *Identity Management / Password Reset* → Testing password reset and recovery flows (token usage, single-use, expiry).
- *Authentication / Brute-Force & Rate Limiting* → Für rate limiting auf recovery endpoints.
- *Session Management / Secure Transport* → Wenn tokens in URL etc.

---

## Testfall A — **Account-Enumeration via unterschiedliche Fehlermeldungen / Timings**

**WSTG Mapping:** Identity Management → Account enumeration tests.

**Kurz-Prüfschritte**

1. Führe `POST /register` oder `POST /forgot-password` (oder das Formular) mit einer E-Mail/Username, von dem du weißt, dass er existiert. Notiere Response-Body, HTTP-Status, Response-Time.
2. Wiederhole mit einer nicht existierenden E-Mail/Username. Vergleiche: Fehlermeldungstext, HTTP-Status, Header, Response-Länge, Timing.
3. Prüfe auch indirekte Kanäle: „Anmeldung erforderlich“ Banner, E-Mail-Queue Verhalten (wird Mail gesendet?), Captcha-Auslöser.
4. Teste Varianten (case, trailing space, URL encoding) um subtile Unterschiede aufzuspüren.

**Automation-Hint**

- Einfache Python/Requests-Script oder Burp Repeater → vergleichen von `response.body`, `status_code`, `Content-Length`, `response.elapsed`.
- Timing-Tests: mehrere Messungen, Mittelwert, StdDev.

**Erwartetes Ergebnis / Beweis**

- Homogene Response (z. B. immer: „Wenn ein Account existiert, bekommst du eine Mail“), gleiche Statuscodes und keine differenzierbaren Timings. Evidence: zwei raw HTTP responses (exist / not-exist) mit identischem Body/Status/Headers (oder differenz minimal und dokumentiert).

**Risiken wenn fehlerhaft**

- Angreifer kann Accounts enumerieren → zielgerichtete Phishing/Brute-Force.

**Schnelle Gegenmaßnahmen**

- Einheitliche Messages, gleiche HTTP-Status (z. B. 200 always), zufällige (but bounded) artificial response delays if absolutely necessary, rate limiting on lookup endpoints.

---

## Testfall B — **Bypass client-side Password-Rules via direkte API-Calls**

**WSTG Mapping:** Identity Management / Input Validation & Server-Side Enforcement.

**Kurz-Prüfschritte**

1. Beobachte Client-Seite: welche Passwortregeln sind enforced (JS checks, regex)?
2. Intercept Register POST request (oder API call) und präge für `password` einen schwachen Wert (`"123"`, `"pass"`, `""`).
3. Sende das modifizierte Request direkt an API (bypassing JS).
4. Teste auch malformed encodings (Unicode homoglyphs) und very long / very short strings.

**Automation-Hint**

- Burp Repeater / curl / Python requests.
- Automatisiertes Testset mit typische weak passwords (top-10k) gegen API (nur mit Authorisierung/Scope).

**Erwartetes Ergebnis / Beweis**

- Server-seitige Validierung blockiert weak password; Response zeigt validation error (server message) und Account wird nicht angelegt. Evidence: raw req/res, DB-check (falls möglich) showing no user created.

**Schnelle Gegenmaßnahmen**

- Server-seitige Password Policy enforcement (min length, complexity, zxcvbn scoring), reject on server, explicit error codes for devs but generic messages for UI, hashing+salting on storage.

---

## Testfall C — **Predictable / long-lived reset tokens / reuse**

**WSTG Mapping:** Identity Management → Password Reset & Token Management.

**Kurz-Prüfschritte**

1. Trigger „forgot password“ flow für ein Testkonto; fange Reset-E-Mail ab (in scope). Notiere reset token format (length, charset), ob Token in URL query param or body, and whether token is hashed in DB (if DB access in scope).
2. Versuche: a) reuse the token after first use, b) use token after expiry (wait/modify expiry), c) brute small token space (if short).
3. Check if token leaks in Referer headers or logs or in email previews.
4. Test magic-link flows: is the link single-use? Does it rotate session on use?

**Automation-Hint**

- Script to request many resets and collect tokens; entropy analysis (length, base64 vs hex).
- If possible, check DB for token storage (hashed vs plaintext).

**Erwartetes Ergebnis / Beweis**

- Token is single-use, short TTL (e.g., 15-60 minutes), not reproducible/predictable, stored hashed server-side or validated by one-way check. PoC: token reuse attempt fails; expired token rejected.

**Schnelle Gegenmaßnahmen**

- Single-use tokens, short TTL, store only token hashes (HMAC), bind token to user id + IP/device fingerprint optionally, send tokens via POST (not GET) where feasible, avoid embedded sensitive data in URL.

---

## Testfall D — **Race-conditions bei Registrierung (duplicate checks / uniqueness bypass)**

**WSTG Mapping:** Identity Management → Account Creation / Logic Flaws.

**Kurz-Prüfschritte**

1. Starte zwei (oder mehrere) parallele Registrierung-Requests für denselben username/email quasi-gleichzeitig (z. B. Threads/processes).
2. Beobachte ob mehr als ein Account mit identischem UniqueKey entsteht oder ob constraints/transactions verhindern duplication.
3. Prüfe DB-Fehler oder application-level duplicate entries.

**Automation-Hint**

- kleines Python Script (ThreadPool / asyncio) das gleichzeitig `n` Register Requests abschickt.
- Beobachte Statuscodes (201/409/500) und response bodies.

**Erwartetes Ergebnis / Beweis**

- Nur 1 Account angelegt; andere Requests return 409 or proper error; DB unique constraints enforced. Evidence: raw logs, DB rows count, request timeline.

**Schnelle Gegenmaßnahmen**

- DB-level UNIQUE constraints, transactions/serializable isolation or optimistic locking, atomische create-or-fail operations, idempotency tokens for registration flows.

---

## Zusätzliche Prüfbereiche & Edge-Cases

### 1) **E-Mail Content Leakage**

- Prüfe, ob E-Mails sensitive Daten enthalten (z. B. Teile des Passworts, internal URLs with tokens, debug info).
- Erwartung: E-Mails enthalten nur minimal hilfreiche Info + user friendly text + non-sensitive link. Use short tokens, avoid sending plaintext secrets.

### 2) **Captcha / Rate Limiting**

- Versuche viele register/forgot requests → beobachte IP throttling / CAPTCHA.
- Erwartet: progressive throttling, captcha after threshold.

### 3) **Logging & Monitoring**

- Check, ob failed attempts trigger alerts or are logged with enough context (timestamp, IP) — wichtig für detection.

### 4) **UX vs Security tradeoff**

- Balance: generic messages vs user friendliness. Document recommended message phrasing for product teams.

---

## Tools & Beispiel-Payloads (nur in autorisierten Tests)

- Tools: Burp Suite (Intruder/Repeater), curl, Python requests, Postman, SMTP trap/mailcatcher (z. B. MailHog), Selenium (für simulating form JS), small concurrency scripts (python threading/asyncio).
- Weak password payloads: `"123"`, `"password"`, `"qwerty"`, top-100 list.
- Parallel registration: 50 concurrent POSTs with same payload.

---

## Beispiel-Schnellfixes (1-Zeiler)

- Einheitliche Response auf `forgot`/`register` (always: „Wenn ein Account existiert, senden wir eine Mail“).
- Server-seitige Passwortrichtlinie (reject weak pw) + client-help text.
- Single-use, short-TTL reset tokens; Token-hashing in DB.
- DB unique constraints + atomic create operations.
- Rate limiting + CAPTCHA + monitoring on register/forgot endpoints.

---

Wenn du willst, mache ich daraus **sofort**:

- a) ein **CSV** mit allen obigen Testcases + WSTG-Mapping + Repro-Steps (für dein Checklist/Scanner),
- b) ein **JSON**Schema (Test-Definitions) für ingestion in ein Test-Harness, oder
- c) generiere ein kleines Python-Script, das parallel Registrations/Timing-Vergleiche automatisiert (nur für autorisierte Testumgebungen).

Welche Ausgabe möchtest du direkt?