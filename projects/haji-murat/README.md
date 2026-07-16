# Haji Murat project snapshot

This directory preserves the input and internal run artifacts used by the adaptation pipeline.

- `config/`: project configuration
- `sources/`: public-domain literary source
- `state/` and `story_state.json`: phase checkpoints and current shared state
- `logs/prompts/`: prompt and model-result captures
- `HM_obsidian-vault/`: structured character, location, timeline, scene, and theme knowledge
- `graphify-in/` and `graphify-out/`: graph preprocessing inputs and outputs
- `output/adaptation_log*.json`: machine-readable adaptation decisions

Standalone creative deliverables and review documents are intentionally not part of this repository. Some state snapshots contain intermediate text because the next pipeline phase consumed it through the shared state.
