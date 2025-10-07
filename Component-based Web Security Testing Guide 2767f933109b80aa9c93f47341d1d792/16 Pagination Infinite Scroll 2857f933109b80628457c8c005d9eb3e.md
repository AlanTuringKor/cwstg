# 16. Pagination/ Infinite Scroll

# Kapitel: Pagination / Infinite Scroll

**Ziel**

Schutz gegen Large-offset Abuse, Resource Exhaustion (DB/CPU/Memory), Cache-Probleme (Cache-poisoning / leaking) und ineffiziente Pagination-Patterns. Prüfen, ob Limit/Offset korrekt gehandhabt werden, ob Cursor-basiertes Pagination unterstützt wird, Rate-Limiting vorhanden ist und Caching-Header korrekt gesetzt sind.

**Scope / Prüfbereiche**

- Limit/offset handling (max limit, negative values, non-numeric)
- Cursor vs offset pagination (cursor recommended for large datasets)
- Rate limiting / throttling for repeated paging requests (infinite scroll abuse)
- Backend query cost (expensive ORDER BY, full table scans for deep offsets)
- Caching headers and CDN behavior (public caching of private pages, cache key poisoning)
- Client behavior (infinite scroll triggering many parallel requests)
- Response sizes & streaming behavior (chunking)
- Logging/monitoring for heavy pagination patterns

**WSTG-Mapping (relevante Bereiche — als Referenz im Report)**

- *WSTG Business Logic / Denial of Service* (resource exhaustion tests).
- *WSTG Input Validation* (validate pagination params).
- *WSTG Data Exposure* (cache/headers causing leakage).
- *WSTG API / Performance* (back-end query safety).

---

## Schnellübersicht Testfälle (mit TestIDs)

- **PG-01** — Huge `offset`/`limit` abuse (DB heavy scans).
- **PG-02** — Rapid infinite-scroll simulation → many requests / concurrency spike.
- **PG-03** — Cache poisoning via varied headers or query strings (CDN/edge serving wrong cached content).
- **PG-04** — Negative / malformed pagination params (robust parsing).
- **PG-05** — Deep paging reveal PII/older sensitive rows (unexpected data disclosure).
- **PG-06** — Missing/insufficient rate limiting per user/IP/API key on paged endpoints.
- **PG-07** — Inefficient server responses (no streaming, full dataset materialization in memory).

---

## Detaillierte Testfälle — Schritte, Automation-Hints, Erwartetes Ergebnis

### PG-01 — Huge `offset`/`limit` abuse (force heavy DB scans)

**WSTG-Mapping:** Input Validation / DoS / Performance.

**Kurz-Schritte**

1. Identifiziere list endpoint, z. B. `GET /items?limit=XX&offset=YY` oder `?page=...`.
2. Führe requests mit extremen Werten aus, z. B.:
    - `?limit=1000000&offset=0`
    - `?limit=1000&offset=10000000`
    - `?limit=9999999`
3. Beobachte Response-Codes, Antwortzeit, CPU/DB load (falls Monitoring zugänglich).
4. Teste progressive deep offsets (offset=1000,10000,100000) und beobachte linear vs. superlinear Zeitanstieg.

**Automation-Hint**

- Script (Python requests) inkrementiert offset in logarithmischen Schritten; sammle timings and status codes.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server begrenzt `limit` (z. B. ≤ 100) oder antwortet mit 4xx (400/422) für absurd values; tiefes paging unterstützt cursor oder returns 403/429; DB load stays bounded. Evidence: request logs, timing CSV, server metrics.
    
    **Schnelle Gegenmaßnahme**
    
- Enforce `max_limit`, validate numeric bounds, return 400 on invalid ranges. Use cursor pagination for large datasets.

---

### PG-02 — Rapid scroll simulation → many requests → resource spike

**WSTG-Mapping:** DoS / Rate limiting.

**Kurz-Schritte**

1. Emuliere infinite scroll: script launches many parallel requests for next pages (e.g., 30 concurrent requests for pages 1..30).
2. Increase concurrency and measure server responses / 5xx rates.
3. Simulate multiple users doing same to test amplification.

**Automation-Hint**

- Use vegeta / JMeter / custom asyncio script to simulate clients with realistic timing and concurrency.
    
    **Erwartetes Ergebnis / Beweis**
    
- Server applies rate limiting / backoff (429) or queues gracefully; no crash or huge latency increase. Evidence: request/response logs, 429 counts, CPU graphs.
    
    **Schnelle Gegenmaßnahme**
    
- Implement per-client/IP rate limiting and concurrent request caps; add exponential backoff / 429 responses; client should implement throttling.

---

### PG-03 — Cache poisoning via varied headers / query strings

**WSTG-Mapping:** Data Exposure / Caching.

**Kurz-Schritte**

1. Observe cache headers for paged responses: `Cache-Control`, `Vary`, `Surrogate-Key`, `Expires`.
2. Request `GET /items?page=1` with special headers (e.g., different `Accept`, `Cookie`, `Authorization` scenarios) and see what the CDN/edge caches.
3. Try to store a cached page that contains private data (authenticated request cached publicly) by manipulating headers or missing `Vary: Authorization`.
4. After cache population, request same resource without auth and see if edge returns cached private content.

**Automation-Hint**

- curl with custom headers to populate CDN cache then fetch from different client context. Check `Age` header and CDN logs.
    
    **Erwartetes Ergebnis / Beweis**
    
- Private/authenticated responses not cached publicly; `Vary` includes `Authorization` or responses set `Cache-Control: private/no-store`. Evidence: cached response exposing PII or headers showing caching policy.
    
    **Schnelle Gegenmaßnahme**
    
- Ensure `Cache-Control: private/no-store` for authenticated responses; configure CDN to respect `Authorization`/Vary; include `Surrogate-Control` only for safe public responses.

---

### PG-04 — Negative / malformed pagination params

**WSTG-Mapping:** Input Validation.

**Kurz-Schritte**

1. Send `limit=-1`, `offset=-10`, `limit=abc`, `limit=1e6` or other malformed values.
2. Observe whether server handles gracefully (400) or crashes/behaves unpredictably.

**Erwartetes Ergebnis / Beweis**

- Invalid params produce 400 with safe message; no server error/stacktrace. Evidence: raw req/res.
    
    **Schnelle Gegenmaßnahme**
    
- Validate and sanitize pagination params; coerce to integers and enforce bounds.

---

### PG-05 — Deep paging reveals older/private rows unexpectedly

**WSTG-Mapping:** Authorization / Data Exposure.

**Kurz-Schritte**

1. Request deep pages that should be restricted by time/privilege (e.g., archived items).
2. Compare responses between privileged vs non-priv users at same offsets. Look for private data leakage due to indexing/ordering differences.

**Erwartetes Ergebnis / Beweis**

- Only allowed rows returned; server enforces ACL on each returned item, not just at page level. Evidence: response contents and checks against item ownership.
    
    **Schnelle Gegenmaßnahme**
    
- Apply per-item ACL checks before including in page response; avoid filtering post-query.

---

### PG-06 — Missing/insufficient rate limiting per user/IP/API key on paged endpoints

**WSTG-Mapping:** DoS mitigation / Abuse.

**Kurz-Schritte**

1. Fire many paged requests from a single IP / API key and observe whether thresholds are enforced.
2. Test burst vs sustained rates.

**Erwartetes Ergebnis / Beweis**

- Rate limiting triggers (429) or progressive throttling; logs show blocked attempts. Evidence: 429 responses and logs.
    
    **Schnelle Gegenmaßnahme**
    
- Implement per-user/IP/API key quota and burst limits; apply circuit breakers.

---

### PG-07 — Inefficient server responses (full dataset materialization / memory blowup)

**WSTG-Mapping:** Performance / Resource usage.

**Kurz-Schritte**

1. Observe whether server constructs full dataset in memory before sending page (use profiling or memory metrics).
2. Trigger list endpoint that might join large tables and see memory usage.
3. Request many pages in parallel to stress memory.

**Erwartetes Ergebnis / Beweis**

- Server streams results or paginates at DB level (LIMIT/OFFSET or cursors) without materializing entire set; stable memory. Evidence: memory/GC metrics, query plans.
    
    **Schnelle Gegenmaßnahme**
    
- Implement streaming response (cursor-based), limit in-DB work, use proper indexes for ordering, avoid `OFFSET` with large values (use seek/cursor).

---

## Tools & Beispiel-Skripte (nur in autorisierten Umgebungen)

- Tools: curl, Python (requests + asyncio), vegeta, JMeter, locust/Artillery, pg_stat_activity / MySQL processlist for DB observation, NewRelic/Prometheus/Grafana for metrics, ffuf for endpoint discovery.
- Beispiel: Python snippet (conceptual) to probe offsets:

```python
import requests, time
for off in [0,10,100,1000,10000,100000]:
    t0=time.time()
    r=requests.get(f"https://app.example/items?limit=100&offset={off}")
    print(off, r.status_code, len(r.content), time.time()-t0)

```

- Use vegeta for concurrency: `echo "GET https://app.example/items?limit=20&offset=0" | vegeta attack -duration=30s -rate=50 | vegeta report`

---

## Reporting-Template (Minimalfelder pro Finding)

- **TestID** (z. B. PG-01)
- **WSTG-Ref** (Performance / Input Validation / Data Exposure)
- **Kurzbeschreibung**
- **Reproduktionsschritte** (raw req/res, script used)
- **Beweis (timings, CPU/DB graphs, raw responses)**
- **Severity (CVSS) + Business Impact**
- **Kurz-Fix** + Detaillierte Remediation
- **Temporary Mitigations** (e.g., apply strict rate limits, disable deep paging)

---

## Schnelle Gegenmaßnahmen (Kurz)

- Enforce sensible `max_limit` and `max_offset` rules; return 400/422 for outliers.
- Prefer cursor/seek pagination over offset for large tables.
- Implement per-client/IP/API-key rate limiting and concurrency caps.
- Use DB indexes that support ordering used in pagination (avoid full scans).
- Add query timeouts and DB query cost limits; set connection pool limits.
- Ensure authenticated responses are not cached publicly (`Cache-Control: private/no-store`) and configure CDN `Vary`/cache keys correctly.
- Implement server-side per-item ACL checks before including in a page.
- Monitor and alert on abnormal paging patterns (many pages in short time).

---

## Tiefergehende Empfehlungen (Architektur & Process)

- Adopt cursor pagination (opaque server-side cursors) that encapsulate state and avoid expensive `OFFSET`.
- Provide “search after” or seek methods for ordered datasets (use index + last_seen_key).
- Implement a Query Gateway that estimates cost and rejects expensive queries before hitting DB.
- Introduce sliding windows / TTL for deep archive access (use archived store optimized for OLAP).
- Add automated tests in CI that simulate deep pagination and measure query performance regressions.
- Instrument DB query plans routinely and auto-alert on queries that degenerate to full table scans.

---