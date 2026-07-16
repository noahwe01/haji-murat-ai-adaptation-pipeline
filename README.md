# Haji Murat AI Adaptation Pipeline

This repository contains the implementation and reproducibility artifacts of a multi-agent pipeline for adapting a long literary source into a feature-film screenplay workflow.

The system combines source chunking, structured story analysis, character and world synthesis, adaptation strategy, scene generation, continuity control, screenplay assembly, and several post-generation quality checks. The repository preserves the actual project configuration, source input, state checkpoints, prompt logs, knowledge notes, Obsidian project data, and Graphify outputs used by the pipeline.

## What is included

- Pipeline source code in `agents/`, `config/`, `utils/`, and the root Python modules
- JSON schemas and preflight tools
- Runtime skills and the Adaptions-Brain knowledge base
- Optional MCP reference-server code, without its local reference corpus
- The Haji Murat project input and configuration
- State checkpoints, prompt logs, Graphify artifacts, and Obsidian project content
- Machine-generated decision logs required to trace adaptation choices

## What is intentionally excluded

- Standalone treatments, screenplays, rendered documents, and submission files
- Assessment forms and unrelated review material
- Personal notes, chat handoffs, and local editor configuration
- Copyrighted reference-corpus payloads and their generated search index
- Secrets, API keys, caches, virtual environments, and dependency folders

State snapshots are preserved as technical run artifacts. Some snapshots contain intermediate generated text inside state fields because later phases consumed that state.

## Repository layout

```text
agents/                         Agent prompt builders and result ingestors
adaptions-brain/                Curated adaptation knowledge notes
config/                         Framework configuration loader
docs/                           Architecture and data-boundary documentation
mcp-server/                     Optional local retrieval-server code
projects/haji-murat/
  config/                       Project-specific pipeline configuration
  sources/                      Public-domain source input
  state/                        Checkpoints and analysis results
  logs/prompts/                 Preserved prompts and model-result captures
  HM_obsidian-vault/            Structured project knowledge
  graphify-in/                  Graph extraction inputs
  graphify-out/                 Character, location, and plotline graphs
  output/adaptation_log*.json   Machine-readable decision audit
schemas/                        Output contracts
skills/                         Runtime methodology modules
tools/                          Preflight and prompt-smoke utilities
utils/                          Chunking, retrieval, logging, and output helpers
```

## Pipeline overview

```mermaid
flowchart LR
    A["Source text"] --> B["Chunking and intake"]
    B --> C["Story analysis"]
    C --> D["Character, world, and story synthesis"]
    D --> E["Strategy: compression, subplots, fusion"]
    E --> F["Dialogue improvisation"]
    F --> G["Scene adaptation"]
    G --> H["Continuity and deduplication"]
    H --> I["Treatment or screenplay assembly"]
    I --> J["Coverage and style validation"]
    J --> K["Pacing, subtext, dialogue, transitions, coherence, table read"]
    K --> L["Targeted revision"]
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the detailed phase and agent map.

## Local setup

Requirements:

- Python 3.10+
- PyYAML
- Node.js 18+ only when using the optional MCP server
- An external LLM execution layer for dispatching the prompts built by the agents

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m tools.preflight --project projects/haji-murat
```

The current CLI directly exposes the post-generation analysis-prompt build:

```bash
python3 projects/haji-murat/run.py --phase 9.5
```

The full historical run used external model dispatch: prompt builders created payloads, model calls were executed outside the repository, and the returned JSON was ingested by the corresponding `run_*` functions. The preserved prompt logs and state checkpoints document that boundary.

## Data and licensing notes

The included Haji Murat source is the public-domain English text used for this project. The Adaptions-Brain contains condensed working notes rather than the underlying reference books or screenplay corpus.

The optional MCP server expects a local `mcp-server/extracted/` directory and generated `mcp-server/index.json`. Those payloads are intentionally absent and ignored by Git.

No license is granted for third-party material. Review the rights status of any source or reference material before creating another distribution.
