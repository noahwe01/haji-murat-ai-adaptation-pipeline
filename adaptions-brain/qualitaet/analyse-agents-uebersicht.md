# Analyse-Agents — Qualitätssicherung über das Drehbuch als Ganzes

## Das Problem (vor v3.1)

Coverage Agent bewertete einzelne Kategorien (Dialog: 90, Struktur: 92). Aber niemand prüfte, ob die 45 Szenen zusammen ein FILM sind — ob das Ganze größer ist als die Summe der Teile.

## Die 6 Analyse-Agents (v3.1, 2026-04-07)

### 1. Narrative Coherence Agent (Opus)
**Fragt:** "Funktioniert das Drehbuch als EIN Erlebnis?"
- Narrative Momentum (wo stagniert die Geschichte?)
- Emotional Architecture (ist die Klimax verdient?)
- Thematic Coherence (spiegeln Transitions/Motifs das Thema?)
- Character Ecosystem (braucht jede Figur zu existieren?)
- Dangling Threads & Missed Opportunities

### 2. Subtext-Auditor (Sonnet)
**Fragt:** "Sagen die Figuren wirklich was sie meinen?"
- 10-Punkte-Skala pro Dialog-Zeile (0 = On-the-Nose, 10 = Deep Subtext)
- 70/30-Regel: Min. 70% Subtext (Score 6+), max 30% direkt
- Worst Offenders + Best Moments Report

### 3. Dialog-Thread-Checker (Sonnet + Pure Python)
**Fragt:** "Bleibt jeder Charakter über Szenen hinweg konsistent?"
- Nutzt Scene Graph für Charakter-Threads
- Prüft: Emotionale Kontinuität, Versprechen/Callbacks, Eskalationslogik, Voice Drift

### 4. Transition-Mapper (Sonnet)
**Fragt:** "Machen die Übergänge zwischen Szenen thematische Arbeit?"
- Match Cuts, Sound Bridges, Contrast Cuts, Visual Rhymes
- Regel: Min. 30% der Übergänge sollten eine Technik nutzen
- Act-Break-Transitions als stärkste Übergänge

### 5. Table-Read Simulation (Opus)
**Fragt:** "Wie klingt der Dialog wenn er gesprochen wird?"
- Speakability (Atemlänge, Natürlichkeit)
- Performance Range (kann der Schauspieler mehrere Interpretationen finden?)
- Rhythm & Breath (Musikkalität des Dialogs)
- Silence Opportunities (wo ist KEIN Dialog mächtiger?)

### 6. Pacing-Analyzer (Sonnet + Pure Python)
**Fragt:** "Hat der Film den richtigen Rhythmus?"
- Pure Python: Dialog-Gewicht, Szenenlängen-Variation, Dead Zones, Momentum-Kurve
- LLM: Akt-Balance (25/50/25), Beschleunigung zum Climax, Cut-Vorschläge

## Integration in die Pipeline

```
Phase 6: Script Writer → Drehbuch
Phase 6.5: Pacing Analyzer + Subtext Auditor + Dialog Thread Checker
Phase 7: Coverage Agent + Style Validator
Phase 7.5: Narrative Coherence + Transition Mapper + Table Read
Phase 8: Revision Agent (mit Issues aus ALLEN Quellen)
```

## Token-Kosten

| Agent | Modell | Tokens/Run |
|-------|--------|-----------|
| Narrative Coherence | Opus | ~5.000 |
| Subtext Auditor | Sonnet | ~2.000 |
| Dialog Thread Checker | Sonnet | ~1.500 |
| Transition Mapper | Sonnet | ~2.000 |
| Table Read | Opus | ~3.000 |
| Pacing Analyzer | Sonnet | ~1.500 |
| **Gesamt** | | **~15.000** |

Bei ~100k Tokens pro Pipeline-Run: +15% Overhead für deutlich tiefere Qualitätsanalyse.
