---
title: Adaptation Criteria — Decision Rules v1
tags: [adaptation, criteria, rules, decision-framework]
version: v1
created: 2026-04-23
scope: medium (iterative; later versions may cover exhaustive edge cases)
domains: [CF, SC, SS, NF, M]
---

# Adaptation Criteria — Decision Rules v1

## Preamble

Dieses Dokument konsolidiert konkrete **IF/THEN-Entscheidungsregeln** für die vier kreativen Kernentscheidungen jeder Literaturadaption:

- **CF** — Character Fusion (Figurenfusion)
- **SC** — Scene Compression (Szenenkompression, inkl. Streichung, Verdichtung, Expansion)
- **SS** — Subplot Suppression (Handlungsstrang-Streichung)
- **NF** — Narrator Frame (Erzähler-/Rahmen-Entscheidungen)
- **M** — Meta-Regeln (Prioritätsauflösung bei Regelkonflikten)

Jede Regel hat eine eindeutige ID (`CF-01`, `SC-03`, `NF-05`, `M-02`) und verweist auf eine benannte Quelle (Seger, McKee, Field, Egri, Stoehr, Snyder, Howard, Kempton). Die IDs werden von Pipeline-Agents in ihren `DECISIONS`-Blocks zitiert — so ist jede kreative Entscheidung auf einen nachvollziehbaren theoretischen Anker zurückführbar.

### Philosophie

**Regeln sind Heuristiken, keine Gesetze.** Sie kodifizieren das Erfahrungswissen etablierter Drehbuchtheoretiker in einer Form, die von KI-Agents anwendbar ist. Abweichungen sind erlaubt — müssen aber explizit begründet werden (`rule_id = "DEVIATION"` + `deviation_justification`).

**Regeln sind domänenspezifisch.** Eine Figurenfusion-Regel ist nicht auf Szenenkompression anwendbar. Bei Regel-Kollisionen zwischen Domänen greifen die Meta-Regeln (M-01 bis M-05).

**Regeln sind versionierbar.** v1 (2026-04-23) deckt ~40 Regeln mittlerer Granularität ab. v2 (geplant) erweitert auf Edge-Cases, Multi-Source-Zitate, und projekt-spezifische Threshold-Tuning.

### Verwendung durch Agents

Jeder kreative Agent (Story Analyst, Adaptation Agent, Revision Agent) bekommt dieses Dokument in seinen System-Prompt injiziert. Im Output produziert der Agent nach seinem JSON/Text einen `DECISIONS`-Block:

```
DECISIONS:
- FUSE Khan Mahoma → Bata: both guides, <4 scenes each, functional overlap → CF-01
- CUT_SUBPLOT thistle-field-second-scene: repeats frame, no plot-engine → SS-02, NF-08
- REFOCAL Nikolaus-Hof: seen only through HM's letter → CF-08
- DEVIATION scene_S007: both compression rules inconclusive → kept for tension arc
```

Post-Dispatch wird der Block vom Orchestrator in `output/adaptation_log.json` geschrieben — ohne jemals wieder in einen Agenten-Kontext geladen zu werden. Die Log-Datei ist reiner Begleit-Artefakt für Reproduzierbarkeitsanalyse und Audit.

### Prioritätskette bei Regelkonflikten

Wenn zwei Regeln einen Konflikt produzieren, gilt:
1. **M-02 (Thema-Priorität)** sticht alle domänenspezifischen Cut-Regeln
2. **M-03 (Historische Anker)** sticht CF-Fusions-Regeln
3. **M-01 (Figur-Integrität)** sticht SS-Subplot-Cut-Regeln, falls Figur in Subplot
4. **M-05 (Voice-Profile-Schutz)** sticht SC-Szenen-Cut, falls nur dort Profile sichtbar
5. **M-04 (Deviation)** — wenn keine der obigen greift: als Abweichung kennzeichnen und begründen

---

## Domain CF — Character Fusion

### [CF-01] Funktionale Figurenfusion
- **IF:** Figur hat < 5 Szenen in Quelltext UND teilt dramatische Hauptfunktion (Mentor / Antagonist / Ally / Threshold-Guardian / Herald) mit einer Tier-1-Figur
- **THEN:** `FUSE` — EINE signaturhafte Zeile oder Geste der Minor-Figur an Tier-1-Figur übertragen, Minor-Name aus Dramatis Personae streichen, im `character_merges`-Feld dokumentieren
- **Quelle:** Seger, Linda — *The Art of Adaptation*, Ch. 6 "Choosing the Characters" ("Combining characters does not necessarily mean adding up the qualities of two characters and giving them to one. It might mean cutting one character, but taking a line of dialogue or action of that character and giving it to another.")
- **Brain-Ref:** [[patterns/figurenfusion]]
- **Beispiel:** *Gone With the Wind* — Will (Roman) → Mammy (Film) erhält Satz "Don't spoil it.... After all, he's her husband, ain't he?"

### [CF-02] Thematische Überlappungs-Prüfung
- **IF:** Fusion-Kandidat_A und Kandidat_B tragen SELBE thematische Funktion im Quellwerk (beide "Opfer des Systems" / beide "Mentor-Stimmen" / beide "nostalgische Anker")
- **THEN:** `FUSE` erlaubt (thematische Überlappung ≥70%)
- **ELSE:** `DO_NOT_FUSE` — thematische Distinktion ist werkstiftend; Fusion würde Polyphonie zerstören
- **Quelle:** Seger — *Art of Adaptation*, Ch. 5–6 (thematic coherence of composite characters)
- **Brain-Ref:** [[patterns/figurenfusion]] Kriterium 1

### [CF-03] Drive-Kohärenz-Prüfung
- **IF:** Fusion-Kandidaten haben kompatible `want`s (keine direkten Motiv-Konflikte, z.B. NICHT: A will X stützen, B will X zerstören)
- **THEN:** `FUSE` erlaubt
- **ELSE:** `DO_NOT_FUSE` — kaputte Kausalität; schwächere Figur stattdessen `CUT`
- **Quelle:** Egri, Lajos — *The Art of Dramatic Writing* (Unity of Opposites, character consistency); Seger (drive-coherence)
- **Brain-Ref:** [[autoren/lajos-egri]], [[patterns/figurenfusion]] Kriterium 3

### [CF-04] Immunität Historischer Anker-Figuren
- **IF:** Figur ist reale historische Person, im Quellwerk dokumentiert als reale Figur der Epoche
- **THEN:** `NEVER_FUSE` — historische Anker sind nicht fusionsfähig (Identitäts-Integrität, Auditierbarkeit). `CUT` bleibt möglich, aber keine Komposit-Bildung
- **Quelle:** Seger — *Art of Adaptation*, Ch. 7 "Adapting from Fact"
- **Anwendung HM:** Shamil, Vorontsov, Nikolaus I., Hadji Murat, Poltoratsky sind alle CF-04-immun. Nur fiktionale Neben-Tscherkessen/-Russen fusionierbar

### [CF-05] Love-Interest-Distinktion (Anti-Pattern-Schutz)
- **IF:** Quelle hat mehrere Love-Interests, die JEWEILS EINEN anderen thematischen Lebensentwurf für Protagonist verkörpern (Anna Karenina: Anna vs. Kitty vs. Dolly tragen drei Ehe-Modelle)
- **THEN:** `DO_NOT_FUSE` — thematische Vielstimmigkeit ist werkstiftend
- **Quelle:** Seger — *Unforgettable Characters*, Ch. 5 (character differentiation as theme); [[patterns/figurenfusion]] Anti-Pattern 1

### [CF-06] Antagonisten-Eskalationsleiter
- **IF:** Quelle inszeniert graduelle Antagonisten-Steigerung (Mittel-Boss → End-Boss)
- **THEN:** `KEEP` mindestens ZWEI Antagonisten-Ebenen — kollabierte Monolith-Antagonisten zerstören dramatischen Rhythmus der Progressive Complications
- **Quelle:** McKee, Robert — *Story*, "Progressive Complications" (Kap. 11)
- **Brain-Ref:** [[autoren/robert-mckee]]

### [CF-07] Multi-POV-Werk-Erhalt
- **IF:** Quelle nutzt Multi-POV als WERKSTIFTENDES Device (Rashomon-Prinzip, *The Last Duel*, *Atonement*)
- **THEN:** `DO_NOT_FUSE_POVS` — POV-Vielfalt ist die Struktur-Leistung des Werks
- **ELSE:** weiter zu CF-08 (Refokalisation möglich)
- **Quelle:** Bolt/Pasternak (Zhivago), Scott/Affleck (Last Duel 2021); [[patterns/figurenfusion]] Anti-Pattern 3

### [CF-08] Refokalisations-Regel (Multi-POV-Kompression)
- **IF:** Quelle ist Multi-POV UND kein POV ist werkstiftend (i.e. CF-07 greift NICHT)
- **THEN:** `REFOCAL` auf Tier-1-Protagonist — andere POVs werden zu RELATIONEN zu ihm (nur was er erlebt/sieht/erfährt). Nicht gezeigte POVs werden via Brief / Bericht / Bote eingeführt
- **Quelle:** McKee — POV-Skala-Reduktion; Bolt (Zhivago); Anna Karenina 2012 (Stoppard)
- **Brain-Ref:** [[patterns/kompression-roman]] McKee-Scale 2 (POV-Skala)

### [CF-09] Komposit-Szenen-Ökonomie-Test
- **IF:** `scenes(A) + scenes(B) > scenes(composite_AB)` nach Fusion
- **THEN:** Fusion ist `ECONOMICAL` — Netto-Szenenreduktion rechtfertigt Kompressions-Cost
- **ELSE:** Fusion `WASTEFUL` — getrennt lassen
- **Quelle:** Seger — *Art of Adaptation* (dramatic economy); [[patterns/figurenfusion]] Kriterium 2

### [CF-10] Human-in-the-Loop-Gate
- **IF:** Fusion-Kandidat mit Graphify-Confidence ≥ 0.7 vom Story Analyst (Phase 1) vorgeschlagen
- **THEN:** `PROPOSE` mit Begründung in `state.adaptation_hints.fusion_candidates[]` — User muss vor Phase 5 explizit bestätigen (Traceability für Methodendokumentation)
- **Rationale:** keine stille KI-Fusion; Audit muss jede Fusion verteidigen können
- **Brain-Ref:** [[patterns/figurenfusion]] Anwendungsregel 1

---

## Domain SC — Scene Compression

### [SC-01] Drei-Fragen-Filter (Seger-Kernregel)
- **IF:** Szene scheitert an ALLEN drei Tests:
  (a) Protagonist-Drive: bewegt sie Protagonist nicht zum Ziel / definiert Ziel nicht neu
  (b) Thematik: trägt sie Kernthema nicht
  (c) Filmische Notwendigkeit: Information bereits woanders erreichbar
- **THEN:** `CUT` Szene komplett
- **IF:** Szene besteht 1/3 Tests → `COMPRESS` (aggressiv auf Kern-Beat)
- **IF:** Szene besteht 2+/3 Tests → `KEEP` (eventuell leicht verdichten)
- **Quelle:** Seger — *Art of Adaptation*, Ch. 5 "Finding the Story" (Goal/Problem/Climax); McKee — scene economy
- **Brain-Ref:** [[patterns/kompression-roman]] "Killing Your Darlings"-Kriterien

### [SC-02] Dual-Function-Faustregel
- **IF:** Szene erfüllt nur EINE Funktion (nur Charakter-Zeigen ODER nur Plot-Voranbringen, nicht beides)
- **THEN:** `CUT` oder `MERGE` mit anderer Einzelfunktions-Szene zu Doppel-Funktions-Szene
- **Quelle:** Snyder, Blake — *Save the Cat* (scene efficiency); [[patterns/streichungen-entscheidungen]] Faustregel
- **Brain-Ref:** [[autoren/blake-snyder]]

### [SC-03] Wertewechsel-Erhaltung (McKee)
- **IF:** Szene enthält Wertewechsel (positiv→negativ oder umgekehrt, z.B. Hoffnung→Verzweiflung, Fremdheit→Vertrauen)
- **THEN:** `PRESERVE` — Wertewechsel sind die atomaren dramatischen Einheiten, nicht kompressibel
- **Quelle:** McKee — *Story*, Ch. 13 "The Composition of a Scene" (scene-value-analysis); Ch. "The Substance of Story"
- **Brain-Ref:** [[konzepte/story-values]]

### [SC-04] Zeit-Skala-Reduktion
- **IF:** Quellabschnitt überspannt lange Zeiträume (Monate/Jahre)
- **THEN:** Kompression via:
  - **Ellipsen-Schnitt** (Bildwechsel = Zeitverlauf)
  - **Motiv-Rückkehr** (Objekt/Ort in verschiedenen Zuständen — Zhivagos Varykino-Haus)
  - **Zeitraffer durch Schnitt** (nicht durch Voice-Over-Zusammenfassung)
- **VERBOTEN:** Voice-Over als Zeitraffer — das ist Prose, nicht Cinema
- **Quelle:** McKee — *Story* (time-scale); Bolt — *Doctor Zhivago* 1965
- **Brain-Ref:** [[patterns/kompression-roman]] McKee-Scale 1

### [SC-05] Redundanter-Beat-Konsolidierung (Chunk-Overlap-Dedup)
- **IF:** Szene_A und Szene_B teilen ≥75% gleiche `source_chunks` UND gleiche dramatische Funktion (Location + Figuren + Beats)
- **THEN:** `MERGE` — höchste-Confidence-Szene beibehalten, Dialog-Draft als Union (nach `text` dedupliziert), Subplot-Threads Union, `continuity_result` re-compute
- **Rationale:** verhindert Kompressions-Artefakte wie in T5.1 (3 Iterationen der Sado-Ankunft, S003–S007)
- **Operationalisierung:** `orchestrator.deduplicate_adapted_scenes()` zwischen Phase 5 und Phase 9
- **Quelle:** keine Literaturbasis — empirisch-gepipelinte Regel aus Coverage-Kritik T5.1

### [SC-06] Literarische-Schönheit-Warnung
- **IF:** Szene ist "schönste Passage des Romans" UND primär innerlich/philosophisch (Tolstoi-Exkurse, Pasternak-Poesie)
- **THEN:** Zwei Optionen: entweder (a) `TRANSLATE_TO_VISUAL` (in Handlung, Objekt, Bild übersetzen) oder (b) `CUT` — NIEMALS als Exposition-Dialog beibehalten
- **Quelle:** McKee — *Story* ("Don't fill characters' mouths with self-explanatory dialogue but find visual expression for their inner conflicts.")
- **Brain-Ref:** [[patterns/kompression-roman]] "Darling-Warnung"

### [SC-07] Initialverletzungs-Erhaltung
- **IF:** Szene enthält Protagonist-Initialverletzung / Inciting Incident (der Moment, der die Geschichte startet — Northup verliert Freiheit, Zhivago verliert Platz in der Welt, Hadji Murad wird zum Gejagten)
- **THEN:** `NEVER_CUT` — Fundament des Charakter-Bogens
- **Quelle:** [[patterns/kompression-roman]] "Was nicht komprimiert werden darf"; Field — Inciting-Incident als Akt-I-Säule
- **Brain-Ref:** [[konzepte/dramatic-question]]

### [SC-08] Struktureller-Wendepunkt-Erhaltung
- **IF:** Szene ist struktureller Wendepunkt nach 8-Sequenzen-Struktur (Plot Point I, Midpoint, Plot Point II, Climax)
- **THEN:** `PRESERVE` — die spezifische Szene kann verändert werden, aber die strukturelle Funktion muss an genau dieser Position bleiben
- **Quelle:** Field — *Screenplay* (paradigm plot points); Stoehr — *8 Sequence Structure*
- **Brain-Ref:** [[konzepte/acht-sequenzen]], [[konzepte/plot-points]]

### [SC-09] Sequenz-Budget-Einhaltung
- **Default-Allokation (120-min Feature):** 10–15 Seiten pro Sequenz (8 Sequenzen × 12.5 Seiten = 100 Seiten Kern + Luft)
- **IF:** Sequenz-Seitenzahl > 20% über Default
- **THEN:** `COMPRESS` innerhalb dieser Sequenz (priorisiert: Szenen mit nur 1 SC-01-Passed)
- **Quelle:** Stoehr — *8 Sequence Structure*; Field — Paradigm page-count ratios
- **Note:** `scene_budget_policy = "soft_target"` (user-entschieden) — Überschreitung bis +50% akzeptabel wenn Geschichte es rechtfertigt; >+50% triggert Revision-Überlegung

### [SC-10] Szenen-Expansion (nur short_story → feature)
- **IF:** Quelle fasst emotionalen Beat in Einzelsatz zusammen UND Beat ist thematisch zentral UND Adaptionsmodus = `short_story_to_feature`
- **THEN:** `EXPAND` zu vollständiger Szene (Ellipsen-Dramatisierung)
- **ELSE (novel_to_feature):** nicht anwendbar — Default bleibt `COMPRESS`
- **Quelle:** Seger — *Art of Adaptation*, Ch. "Dramatizing Ellipses"
- **Brain-Ref:** [[patterns/expansion-kurzgeschichte]]

---

## Domain SS — Subplot Suppression

### [SS-01] Subplot-Zahl-Deckel
- **IF:** Aktuelle Subplot-Zahl > 4
- **THEN:** `ELIMINATE` schwächsten nach (a) Thema-Priorität (b) Protagonist-Verbindung (c) Szenen-Zahl
- **Quelle:** Seger — *Art of Adaptation* ("Be careful if you have more than four subplots.")
- **Brain-Ref:** [[patterns/kompression-roman]]

### [SS-02] Subplot-Thema-Test
- **IF:** Subplot spiegelt / kontrastiert / verstärkt Kernthema NICHT
- **THEN:** `CUT_SUBPLOT` komplett (nicht kompromieren, nicht kürzen — streichen)
- **Quelle:** [[patterns/streichungen-entscheidungen]] Schicht 3 ("Welche Handlungsstränge sind strukturell tragend?"); Seger
- **Brain-Ref:** [[patterns/streichungen-entscheidungen]]

### [SS-03] Welt-Exposition-Only-Cut
- **IF:** Subplot-Funktion ist reine "Welt-Ausbreitung" (historischer Kontext, Milieu-Beschreibung) OHNE Protagonist-Beteiligung
- **THEN:** `CUT` oder `REDUCE` zu atmosphärischem Detail in A-Plot-Szene
- **Quelle:** Bolt (Zhivago cut medizinische Karriere, philosophische Passagen)
- **Brain-Ref:** [[patterns/kompression-roman]]

### [SS-04] Auktoriale-Digression-Cut
- **IF:** "Subplot" ist eigentlich auktorialer Kommentar / philosophische Exkursion (nicht dramatisiert, keine Figuren-Handlung)
- **THEN:** `CUT` immer — non-filmable per Definition
- **Quelle:** McKee — show-don't-tell; Field — cinematic vs. literary
- **Anwendung HM:** Tolstois Exkurse über Krieg, Politik, Religion sind SS-04-Kandidaten — werden in die Handlung integriert ODER gestrichen

### [SS-05] Drei-Subplot-Struktur
- Ein 90–120-Minuten-Feature trägt maximal:
  - **A-Plot:** Haupthandlung (Protagonist, zentraler Konflikt)
  - **B-Plot:** Beziehungs-/Liebes-Handlung ODER zweite persönliche Achse
  - **C-Plot:** Spiegel-/Kontrast-Handlung (reflektiert oder kontrastiert A thematisch)
- Alle weiteren Handlungsstränge: `FUSE` in A/B/C, `CUT`, oder `REDUCE` zu Micro-Motiv
- **Quelle:** Field — *Screenplay* (B-story structure); Seger — [[patterns/streichungen-entscheidungen]] Schicht 3

### [SS-06] Spiegel-Subplot-Erhaltung
- **IF:** Subplot spiegelt Protagonist-Bogen (zweite Figur durchläuft analoge Reise, z.B. Eldar als Spiegel zu HMs Loyalitäts-Konflikt)
- **THEN:** `KEEP` — Spiegel-Subplots verstärken Thema durch Echo-Effekt
- **Quelle:** Egri — Unity of Opposites (dramatische Dialektik); Aristoteles — Wiederholung als Erkenntnisverstärker

### [SS-07] Comic-Relief-Integration
- **IF:** Quelle hat Comic-Relief-Subplot UND Ton der Adaption lässt es zu
- **THEN:** `INTEGRATE` via SEKUNDÄR-Figur innerhalb A/B/C, nicht als separater Subplot
- **Quelle:** Field — B-Plot-Funktionalität; [[patterns/streichungen-entscheidungen]]

### [SS-08] Eskalations-Subplot-Erhaltung
- **IF:** Subplot liefert Einsatz-Eskalation am Midpoint (Sequenz 4 Ende) oder Plot Point II (Sequenz 6 Ende)
- **THEN:** `KEEP` — strukturelle Last an dramatischen Wendepunkten
- **Quelle:** Stoehr — 8-Sequenzen (Second Culmination); McKee — Progressive Complications

### [SS-09] Historischer-Kontext-Kompression
- **IF:** Subplot = historische Umgebung (Krieg, politische Ereignisse) UND Quelle ist historische Adaption
- **THEN:** `COMPRESS` in Akt-1-Setup + gelegentliche Erinnerungs-Beats; KEIN B-Plot-Status
- **Quelle:** Lean/Bolt — *Lawrence of Arabia* (arabische Revolte in HM-Orient-Szenen komprimiert); Bondarchuk — *War and Peace* 1966
- **Anwendung HM:** Kaukasus-Krieg als Ganzes bleibt Setting, nicht Subplot. Nur konkrete Schlachten mit HM-Beteiligung dürfen Szenenraum beanspruchen

### [SS-10] Redundant-Subplot-Merge
- **IF:** Zwei Subplots teilen Thema + Funktion (beide "Familie als Druckmittel", beide "Loyalitäts-Prüfung")
- **THEN:** `MERGE` zu einem Komposit-Plot-Strang
- **Parallel zu:** CF-01 (Komposit für Figuren) — hier für Plot-Linien

---

## Domain NF — Narrator Frame

### [NF-01] Narrator-Funktions-Translation (Basis-Regel)
- **IF:** Quelle hat Erzählstimme (beliebigen Typs)
- **THEN:** Identifiziere PRIMÄRE Funktion:
  - (a) **Zeit-Strukturierung** → filmisches Äquivalent: Schnitt, Zwischentitel, Rahmenhandlung
  - (b) **Wertung** → Figurenverhalten, Kamerahaltung (hoch/tief/nah/fern)
  - (c) **Ironie** → Kontrast zwischen Bild und Dialog
  - (d) **Unzuverlässigkeit** → Mehrfach-Perspektive, Wiederholung
- **THEN:** Anwendung der funktions-spezifischen Regel (NF-02 bis NF-07)
- **Quelle:** [[patterns/erzaehler-eliminieren]] Anwendungsregel; McKee — narrative devices

### [NF-02] Unzuverlässiger-Erzähler → Visueller Perspektivwechsel
- **IF:** Quelle hat unzuverlässigen Ich-Erzähler (lügt / ist voreingenommen / sieht nur Teil der Wahrheit)
- **THEN:** Multi-Perspektiven-Szenen-Wiederholung (*Atonement*-Pattern) — gleiche Szene zweimal aus unterschiedlichen POVs
- **VERBOTEN:** Voice-Over-"Korrektur" durch anderen Erzähler
- **Quelle:** Hampton — *Atonement* screenplay; McEwan — *Atonement* novel
- **Brain-Ref:** [[patterns/erzaehler-eliminieren]] Lösung 1

### [NF-03] Rahmen-Erzähler → Struktureller Bracket
- **IF:** Quelle hat Rahmen-Erzähler, dessen Suche SELBST dramatische Einsätze hat (Yevgraf sucht Zhivagos Tochter)
- **THEN:** `KEEP` als Bracket (Opening + Closing Echo), Rahmen-Figur wird eigene dramatische Linie
- **ELSE:** `DISSOLVE_FRAME` — keine dekorativen Erzähler
- **Quelle:** Bolt — *Doctor Zhivago* 1965
- **Brain-Ref:** [[patterns/erzaehler-eliminieren]] Lösung 2

### [NF-04] Auktorialer-Erzähler-Auflösung
- **IF:** Quelle hat allwissenden auktorialen Erzähler (Tolstois "But what vitality!")
- **THEN:** `CUT` Erzähler-Stimme; Kommentar in Protagonist-Verhalten / Kamera-Entscheidung / Bild-Montage übersetzen
- **VERBOTEN:** Beibehaltung als Voice-Over
- **Quelle:** McKee — show-don't-tell (applied to narrator)
- **Brain-Ref:** [[patterns/erzaehler-eliminieren]] (angewandt auf Tolstoi-Kontext)

### [NF-05] Chronist-Ton → Distanz in Kamera
- **IF:** Quelle ist Zeugenbericht / Chronik (Ich-Erzähler in dritter Person, sachlich, distanziert — Northup über sich selbst)
- **THEN:** Übersetzung in Weit-/Halbtotal-Framing + protagonistische Zurückhaltung im Spiel (12 Years a Slave-Pattern)
- **VERBOTEN:** Voice-Over
- **Quelle:** Ridley/McQueen — *12 Years a Slave* 2013
- **Brain-Ref:** [[patterns/erzaehler-eliminieren]] Lösung 3

### [NF-06] Kontrast-Stimme (Brief-Encounter-Pattern)
- **IF:** Voice-Over wird eingesetzt, MUSS es mit dem sichtbaren Bild kontrastieren (nicht duplizieren)
- **THEN:** `KEEP_VOICE_OVER` nur wenn Stimme sagt, was Bild NICHT zeigt
- **ELSE:** `CUT_VOICE_OVER`
- **Quelle:** Lean/Coward — *Brief Encounter* 1945
- **Brain-Ref:** [[patterns/erzaehler-eliminieren]] Lösung 4

### [NF-07] Epilog-Erzähler-als-Subjekt
- **IF:** Unzuverlässigkeit des Erzählers IST das thematische Zentrum der Quelle
- **THEN:** Erzähler wird On-Screen-Figur im Epilog; Erzählung wird SELBST zum Subjekt ("sie gesteht die Manipulation")
- **Quelle:** Hampton/Wright — *Atonement* Epilog (ältere Briony im TV-Interview)
- **Brain-Ref:** [[patterns/erzaehler-eliminieren]] Lösung 5

### [NF-08] Doppel-Frame-Warnung
- **IF:** Quelle hat Frame (z.B. Distel-Prolog) UND Haupthandlung
- **THEN:** Frame einmalig am Opening nutzen; KEINE Wiederholung im Closing AUSSER Closing-Echo bringt thematisches Fortschreiten
- **Rationale:** T5.1 Coverage flaggte "doubled thistle metaphor" — zweite Frame-Szene erklärte erste und wirkte redundant
- **Quelle:** empirisch aus Coverage-Kritik T5.1; Lawrence of Arabia (Lean öffnet mit Motorrad-Tod, kein Closing-Frame)

### [NF-09] Charakter-POV-Primäre-Regel
- **IF:** Quelle hat auktorialen Erzähler ABER Protagonist-POV ist zugänglich (HMs innere Gedanken werden gezeigt)
- **THEN:** Verhalten/Entscheidungen des Protagonisten AS DE-FACTO Erzähler — keine zusätzliche Stimme nötig
- **Quelle:** Bolt — Lawrence of Arabia (Lawrences Handlung trägt den Roman ohne O'Toole-Voice-Over)

---

## Domain M — Meta-Regeln (Prioritätsauflösung)

### [M-01] Figur-Integrität über Subplot-Cut
- **IF:** CF-01 sagt FUSE Figur X UND SS-02 sagt CUT Subplot Y, der Figur X enthält
- **THEN:** Fusion ZUERST, Subplot-Entscheidung DANACH mit fusionierter Figur — Figur-Integrität geht Subplot-Streichung vor
- **Rationale:** Character-Arc-Kontinuität ist dramatisches Fundament

### [M-02] Thema-Priorität (Supreme)
- **IF:** IRGENDEINE Regel würde Szene / Figur / Subplot streichen, die das KERNTHEMA trägt
- **THEN:** `DO_NOT_CUT` — komprimieren, umstrukturieren, integrieren — aber thematische Last muss erhalten bleiben
- **Quelle:** Egri — *Art of Dramatic Writing* (Prämisse als Werkstütze); [[konzepte/praemisse]]
- **Priorität:** M-02 sticht CF-01, SC-01, SS-01 — alle Cut-Regeln verlieren gegen Thema-Erhaltung

### [M-03] Historische-Anker-Immunität (Cross-Domain)
- **IF:** CF-04 (historische Figur, nicht fusionierbar) kollidiert mit CF-01 (fusioniere wenn < 5 Szenen)
- **THEN:** CF-04 gewinnt — historische Figuren niemals fusioniert, Character kann nur `CUT` oder `KEEP`
- **IF:** SS-09 (historischer Kontext komprimieren) kollidiert mit benannten realen Ereignissen um benannte reale Personen
- **THEN:** Reale Ereignisse bleiben szenisch erhalten (auch komprimiert), SS-09 gilt nur für generischen Hintergrund

### [M-04] Deviation Erlaubt mit Begründung
- **IF:** Keine Regel passt EXAKT ODER zwei Regeln konfligieren nach Anwendung M-01/02/03
- **THEN:** `rule_id = "DEVIATION"` + Pflicht-Feld `deviation_justification` (welches Prinzip wurde stattdessen angewandt, z.B. "Werkgeist der Quelle verlangt Exception")
- **Rationale:** Kriterien sind Heuristik, keine Dogmatik. Abweichungen sind OK, müssen aber nachvollziehbar sein — Audit kann sie verteidigen
- **Deviation-Quota:** <15% aller Entscheidungen pro Run; höhere Quote zeigt Kriterien-Lücke, triggert v2-Revision

### [M-05] Voice-Profile-Integrität über Szenen-Ökonomie
- **IF:** SC-01 sagt CUT Szene UND diese Szene ist die EINZIGE Stelle, wo Tier-1-Charakters Voice-Profile in Aktion zu sehen ist (z.B. HMs "Ne habar?"-Ritual oder Sados Prayer-Geste)
- **THEN:** Zuerst versuchen: `MERGE` in Nachbar-Szene unter Erhalt des Voice-Signature-Beats
- **ELSE (wenn MERGE unmöglich):** CUT nur wenn Voice-Signature bereits in >=2 anderen Szenen etabliert ist
- **Rationale:** Voice-Integrität ist empirisch höchster Coverage-Score-Treiber (T5.1: Dialog-Score 68 bei erhaltenen Voice-Profiles)

---

## Regel-Summary-Tabelle

| Domain | Count | Primär-Quelle | Sekundär-Quellen |
|---|---|---|---|
| CF (Character Fusion) | 10 | Seger — *Art of Adaptation* Ch. 6–7 | Egri (drive-coherence), McKee (progressive complications) |
| SC (Scene Compression) | 10 | Seger Ch. 5; McKee — *Story* Ch. 13 | Field, Snyder, Stoehr |
| SS (Subplot Suppression) | 10 | Seger (four-subplot cap); [[patterns/streichungen-entscheidungen]] | Field (B-story), Egri (dialectic) |
| NF (Narrator Frame) | 9 | [[patterns/erzaehler-eliminieren]]; Hampton/Wright, Bolt/Lean, Ridley/McQueen | McKee (narrative voice) |
| M (Meta / Priority) | 5 | Egri (theme supremacy); empirisch (T5.1) | — |
| **Total** | **44** | | |

---

## Changelog

### v1 — 2026-04-23
- Initial release, Scope = Medium
- 44 Regeln über 5 Domänen (CF, SC, SS, NF, M)
- Quellen-Basis: 4 bestehende Pattern-Files (figurenfusion, kompression-roman, streichungen-entscheidungen, erzaehler-eliminieren) + 7 Autor-Profile in `adaptions-brain/autoren/` + MCP-Server-Titel (Seger *Art of Adaptation*, McKee *Story*, Egri *Dramatic Writing*, Field *Screenplay*, Snyder *Save the Cat*, Stoehr *8 Sequence*, Kempton *Dialogue*)
- Eine empirische Regel (SC-05 Dedup) aus T5.1-Coverage-Kritik
- Deviation-Quota-Ziel: ≤15% aller Agent-Entscheidungen

### v2 (geplant)
- Erweiterung auf ~80 Regeln mit Edge-Cases
- Multi-Source-Zitate pro Regel (aktuell: 1 Primärquelle)
- MCP-Excerpt-References (chunk_index) für direkte Zitat-Verifikation
- Projekt-spezifische Override-Mechanismen (`projekte/<n>/adaptation_criteria_overrides.md`) dokumentiert — wird bei Bedarf befüllt

---

## Referenzen

### Quellen (Bücher, via MCP-Server zugänglich)
- Seger, Linda. *The Art of Adaptation.* Henry Holt, 1992. [MCP: `The_Art_of_Adaptation_chapters_4-8_ocr.txt`]
- Seger, Linda. *Creating Unforgettable Characters.* Henry Holt, 1990. [MCP: `Linda_Seger_Creating_unforgettable_characters.txt`]
- McKee, Robert. *Story: Substance, Structure, Style, and the Principles of Screenwriting.* ReganBooks, 1997. [MCP: `Robert_Mckee_Story.txt`]
- Egri, Lajos. *The Art of Dramatic Writing.* Simon & Schuster, 1946. [MCP: `The_Art_of_dramatic_writing.txt`]
- Field, Syd. *Screenplay: The Foundations of Screenwriting.* Revised Edition, Delta Trade Paperbacks, 2005. [MCP: `Syd_Field_Screenwriting.txt`]
- Snyder, Blake. *Save the Cat!* Michael Wiese Productions, 2005. [MCP: `Blake_Snyder_Save_the_Cat.txt`]
- Stoehr, Hannes. *8 Sequence Structure.* stoehrfilm.eu. [MCP: `8_Sequence_Structure_Regie_1_long_version_Stoehr.txt`]
- Kempton, Gloria. *Dialogue.* Writer's Digest, 2004. [MCP: `Gloria_Kempton_Dialogue.txt`]
- Howard, David. *The Tools of Screenwriting.* St. Martin's Press, 1995. [MCP: `The_Tools_of_Screenwriting_by_David_Howard.txt`]

### Brain-Pattern-Files (destilliert)
- [[patterns/figurenfusion]] — Segers drei Fusionskriterien + HM-spezifische Anti-Patterns
- [[patterns/kompression-roman]] — Drei-Fragen-Filter + McKee-Scale-Reduktion
- [[patterns/streichungen-entscheidungen]] — 4-Schichten-Framework (Thema → Figuren → Plot → Visuell)
- [[patterns/erzaehler-eliminieren]] — 5 Lösungs-Patterns für Narrator-Translation
- [[konzepte/acht-sequenzen]] — Stoehr-basierte Struktur-Vorlage (120-min Feature)
- [[konzepte/story-values]] — McKees Wertewechsel-Framework
- [[konzepte/vier-figurenfunktionen]] — Thematic anchor for fusion decisions

### Fall-Studien (48 Screenplays im MCP)
- *Gone With the Wind* — Segers CF-01-Kern-Beispiel (Will → Mammy)
- *Doctor Zhivago* 1965 (Bolt/Lean) — CF-08 Refokalisation, NF-03 Rahmen-Erzähler
- *12 Years a Slave* 2013 (Ridley/McQueen) — CF-01, NF-05 Chronist-Ton
- *Atonement* 2007 (Hampton/Wright) — NF-02, NF-07 unzuverlässiger Erzähler
- *Brief Encounter* 1945 (Coward/Lean) — NF-06 Kontrast-Voice-Over
- *Lawrence of Arabia* 1962 (Bolt/Lean) — NF-09 Char-POV, SS-09 Historische Kompression
- *The Last Duel* 2021 (Affleck/Damon/Holofcener/Scott) — CF-07 Multi-POV Preservation
- *Anna Karenina* 2012 (Stoppard/Wright) — CF-05 Love-Interest-Distinktion, CF-08 Refokalisation
- *The English Patient* 1996 (Minghella) — SC-04 Time-Scale, NF-03 Multi-Ebenen-Frame
- *The Godfather* 1972 (Coppola/Puzo) — CF-01 Dons→Barzini, [[patterns/streichungen-entscheidungen]] Tom Hagen

---

#adaptation #criteria #decision-rules #traceability-ready #v1
