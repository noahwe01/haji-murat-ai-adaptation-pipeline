# Literaturadaption Skills – Pipeline-Methodik

## 15 Skills für die Adaption von Romanen, Novellen & Kurzgeschichten in Treatments und Drehbücher

Fachlich fundiert auf Basis von: **Syd Field** (Screenplay), **Prof. Hannes Stoehr** (8-Sequenzen-Struktur), **Linda Seger** (The Art of Adaptation) und professionellen Treatment-Standards.

---

## Wie diese Skills geladen werden

Diese Skills sind **Pipeline-Runtime-Dependencies**. Sie werden deterministisch pro Agent-Rolle von `utils/skill_loader.py:load_skills_for_agent()` gelesen und in die Agent-Prompts injiziert.

Die Zuordnung Agent → Skills steht im `AGENT_SKILLS`-Dict in `skill_loader.py`. Wer einen Skill hinzufügt, muss ihn auch dort verdrahten — sonst bleibt er unsichtbar.

Archivierte Files (Fremd-Pipeline, XML-Output, Kurzfilm) liegen unter `_legacy/` und werden nicht geladen.

---

## Übersicht aller Skills

### Master-Skill
| Skill | Beschreibung |
|---|---|
| `adaptation-workflow` | **Einstiegspunkt** – orchestriert alle Skills in 7 Phasen vom Buch zum Drehbuch |

### Analyse & Planung
| Skill | Beschreibung |
|---|---|
| `source-material-analysis` | Prüft Vorlagen auf Filmtauglichkeit, Widerstände und Adaptionsstrategie |
| `logline-creation` | Verdichtet die Kerngeschichte in einen Satz (Protagonist + Auslöser + Ziel + Einsatz) |
| `story-to-3act-structure` | Überträgt die Handlung in die 3-Akt/8-Sequenzen-Struktur |

### Figuren & Konflikte
| Skill | Beschreibung |
|---|---|
| `character-want-need` | Entwickelt Figurenbögen mit Want vs. Need und Character-Revealing Actions |
| `adaptation-conflict-design` | Gestaltet externe/interne Konflikte und Eskalation über die Sequenzen |
| `cultural-authenticity` | Sichert kulturelle, religiöse und identitätsbezogene Authentizität |

### Struktur & Szenen
| Skill | Beschreibung |
|---|---|
| `plot-point-mapping` | Kartiert die 5 Schlüssel-Wendepunkte (Inciting Incident bis Resolution) |
| `subplot-weaving` | Wählt, verschmilzt und streicht Nebenhandlungen für die Filmerzählung |
| `scene-card-breakdown` | Zerlegt die Vorlage in Scene Cards / Step Outline (nach Tally/Sargent) |

### Schreiben & Formatieren
| Skill | Beschreibung |
|---|---|
| `film-treatment-creation` | Erstellt professionelle Treatments (5–15 Seiten) mit allen Pflichtbestandteilen |
| `prose-to-visual-scenes` | Übersetzt Prosa-Passagen in filmbare Szenen (Innenleben → Verhalten) |
| `dialogue-adaptation` | Adaptiert literarische Dialoge und innere Monologe für die Leinwand |
| `theme-to-screen` | Macht Themen durch Figurenhandlung sichtbar statt durch Exposition |
| `screenplay-formatting` | Formatiert Szenen im Industriestandard (Sluglines, Action, Dialog) |

---

## Empfohlener Workflow

```
Phase 1: source-material-analysis
    ↓
Phase 2: logline-creation → story-to-3act-structure
    ↓
Phase 3: character-want-need → cultural-authenticity
    ↓
Phase 4: adaptation-conflict-design → plot-point-mapping
    ↓
Phase 5: scene-card-breakdown → subplot-weaving
    ↓
Phase 6a: film-treatment-creation (Treatment)
    ODER
Phase 6b: prose-to-visual-scenes → dialogue-adaptation
           → theme-to-screen → screenplay-formatting (Drehbuch)
    ↓
Phase 7: Qualitätssicherung (alle Skills als Prüflinse)
```

---

## Quellen

- Syd Field: *Screenplay – The Foundations of Screenwriting*
- Prof. Hannes Stoehr: *8 Sequence Structure (Long Version)*
- Linda Seger: *The Art of Adaptation – Turning Fact and Fiction into Film*
- Filmtreatment-Leitfaden: *Was ist ein Treatment im Film?*
