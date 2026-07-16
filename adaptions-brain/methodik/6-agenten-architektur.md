# 7-Agenten-Architektur (kostenoptimiert)

## Die 7 Agenten

| # | Agent | Modell | Rolle |
|---|-------|--------|-------|
| 1 | **Orchestrator** | Sonnet | Dirigent, State, QA, Continuity Watcher |
| 2 | **Story Analyst** | Sonnet | Plot, Akte, Subplots, Spannung, Filmability |
| 3 | **Character Agent** | Opus (Synthese+Impro) / Sonnet (Extraktion) | Charakterbibel, Voice Profiles, Dialog-Impro |
| 4 | **World Agent** | Sonnet | Locations, Timeline, Production-Design |
| 5 | **Adaptation Agent** | Opus (High-Tension) / Sonnet (Low-Tension) | Literarisch → Filmisch |
| 6 | **Script Writer** | Opus (Dialog-Polish) / Sonnet (Assembly) | Fountain-Format, Treatment, Dialog-Polish |
| 7 | **Coverage Agent** | Sonnet | Script-Reader-Simulation, Coverage Report |

## Workflow: 10 Phasen

```
Phase 0: Intake & Config              [USER: Style-Manifest + Casting]
Phase 1: Deep Analysis (merged)       [Sonnet Sub-Agents: Plot+Figuren+Locations in einem Pass]
Phase 2: Synthese                     [Voice Profiles (Opus), World-Bibel, Beziehungsmatrix]
    → USER: Figuren + Akte validieren
Phase 3: Strategie                    [USER: Subplot-Auswahl, Ziel-Runtime]
Phase 4: Dialog-Improvisation         [Opus: 5-8 Schlüsselszenen als Impro-Probe]
Phase 5: Adaptation                   [Adaptives Batching + Continuity Checks]
Phase 6: Treatment Assembly           [Sonnet]
Phase 7: Coverage Evaluation          [USER: Coverage Report reviewen]
Phase 8: Gezielte Revision            [0-2 Zyklen, automatisch]
Phase 9: Drehbuch (optional)          [USER: Genehmigung + finaler Review]
```

## Qualitäts-Features

- **Dialog-Improvisation**: Character Agent spielt Schlüsselszenen als Impro-Probe
- **Character Casting**: Optional — Schauspieler-Vorschläge verankern Voice Profiles
- **Few-Shot Referenzszenen**: MCP-Server liefert professionelle Referenzen als Stil-Anker
- **Emotionale Choreographie**: Pflichtfeld pro Szene (audience_feels / character_feels)
- **Mehrdimensionale Konfidenz**: 5 Kategorien gewichtet (Dialog 25%, Character 25%, Plot 20%, Show-dont-tell 15%, Filmability 15%)

## Kostenoptimierungen

- **Merged Deep Analysis**: Plot + Figuren + Locations in einem Pass pro Chunk (50% weniger Turns)
- **Adaptives Chunk-Batching**: Low-Tension Chunks in 2-3er Batches
- **Sonnet für Analyse, Opus nur für Kreativ-Peaks**: ~35% Opus-Anteil statt 100%
- **TOON-Format für State**: ~25% Token-Ersparnis
- **Gebatchte Obsidian-Syncs**: Nur nach Phase 2 + Phase 7

## Konfidenz-System

| Score | Status | Aktion |
|-------|--------|--------|
| 0.90–1.0 | APPROVED | Direkt ins Skript |
| 0.75–0.89 | REVIEW | Übernommen, User-Review markiert |
| 0.60–0.74 | REVISE | Adaptation Agent überarbeitet |
| <0.60 | ESCALATE | Zurück zur Neuanalyse + User-Alert |

## Coverage-Bewertung

| Kategorie | Gewicht |
|-----------|---------|
| Konzept | 10% |
| Struktur | 20% |
| Figuren | 20% |
| Dialog | 20% |
| Pacing | 15% |
| Visuelles Erzählen | 10% |
| Marktfähigkeit | 5% |

Verdikt: RECOMMEND (80+) / CONSIDER (65-79) / PASS (50-64) / FAIL (<50)

## Projekte

| Projekt | Zweck | Status |
|---------|-------|--------|
| Der Schneesturm (Puschkin) | Referenzprojekt | Archiv |
| Hadji Murat (Tolstoi) | Projektadaption | Geplant |
