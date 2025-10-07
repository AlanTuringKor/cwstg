# 14. Image Gallery/ Media Viewer

# Kapitel: Image Gallery / Media Viewer

**Ziel**

Sicheres Rendern und Bereitstellen von Medieninhalten. Schutz vor **metadata-based XSS**, **unsicherem Content-Sniffing** und **unerlaubtem Zugriff auf private Medien**. Sicherstellen, dass EXIF/Metadaten nicht als HTML/JS ausgeführt werden, Medien nur für berechtigte Nutzer zugänglich sind und korrekte HTTP-Header gesetzt sind.

**Scope / Prüfbereiche**

- Rendering pipeline (clientseitig & serverseitig)
- Metadata handling (EXIF, ICC, XMP, Comments)
- Zugriffskontrolle (per-asset ACL, owner checks)
- Direct URL access & guessing resistance
- HTTP headers (Content-Type, Content-Disposition, Cache-Control, X-Content-Type-Options)
- Thumbnail generation (safe rasterization)
- Privacy (strip GPS/PII metadata before serving)

**WSTG-Mapping (relevante Bereiche)**

- **WSTG-INPV** – Input Validation & File Handling (Metadaten)
- **WSTG-AUTHZ** – Authorization Testing (Direct Object Reference auf Media)
- **WSTG-INFO** – Information Leakage (EXIF/GPS-Daten, sniffing)
- **WSTG-ERRH** – Error Handling (fehlende 403/404)
- **WSTG-FILE** – Unrestricted File Upload / Content Serving

---

## Testfälle (Kurzliste mit TestIDs)

- **MG-01** — Stored XSS über Bild-Metadaten (EXIF, ICC, XMP).
- **MG-02** — Direct URL Access zu privatem Bild (IDOR).
- **MG-03** — Content-Type Sniffing / falsche Header.
- **MG-04** — Content-Disposition: inline vs. attachment (clickjacking / execution risk).
- **MG-05** — GPS/PII-Leakage in Metadaten (Privacy).
- **MG-06** — Thumbnail / Media pipeline RCE (unsichere Image-Libs).
- **MG-07** — Caching private assets in öffentlichen CDNs.

---

## Detaillierte Testfälle — Schritte, Automation-Hints, Erwartetes Ergebnis

### MG-01 — Stored XSS via image metadata (EXIF)

**WSTG-Mapping:** Input Validation / XSS.

**Kurz-Schritte**

1. Erstelle JPEG/PNG mit EXIF-Comment: `<script>alert('XSS')</script>`.
2. Upload in Galerie und als anderer User betrachten.
3. Prüfen, ob Kommentar im DOM / Tooltip / Title unescaped angezeigt wird.

**Automation-Hint**

- exiftool zum Injizieren von Payloads. Selenium / headless Chrome, um Execution zu erkennen.
    
    **Erwartetes Ergebnis / Beweis**
    
- Keine Script-Execution; Metadaten nicht sichtbar oder escaped. Screenshot + raw HTML response.
    
    **Schnelle Gegenmaßnahme**
    
- Strip oder sanitize EXIF vor Speichern; Metadaten nie ungefiltert rendern.

---

### MG-02 — Direct URL Access zu privaten Bildern

**WSTG-Mapping:** Authorization Testing / IDOR.

**Kurz-Schritte**

1. Lade privates Bild hoch (z. B. `/media/private/123.jpg`).
2. Logge aus oder wechsel zu einem anderen User.
3. Rufe URL direkt auf.

**Automation-Hint**

- curl / wget mit/ohne Auth-Header.
    
    **Erwartetes Ergebnis / Beweis**
    
- 403/404 für nicht-berechtigte Zugriffe. Evidence: raw request/response.
    
    **Schnelle Gegenmaßnahme**
    
- Erzwinge ACL-Check per Request; randomize Pfade (UUID), assets nur via authorized proxy ausliefern.

---

### MG-03 — Content-Type Sniffing / falsche Header

**WSTG-Mapping:** Information Leakage / Content Serving.

**Kurz-Schritte**

1. Lade Bild hoch und prüfe Header: `Content-Type: image/jpeg`, `X-Content-Type-Options: nosniff`.
2. Versuche Upload von Polyglot (`.jpg` mit `<script>`).
3. Prüfe Browser-Verhalten (wird als Script interpretiert?).

**Erwartetes Ergebnis / Beweis**

- Korrekte MIME-Type, `nosniff` gesetzt; Browser interpretiert nie als HTML/JS. Screenshot der Response-Header.
    
    **Schnelle Gegenmaßnahme**
    
- Erzwinge `Content-Type: image/*`; `X-Content-Type-Options: nosniff`.

---

### MG-04 — Content-Disposition

**WSTG-Mapping:** Response Handling / Clickjacking.

**Kurz-Schritte**

1. Prüfe Header `Content-Disposition: inline` vs. `attachment`.
2. Lade HTML- oder SVG-Datei als Bild hoch und prüfe, ob inline dargestellt wird.

**Erwartetes Ergebnis / Beweis**

- Für Bilder erlaubt `inline`; für andere Formate (SVG, HTML, PDF) → `attachment`. Evidence: response headers.
    
    **Schnelle Gegenmaßnahme**
    
- Erzwinge `attachment` für alle nicht-sicheren Media-Typen.

---

### MG-05 — GPS/PII-Leakage

**WSTG-Mapping:** Information Leakage.

**Kurz-Schritte**

1. Lade Foto mit EXIF-GPS hoch.
2. Betrachte Gallery-View oder API-Response.
3. Prüfe, ob Koordinaten/PII ausgegeben werden.

**Erwartetes Ergebnis / Beweis**

- Keine GPS/PII-Daten in Responses; stripped. Evidence: exiftool dump vs. served file.
    
    **Schnelle Gegenmaßnahme**
    
- Strip GPS/PII bei Upload oder Anzeige.

---

### MG-06 — Thumbnail / Media pipeline RCE (ImageMagick, ffmpeg, etc.)

**WSTG-Mapping:** File Handling / Unrestricted File Upload.

**Kurz-Schritte**

1. Upload speziell präparierte Datei (ImageTragick PoC, bösartige video/mp4).
2. Beobachte Thumbnail-Generator-Fehler oder RCE (nur in Lab!).

**Erwartetes Ergebnis / Beweis**

- Keine RCE, Service bricht sicher ab. Logs + PoC file.
    
    **Schnelle Gegenmaßnahme**
    
- Image/Video Processing in Sandbox; Libs aktuell halten; gefährliche Funktionen disablen.

---

### MG-07 — Caching private assets

**WSTG-Mapping:** Caching / Data Exposure.

**Kurz-Schritte**

1. Prüfe `Cache-Control` Header für private Media.
2. Wenn `public, max-age=...` → Asset könnte in CDN gecacht werden.
3. Prüfe ob private Assets nach Logout noch aus CDN abrufbar sind.

**Erwartetes Ergebnis / Beweis**

- Private Media → `Cache-Control: private, no-store`; keine Public Caches. Evidence: response headers + behavior.
    
    **Schnelle Gegenmaßnahme**
    
- Setze Cache-Control für private Assets restriktiv; nur öffentliche Medien im CDN.

---

## Tools & Payload-Beispiele (nur autorisiert)

- **exiftool**: Inject `<script>alert(1)</script>` in EXIF-Comment.
- **curl**: `curl -i https://app.example/media/123.jpg` (prüfen Headers).
- **Burp**: Intercept/modify requests für IDOR.
- **PoC Polyglot**: `cat image.jpg malicious.html > polyglot.jpg`.
- **Monitoring**: Logs für Direct Access und Cache Miss/Hit prüfen.

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. MG-02)
- **WSTG-Ref** (z. B. WSTG-AUTHZ / WSTG-INPV)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw req/res, Tools)
- **Beweis** (Screenshot, Log-Auszug, Header)
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detail-Remediation
- **Temporäre Mitigation** (z. B. CDN-Bust, Access sofort sperren)

---

## Schnelle Gegenmaßnahmen (Kurz)

- Strip/Clean Metadata bei Upload; nie EXIF in HTML rendern.
- Private Assets nur via authorized proxy; ACL per Request prüfen.
- `Content-Type` korrekt + `X-Content-Type-Options: nosniff`.
- `Content-Disposition: attachment` für unsichere Formate.
- GPS/PII automatisch entfernen.
- Sandbox für Image/Video Processing.
- Cache-Control: `private, no-store` für sensitive Assets.

---

## Tiefergehende Empfehlungen

- Einheitliche Media-Service-Komponente (Proxy) als einzige Quelle für Asset-Auslieferung.
- Regelmäßige Security-Tests mit bekannten Image/Video Exploits (ImageTragick, ffmpeg bugs).
- Logging & Monitoring für Asset Access (Missbrauchsmuster: URL Guessing, Abnormal Requests).
- Privacy by Design: Default strip aller sensiblen Metadaten.
- Content Security Policy (`img-src 'self' data:`) + Download-Handler für non-image assets.

---