# Voice Profile Injection — Vollständige 9-Dimensionen-Strategie

## Die 9 Dimensionen eines Voice Profiles

| # | Dimension | Was sie liefert | Token-Budget |
|---|-----------|----------------|-------------|
| 1 | `voice_description` | Gesamtcharakter der Stimme, Entwicklung über Akte | ~40 |
| 2 | `vocabulary_level` | Bildungsgrad, Milieu, Sprachregister | ~15 |
| 3 | `sentence_structure` | Satzlänge, Komplexität, Muster | ~15 |
| 4 | `verbal_tics` | Wiederkehrende Ausdrücke, Sprachmuster | ~20 |
| 5 | `avoidances` | Was die Figur NIE sagt — oft aufschlussreicher als Tics | ~20 |
| 6 | `emotional_expression` | Wie die Figur Gefühle zeigt/verbirgt | ~30 |
| 7 | `speech_rhythm` | Tempo, Pausen, Beschleunigung unter Druck | ~15 |
| 8 | `dialog_examples` | 5 emotionale Zustände mit Beispielzeilen | ~40 |
| 9 | `subtext_rules` | Was die Figur wirklich meint vs. was sie sagt | ~25 |

**Gesamt: ~200 Tokens pro Charakter** (bei 5-6 Hauptfiguren: ~1000-1200 Tokens)

## Warum alle 9 Dimensionen kritisch sind

### Das Truncation-Problem (v2.0)
In der ursprünglichen Pipeline wurden nur 3-5 Dimensionen injiziert:
- `voice_description` (gekürzt)
- `verbal_tics` (gekappt auf 3)
- `avoidances` (gekappt auf 3)

**Resultat:** Dialog klang generisch. Figuren waren austauschbar. Coverage-Score für Dialog: 68/100.

### Was die fehlenden Dimensionen bewirken

**`dialog_examples`** sind der größte Hebel: Das LLM bekommt konkrete Referenzzeilen für 5 emotionale Zustände (neutral, unter Druck, hoffnungsvoll, wütend, verletzlich). Das ist Few-Shot-Learning für Dialog-Generierung.

**`subtext_rules`** verhindern On-the-Nose-Dialog: Wenn das LLM weiß, dass Maria "Ich könnte niemals" sagt und damit "Ich bin bereits gebunden" meint, schreibt es besseren Subtext.

**`emotional_expression`** gibt dem LLM die Anweisung, WIE eine Figur Emotion zeigt — nicht nur welche Worte sie benutzt, sondern auch physische Reaktionen, Schweigen, Deflection.

### Caps sind kontraproduktiv
`verbal_tics[:3]` und `avoidances[:3]` kappe die Liste bei 3 Einträgen. Problem: Oft sind gerade die Einträge 4-5 die subtilsten und differenzierendsten. Bei einer Kurzgeschichte mit nur 4-5 Hauptfiguren hat man Token-Budget für alle Einträge.

## Bewährt (aus Der Schneesturm, 2026-04-07)
- Volle 9-Dimensionen-Injektion bringt ~5600 Chars für 5 Charaktere
- Token-Budget bleibt unter 1500 — kein spürbarer Impact auf Kontextfenster
- Dialog-Beispiele als Few-Shot sind der einzelne größte Qualitätshebel

## Anwendungsregel
**Immer alle 9 Dimensionen injizieren.** Keine Caps. Die Token-Kosten sind minimal (1-2% des Kontextfensters), der Qualitätsgewinn für Dialog ist massiv.
