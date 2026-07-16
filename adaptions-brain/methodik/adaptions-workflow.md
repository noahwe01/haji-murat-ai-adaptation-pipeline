# Adaptions-Workflow — Überblick

## Die 7 Phasen

1. **Analyse** — Quelltext chunken, Erzählstruktur extrahieren
2. **Kerngeschichte** — Logline, Drei-Akt-Struktur identifizieren
3. **Figuren** — Want/Need, Bögen, kulturelle Authentizität
4. **Konflikte** — Konfliktdesign, Plot Points mappen
5. **Szenen** — Scene Cards, Subplots verweben
6. **Schreiben** — Treatment oder Drehbuch
7. **QA** — Alle Skills als Prüflinse, Kontinuitäts-Check

## Agenten-Reihenfolge (nie ändern)

1. Story Analyst → 2. Adaptation Agent → 3. Kontinuitäts-Wächter → 4. Script Writer

## Chunk Memory — Inter-Chunk-Kohärenz

### Das Problem
Ohne akkumulierten Kontext analysiert jeder Chunk isoliert. Folgen:
- **Figuren-Rediscovery:** Das LLM "entdeckt" Maria in Chunk 5 erneut, obwohl sie in Chunk 1 eingeführt wurde → Duplikate, inkonsistente Rollen-Zuweisungen.
- **Akt-Inkonsistenz:** Ohne zu wissen wo wir im Gesamtwerk stehen, ordnet das LLM Chunks falsch zu (z.B. Akt-III-Material als Akt II klassifiziert).
- **Plot-Element-Lücken:** Verbindungen zwischen entfernten Chunks gehen verloren.

### Die Lösung: `_build_memory_summary()`
Vor jedem Chunk wird eine kompakte Zusammenfassung des bisherigen Analysestandes in den Prompt injiziert:
- Fortschritt (z.B. "3/10 Chunks, 30%")
- Bekannte Figuren (Name + Rolle, max 8)
- Letzte 5 Plot-Elemente als Kette
- Gesamtzahl der Plot-Elemente

### Token-Budget
~200-400 Tokens pro Chunk-Analyse. Minimal im Vergleich zum Chunk selbst (~2000 Wörter).

## Bewährt (aus Der Schneesturm, 2026-04-07)
- Memory-Summary aktiviert (`build_analysis_prompt()` als Public API)
- Ermöglicht dem LLM, auf bereits erkannte Figuren zu referenzieren statt sie neu zu erfinden

## Lessons Learned

_Wird mit jedem Projekt ergänzt._
