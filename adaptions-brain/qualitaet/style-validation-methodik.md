# Style Validation — Automatische Stil-Konsistenzprüfung

## Konzept

Der Style Validator prüft, ob das generierte Screenplay mit dem deklarierten Style Manifest übereinstimmt. Er ist kein kreativer Agent — er ist ein Prüfer.

## Die 5 Kategorien

| Kategorie | Gewicht | Was geprüft wird |
|-----------|---------|-----------------|
| **Tone Consistency** | 25% | Stimmt der Ton durchgehend? Passen Stimmungswechsel? |
| **Dialog Register** | 20% | Klingt jede Figur wie ihr Voice Profile? Passt das Register zum Genre? |
| **Visual Vocabulary** | 20% | Passen Action Lines zum deklarierten visuellen Stil? Referenzfilm-Ästhetik? |
| **Thematic Threads** | 20% | Werden deklarierte Themen durch Szenen gewoben? Show, nicht tell? |
| **Pacing & Rhythm** | 15% | Stimmt der Szenen-Rhythmus? Wechseln leise/laute Beats? Beschleunigung zum Climax? |

## Warum Tone Consistency 25% bekommt

Ton ist das, was ein Publikum als Erstes spürt — noch vor Plot oder Figuren. Ein Film wie "Atonement" lebt von seinem bittersweet-melancholischen Ton. Ein einziger Ton-Bruch (z.B. eine unangebracht komische Szene) kann den gesamten Eindruck zerstören. Daher höchste Gewichtung.

## Referenzfilm-Anker-Methode

Die Referenzfilme im Style Manifest dienen als **ästhetische Anker**:
- "Wie würde diese Szene in Atonement aussehen?"
- "Würde Pawlikowski diese Action Line so formulieren?"
- "Passt dieser Dialog zu Cold War (2018)?"

Der Validator prüft nicht, ob der Film ein Klon der Referenzen ist — sondern ob er im selben ästhetischen Raum operiert.

## Integration in die Pipeline

```
Phase 7: Coverage Agent → Coverage Report
Phase 7b: Style Validator → Style Report
Phase 8: Revision Agent ← nimmt Issues aus Coverage + Style
```

Der Style Validator läuft NACH dem Coverage Agent (braucht dessen Kompression) und VOR dem Revision Agent (liefert Issues).

## Modell: Sonnet

Style Validation ist analytisch, nicht kreativ. Sonnet reicht — spart Opus-Tokens für den Revision Agent.

## Implementiert (Der Schneesturm, 2026-04-07)
- 5 Kategorien mit gewichteter Score-Berechnung
- Nutzt `_compress_for_coverage()` für Volltext-Evaluation
- Speichert Report in `state["style_validation"]`
- `get_style_issues()` extrahiert actionable Issues für Revision Agent
