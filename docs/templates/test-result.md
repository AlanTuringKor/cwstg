# Ergebnis eines Testlaufs

[Übersicht](../../README.md) · [Testablauf](../methodology.md)

Für jede Kombination aus Test, Endpunkt und Identität kopieren. Platzhalter ersetzen; die Test-ID aus dem Kapitel unverändert übernehmen.

| Feld | Eintrag |
| --- | --- |
| Lauf-ID | `<projekt>-<laufnummer>` |
| CWSTG-Test-ID und Kapitellink | `<ID und Link>` |
| Datum / Prüfer | `<UTC-Zeitpunkt, Name>` |
| Anwendung / Umgebung / Build | `<Name, Testumgebung, Commit oder Version>` |
| Endpunkt / Methode / UI-Funktion | `<Pfad, HTTP-Methode, Einstieg>` |
| Identität / Rolle / Mandant | `<Testkonto ohne Zugangsdaten>` |
| Objekt / Besitzer | `<Test-ID, Eigentümer, Ausgangszustand>` |
| Testbudget | `<max. Requests, Rate, Parallelität, Laufzeit, Abbruchschwelle>` |
| Status | `<BESTANDEN / FEHLGESCHLAGEN / BLOCKIERT / NICHT_GETESTET / NICHT_ANWENDBAR>` |
| Finding-ID | `<falls vorhanden>` |

## Sollverhalten und Voraussetzungen

`<Geprüfte Sicherheitsgrenze, zulässiger Zugriff, vorhandene bzw. fehlende Voraussetzungen.>`

## Reproduktion

1. `<Funktionierenden Kontrollfall mit Testdaten ausführen.>`
2. `<Gezielte Änderung mit exaktem Parameter und Wert durchführen.>`
3. `<Antwortdaten und Zustand kontrollieren; asynchrone Aktionen berücksichtigen.>`

## Beobachtung und Belege

`<Erwartetes und tatsächliches Verhalten; redigierte Requests/Responses; Zustand vorher/nachher; Korrelations-IDs oder geschützte Belegreferenzen.>`

## Grenzen und Begründung

`<Warum dieser Status? Nicht geprüfte Varianten, Timing-Streuung, fehlende Einsicht, Grund für Blockierung oder Nichtanwendbarkeit.>`

## Bereinigung und Nachtest

`<Entfernte Testdaten oder verbleibende Artefakte; nächster Schritt; Build und Verweis auf den separaten Nachtestlauf.>`
