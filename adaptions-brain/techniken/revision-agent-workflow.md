# Revision Agent — Gezielte Szenen-Revision statt Komplett-Rewrite

## Kernprinzip

**Gezielte Revision, nicht Komplett-Rewrite.** Der Revision Agent bekommt spezifische Issues mit Scene-IDs und überarbeitet NUR diese Szenen. Alles andere bleibt unverändert.

## Warum nicht einfach alles neu schreiben?

1. **Kontext-Verlust:** Ein Komplett-Rewrite verliert die Konsistenz, die über mehrere Iterationen aufgebaut wurde.
2. **Token-Kosten:** Opus-Call für 45 Szenen vs. 3-5 Szenen — Faktor 10× Unterschied.
3. **Regressions-Risiko:** Jede Szene, die nicht überarbeitet werden MUSS, ist ein Risiko für neue Fehler.
4. **Validierung:** Gezielte Revision ist leichter zu validieren — man prüft nur die geänderten Szenen.

## Workflow

```
Coverage Report → top_issues (mit Scene-IDs)
Style Report → issues (mit Scene-IDs)
         ↓
Revision Agent erhält:
  - Die betroffenen Szenen (volltext)
  - Kontext-Szenen (±1 Szene vor/nach)
  - Voice Profiles (alle 9 Dimensionen)
  - Style Manifest
  - Die spezifischen Issues mit Instruktionen
         ↓
Output:
  - Überarbeitete Szenen (gleiche Struktur wie adapted_scenes)
  - Changelog (was geändert, warum)
```

## Kontext-Szenen sind kritisch

Der Revision Agent sieht immer die Szene VOR und NACH der Zielszene. Ohne diesen Kontext:
- Übergänge passen nicht mehr
- Emotionale Bögen werden unterbrochen  
- Figurenzustände stimmen nicht (z.B. Figur ist in vorheriger Szene verletzt → muss in revidierter Szene auch verletzt sein)

## Modell: Opus

Revision ist kreative Arbeit — der Agent muss Dialog umschreiben, Subtext einfügen, Ton anpassen. Das erfordert Opus-Niveau. Sonnet kann analysieren, aber nicht auf dem Level umschreiben.

## Revision-Zähler

Jede Szene trackt `revision_count`. Das ermöglicht:
- "Wurde diese Szene schon 3× überarbeitet?" → Eskalation an den User
- "Welche Szenen sind stabil (0 Revisionen) vs. instabil (3+ Revisionen)?"
- `max_revision_cycles` in der Config verhindert Endlos-Schleifen

## Input-Quellen für Issues

1. **Coverage Agent:** Dialog-Score < 85, Pacing-Probleme, Struktur-Issues
2. **Style Validator:** Ton-Brüche, Register-Inkonsistenzen, fehlende Themen
3. **Continuity Watcher:** Figuren-State-Fehler, Location-Inkonsistenzen
4. **Manuell:** User meldet spezifische Szenen-Probleme

## Implementiert (Der Schneesturm, 2026-04-07)
- `build_revision_prompt()` baut Prompt mit Target-Szenen, Kontext, Voice Profiles
- `run_revision_agent()` ersetzt Szenen im State, loggt Changelog
- Orchestrator routet zu Opus
- `route_revision()` im Orchestrator erstellt Tasks aus Coverage-Issues
