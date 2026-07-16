# Scene Graph — Vernetzte Szenen-Abfragen ohne LLM-Kosten

## Was der Scene Graph ist

Ein reiner Python-Datenstruktur-Index über alle `adapted_scenes`. Kein LLM-Call nötig. Wird aus dem bestehenden State gebaut und ermöglicht Queries, die mit flachen Listen unmöglich oder teuer wären.

## Struktur

```
scene_graph:
  character_scenes:    {character_name → [scene_ids]}
  location_scenes:     {location_slug → [scene_ids]}
  character_pairs:     {"charA|charB" → [scene_ids]}
  subplot_scenes:      {subplot_id → [scene_ids]}
  timeline_sequence:   [{scene_id, characters, location, duration}]
```

## Beispiel-Queries

### "In welchen Szenen tritt Bourmin auf?"
```python
get_character_scenes("Bourmin")  # → ['S022', 'S023', 'S024', 'S030', ...]
```

### "Wo treffen Maria und Bourmin aufeinander?"
```python
get_character_pair_scenes("Maria", "Bourmin")  # → ['S036', 'S037', ...]
```

### "Welche Szenen spielen am Estate?"
```python
get_location_scenes("ESTATE")  # → ['S001', 'S003', ...]
```

### "Welche Figuren-Paare haben die meisten Szenen zusammen?"
```python
sorted(graph["character_pairs"].items(), key=lambda x: len(x[1]), reverse=True)
```

## Anwendungsfälle für die Pipeline

### 1. Continuity Checking
- Prüfe: Taucht ein Charakter in einer Szene auf, in der er laut Graph nicht ist?
- Prüfe: Ist die Location konsistent mit der Timeline?
- Kosten: **0 Tokens** (vs. LLM-basierter Continuity Check)

### 2. Coverage-Analyse
- Welche Figuren sind unter-repräsentiert? (wenige Szenen)
- Welche Locations werden nur einmal genutzt? (Set-Kosten vs. Wirkung)
- Welche Figuren-Paare interagieren nie? (fehlende Konfrontation?)

### 3. Revision-Targeting
- Revision Agent: "Überarbeite alle Szenen mit Maria + Vladimir" → exakte Scene-IDs aus dem Graph
- Style Validator: "Prüfe Ton-Konsistenz über alle ESTATE-Szenen"

### 4. Subplot-Tracking
- Welche Szenen gehören zum Subplot "snowstorm_fate"?
- Wird der Subplot über alle drei Akte verteilt?

## Empirisch (Der Schneesturm, 2026-04-07)
- 6 Figuren, 29 Locations, 12 Figuren-Paare, 45 Timeline-Einträge
- Top-Paar: Maria|Vladimir (20 Szenen) — dominant wie erwartet für eine Liebestragödie
- Bourmin taucht in 14 Szenen auf — 31% der Szenen, angemessen für die zweite Hälfte
- Build-Zeit: ~1ms (instantan)

## Wichtig: Charakter-Names matchen
Die Graph-Keys nutzen die exakten Namen aus `state["adapted_scenes"][]["characters"]`. Bei "Der Schneesturm" ist das `"Maria"`, nicht `"Maria Gavrilovna"`. Immer den State prüfen, nicht raten.
