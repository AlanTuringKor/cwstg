import csv
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("check_docs", Path(__file__).resolve().parents[1] / "scripts/check_docs.py")
docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(docs)

REFERENCE = "https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/03-Testing_for_Session_Fixation"
REGISTRY = {"WSTG-v42-SESS-03": {"title": "Session Fixation", "url": REFERENCE}}


def chapter(number):
    return f"""# {number:02d} · Beispiel

[Übersicht](../../README.md) · [Testablauf](../methodology.md) · [Ergebnisvorlage](../templates/test-result.md)

## Ziel

Ein Testziel.

## Voraussetzungen

Ein Testkonto.

## Testfälle

### CWSTG-{number:02d}-01 — Beispiel, mit Komma

**Referenzen:** [WSTG-v42-SESS-03]({REFERENCE})

**Prüfschritte:**

1. Einen Kontrollfall durchführen.
2. Den geänderten Zustand prüfen.

**Sicheres Ergebnis:** Der Zustand bleibt geschützt.

**Belege:** Zustandsvergleich.

**Abhilfe:** Serverseitige Prüfung.

## Quellen

[OWASP]({REFERENCE})
"""


class LinkTests(unittest.TestCase):
    def test_balanced_and_encoded_destinations(self):
        text = "[A](chapter_(one).md#ziel) ![B](old%20name.md) [C](<some file.md>)"
        self.assertEqual(list(docs.links(text)), [("A", "chapter_(one).md#ziel"), ("B", "old%20name.md"), ("C", "some file.md")])

    def test_examples_do_not_create_links_or_headings(self):
        text = "~~~markdown\n# Example\n[bad](missing.md)\n~~~\n# Ziel\n"
        self.assertEqual(list(docs.links(docs.prose(text))), [])
        self.assertEqual(docs.anchors(text), {"ziel"})

    def test_duplicate_heading_anchors(self):
        self.assertEqual(docs.anchors("# Überblick\n## Ziel\n## Ziel\n"), {"überblick", "ziel", "ziel-1"})

    def test_local_file_fragment_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "README.md"
            target = root / "some file_(one).md"
            target.write_text("# Ziel\n", encoding="utf-8")
            self.assertEqual(docs.check_links(root, path, "[ok](some%20file_(one).md#ziel)", REGISTRY), [])
            for bad, message in [("missing.md", "Linkziel fehlt"), ("some%20file_(one).md#no", "Sprungmarke fehlt"), ("../outside.md", "verlässt das Repository")]:
                self.assertTrue(any(message in error for error in docs.check_links(root, path, f"[bad]({bad})", REGISTRY)))

    def test_wstg_id_must_match_destination(self):
        path = Path("/tmp/README.md")
        errors = docs.check_links(path.parent, path, "[WSTG-v42-SESS-03](https://example.org/wrong)", REGISTRY)
        self.assertTrue(any("passen nicht zusammen" in error for error in errors))
        alternate = REFERENCE.replace("https://owasp.org/www-project-web-security-testing-guide/v42/", "https://wstg.owasp.org/v4.2/") + ".html"
        self.assertEqual(docs.check_links(path.parent, path, f"[WSTG-v42-SESS-03]({alternate})", REGISTRY), [])
        errors = docs.check_links(path.parent, path, "[WSTG-v42-SESS-03 Session Fixation](https://example.org/wrong)", REGISTRY)
        self.assertTrue(any("passen nicht zusammen" in error for error in errors))

    def test_unclosed_links_rejected(self):
        path = Path("/tmp/README.md")
        for text in ("[broken](missing.md", "[broken](missing.md\n", "[broken](<missing.md"):
            errors = docs.check_links(path.parent, path, text, REGISTRY)
            self.assertTrue(any("Nicht geschlossener" in error for error in errors))

    def test_both_owasp_hosts_require_pinned_versions(self):
        path = Path("/tmp/README.md")
        for url in ("https://wstg.owasp.org/stable/4-Web_Application_Security_Testing/", REFERENCE.replace("/v42/", "/latest/")):
            errors = docs.check_links(path.parent, path, f"[OWASP]({url})", REGISTRY)
            self.assertTrue(any("Version nicht festgelegt" in error for error in errors))

    def test_unknown_and_unversioned_ids_fail(self):
        path = Path("/tmp/README.md")
        for label in ("WSTG-v42-FILE-99", "WSTG-SESS-03"):
            self.assertTrue(docs.check_links(path.parent, path, f"[{label}]({REFERENCE})", REGISTRY))


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ("docs/components", "docs/templates", "data"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        for name in ("README.md", "docs/methodology.md", "docs/templates/test-result.md"):
            (self.root / name).write_text("# Ziel\n", encoding="utf-8")
        (self.root / "data/wstg-v42.json").write_text(json.dumps({"tests": REGISTRY}), encoding="utf-8")
        for number in range(1, 17):
            (self.root / f"docs/components/{number:02d}-example.md").write_text(chapter(number), encoding="utf-8")

    def change_first(self, before, after):
        path = self.root / "docs/components/01-example.md"
        path.write_text(path.read_text(encoding="utf-8").replace(before, after), encoding="utf-8")

    def test_complete_fixture_and_csv_round_trip(self):
        errors, rows, count = docs.validate(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 16)
        self.assertEqual(count, 19)
        self.assertEqual(list(csv.DictReader(io.StringIO(docs.catalog_csv(rows)))), rows)

    def test_duplicate_id_rejected(self):
        self.change_first("## Quellen", chapter(1).split("## Testfälle\n", 1)[1])
        errors, _, _ = docs.validate(self.root)
        self.assertTrue(any("Doppelte Test-ID" in error for error in errors))

    def test_wrong_chapter_and_malformed_test_heading_rejected(self):
        self.change_first("CWSTG-01-01", "CWSTG-02-01")
        errors, _, _ = docs.validate(self.root)
        self.assertTrue(any("passt nicht zum Kapitel" in error for error in errors))
        self.change_first("### CWSTG-02-01 —", "### CWSTG-02-01 -")
        errors, _, _ = docs.validate(self.root)
        self.assertTrue(any("Ungültige Testüberschrift" in error for error in errors))

    def test_empty_required_field_rejected(self):
        self.change_first("**Belege:** Zustandsvergleich.", "**Belege:**   ")
        errors, _, _ = docs.validate(self.root)
        self.assertTrue(any("Pflichtfeld fehlt oder ist leer: Belege" in error for error in errors))

    def test_missing_chapter_rejected(self):
        (self.root / "docs/components/16-example.md").unlink()
        errors, _, _ = docs.validate(self.root)
        self.assertTrue(any("Kapitel 01 bis 16" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
