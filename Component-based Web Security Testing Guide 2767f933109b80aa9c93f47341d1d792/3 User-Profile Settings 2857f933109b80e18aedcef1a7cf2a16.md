# 3. User-Profile / Settings

# Kapitel: User-Profile / Settings

**Ziel**

Verhindern von IDOR (Insecure Direct Object Reference), Privilege-Tampering, Stored XSS und unsicheren Direktzugriffen auf Profil-Daten oder -Assets.

**Scope / Prüfbereiche**

Authorization checks (serverseitig), Objekt-ID-Handling (nicht vorhersagbare IDs, canonical mapping), Input-Sanitization (profilfelder, Bio, Display-Name), File/Avatar Uploads (Content-Sniffing, Ausführung), Profil-Enumeration (user-list, autocomplete), Logging/Monitoring.

**WSTG-Mapping (relevante Bereiche)**

- **WSTG Authorization Tests** — Tests zu fehlender/fehlerhafter Zugriffskontrolle (IDOR, horizontal/vertical privilege).
- **WSTG Input Validation** — Tests zu Stored/Reflected XSS in User-input.
- **WSTG File Handling / File Upload** — Tests zu Upload-RCE, content sniffing, storage location.
- **WSTG Session & Authentication-related checks** — wenn Änderungen an Rollen / Claims stattfinden.
    
    (Verwende diese WSTG-Bereiche beim Reporten als Referenz.)
    

---

## Testfälle (Detail + WSTG-Map)

### Testfall UP-01 — **IDOR: Zugriff auf `/profile/{id}` mit fremder id**

**WSTG-Mapping:** Authorization / IDOR tests (WSTG Authorization).

**Kurz-Schritte**

1. Melde dich als *User A* an (herkömmliche Session/Cookie).
2. Rufe `/profile/{id_B}` auf, wobei `id_B` die ID von User B ist (bekannt oder by enumeration).
3. Prüfe Response: returned data, HTTP Status, sensitive Felder (E-Mail, Telefonnummer, Rollen, private Flags).
4. Wiederhole mit APIs: `GET /api/users/{id}`, `GET /profile?id=...`, `POST /profile/view` (versch. Endpunkte).

**Automation-Hint**

- Script: iteriere über ID-Range / inkrementelle IDs, sammle 200/403/404 Antworten → find patterns.
- Burp / ffuf für automatisches Forced-Browsing auf REST-Endpunkten.

**Erwartetes Ergebnis / Beweis**

- Unauthorized requests → `403` oder `404` (keine sensitiven Daten). Evidence: raw request + response, Liste gefundener IDs (falls Disclosure).

**Schnelle Gegenmaßnahme**

- Serverseitige ACL: `ownerId == session.userId || hasRole(admin)`; keine direkte Nutzung von client-vermittelten IDs ohne mapping; canonical ID mapping.

---

### Testfall UP-02 — **Privilege tampering: Tamper requests to change `role` / `isAdmin` in profile update**

**WSTG-Mapping:** Authorization / Business Logic (WSTG Authorization & Logic flaws).

**Kurz-Schritte**

1. Als normaler User A: Intercept `PUT /api/users/{A}` oder `POST /profile/update`.
2. Ändere JSON payload: setze `"role":"admin"` oder `"isAdmin": true` oder füge `roles: ["ROLE_ADMIN"]`.
3. Replay the request; prüfe Response und tatsächlichen Status im UI (Backend sollte ablehnen).
4. Prüfe auch JWT/Token claims: manipulierte Token (falls clientseitig editierbar) oder zusätzliche Claims im Request.

**Automation-Hint**

- Burp Repeater / Intruder für schnelle Tamper-Versuche; Scripted requests zur Massentestung.

**Erwartetes Ergebnis / Beweis**

- Server ignoriert clientseitige Rollenänderungen; Response = 4xx / validation error; DB zeigt keine role-Änderung. Evidence: raw req/res, DB/GET vor+nach.

**Schnelle Gegenmaßnahme**

- Serverseitige Authorisierung vor Persistierung; Rollen nur über dedizierte Admin-APIs änderbar und mit Audit-Trail; JWTs signieren & serverseitig validieren.

---

### Testfall UP-03 — **Stored XSS via profile bio, display name, avatar metadata**

**WSTG-Mapping:** Input Validation / XSS tests (WSTG Input Validation).

**Kurz-Schritte**

1. Als User A: Trage in `bio`, `displayName` oder `location` payloads ein wie `<script>alert(1)</script>` oder weniger offensichtliche: `"><img src=x onerror=alert(1)>`.
2. Speichere und öffne Profil A als *anderen* Benutzer B (oder als anonymer Besucher).
3. Beobachte: Ausführung von Skript, DOM-Injection, Response-Rendering. Prüfe auch avatar-Metadaten (EXIF comments) mit JS-Injection.
4. Teste encoded/obfuskierte Varianten: `&lt;script&gt;`, JS-Eventhandler, SVG payloads, `<a href=javascript:...>`.

**Automation-Hint**

- Burp, Selenium (für Rendering in Browser), headless Chrome zur Erkennung von JS-Execution.
- Tools: DOM XSS scanners, Payload-Listen (DOM + Stored XSS).

**Erwartetes Ergebnis / Beweis**

- Keine Scriptausführung; Display-Name/Bio escaped; PoC: Screenshot oder screenrec der XSS Ausführung + raw stored content in DB (falls zugänglich).

**Schnelle Gegenmaßnahme**

- Serverseitige Sanitization (Whitelist approach), safe HTML-sanitizer (z. B. DOMPurify auf Server/Client), Content-Security-Policy (CSP), HttpOnly cookies, escape on output.

---

### Testfall UP-04 — **Upload arbitrary file as avatar and attempt to execute**

**WSTG-Mapping:** File Upload / File Handling tests (WSTG File Handling).

**Kurz-Schritte**

1. Versuche Uploads mit mehreren Varianten: `shell.php.jpg` (PHP content with image header fudging), `.htaccess` upload (if Apache), SVG with `<script>`, image with EXIF containing `<script>`, or `.jsp` depending on backend.
2. Nach Upload: rufe die Datei direkt über die bereitgestellte URL auf (GET). Prüfe ob sie als Bild serviert wird oder als ausführbar interpretiert wird.
3. Prüfe Headers: `Content-Type`, `Content-Disposition`. Versuche code execution (nur in autorisierten Labs).
4. Teste path traversal in filename or upload endpoint to write outside intended dir.

**Automation-Hint**

- Burp Intruder + payloads for multiple extensions; ffuf for probing upload directory; small script to try many crafted files.

**Erwartetes Ergebnis / Beweis**

- Dateien dürfen nicht als Scripts ausgeführt; Zugriff auf Datei ergibt image content type; Nicht-Owner requests auf private images = 403. Evidence: raw upload req/res, GET response headers, behavior.

**Schnelle Gegenmaßnahme**

- Store uploads outside webroot or serve via proxy that sets safe headers; verify magic bytes (not only extension); rename files server-side; set `Content-Disposition: attachment` for downloads; disable script execution in upload directories.

---

## Ergänzende Prüfungen & Edge Cases

- **Profile Enumeration / Autocomplete**: Prüfe `/api/users/search?query=...` auf massenhafte enumeration (einfache Rate-Limit/ACL).
- **Partial disclosure via metadata**: Avatar URLs, `rel` links oder microdata können Email/phone leak verursachen.
- **Access controls on history/logs**: Profile change history oder audit logs müssen geschützt sein.
- **Client-side stored data**: Prüfe ob sensitive profile-data in localStorage/IndexedDB landet (XSS-Amplification).
- **Privacy & GDPR**: Prüfe Einsicht/Export von personenbezogenen Daten via profile endpoints (Data Subject Access).

---

## Tools & Beispiel-Payloads (nur autorisiert verwenden)

- Tools: Burp Suite (Proxy/Repeater/Intruder), sqlmap not needed here, ffuf/dirb, curl, Selenium/headless Chrome, exiftool (prüft EXIF), small Python scripts (requests + threading).
- Beispiel-Payloads:
    - XSS: `<script>alert(1)</script>`, `"><img src=x onerror=alert(1)>`, `"><svg onload=alert(1)>`.
    - Upload: `<?php echo "pwned"; ?>` saved with `.php.jpg` header + correct magic bytes.
    - IDOR enum: incrementale IDs `1..N`, UUID guess attempts.

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID**: `UP-IDOR-01`, `UP-TAMPER-02`, `UP-XSS-03`, `UP-UPLOAD-04`
- **WSTG-Ref**: z. B. „Authorization / IDOR“, „Input Validation / Stored XSS“, „File Upload / File Handling“
- **Kurzbeschreibung**
- **Reproduktionsschritte (raw request + payload)**
- **Beweis (Raw req/res, Screenshots, DB rows if available)**
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation
- **Mitigation/Compensating Controls** (z. B. temporary ACLs, monitoring)

---

## Schnelle Gegenmaßnahmen (zusammengefasst)

- Serverseitige ACL/Ownership-Checks bei jedem read/update auf Profil-Ressourcen.
- Keine vertrauenswürdigen clientseitigen Felder (role/isAdmin) akzeptieren; Rollenänderungen nur über Admin-API.
- Output-Escaping + serverseitige Sanitizer (Whitelist) + CSP.
- Uploads außerhalb Webroot, Datei-Rename, Magic-byte Prüfung, Content-Type Setzung auf `image/*` + `Content-Disposition: inline`/`attachment` policy as needed.
- Rate-Limiting / Throttling für profile enumeration and upload endpoints.
- Audit logging für role changes and sensitive profile edits.

---