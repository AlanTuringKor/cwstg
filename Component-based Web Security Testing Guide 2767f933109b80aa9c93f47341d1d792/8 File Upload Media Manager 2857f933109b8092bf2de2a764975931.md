# 8. File Upload / Media Manager

# Kapitel: File Upload / Media Manager

**Ziel**

Verhindern von RCE über Uploads, Content-Sniffing Bypasses, Path-Traversal, unautorisierter Zugriff auf gespeicherte Dateien sowie XSS via Bild-Metadaten oder SVG. Sicherstellen, dass Uploads validiert, gespeichert, serviert und geprüft werden (antivirus / size limits / MIME checks).

**Scope / Prüfbereiche**

- MIME / content sniffing vs declared Content-Type
- Prüfung der Datei-Inhalte (magic bytes)
- Filename normalization / path traversal prevention
- Storage location (outside webroot, object storage policy)
- Access control (public/private assets, signed URLs)
- Execution prevention (no script execution for uploads)
- Metadata (EXIF) XSS, SVG sanitization
- Thumbnail generation vulnerabilities (unsafe image parsing libs)
- Quotas / rate limiting / large file DoS
- Presigned / public S3 URL risks, CORS, caching headers
- Virus / malware scanning, logging & alerting for uploads

**WSTG-Mapping (relevante Bereiche)**

- *File Uploads / Unrestricted File Upload* — tests for RCE and execution via uploaded files.
- *Input Validation* — magic-byte checks, filename sanitization.
- *Information Leakage / Error Handling* — debug info on upload failures.
- *Business Logic / Access Control* — private/public asset permissioning.
- *Denial of Service* — huge uploads / thumbnail generation exhaustion.
    
    (Verwende diese WSTG-Referenzen im Report.)
    

---

## Testfälle (Kurzliste mit IDs)

- **FU-01** — Upload script disguised as image (double extension / magic-byte evasion).
- **FU-02** — Path traversal via filename / Content-Disposition.
- **FU-03** — Direct access → execution when stored in webroot.
- **FU-04** — Image metadata (EXIF) / filename based XSS when metadata rendered.
- **FU-05** — SVG upload with embedded JS (XSS) or external references.
- **FU-06** — Malicious image triggers RCE in image processing libs (thumbnailing).
- **FU-07** — Large file uploads to exhaust disk/CPU / quotas.
- **FU-08** — Presigned S3 / object storage misconfig (public write/read) & CORS abuse.
- **FU-09** — Missing or unsafe response headers (Content-Type sniffing, cache of private assets).
- **FU-10** — Lack of antivirus / malware scanning on uploads.

---

## Detaillierte Testfälle — Schritte, Hints, Erwartetes Ergebnis

### FU-01 — Upload script disguised as image (double extension, magic bytes)

**WSTG-Mapping:** File Uploads / Input Validation.

**Kurz-Schritte**

1. Erzeuge Datei mit PHP/ASP/JSP payload but prepend valid image magic bytes (JPEG `FF D8 FF`, PNG `89 50 4E 47`). Name it `shell.php.jpg` or `avatar.jpg.php`.
2. Upload via normal avatar/upload form.
3. Sobald upload abgeschlossen, request the returned URL and observe server behavior (render as image, download, attempt execute if URL ends with `.php`).
4. If server stores in S3, try to request public URL or call object via webserver that could interpret it.

**Automation-Hint**

- Burp file upload with custom file. Script to iterate extension combos and magic bytes.
    
    **Erwartetes Ergebnis / Beweis**
    
- Upload accepted only if validated; file served as image only (Content-Type image/*); no server executes code. Evidence: raw upload request/response + GET response headers & body (no PHP output).
    
    **Remediation / Quickfix**
    
- Verify magic bytes and MIME mapping on server; store outside webroot and serve via signed proxy; rename stored files to random safe names and enforced `Content-Type`.

---

### FU-02 — Path traversal in filename / Content-Disposition

**WSTG-Mapping:** Input Validation / File Handling.

**Kurz-Schritte**

1. Upload filename using `../`, `%2e%2e/`, backslashes `..\`, or long unicode sequences. E.g. `../../webroot/shell.php` or `..%2f..%2fwebroot%2fshell.php`.
2. Inspect storage path, returned URL and whether server honors traversal.
3. Try manipulating `Content-Disposition` or multipart form boundary to influence save path.

**Automation-Hint**

- Use Burp to tamper filename param in multipart body; test different encodings.
    
    **Erwartetes Ergebnis / Beweis**
    
- Filenames normalized/stripped; files cannot be written outside intended upload dir. Evidence: directory listing (if accessible), upload location metadata, raw req/res.
    
    **Remediation**
    
- Normalize filenames, remove path separators, enforce allowlist of filename chars, compute server-side storage path only from safe random name or UID.

---

### FU-03 — Direct access to uploaded file (execution in webroot)

**WSTG-Mapping:** File Uploads / Server config.

**Kurz-Schritte**

1. If upload returns a path under webroot (e.g., `/uploads/shell.php.jpg`), try requesting path with `.php` interpretation: `GET /uploads/shell.php.jpg` and with modified Accept header or direct call to certain handlers.
2. If webserver supports content-negotiation, try `GET /uploads/shell.php.jpg/` or `GET /uploads/shell.php.jpg?x=1`.
3. If app uses rewrite rules, attempt to trigger execution via crafted URL.

**Expected / Beweis**

- Files should never be interpreted as scripts; response should be delivered as static asset or Download, not executed. Evidence: output content, no server-side code execution trace.
    
    **Remediation**
    
- Store uploads outside webroot; serve via safe handler that sets `Content-Type` and `Content-Disposition`; disable script execution in upload directories (webserver config).

---

### FU-04 — Image metadata (EXIF) XSS / metadata-based attacks

**WSTG-Mapping:** Input Validation / XSS.

**Kurz-Schritte**

1. Create image whose EXIF comment contains payloads: `<script>alert(1)</script>` or `"><img src=x onerror=alert(1)>`.
2. Upload and then view profile/gallery where metadata or previews are displayed (e.g., "Uploaded by" or tooltip).
3. Verify whether metadata is rendered unsafely into HTML (title attribute, data attributes).

**Automation-Hint**

- exiftool to embed payloads; Selenium to render and detect JS execution.
    
    **Erwartetes Ergebnis / Beweis**
    
- Metadata sanitized/escaped before rendering; no JS executed. Evidence: screenshot of rendered page (no alert) and raw image metadata.
    
    **Remediation**
    
- Strip or sanitize EXIF metadata server-side; do not inject raw metadata into HTML without escaping; use `textContent`.

---

### FU-05 — SVG upload with embedded JS (XSS) or external references

**WSTG-Mapping:** File Uploads / XSS.

**Kurz-Schritte**

1. Create SVG that contains `<script>` or `onload` handlers or external resource references `<image xlink:href="http://evil/...">`.
2. Upload and view SVG inline (if app inlines or renders SVG as HTML).
3. If app serves SVG as `image/svg+xml`, check if browser executes script when rendering inline vs `<img>` vs `background-image`.

**Expected / Beweis**

- SVG either sanitized (script removed) or delivered as safe download (Content-Disposition: attachment) not inline. Evidence: payload + rendered behavior.
    
    **Remediation**
    
- Reject or strictly sanitize SVGs (remove scripts, external refs), serve as download rather than inline, or rasterize SVG on server to PNG.

---

### FU-06 — Malicious image triggers RCE in image processing libs (thumbnail generation)

**WSTG-Mapping:** File Handling / Untrusted Input Processing.

**Kurz-Schritte**

1. Upload specially crafted images that exploit known vulnerabilities in libs (ImageMagick, GraphicsMagick, libvips) — e.g., ImageTragick patterns (if allowed) or large crafted headers. (Only in authorized test lab or with vendor CVE knowledge.)
2. Trigger thumbnail generation or metadata extraction and monitor server for crashes or code execution.
3. Observe process spikes, crashes or shell commands executed (in lab).

**Automation-Hint**

- Known PoC payloads for CVEs in image libs (only in authorized environments). Monitor process and logs.
    
    **Erwartetes Ergebnis / Beweis**
    
- Image processing is sandboxed, time-limited, and cannot execute commands. Evidence: logs showing failure but no RCE.
    
    **Remediation**
    
- Use safe/latest libs, patch promptly, run image processors in isolated containers with least privilege, limit memory/time, use imagemagick policy.xml to disable dangerous coders.

---

### FU-07 — Large file uploads / quota exhaustion (DoS)

**WSTG-Mapping:** Denial of Service via resource abuse.

**Kurz-Schritte**

1. Attempt uploads close to size limits and then extremely large files to see if server enforces max size.
2. Simultaneously upload many large files to test disk/CPU exhaustion or queue saturation.
3. Test multiple concurrent thumbnailing jobs.

**Erwartetes Ergebnis / Beweis**

- Server rejects > configured max size with clear 4xx code; rate limits apply; resource consumption constrained. Evidence: server responses, monitoring metrics.
    
    **Remediation**
    
- Enforce upload size limits at webserver/proxy and application; use chunked uploads only with authenticated clients; implement quotas per user and global rate limiting.

---

### FU-08 — Presigned S3 / Object Storage misconfig & CORS abuse

**WSTG-Mapping:** Deployment / Access Control.

**Kurz-Schritte**

1. If app uses presigned URLs for upload, attempt to reuse presigned URL after expiry or alter object key to write to other paths.
2. Inspect S3 permissions — can objects be publicly listed/read? Test CORS headers to see if cross-origin reads allowed.
3. Attempt to upload malicious file via presigned URL and then access via CDN/via webserver.

**Erwartetes Ergebnis / Beweis**

- Presigned URLs expire, are bound to a single key, storage ACLs prevent public write/listing. Evidence: presigned URL behavior and object ACLs.
    
    **Remediation**
    
- Presigned URLs bound to exact object key, short TTL, server-side validation after upload, restrict CORS to allowed origins, store sensitive assets private and serve via authenticated proxy.

---

### FU-09 — Unsafe response headers (Content-Type sniffing, caching private assets)

**WSTG-Mapping:** Content Security / Information Leakage.

**Kurz-Schritte**

1. Request uploaded asset and check response headers: `Content-Type`, `Content-Disposition`, `Cache-Control`, `X-Content-Type-Options`.
2. If `X-Content-Type-Options` missing, attempt MIME sniffing by browser to trigger script execution.
3. Check `Cache-Control` for private assets — ensure `no-store` or `private`.

**Erwartetes Ergebnis / Beweis**

- `Content-Type` accurate and enforced; `X-Content-Type-Options: nosniff` present; private assets not cached publicly. Evidence: headers and behavior in browser.
    
    **Remediation**
    
- Set `X-Content-Type-Options: nosniff`, correct `Content-Type`, `Content-Disposition: attachment` for downloads as needed, and `Cache-Control: private/no-store`.

---

### FU-10 — Lack of antivirus / malware scanning on uploads

**WSTG-Mapping:** Operational Security / Malware Detection.

**Kurz-Schritte**

1. Upload EICAR test file (harmless test signature) to verify scanning pipeline.
2. Upload known-malicious patterns in lab to verify AV triggers and quarantine.
3. Check whether scanning is synchronous (blocking upload) or asynchronous (post-processing) and whether quarantine happens.

**Erwartetes Ergebnis / Beweis**

- Upload blocked/flagged and quarantined; admin alerted. Evidence: upload logs, quarantine status.
    
    **Remediation**
    
- Integrate AV scanning (ClamAV, commercial) on upload pipeline; quarantine on detection; alerting and retention of suspicious artifacts for analysis.

---

## Tools & Beispiel-Payloads (nur autorisiert verwenden)

- Tools: Burp Suite (file upload tampering), curl, exiftool (embed EXIF payload), imagemagick/imagemagick-policy testing in lab, ffuf for path fuzzing, headless Chrome / Selenium for rendering checks, AWS CLI / s3cmd for presigned URL testing, monitoring tools to observe CPU/memory, EICAR test string for AV validation.
- Example payloads: `shell.php.jpg` with `<?php phpinfo(); ?>` plus JPEG magic bytes; SVG with `<script>alert(1)</script>`; EXIF comment with XSS string; filename `..%2f..%2f/etc/passwd`.

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. FU-01)
- **WSTG-Ref** (z. B. File Uploads / Unrestricted File Upload)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw multipart request + file)
- **Beweis (raw req/res, headers, screenshots, logs)**
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation (server config, library updates)
- **Temporary Mitigations** (e.g., disable upload feature, limit to admins)

---

## Schnelle Gegenmaßnahmen (Kurz)

- Validate magic bytes + file extension mapping; reject mismatch.
- Rename stored files to safe random UUIDs; never use user-supplied names for storage paths.
- Store uploads outside webroot; serve via proxy that sets safe headers.
- Disable script execution in upload directories (webserver config).
- Strip/sanitize image metadata; sanitize/reject SVG or rasterize server-side.
- Enforce size quotas, chunked uploads with auth and quota checks.
- Run AV scanning and quarantine suspicious files.
- Sandbox image processing (separate container/process with cgroups limits).
- Presigned URLs: short TTL, exact key binding, server verification post-upload.
- Set `X-Content-Type-Options: nosniff`, correct `Content-Type`, `Cache-Control` for private assets.

---

## Tiefergehende Empfehlungen (Architektur / Process)

- Image processing in isolated workers (ephemeral containers) with strict resource limits and non-privileged user.
- Centralized upload gateway that normalizes, validates, scans and stores files into object storage with strict ACL.
- Regular dependency management and patching of image libraries (monitor CVEs).
- Automated regression tests for upload flows, and CI check for dangerous permissive policies (e.g., `policy.xml` for ImageMagick).
- Logging & SIEM rules for suspicious upload patterns and AV detections.

---