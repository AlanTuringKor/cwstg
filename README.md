# 🧩 CWSTG — Component-based Web Security Testing Guide
**Modular Security Testing for Real-World Web Apps**

---

## 📖 Überblick

Der **Component-based Web Security Testing Guide (CWSTG)** ist ein praxisorientierter Leitfaden zur Sicherheitsüberprüfung von Webanwendungen.  
Im Gegensatz zu klassischen Frameworks wie dem **OWASP WSTG**, die nach abstrakten Testkategorien aufgebaut sind, betrachtet CWSTG die Anwendung **aus Sicht typischer UI- und Funktionskomponenten** – also so, wie echte Benutzer (und Angreifer) sie erleben.

Ziel ist es, **schneller nachvollziehbare, reproduzierbare und komponentenorientierte Tests** zu ermöglichen.

---

## 🎯 Zielsetzung

CWSTG soll:
- den Einstieg in Web Security Testing **vereinfachen**,  
- **Pentester, Entwickler und Management** in einer gemeinsamen Sprache verbinden,  
- und eine **strukturierte Grundlage** bieten, die kontinuierlich gepflegt und erweitert wird.

---

## 🧱 Struktur

CWSTG gliedert eine typische Webanwendung in wiederkehrende Komponenten:

| Komponente | Beispielhafte Prüfziele |
|-------------|--------------------------|
| Login / Authentifizierung | SQLi, Brute Force, Session Handling |
| Register / Forgot Password | Account Enumeration, Token Abuse |
| User Profile / Settings | IDOR, Privilege Tampering, Stored XSS |
| Role / Permission UI | ACL Bypass, JWT Manipulation |
| Admin Panel / Dashboard | Forced Browsing, Privilege Escalation |
| File Upload / Media | RCE, Path Traversal, Content Sniffing |
| Search / Filter | Query Injection, XSS, DoS |
| Forms / Multi-Step | CSRF, Logic Flaws, Hidden Input Manipulation |
| Comments / Mentions | Stored XSS, Spam, Mass Mention Abuse |

Jede Komponente enthält:
- **Ziel** – Was gesichert werden soll  
- **Prüfbereiche** – Wo Risiken typischerweise liegen  
- **Testfälle** – Konkrete reproduzierbare Prüfungen mit WSTG-Mapping  
- **Kurz-Prüfschritte** – Vorgehensweise  
- **Beweis / Erwartung** – Was ein sicherer Zustand ist  
- **Schnelle Gegenmaßnahmen** – Sofortige Fixes  

---

## 🧭 Warum CWSTG?

🔹 **Einsteigerfreundlich**  
CWSTG übersetzt abstrakte Schwachstellen in **konkrete UI-Komponenten** – ideal für Tester, die Web-Pentests besser verstehen oder dokumentieren wollen.  

🔹 **Verständlich für Management & Nicht-Pentester**  
Die klare Struktur (Login, Suche, Datei-Upload, etc.) macht Findings **auch ohne technische Tiefe nachvollziehbar** und priorisierbar.  

🔹 **Praxisorientiert & modular**  
Jede Komponente kann separat getestet, dokumentiert oder automatisiert werden.  

🔹 **Pflegbar & erweiterbar**  
Da sich Web-Technologien laufend ändern (SPA, API-first, etc.), soll CWSTG **regelmäßig aktualisiert und durch Community-Beiträge erweitert werden**.

> 📌 *„CWSTG lebt von Praxiswissen – jedes Projekt macht es besser.“*

---

## 🛠️ Beziehung zu anderen Standards

| Framework | Verhältnis zu CWSTG |
|------------|--------------------|
| **OWASP WSTG** | Basis für WSTG-Mappings (technische Tiefe) |
| **OWASP ASVS** | Ergänzende Anforderungen (Security Controls) |
| **NIST SP 800-115** | Strukturähnliches Test-Vorgehen |
| **ISO 27001 / 27005** | Für Risikobewertung und Management-Kommunikation |

CWSTG **baut auf** diesen Standards auf, **ersetzt sie aber nicht**. Es dient als praktische Brücke zwischen Theorie und realem Testing-Alltag.

---

## 🔄 Pflege und Weiterentwicklung

CWSTG ist ein **lebendes Framework**.  
Neue Technologien, UI-Komponenten und Angriffsmuster (z. B. SPA Routing, GraphQL APIs, OAuth Flows) sollen regelmäßig ergänzt werden.

**Empfohlener Workflow:**
1. Bei jedem Projekt neue Findings in bestehende Kapitel einordnen.  
2. Falls ein neues UI-Muster auftaucht → neues Kapitel vorschlagen.  
3. Regelmäßig prüfen, ob WSTG- oder ASVS-Verweise aktualisiert wurden.  

---

## 👥 Zielgruppe

- Pentester und Security Engineers  
- QA- und DevSecOps-Teams  
- Entwickler mit Interesse an Sicherheit  
- Security Manager, Auditoren und Consultants  
- Technische Redakteure und Trainer  

---

## 🧩 Beispiel: Login-Komponente

```text
Ziel: Sichere Authentifizierung, robuste Session-Verwaltung
WSTG-Mapping: WSTG-ATHN-02, WSTG-SESS-05
Testfälle:
  - SQL-Injection in username/password
  - Brute Force / Credential Stuffing
  - Session Fixation
  - Cookie Flags (Secure, HttpOnly, SameSite)
Erwartung:
  - Keine SQL-Fehler, 403/429 bei Brute-Force, sichere Cookies
```

---

## 🧠 Lizenz & Mitwirkung

CWSTG steht unter einer offenen Lizenz (Creative Commons Attribution-ShareAlike 4.0).  
Beiträge sind willkommen – neue Komponenten, Testideen oder Tool-Mappings können als Pull Requests eingereicht werden.

---

## 📬 Kontakt / Beitrag

**Projektmaintainer:**  
*Mingi Hong*  

---

> 🐝 **CWSTG – Modular Security Testing for Real-World Web Apps**  
> _“Modular Security Testing for Real-World Web Apps.”_
