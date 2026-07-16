# Dialog Polish Pass — Zwei-Pass-Strategie für Screenplay-Dialog

## Konzept

Screenplay-Dialog wird in zwei Pässen geschrieben:
1. **Assembly Pass** (Sonnet): Struktur, Scene Headers, Action Lines, erster Dialog-Entwurf
2. **Polish Pass** (Opus): Nur Dialog überarbeiten — Voice Profiles, Subtext, Distinktheit

## Warum zwei Pässe?

### Problem mit einem Pass
Der Assembly-Pass fokussiert auf Struktur: Szenenübergänge, Action-Line-Format, Pacing. Dialog ist dabei "gut genug", aber nicht exzellent. Das LLM balanciert zu viele Aufgaben gleichzeitig.

### Vorteil des Polish-Pass
- **Fokus:** Nur Dialog, keine Strukturänderungen → LLM kann sich voll auf Stimmen konzentrieren
- **Voice Profiles:** Vollständige 9-Dimensionen-Profile werden injiziert (siehe [[voice-profile-injection]])
- **Quality Checks:** 5 explizite Prüfungen pro Durchgang:
  1. Klingt jeder Charakter wie sein Voice Profile?
  2. Gibt es On-the-Nose-Dialog?
  3. Trägt jeder Austausch Subtext?
  4. Wäre der Charakter ohne Namenszusatz erkennbar?
  5. 70/30-Regel: 70% Subtext, max 30% direkt

### Die 70/30-Regel
Professioneller Film-Dialog folgt einer Faustregel: Mindestens 70% des Gesprochenen kommuniziert INDIREKT (durch Subtext, Metapher, Deflection). Maximal 30% darf direkt sein. On-the-Nose-Dialog ("Ich bin traurig") funktioniert in Romanen, aber nicht im Film.

## Modell-Routing

- **Assembly:** Sonnet (analytisch, strukturell, kostengünstig)
- **Polish:** Opus (kreativ, nuanciert, versteht Subtext besser)
- **Routing-Key:** `pass_type="dialog_polish"` → Orchestrator routet automatisch zu Opus

## Token-Budget

~5.000-8.000 zusätzliche Tokens pro Pipeline-Run (5 Screenplay-Batches × ~1.500 Tokens pro Polish-Call). Bei Opus-Pricing relevant, aber der Dialog-Qualitätsgewinn rechtfertigt die Kosten.

## Wann NICHT polieren

- **Treatment-Modus:** Treatments haben keinen formatierten Dialog → kein Polish nötig
- **Dialog-Score ≥ 90:** Wenn Coverage den Dialog bereits hoch bewertet, ist ein Polish-Pass optional (spart Opus-Tokens)

## Implementiert (Der Schneesturm, 2026-04-07)
- `build_dialog_polish_prompt()` baut System-Prompt mit vollständigen Voice Profiles
- `run_dialog_polish()` ersetzt Screenplay-Batches mit polierten Versionen
- Rückwärtskompatibel: Funktioniert mit bestehenden Screenplays ohne Umbau
