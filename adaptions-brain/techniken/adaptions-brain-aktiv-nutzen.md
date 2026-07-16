# Adaptions-Brain aktiv nutzen — Pflichtprotokoll

## Das Problem

Das Adaptions-Brain hat 92+ Notes, 600+ Wikilinks, 740 KB Wissen. Aber es wird nur PASSIV genutzt — als Referenz nach dem Schreiben. Es muss AKTIV genutzt werden — als Ressource WÄHREND des Schreibens.

## Pflicht-Protokoll pro Phase

### VOR Phase 1 (Story Analysis)
Laden:
- `patterns/expansion-kurzgeschichte.md` — welche Expansion-Strategie passt?
- `konzepte/drei-akt-struktur.md` — Timing-Checkpoints für die Akte
- `patterns/perspektivwechsel.md` — wessen Geschichte ist das?

### VOR Phase 5 (Adaptation)
Laden:
- `konzepte/subtext.md` — 70/30 Regel in den Prompt injizieren
- `konzepte/on-the-nose.md` — 5 Anti-Patterns als Negativbeispiele
- `techniken/dialog-durch-handlung.md` — Aktion-statt-Rede Prinzip
- `techniken/stille-als-dialog.md` — wo bewusst schweigen?
- `konzepte/figurenstimme-differenzieren.md` — Voice Profile Dimensions
- `dialog-bibliothek/[relevanter-szenen-typ].md` — Referenzdialoge für die aktuelle Szene

### VOR Phase 6 (Script Writing)
Laden:
- `techniken/dialog-kompression.md` — Halving Rule
- `techniken/rhythmus-pacing.md` — Short-Long-Short Muster
- `techniken/szenenuebergang-typen.md` — Match Cuts, J-Cuts planen
- `techniken/emotionale-vorbereitung.md` — Setup/Payoff Inventar
- `patterns/pipeline-anti-patterns.md` — bekannte Fehler vermeiden

### VOR Phase 7 (Coverage)
Laden:
- `konzepte/character-arc.md` — 4 Arc-Types als Prüflinse
- `patterns/nebenfigur-aufwerten.md` — sind Nebenfiguren dimensional?
- `techniken/cold-open.md` — funktioniert der Einstieg?

### NACH Phase 7 (Lernen)
Aktualisieren:
- Bewährte Techniken mit ✓ markieren
- Fehlgeschlagene Techniken mit ⚠ markieren
- Neue Erkenntnisse als Notes anlegen

## Implementierung

Das Brain wird nicht "gelesen" — es wird als **Prompt-Erweiterung** injiziert. Relevante Techniken werden als Regeln in den System-Prompt des jeweiligen Agents kopiert.

**Beispiel:** Adaptation Agent Phase 5 bekommt zusätzlich:
```
DIALOG RULES (from Adaptions-Brain):
- 70/30 Rule: 70% subtext, 30% direct
- Third Thing: Characters discuss external topic to avoid on-the-nose
- Action before speech: Physical reaction comes BEFORE verbal response
- Silence IS dialog: Pauses and gestures carry emotional content
- Blindtest: Could you identify the speaker without the character name?
```

Das sind ~50 Tokens extra. Der Impact ist massiv.
