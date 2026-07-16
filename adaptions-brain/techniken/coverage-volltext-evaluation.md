# Coverage: Volltext-Evaluation statt Truncation

## Das Problem

Ein Coverage Agent, der nur die ersten 50.000 Zeichen eines Screenplays sieht, bewertet blind:
- **Akt III fehlt komplett** — Resolution, Climax, Denouement werden nicht gelesen
- **Pacing-Score ist falsch** — kann nur den Aufbau bewerten, nicht ob er sich auszahlt
- **Struktur-Score ist blind** — der entscheidende Plot Point 2 liegt bei ~75% des Textes
- **Dialog-Score verfälscht** — Figuren-Entwicklung zeigt sich erst im letzten Drittel
- **Marktfähigkeit nicht bewertbar** — ohne Ending kein Urteil über "satisfying resolution"

Bei einem 19.000-Wort-Screenplay (~96k chars) schneidet `[:50000]` exakt 48% ab.

## Lösung: Intelligente Kompression

### Algorithmus
1. **Wenn Text passt** (≤ 50k chars): unverändert zurückgeben
2. **Szenen-Boundaries erkennen** (Regex: `INT.`, `EXT.`, `--- S`)
3. **Pro Szene behalten:**
   - Scene Header (Slugline)
   - Erste 3 Action-Sätze
   - Alle Dialog-Cues mit erster Zeile
   - Letzter Satz
4. **Falls immer noch zu lang:** Middle-Scenes auf Header-only komprimieren, Anfang (20%) und Ende (30%) volle Kompression behalten

### Warum NICHT Multi-Pass?
Multi-Pass (jeden Chunk einzeln evaluieren, dann aggregieren) verdoppelt die Token-Kosten. Bei einem $100/Monat Budget ist das kritisch. Die Kompression verliert ~50% Text, behält aber die dramatische Struktur (Headers, Dialog-Stimmen, Schlüsselszenen).

### Ergebnis (Der Schneesturm, 2026-04-07)
- Original: 65.640 chars → Komprimiert: 30.296 chars (53% Reduktion)
- 49 Szenen erhalten
- ACT THREE bei 79% des komprimierten Textes (vorher: abgeschnitten)
- Bourmin (entscheidende Figur für Resolution) ab 59% sichtbar

## Anwendungsregel
**Nie `[:50000]` verwenden.** Immer `_compress_for_coverage()` nutzen. Die Kompression ist deterministisch (kein LLM nötig) und kostet 0 Tokens.

## Warnung (Anti-Pattern)
Multi-Pass klingt eleganter, aber: 
- Doppelte Kosten (2× Sonnet-Call)
- Aggregation von Teilscores ist mathematisch fragwürdig (ein Pacing-Score aus dem Mittelteil sagt nichts über das Gesamtpacing)
- Der Coverage Agent braucht die Gesamtstruktur, nicht die Summe der Teile
