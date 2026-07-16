"""
Config Loader — Loads projekt.yaml and returns a flat dict.
Supports all 7-agent architecture fields including expansion strategy,
coverage thresholds, and model routing configuration.
"""

from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None


def _resolve_config_path(explicit: Optional[Path] = None) -> Path:
    """Finds projekt.yaml. Project-repo layout (cwd/config/) takes precedence
    over framework-colocated (loader's __file__ parent) so the framework can
    live in a submodule while config stays in the project repo.
    """
    if explicit is not None:
        return Path(explicit)
    cwd_config = Path.cwd() / "config" / "projekt.yaml"
    if cwd_config.exists():
        return cwd_config
    return Path(__file__).parent / "projekt.yaml"


CONFIG_PATH = _resolve_config_path()

DEFAULTS = {
    # Project
    "title": "My Film Project",
    "source_file": "story.txt",
    "output_mode": "treatment",
    "source_language": "en",
    "output_language": "en",
    "target_runtime": 90,

    # Chunking
    "chunk_size": 2000,
    "chunk_overlap": 200,
    "debug_chunks": None,

    # Style
    "genre": "Drama",
    "tone": "thoughtful, quiet",
    "reference_films": ["Aftersun", "C'mon C'mon"],
    "special_notes": "",
    "language": "English",

    # Agents
    "model_override": None,
    "confidence_threshold": 0.75,
    "max_revision_cycles": 2,
    "impro_key_scenes": 5,
    "impro_tension_threshold": 0.6,
    "scene_budget": 50,
    "tension_opus_threshold": 0.7,

    # Script Writer
    "batch_treatment": 8,
    "batch_screenplay": 5,

    # Pacing (set higher for slow-cinema adaptations; 1.2 = modern feature default,
    # 1.8 = tableau-oriented pacing. Consumed by Pacing Analyzer's
    # dead-zone thresholds: the higher the expected variance, the more tolerant the
    # analyzer is toward long contemplative scenes.)
    "pacing_expected_variance": 1.2,

    # Coverage
    "verdict_recommend": 80,
    "verdict_consider": 65,
    "verdict_pass": 50,
    "top_n_issues": 5,

    # Expansion / Compression
    # Valid modes:
    #   None                    → default, no composition targets (source-proportional)
    #   "short_story_to_feature" → Expansion (source 20% / ellipses 30% / subplots 25% / worldbuilding 25%)
    #   "novel_to_feature"       → Compression (source 25% / cuttable 60% / restructured 10% / bridges 5%)
    "expansion_mode": None,
    "composition_targets": {
        # Expansion keys (used when mode == "short_story_to_feature")
        "direct_source_pct": 20,
        "dramatized_ellipses_pct": 30,
        "invented_subplots_pct": 25,
        "worldbuilding_external_pct": 25,
        # Compression keys (used when mode == "novel_to_feature")
        "source_compression_pct": 25,     # Kernszenen direkt aus dem Roman
        "cuttable_material_pct": 60,      # Subplots/Nebenfiguren/Exkurse, die gestrichen werden
        "restructured_pct": 10,           # Figurenfusion, umgestellte Akte, neu fokalisierte Szenen
        "invented_bridges_pct": 5,        # reine Übergangsszenen (keine neuen Plots)
    },
}


def load_config(config_path: Optional[Path] = None) -> dict:
    """Loads projekt.yaml and returns a flat dict.

    Falls back to DEFAULTS if the YAML file doesn't exist
    or PyYAML is not installed.
    """
    path = _resolve_config_path(config_path)
    if yaml is None or not path.exists():
        return dict(DEFAULTS)

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    config = dict(DEFAULTS)

    # --- projekt ---
    projekt = raw.get("projekt", {})
    if projekt.get("titel"):
        config["title"] = projekt["titel"]
    if projekt.get("autor_roman"):
        config["author"] = projekt["autor_roman"]
    elif projekt.get("author"):
        config["author"] = projekt["author"]
    if projekt.get("quelldatei"):
        config["source_file"] = projekt["quelldatei"]
    if projekt.get("output_modus"):
        config["output_mode"] = projekt["output_modus"]
    if projekt.get("source_language"):
        config["source_language"] = projekt["source_language"]
    if projekt.get("output_language"):
        config["output_language"] = projekt["output_language"]
    if projekt.get("ziel_laufzeit") is not None:
        config["target_runtime"] = projekt["ziel_laufzeit"]

    # --- chunking ---
    chunking = raw.get("chunking", {})
    if chunking.get("chunk_groesse") is not None:
        config["chunk_size"] = chunking["chunk_groesse"]
    if chunking.get("chunk_overlap") is not None:
        config["chunk_overlap"] = chunking["chunk_overlap"]
    config["debug_chunks"] = chunking.get("debug_chunks")

    # --- style ---
    style = raw.get("style", {})
    if style.get("genre"):
        config["genre"] = style["genre"]
    if style.get("ton"):
        config["tone"] = style["ton"]
    if style.get("referenzfilme"):
        config["reference_films"] = style["referenzfilme"]
    if "besonderheiten" in style:
        config["special_notes"] = style["besonderheiten"]
    if style.get("language"):
        config["language"] = style["language"]

    # --- agents ---
    agents = raw.get("agents", {})
    if agents.get("model_override") is not None:
        config["model_override"] = agents["model_override"]
    if agents.get("confidence_threshold") is not None:
        config["confidence_threshold"] = agents["confidence_threshold"]
    if agents.get("max_revision_cycles") is not None:
        config["max_revision_cycles"] = agents["max_revision_cycles"]
    if agents.get("impro_tension_threshold") is not None:
        config["impro_tension_threshold"] = agents["impro_tension_threshold"]
    if agents.get("impro_key_scenes") is not None:
        config["impro_key_scenes"] = agents["impro_key_scenes"]
    if agents.get("scene_budget") is not None:
        config["scene_budget"] = agents["scene_budget"]
    if agents.get("tension_opus_threshold") is not None:
        config["tension_opus_threshold"] = agents["tension_opus_threshold"]

    # --- script_writer ---
    sw = raw.get("script_writer", {})
    if sw.get("batch_treatment") is not None:
        config["batch_treatment"] = sw["batch_treatment"]
    elif sw.get("batch_groesse_treatment") is not None:
        config["batch_treatment"] = sw["batch_groesse_treatment"]
    if sw.get("batch_screenplay") is not None:
        config["batch_screenplay"] = sw["batch_screenplay"]
    elif sw.get("batch_groesse_screenplay") is not None:
        config["batch_screenplay"] = sw["batch_groesse_screenplay"]

    # --- coverage ---
    coverage = raw.get("coverage", {})
    thresholds = coverage.get("verdict_thresholds", {})
    if thresholds.get("recommend") is not None:
        config["verdict_recommend"] = thresholds["recommend"]
    if thresholds.get("consider") is not None:
        config["verdict_consider"] = thresholds["consider"]
    if thresholds.get("pass") is not None:
        config["verdict_pass"] = thresholds["pass"]
    if coverage.get("top_n_issues") is not None:
        config["top_n_issues"] = coverage["top_n_issues"]

    # --- expansion ---
    expansion = raw.get("expansion", {})
    if expansion.get("mode"):
        config["expansion_mode"] = expansion["mode"]
    if expansion.get("composition_targets"):
        config["composition_targets"] = expansion["composition_targets"]

    # --- pacing ---
    pacing = raw.get("pacing", {})
    if pacing.get("expected_variance") is not None:
        config["pacing_expected_variance"] = pacing["expected_variance"]

    return config


def build_style_manifest_from_config(config: Optional[dict] = None) -> dict:
    """Maps flat config fields to a state["style_manifest"] dict.

    Used by ``state_store.init_state`` so the manifest is always populated
    from ``config/projekt.yaml`` even when the caller doesn't build one
    explicitly. Previously the manifest defaulted to ``{}`` and downstream
    agents (Adaptation, Style Validator) fell back to generic defaults.
    """
    if config is None:
        config = load_config()
    return {
        "genre": config.get("genre"),
        "tone": config.get("tone"),
        "reference_films": list(config.get("reference_films", [])),
        "special_notes": config.get("special_notes", ""),
        "language": config.get("language", "English"),
        "pacing_expected_variance": config.get("pacing_expected_variance"),
    }
