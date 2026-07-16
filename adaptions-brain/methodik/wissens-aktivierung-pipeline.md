# Wissens-Aktivierung in der Pipeline

## Das Problem (vor v3.1)

Das Adaptions-Brain (90+ Notes, 388 KB) war zu 97,4% ungenutzt. Nur 1 von 9 Agents lud Skills. Budget war auf 2.000 Chars gekappt.

## v3.2 Update: Dynamisches Brain-Retrieval (2026-04-07)

### Wie ein echtes Gehirn
Das System arbeitet jetzt in 3 Stufen:
1. **Statische Skills** — Jeder Agent lädt seine festen Skills (17 aus `skills/`, 7 aus Brain)
2. **Dynamisches Retrieval** — Pro Chunk/Szene werden kontextbasiert Brain-Notes geladen (Keyword-Matching auf Chunk-Text → Dialog-Bibliothek + Konzepte)
3. **Wissenslücken-Erkennung** — Wenn eine Brain-Note fehlt: automatisch in State geloggt, am Ende dem User gemeldet

### Keyword → Brain-Note Mapping
- "confession", "secret", "truth" → `dialog-bibliothek/gestaendnis-szenen.md`
- "love", "longing", "desire" → `dialog-bibliothek/liebes-szenen.md`
- "dialog", "subtext" → `konzepte/subtext.md`
- "exposition" → `konzepte/exposition-timing.md`
- etc. (15 Szenen-Typen, 15 Konzept-Trigger)

### Knowledge Gap Workflow
```
Agent braucht Wissen → Brain-Suche → Datei fehlt?
  Ja → log_knowledge_gap() → report_knowledge_gaps() am Session-Ende
  → User erstellt Brain-Note → nächster Run: automatisch geladen
```

## Die Lösung (v3.1, 2026-04-07)

### 3-Stufen-Suchpfad
```
1. skills/                    → Projekt-lokale Skill-Definitionen
2. obsidian-vault/config/     → Projekt-spezifische Overrides
3. adaptions-brain/           → Geteiltes Drehbuchwissen
   ├── techniken/
   ├── konzepte/
   ├── patterns/
   ├── qualitaet/
   ├── dialog-bibliothek/
   └── methodik/
```

### Alle 9 Agents laden jetzt Skills

| Agent | Skills | Chars | Brain-Notes |
|-------|--------|-------|-------------|
| story_analyst | 16 | ~6k | Nein (project skills) |
| character_agent | 14 | ~6k | figurenstimme-differenzieren |
| world_agent | 5 | ~2k | Nein (project skills) |
| adaptation_agent | 17 | ~6k | voice-profile-injection |
| script_writer_treatment | 1 | ~2k | Nein |
| script_writer_screenplay | 21 | ~6k | dialog-polish-pass |
| coverage_agent | 14 | ~6k | coverage-volltext-evaluation |
| style_validator | 1 | ~2k | style-validation-methodik |
| revision_agent | 6 | ~4k | revision-agent-workflow |

### Budget: 6.000 Chars (vorher 2.000)
3× mehr Wissen pro Agent. Immer noch nur ~1,5% des Kontextfensters. Kein messbarer Impact auf Latenz oder Kosten.

## Wie das Brain jetzt wächst

Jeder neue Fix/Feature schreibt eine Brain-Note. Diese Note wird automatisch beim nächsten Pipeline-Run als Skill geladen, weil der Suchpfad das Brain einschließt.

```
Implementierung → Brain-Note → nächster Run → Skill geladen → besseres Ergebnis
```

## Style → Revision Verbindung

`orchestrator.route_revision()` sammelt jetzt Issues aus BEIDEN Quellen:
- Coverage Report (Dialog, Pacing, Struktur)
- Style Validation (Ton, Register, Visuelles, Themen)

Revision Agent bekommt alle Issues als Input.
