# Pipeline architecture

## Control model

The pipeline separates deterministic orchestration from model execution:

1. Python modules load project configuration and current story state.
2. Agent modules build bounded prompts for one phase or artifact.
3. An external LLM execution layer returns structured results.
4. Agent-specific ingestors validate and merge those results into `story_state.json`.
5. The orchestrator advances phase status, versions state, and routes quality failures into revision.

The orchestrator does not create creative text itself. It coordinates phases, validates state transitions, and applies the quality gates.

## Phase sequence

| Phase | Function | Primary modules | Persistent result |
|---|---|---|---|
| 0 | Source intake and length classification | `utils/chunker.py`, `agents/orchestrator.py` | chunked source state |
| 1 | Chunk-level story analysis | `agents/story_analyst.py` | characters, plot, themes, compression candidates |
| 2 | Character, world, and story synthesis | `agents/character_agent.py`, `agents/world_agent.py` | voice profiles, relationships, locations, timeline |
| 3 | Adaptation strategy | `agents/orchestrator.py`, Graphify helpers | subplot pruning, fusion decisions, style validation |
| 4 | High-tension dialogue improvisation | `agents/character_agent.py` | character-specific dialogue material |
| 5 | Scene adaptation | `agents/adaptation_agent.py` | structured adapted scenes |
| 5.5 | Duplicate-scene audit | `agents/scene_dedup_auditor.py` | duplicate flags and merge candidates |
| 6 | Long-form assembly | `agents/script_writer.py` | treatment state |
| 7 | Coverage and style checks | `agents/coverage_agent.py`, `agents/style_validator.py` | coverage and style reports |
| 9 | Screenplay assembly | `agents/script_writer.py` | screenplay state |
| 9.5 | Post-generation analysis | six analysis agents | pacing, subtext, dialogue, transition, coherence, table-read results |
| 8 | Targeted revision | `agents/revision_agent.py` | revised scenes and decision log |

## Agent map

### Generative and synthesis agents

- Story Analyst: source extraction, structure, themes, compression opportunities
- Character Agent: psychology, want/need, voice profiles, casting anchors, dialogue improvisation
- World Agent: locations, timeline, atmosphere, production constraints
- Adaptation Agent: scene construction under the approved strategy
- Script Writer: treatment and screenplay assembly
- Revision Agent: issue-targeted rewriting

### Control and validation agents

- Orchestrator
- Continuity Watcher
- Scene Dedup Auditor
- Coverage Agent
- Style Validator
- Filmability Validator
- Source Fidelity Validator
- Document Continuity Checker

### Analysis layer

- Pacing Analyzer
- Subtext Auditor
- Dialogue Thread Checker
- Transition Mapper
- Narrative Coherence Analyzer
- Table Read

## Shared state

`state_store.py` is the persistence boundary. It owns:

- state loading, saving, versioning, and compatibility accessors;
- phase and status metadata;
- character, world, plot, scene, treatment, screenplay, and evaluation fields;
- continuity issues and knowledge gaps;
- prompt-safe views that remove irrelevant state before dispatch.

The preserved state directory contains checkpoints from different phases. These are run evidence, not all independent outputs.

## Knowledge retrieval

`utils/skill_loader.py` resolves four layers:

1. runtime skills in `skills/`;
2. project-local vault overrides;
3. Adaptions-Brain notes;
4. an optional local MCP index.

Each role has a retrieval budget so large source and knowledge collections do not silently dominate prompt context.

## Graphify integration

Graphify preprocesses the source into:

- a character graph for co-occurrence and fusion candidates;
- a location graph for spatial consolidation;
- plotline clusters for narrative prioritization.

The resulting JSON artifacts are consumed as strategy evidence. They do not make final adaptation decisions without the pipeline's decision and review steps.

## Reproducibility boundary

The repository preserves prompt payloads, selected returned results, decision logs, and state checkpoints. It does not contain model credentials or the external dispatch service. Repeating the exact model calls may still vary with model version and provider behavior.
