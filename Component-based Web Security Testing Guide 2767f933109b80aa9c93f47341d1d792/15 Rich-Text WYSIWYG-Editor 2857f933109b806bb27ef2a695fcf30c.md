# 15. Rich-Text / WYSIWYG-Editor

# Kapitel: Rich-Text / WYSIWYG-Editor

**Ziel**

Verhindern von Stored XSS, Unsafe-HTML und Bypass von Sanitizern in WYSIWYG-/Rich-Text-Feldern (z. B. Kommentare, Beiträge, Profil-Beschreibungen). Sicherstellen, dass eingebettete Medien, Attribute und CSS keine Ausführung von JavaScript ermöglichen.

**Scope / Prüfbereiche**

- Whitelist- vs. Blacklist-Sanitization (Server/Client)
- Image/Media Embeds (data: URIs, remote resources)
- Gefährliche Attribute (`onerror`, `onclick`, `style`, `xlink:href`, `srcset`, `data-`attributes)
- SVGs, MathML, CSS expressions, `javascript:`URIs
- HTML-Entities / Obfuskationen, Nested tags, Comments, URL-encoded payloads
- Output-Escaping beim Rendern (innerHTML vs textContent)
- Throttling/size limits für pasted content und attachments
- Audit/Logging von user-generated content

**WSTG-Mapping (relevante Bereiche)**

- **WSTG-XSS** — Testing for Reflected & Stored XSS (Payloads, DOM/Server)
- **WSTG-INPV** — Input Validation / Encoding issues (entity/encoding bypass)
- **WSTG-OUTPUT** — Output Encoding / Content Security Policy recommendations
- **WSTG-FILE** — wenn Editor Uploads (images/SVG) erlaubt

> Hinweis: alle Tests nur in autorisierten Testumgebungen und mit schriftlicher Genehmigung durchführen.
> 

---

## Testfälle (Kurzliste mit TestIDs)

- **RT-01** — Direct Stored XSS mit erlaubten Tags + event-attribute (`<img onerror=...>`).
- **RT-02** — Attribute-URI Injection (`javascript:`, `data:text/html;base64, ...`) in `href`/`src`.
- **RT-03** — Nested / encoded / obfuscated payloads (`&lt;script&gt;`, `&#x6a;avascript:`).
- **RT-04** — SVG payloads with `<script>` or `onload` and external references.
- **RT-05** — CSS expression / style attribute abuse (`background:url("javascript:...")` / `expression()` legacy).
- **RT-06** — Content pasted from MS Word / RTF including hidden tags or comments that can evade sanitizer.
- **RT-07** — Allowed embed features (iframe/media) abused for clickjacking or to load malicious content.

---

## Detaillierte Testfälle — Schritte, Automation-Hints, Erwartetes Ergebnis

### RT-01 — Stored XSS via allowed tags + malicious attributes

**Kurz-Schritte**

1. Als Test-User: Erstelle Beitrag/Bio mit z. B. `<img src=x onerror=alert('XSS')>` oder `<a href="#" onclick="alert(1)">click</a>`.
2. Speichern und Betrachten der Seite als anderer, nicht-privilegierter Benutzer (oder Incognito).
3. Prüfe Ausführung (Alert/console execution) und ob Payload in DB gespeichert ist (wenn DB-Zugriff in Scope).

**Automation-Hint**

- Selenium / headless Chrome zum automatischen Rendern und Erkennen von JS-Ausführung; Burp zur Einspeisung.
    
    **Erwartung / Beweis**
    
- Kein Script-Execution; alert nicht ausgeführt; editor/storage zeigt escaped content. PoC: raw saved content + Screenshot of rendered page.

---

### RT-02 — `javascript:` / `data:` URI & srcset abuse

**Kurz-Schritte**

1. Versuche `href="javascript:alert(1)"`, `src="javascript:...` oder `src="data:text/html;base64,..."`.
2. Teste `srcset`/`picture` source variants, um fallback URIs zu misbrauchen.
3. Beobachte ob Links/Images beim Klicken/Rendering JS ausführen.

**Erwartetes Ergebnis**

- URIs mit `javascript:` werden entfernt/neutralisiert; `data:` für HTML/JS abgelehnt; `srcset` validiert.

---

### RT-03 — Encoded / nested / entity obfuscation bypass

**Kurz-Schritte**

1. Einspeisen von Varianten: `&lt;img src=x onerror=alert(1)&gt;`, `\u003Cscript\u003Ealert(1)\u003C/script\u003E`, `&#x6a;avascript:alert(1)`.
2. Teste mehrfaches Dekodieren (serverseitig + clientseitig) — z. B. `&amp;lt;script&amp;gt;...`.
3. Prüfe ob Sanitizer mehrfach dekodiert und dann ausgibt.

**Erwartetes Ergebnis**

- Sanitizer normalisiert/dekodiert sicher oder lehnt ambigue Eingaben ab; keine Execution.

---

### RT-04 — SVG & XML payloads

**Kurz-Schritte**

1. Upload/Einfügen von SVG mit `<script>`, `onload`, `xlink:href="javascript:..."` oder externen Ressourcen.
2. Prüfe Verhalten bei Inline-SVG (in HTML) vs. `<img src="file.svg">` vs. `object`/`embed`.
3. Teste auch `<foreignObject>` und CSS inside SVG.

**Erwartetes Ergebnis**

- SVGs werden strikt sanitisiert (remove `<script>`, event-handler, external refs) oder serverseitig zu PNG gerastert; wenn inline gerendert, dürfen keine JS/CSS-Malicious Elemente ausgeführt werden.

---

### RT-05 — CSS / style attribute abuse

**Kurz-Schritte**

1. Füge `style="background-image:url('javascript:alert(1)')"` oder `style="xss:expression(alert(1))"` ein.
2. Prüfe, ob Styles im gerenderten DOM evaluiert werden oder inlined styles neutralisiert werden.

**Erwartetes Ergebnis**

- Gefährliche style-Attribute entfernt; nur erlaubte CSS-Eigenschaften/Value-Pattern zugelassen.

---

### RT-06 — Pasted content / hidden metadata / comments

**Kurz-Schritte**

1. Paste content from Word/Outlook that contains hidden tags, comments, or VML.
2. Prüfe ob der Editor diese schranksicheren Elemente sanitizes oder Schatten-HTML überlässt, das später JS ermöglichen kann.

**Erwartetes Ergebnis**

- RTF/Word Artefakte werden bereinigt; nur allowed tags/attributes bleiben.

---

### RT-07 — Iframe/Media embed abuse & clickjacking vectors

**Kurz-Schritte**

1. Versuch iFrame Einbettungen mit remote content oder `sandbox`Bypass.
2. Teste ob eingebettete media URLs remote JS ausführen oder private cookies exfiltrieren.

**Erwartetes Ergebnis**

- Embeds entweder verboten oder in `sandbox` mit strengsten Flags, `allow-scripts`/`allow-same-origin` nur bei Trusted URLs.

---

## Tools & nützliche Payload-Beispiele (nur in autorisierten Umgebungen)

- Tools: Burp Suite, Selenium / Puppeteer, DOM XSS scanners, exiftool (für pasted images), headless Chrome (detect alert), Content Security Policy Report URI testing.
- Beispiel-Payloads (nur für PoC in scope):
    - `<img src=x onerror=alert('XSS')>`
    - `<a href="javascript:alert(1)">link</a>`
    - `"><svg onload=alert(1)>`
    - `&lt;script&gt;alert(1)&lt;/script&gt;` (entity encoded)
    - SVG: `<svg><script>alert(1)</script></svg>`
    - CSS: `<div style="background-image:url('javascript:alert(1)')">`
    - data URI: `<img src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">`

---

## Automatisierungs-Hints

- Lege eine Payload-Liste (DOM + Stored XSS + SVG + CSS) an und automatisiere Inserts via API or UI scripting.
- Verwende headless browser (Puppeteer) um JS-Execution und DOM-Mutationen zu beobachten (console errors, dialog events).
- Teste doppelte Dekodierpfade: sende mehrfach enkodierte Inhalte und beobachte stored value.

---

## Erwartetes Ergebnis / Beweismittel

- Editor/Server sanitizes content according to a strict whitelist; no JS executes when viewing as another user.
- Proofs: raw gespeicherter HTML-Inhalt (DB snapshot or API GET), Screenshot/Video of rendered page showing no alert, logs of sanitize actions.

---

## Schnelle Gegenmaßnahmen (Kurz)

- Server-seitige Sanitization mit einer **Whitelist** (erlaubte Tags + erlaubte attributes) — *never* rely only on client-side sanitizer.
- Empfohlene libs: DOMPurify (JS) / OWASP Java HTML Sanitizer / Bleach (Python) — immer serverseitig verwenden und konfigurieren.
- Entferne gefährliche Attribute (`on*`, `style` wenn nicht notwendig), disallow `javascript:`/`data:` URIs for `href`/`src`.
- SVG: entweder komplett ablehnen, sanitizen (remove scripts, external refs) oder serverseitig in PNG rasterizen.
- Setze Content-Security-Policy (z. B. `default-src 'self'; script-src 'none'` für user generated areas) sowie `X-Content-Type-Options: nosniff`.
- Escape on output (use `textContent`/template engines that auto-escape).
- Limit paste size, scan uploaded images, log and alert on suspicious content patterns.
- Review and test sanitizer config regularly (unit tests with malicious payloads).

---

## Tiefergehende Empfehlungen (Architektur / Process)

- Implementiere eine Test-Suite mit known XSS payloads, die bei CI gegen Sanitizer-Konfiguration laufen.
- Use CSP reporting and monitor reports to detect attempts.
- Isolate content rendering: show user content in an iframe with `sandbox` and strict CSP if inline rendering unavoidable.
- Maintain allowlist policy per context (e.g., comment vs. blog post vs. admin area) and document permitted tags/attributes.
- Periodic dependency scanning and patching of sanitizer libraries and rendering libs.

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. RT-01)
- **WSTG-Ref** (z. B. WSTG-XSS, Input Validation)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw POST/PUT with payload)
- **Beweis** (saved HTML, screenshot of rendered page, logs)
- **Schweregrad (CVSS) + Business Impact**
- **Kurz-Fix** + detaillierte Remediation (konkrete sanitizer config)
- **Temporäre Mitigation** (disable editor, restrict tags)

---