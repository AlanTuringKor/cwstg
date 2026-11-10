#!/usr/bin/env python3
"""Validate CWSTG Markdown and generate its CSV catalog, without network access.

The repository uses inline Markdown links and ATX headings. This intentionally
small checker supports those conventions, including balanced URL parentheses.
"""

import argparse
import csv
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CASE = re.compile(r"^### (CWSTG-(\d{2})-(\d{2})) — (.+)$", re.MULTILINE)
WSTG = re.compile(r"\bWSTG-(?:v\d+-)?[A-Z]+-\d{2}\b")
FIELDS = ("Referenzen", "Prüfschritte", "Sicheres Ergebnis", "Belege", "Abhilfe")
CATALOG = Path("docs/test-catalog.csv")


def prose(markdown):
    """Remove fenced examples so they cannot create fake links or test cases."""
    lines = []
    fence = None
    for line in markdown.splitlines(keepends=True):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, rest = match.groups()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not rest.strip():
                fence = None
            lines.append("\n")
        else:
            lines.append(line if fence is None else "\n")
    return "".join(lines)


def links(markdown, errors=None):
    """Yield inline link/image labels and destinations, with balanced parentheses."""
    for match in re.finditer(r"!?\[([^\]\n]*)\]\(", markdown):
        start = match.end()
        if start < len(markdown) and markdown[start] == "<":
            end = markdown.find(">)", start)
            if end != -1:
                yield match.group(1), markdown[start + 1:end]
            elif errors is not None:
                errors.append(f"Nicht geschlossener Markdown-Link: {match.group(1)}")
            continue
        depth = 1
        end = start
        while end < len(markdown) and depth:
            char = markdown[end]
            if char == "\n":
                break
            if char == "\\":
                end += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            end += 1
        if depth == 0:
            yield match.group(1), markdown[start:end - 1]
        elif errors is not None:
            errors.append(f"Nicht geschlossener Markdown-Link: {match.group(1)}")


def anchors(markdown):
    """GitHub-style slugs for the simple ATX headings used in this repository."""
    result = set()
    for title in re.findall(r"^#{1,6} (.+)$", prose(markdown), re.MULTILINE):
        title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", title)
        title = re.sub(r"\s+#+\s*$", "", title)
        base = "".join(c for c in title.lower() if c.isalnum() or c in " _-").replace(" ", "-")
        slug = base
        suffix = 0
        while slug in result:
            suffix += 1
            slug = f"{base}-{suffix}"
        result.add(slug)
    return result


def wstg_target(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https":
        return None
    prefix = "/www-project-web-security-testing-guide/v42/"
    if parsed.netloc == "owasp.org" and parsed.path.startswith(prefix):
        path = parsed.path[len(prefix):]
    elif parsed.netloc == "wstg.owasp.org" and parsed.path.startswith("/v4.2/"):
        path = parsed.path[len("/v4.2/"):]
    else:
        return None
    return path.removesuffix("/").removesuffix(".html")


def check_links(root, path, text, registry):
    errors = []
    for label, target in links(prose(text), errors):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            if "utm_" in parsed.query:
                errors.append(f"Trackingparameter: {target}")
            is_wstg = parsed.netloc == "wstg.owasp.org" or (
                parsed.netloc == "owasp.org" and "/www-project-web-security-testing-guide/" in parsed.path
            )
            if is_wstg and re.search(r"/(latest|stable)/", parsed.path):
                errors.append(f"WSTG-Version nicht festgelegt: {target}")
            for reference in WSTG.findall(label):
                entry = registry.get(reference)
                if entry is None:
                    errors.append(f"Unbekannte WSTG-ID: {reference}")
                elif wstg_target(target) != wstg_target(entry["url"]):
                    errors.append(f"WSTG-ID und Linkziel passen nicht zusammen: {reference} -> {target}")
            continue
        resolved = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
        if not resolved.is_relative_to(root.resolve()):
            errors.append(f"Link verlässt das Repository: {target}")
        elif not resolved.exists():
            # The generated catalog is checked separately, and may not exist yet.
            if resolved != root.resolve() / CATALOG:
                errors.append(f"Lokales Linkziel fehlt: {target}")
        elif parsed.fragment and resolved.suffix == ".md":
            if unquote(parsed.fragment) not in anchors(resolved.read_text(encoding="utf-8")):
                errors.append(f"Sprungmarke fehlt: {target}")
    for reference in set(WSTG.findall(prose(text))):
        if reference not in registry:
            errors.append(f"Unbekannte oder unversionierte WSTG-ID: {reference}")
    return errors


def chapter_cases(path, text):
    errors = []
    rows = []
    text = prose(text)
    number = path.name[:2]
    if len(re.findall(r"^# ", text, re.MULTILINE)) != 1:
        errors.append("Genau eine H1 erforderlich")
    for heading in ("Ziel", "Voraussetzungen", "Testfälle", "Quellen"):
        if f"\n## {heading}\n" not in text:
            errors.append(f"Kapitelabschnitt fehlt: {heading}")
    for target in ("../../README.md", "../methodology.md", "../templates/test-result.md"):
        if target not in {url for _, url in links(text)}:
            errors.append(f"Navigation fehlt: {target}")
    matches = list(CASE.finditer(text))
    for heading in re.findall(r"^### CWSTG[^\n]*", text, re.MULTILINE):
        if not CASE.fullmatch(heading):
            errors.append(f"Ungültige Testüberschrift: {heading}")
    if not matches:
        errors.append("Keine Testfälle gefunden")
    for index, match in enumerate(matches):
        case_id, chapter, _, title = match.groups()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = re.split(r"\n## ", text[match.end():end], maxsplit=1)[0]
        if chapter != number:
            errors.append(f"Test-ID passt nicht zum Kapitel: {case_id}")
        fields = {}
        for field in FIELDS:
            section = re.search(r"\*\*" + re.escape(field) + r":[*][*][ \t]*(.*?)(?=\n\*\*[^\n]+:\*\*|\Z)", body, re.DOTALL)
            if section is None or not section.group(1).strip():
                errors.append(f"{case_id}: Pflichtfeld fehlt oder ist leer: {field}")
            else:
                fields[field] = section.group(1)
        refs = list(links(fields.get("Referenzen", "")))
        if not any(urlsplit(url).scheme == "https" for _, url in refs):
            errors.append(f"{case_id}: Konkrete HTTPS-Referenz fehlt")
        if not re.search(r"^1\. ", fields.get("Prüfschritte", ""), re.MULTILINE):
            errors.append(f"{case_id}: Nummerierte Prüfschritte fehlen")
        rows.append({
            "test_id": case_id,
            "title": title.strip(),
            "wstg_ids": ";".join(sorted(set(WSTG.findall(fields.get("Referenzen", ""))))),
            "sources": ";".join(dict.fromkeys(url for _, url in refs)),
            "chapter": path.as_posix(),
        })
    return errors, rows


def catalog_csv(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=("test_id", "title", "wstg_ids", "sources", "chapter"), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def validate(root):
    registry = json.loads((root / "data/wstg-v42.json").read_text(encoding="utf-8"))["tests"]
    errors = []
    rows = []
    chapters = sorted((root / "docs/components").glob("*.md"))
    if sorted(p.name[:2] for p in chapters) != [f"{n:02d}" for n in range(1, 17)]:
        errors.append("Genau die Kapitel 01 bis 16 sind erforderlich")
    markdown_files = sorted(p for p in root.rglob("*.md") if ".git" not in p.relative_to(root).parts)
    for path in markdown_files:
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        errors.extend(f"{relative}: {error}" for error in check_links(root, path, text, registry))
        if path in chapters:
            chapter_errors, chapter_rows = chapter_cases(relative, text)
            errors.extend(f"{relative}: {error}" for error in chapter_errors)
            rows.extend(chapter_rows)
    seen = set()
    for row in rows:
        if row["test_id"] in seen:
            errors.append(f"Doppelte Test-ID: {row['test_id']}")
        seen.add(row["test_id"])
    return errors, rows, len(markdown_files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-catalog", action="store_true", help="CSV-Katalog nach erfolgreicher Prüfung aktualisieren")
    args = parser.parse_args()
    errors, rows, count = validate(ROOT)
    catalog = ROOT / CATALOG
    expected = catalog_csv(rows)
    if args.write_catalog:
        if not errors:
            catalog.write_text(expected, encoding="utf-8", newline="")
    elif not catalog.exists() or catalog.read_text(encoding="utf-8") != expected:
        errors.append("CSV-Katalog fehlt oder ist veraltet: python3 scripts/check_docs.py --write-catalog")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {count} Markdown-Dateien, 16 Kapitel, {len(rows)} eindeutige Testfälle; Links, WSTG-Zuordnungen und CSV-Katalog geprüft.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
