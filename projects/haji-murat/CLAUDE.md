# CLAUDE.md — Haji Murat project instructions

This file supplements the repository-level `../../CLAUDE.md` for work inside
`projects/haji-murat/`. The root rules remain binding unless this file provides
a more specific project instruction.

## Project identity

| Field | Verified value |
|---|---|
| Title | `Hadji Murat` |
| Source | `sources/hadji_murat.txt` |
| Source length | 46,290 words |
| Chunking | 2,500 words, 300-word overlap, 119 chunks |
| Adaptation mode | `novel_to_feature` |
| Target runtime | 120 minutes |
| Scene budget | 60 |
| Source language | English |
| Output language | English |
| Configured final mode | `screenplay` |
| Maximum revision cycles | 2 |

These are checked project constants, not a status report. For current progress,
read `story_state.json`. Do not copy a current status into this file because it
would become stale after the next phase.

## Project authority

Within this directory, use this order:

1. `config/projekt.yaml` for intended project settings;
2. `story_state.json` for current run state;
3. `state/` for checkpoints and phase-specific evidence;
4. `output/adaptation_log*.json` for adaptation decisions;
5. `HM_obsidian-vault/` and `graphify-out/` for structured project knowledge;
6. `logs/prompts/` for dispatch provenance.

If configuration, active state, and a historical artifact disagree, report the
disagreement. Do not silently normalize the active state or retrofit an older
checkpoint.

## Narrative constraints

The project configuration defines the adaptation as a historical war tragedy
and anti-imperial fable. Preserve these constraints unless the configuration is
explicitly changed:

- keep the tone tragic and sober, with epic distance and intimate moments;
- show violence without glorification;
- preserve moral ambiguity around empire and resistance;
- refocalize the multi-viewpoint source around Hadji Murat as the central
  protagonist;
- express the other viewpoints through their relationship to that central arc;
- treat Shamil, Vorontsov, and Nicholas I as historical anchors, not fusion
  candidates;
- treat retention or removal of the thistle frame as an explicit strategy
  decision, never as an automatic default;
- invented material may bridge transitions but must not create unsupported new
  plotlines.

Graphify findings identify candidates and structural evidence. They do not make
final fusion, pruning, or prioritization decisions by themselves.

## Project paths

```text
config/projekt.yaml              Project configuration
sources/hadji_murat.txt          Source input
story_state.json                 Active shared state
state/                           Backups, snapshots, and analysis results
logs/prompts/                    Preserved prompt and result captures
HM_obsidian-vault/               Project-local knowledge and continuity notes
graphify-in/                     Graph extraction inputs
graphify-out/                    Character, location, and plotline graphs
output/adaptation_log.json       Current decision audit
output/adaptation_log.pre_E.json Earlier preserved decision audit
run.py                           Project-aware CLI entry point
```

The working directory matters. `run.py` changes into this project directory so
that `state_store.py` resolves `story_state.json` and `state/`, while the shared
framework remains available two levels above.

## State handling

The active state is approximately a complete run workspace, not a minimal
configuration file. It includes source chunks, analysis, characters, world,
adapted scenes, continuity findings, assembled text fields, and evaluation
results.

Before changing it:

1. inspect `meta.status`, `meta.current_phase`, and the fields owned by the
   requested phase;
2. create a versioned checkpoint using the repository state utilities;
3. preserve all unrelated keys and historical evidence;
4. validate JSON parsing and the intended status transition after the change;
5. record adaptation decisions in the decision log when required.

Do not assume `meta.status` and `meta.current_phase` agree. If they do not,
treat that as a finding to explain, not permission to rewrite either value.

The configured status flow is inherited from the root guide. Historical files
under `state/archive/`, `state/backups/`, and `state/snapshots/` are immutable run
evidence unless a dedicated migration is requested.

## Quality gates

Use the project values from `config/projekt.yaml`:

- confidence threshold: `0.75`;
- dialogue-improvisation tension threshold: `0.6`;
- high-tension routing threshold: `0.7`;
- coverage verdicts: `RECOMMEND >= 80`, `CONSIDER >= 65`, `PASS >= 50`;
- top coverage issues retained: `5`;
- expected pacing variance: `1.8`;
- treatment batches: `8` scenes;
- screenplay batches: `5` scenes.

Scores do not replace issue-level review. Before revision, trace each proposed
change to source evidence, continuity evidence, a schema failure, or a specific
quality finding.

## Safe commands

Run from the repository root:

```bash
python3 -m tools.preflight --project projects/haji-murat
python3 -m tools.prompt_smoke --project projects/haji-murat
python3 projects/haji-murat/run.py --phase 9.5
```

Run from this project directory only when a module expects project-relative
configuration or state:

```bash
python3 run.py --phase 9.5
```

The Phase 9.5 command builds prompt files; it does not execute model calls. The
full historical run depended on external dispatch and explicit result ingestion.

## Project-specific prohibitions

- Do not add separate creative deliverables to `output/`; only the tracked
  machine-readable adaptation logs belong there.
- Do not remove embedded `treatment_text` or `final_script` fields from state
  snapshots merely because standalone deliverables are excluded.
- Do not replace the public-domain source file without recording provenance and
  revalidating word count and chunk boundaries.
- Do not add local vault settings, application state, session plans, or handoff
  files.
- Do not add external reference-corpus payloads or generated retrieval indexes.
- Do not start a regeneration or revision cycle as a side effect of inspection,
  documentation, or validation work.
