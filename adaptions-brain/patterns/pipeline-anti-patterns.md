# Pipeline Anti-Patterns: Was bei Multi-Agent-Adaptionen schiefgeht

## Das Kernproblem

Multi-Agent-Systeme verlieren Information an Phasengrenzen. Jeder Agent sieht nur einen Ausschnitt dessen, was der vorherige Agent produziert hat. Die Summe der Teile ist WENIGER als das Ganze.

## Anti-Pattern 1: Voice Profile Truncation

**Was passiert:** Character Agent erstellt reiche Stimmprofile (9 Dimensionen). Adaptation Agent bekommt davon 3 Felder.

**Warum es passiert:** Token-Budget. Die volle Voice-Profile-Injection kostet ~200 Tokens pro Charakter × 8 Charaktere = 1.600 Tokens. Die truncated Version kostet ~50 × 8 = 400 Tokens.

**Konsequenz:** Dialog klingt generisch. Figurenstimmen verwässern. Subtext-Regeln werden ignoriert.

**Lösung:** Voice Profiles sind KEINE Token-Budgetposten. Sie sind die Kernressource des Screenplays. Immer vollständig injizieren. Lieber weniger Context-Window für andere Dinge opfern.

## Anti-Pattern 2: Isolated Chunk Analysis

**Was passiert:** Story Analyst analysiert jeden Chunk ohne Kontext der vorherigen Chunks.

**Warum es passiert:** Dead Code — Memory-Summary-Funktion existiert, wird aber nicht aufgerufen.

**Konsequenz:** Wiederkehrende Motive werden als "neu" erkannt. Figuren-Register hat Duplikate. Themen-Häufigkeiten stimmen nicht.

**Lösung:** Jeder Chunk-Prompt bekommt: "Bisher erkannt: [Figuren], [Themen], [letzter Plot-Punkt]". Minimal 50-100 Tokens Kontext reichen aus.

## Anti-Pattern 3: Scene-Isolation im Script Writer

**Was passiert:** Script Writer bekommt Szenen einzeln oder in kleinen Batches. Sieht nie die Gesamt-Struktur.

**Konsequenz:** Jede Szene ist für sich optimiert. Aber der Film als Ganzes hat keine Dramaturgie — keine Rhythmus-Variation, keine bewussten Kontraste, keine aufbauende Spannung.

**Lösung:** Dem Script Writer zusätzlich zum Batch einen "Story Spine" mitgeben: 3-Akt-Struktur, Midpoint, Tension Curve, wo dieser Batch im Gesamt-Arc steht.

## Anti-Pattern 4: Coverage auf Teiltext

**Was passiert:** Coverage Agent schneidet den Script-Text nach 50k Zeichen ab.

**Konsequenz:** Act III wird nie evaluiert. Confession-Sequenz, Resolution, Payoffs — alles unsichtbar für die Qualitätssicherung.

**Lösung:** Multi-Pass Coverage (Act-weise evaluieren) oder Scene-Summary-Compression (jede Szene auf 3 Sätze, dann den ganzen Film covern).

## Bewährt ✓ (aus Der Schneesturm, 2026-04-06)

### Was trotz dieser Probleme funktioniert
- **Treatment-Pipeline**: Treatment wird von Claude Code als ein Durchgang geschrieben, nicht von den Agents. Deshalb ist das Treatment besser als das Screenplay — kein Informationsverlust.
- **Coverage als iteratives Feedback**: Auch mit Teiltext-Evaluation treibt Coverage die Verbesserung (74.3 → 83.2 → 90.6).
- **Expansion-Strategie**: Die 20/30/25/25 Formel funktioniert als kreatives Gerüst.
