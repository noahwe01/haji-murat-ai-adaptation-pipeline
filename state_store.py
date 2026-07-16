"""
STATE STORE
===========
Persistent JSON object — the shared "memory" of all agents.
No agent works with the full source text in context.
Instead: read/write to this common state.

15-Agent architecture (Pipeline v3.2) with backward compatibility:
- State versioning (backup before each phase)
- English keys for new projects, dual-read for old German keys
- Extended fields (casting, voice profiles, coverage, impro material)
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


STATE_FILE = "story_state.json"
STATE_DIR = "state"


def _compat(data: dict, en_key: str, de_key: str, default=None):
    """Backward-compatible read — tries English key first, then German fallback."""
    return data.get(en_key, data.get(de_key, default))


def init_state(story_title: str, style_manifest: Optional[dict] = None, casting: Optional[dict] = None) -> dict:
    """Creates a new empty state for a project (English keys).

    If ``style_manifest`` is None or empty, it is auto-merged from
    ``config/projekt.yaml`` via ``build_style_manifest_from_config``.
    This prevents downstream agents (Adaptation, Style Validator) from
    seeing an empty manifest and falling back to generic defaults.
    """
    Path(STATE_DIR).mkdir(exist_ok=True)

    if not style_manifest:
        from config.loader import build_style_manifest_from_config
        style_manifest = build_style_manifest_from_config()

    state = {
        "meta": {
            "title": story_title,
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "source_language": "en",
            "output_language": "en",
            "target_runtime_minutes": None,
            "scene_budget": None,
            "revision_cycle": 0,
            "source_length_class": None,  # short_story | novella | novel
            "word_count": None,
            "output_mode": "treatment",
            "expansion_mode": None,
        },
        "style_manifest": style_manifest,
        "casting": casting or {},
        "chunks": [],
        "plot": {
            "summary": "",
            "logline": "",
            "acts": [],
            "subplots": [],
            "tension_curve": [],
            "themes": [],
        },
        "characters": {},
        "character_relationships": [],
        "world": {
            "locations": [],
            "timeline": [],
            "time_period": "",
            "atmosphere": "",
            "production_notes": [],
        },
        "reference_context": {},
        "impro_material": {},
        "adapted_scenes": [],
        "continuity_log": [],
        "final_script": "",
        "treatment_text": "",
        "coverage_report": None,
        "revision_history": [],
        "confidence_stats": {
            "mean": None,
            "min": None,
            "max": None,
            "below_threshold": 0,
            "distribution": {},
        },
    }
    save_state(state)
    return state


def load_state() -> dict:
    """Loads state from file. Raises error if not found."""
    if not Path(STATE_FILE).exists():
        raise FileNotFoundError(
            f"No state found. Run project initialization first."
        )
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """Writes state to file. Warns on oversize."""
    content = json.dumps(state, ensure_ascii=False, indent=2)
    size_mb = len(content.encode("utf-8")) / (1024 * 1024)

    if size_mb > 2.0:
        _archive_resolved_issues(state)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def version_state(phase_label: str) -> str:
    """Creates a versioned backup before a phase. Returns backup path."""
    Path(STATE_DIR).mkdir(exist_ok=True)
    backup_path = os.path.join(STATE_DIR, f"story_state_{phase_label}.json")
    if Path(STATE_FILE).exists():
        shutil.copy2(STATE_FILE, backup_path)
    return backup_path


def restore_state(phase_label: str) -> dict:
    """Restores a state from a phase backup."""
    backup_path = os.path.join(STATE_DIR, f"story_state_{phase_label}.json")
    if not Path(backup_path).exists():
        raise FileNotFoundError(f"No backup found for phase '{phase_label}'.")
    with open(backup_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    save_state(state)
    return state


def update_state(key_path: str, value: Any) -> dict:
    """Updates a value in the state via dot-notation.
    Example: update_state("plot.summary", "A chess genius...")
    """
    state = load_state()
    keys = key_path.split(".")
    target = state
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value
    save_state(state)
    return state


def append_to_state(key_path: str, value: Any) -> dict:
    """Appends a value to a list in the state."""
    state = load_state()
    keys = key_path.split(".")
    target = state
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]].append(value)
    save_state(state)
    return state


def get_from_state(key_path: str) -> Any:
    """Reads a value from the state via dot-notation."""
    state = load_state()
    keys = key_path.split(".")
    target = state
    for key in keys:
        target = target[key]
    return target


def detect_source_length_class(word_count: int) -> str:
    """Classifies source text length for adaptive processing.
    Determines the creative challenge (expansion vs. compression).
    Target runtime is ALWAYS 90-120 min (feature length).
    """
    if word_count < 10_000:
        return "short_story"   # → expansion needed
    elif word_count < 50_000:
        return "novella"       # → moderate adaptation
    else:
        return "novel"         # → compression needed


def update_confidence_stats(state: dict) -> dict:
    """Calculates confidence statistics from adapted_scenes."""
    scenes = state.get("adapted_scenes", [])
    if not scenes:
        return state

    scores = [
        _compat(s, "confidence", "konfidenz", 0)
        for s in scenes
        if _compat(s, "confidence", "konfidenz") is not None
    ]
    if not scores:
        return state

    state["confidence_stats"] = {
        "mean": round(sum(scores) / len(scores), 3),
        "min": round(min(scores), 3),
        "max": round(max(scores), 3),
        "below_threshold": sum(1 for s in scores if s < 0.75),
        "distribution": {
            "approved_090_100": sum(1 for s in scores if s >= 0.90),
            "review_075_089": sum(1 for s in scores if 0.75 <= s < 0.90),
            "revise_060_074": sum(1 for s in scores if 0.60 <= s < 0.75),
            "escalate_below_060": sum(1 for s in scores if s < 0.60),
        },
    }
    return state


def log_continuity_issue(issue: str, scene_id: str = "", resolved: bool = False, resolution: str = "") -> None:
    """Logs continuity issues for final review."""
    append_to_state("continuity_log", {
        "timestamp": datetime.now().isoformat(),
        "scene_id": scene_id,
        "issue": issue,
        "resolved": resolved,
        "resolution": resolution,
    })


def log_revision(scene_id: str, revision: int, changed_fields: list, reason: str) -> None:
    """Documents a scene revision."""
    append_to_state("revision_history", {
        "scene_id": scene_id,
        "revision": revision,
        "changed_fields": changed_fields,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    })


def _archive_resolved_issues(state: dict) -> None:
    """Archives resolved continuity issues when state gets too large."""
    resolved = [i for i in state["continuity_log"] if i.get("resolved")]
    if not resolved:
        return

    archive_path = os.path.join(STATE_DIR, "continuity_log_archive.json")
    existing = []
    if Path(archive_path).exists():
        with open(archive_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing.extend(resolved)
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    state["continuity_log"] = [i for i in state["continuity_log"] if not i.get("resolved")]


def strip_chunk_text(state: dict) -> dict:
    """Replaces raw text in chunks with hash + preview after analysis.
    Saves tokens when state is loaded as context.
    Defensive: only strips chunks that have char_start + char_end (Reload-Pfad
    via reload_chunk_text). Chunks ohne diese Felder bleiben unverändert.
    """
    import hashlib
    for chunk in state.get("chunks", []):
        if "text" not in chunk or len(chunk["text"]) <= 100:
            continue
        if "char_start" not in chunk or "char_end" not in chunk:
            # Kein Reconstruction-Pfad → nicht strippen, Datenverlust vermeiden
            continue
        chunk["text_hash"] = hashlib.md5(chunk["text"].encode()).hexdigest()
        chunk["text_preview"] = chunk["text"][:200] + "..."
        del chunk["text"]
    save_state(state)
    return state


def reload_chunk_text(state: dict, chunk_index: int) -> str:
    """Rekonstruiert Chunk-Text aus state["meta"]["source_file"] + char_start/end.

    Verifiziert via text_hash, dass Quelle nicht abweicht. Wirft ValueError bei
    Mismatch (Quelle editiert) oder FileNotFoundError (Pfad weg).
    """
    import hashlib
    chunks = state.get("chunks", [])
    if chunk_index < 0 or chunk_index >= len(chunks):
        raise IndexError(f"chunk_index {chunk_index} out of range (0..{len(chunks)-1})")
    chunk = chunks[chunk_index]
    if "text" in chunk:
        return chunk["text"]
    source_file = state.get("meta", {}).get("source_file")
    if not source_file:
        raise ValueError("state['meta']['source_file'] missing — cannot reconstruct")
    char_start = chunk.get("char_start")
    char_end = chunk.get("char_end")
    if char_start is None or char_end is None:
        raise ValueError(f"chunk {chunk.get('id')} missing char_start/char_end")
    with open(source_file, "r", encoding="utf-8") as f:
        source = f.read()
    restored = source[char_start:char_end].strip()
    expected_hash = chunk.get("text_hash")
    if expected_hash:
        actual = hashlib.md5(restored.encode()).hexdigest()
        if actual != expected_hash:
            raise ValueError(
                f"Hash mismatch chunk {chunk.get('id')}: source may have changed. "
                f"Expected {expected_hash}, got {actual}."
            )
    return restored


def normalize_state_meta_from_config(
    state: dict, config: dict, project_root: Optional[Path] = None
) -> dict:
    """Sync state.meta with project config. Heals drift from older runs
    (e.g. HM-State pre-C.5 had no source_file / wrong length_class).

    Sets:
      - meta.source_file (existence-checked relative to project_root if given)
      - meta.target_runtime_minutes
      - meta.expansion_mode
      - meta.source_length_class — word_count >= 40k overrides novella default
      - meta.adaptation_challenge + meta.expansion_note (derived from length_class)

    Pure: no save_state. Caller controls persistence + backup.
    """
    meta = state.setdefault("meta", {})

    source_file = config.get("source_file")
    if source_file:
        meta["source_file"] = source_file
        if project_root is not None:
            full_path = Path(project_root) / source_file
            if not full_path.exists():
                raise FileNotFoundError(
                    f"source_file {full_path} not found"
                )

    if config.get("target_runtime") is not None:
        meta["target_runtime_minutes"] = config["target_runtime"]

    expansion_mode = config.get("expansion_mode")
    if expansion_mode is not None:
        meta["expansion_mode"] = expansion_mode

    word_count = meta.get("word_count") or 0
    mode_to_class = {
        "short_story_to_feature": "short_story",
        "novella_to_feature": "novella",
        "novel_to_feature": "novel",
    }
    if word_count >= 40_000:
        length_class = "novel"
    elif expansion_mode in mode_to_class:
        length_class = mode_to_class[expansion_mode]
    elif word_count:
        length_class = detect_source_length_class(word_count)
    else:
        length_class = meta.get("source_length_class")

    if length_class:
        meta["source_length_class"] = length_class

    if length_class == "short_story":
        meta["adaptation_challenge"] = "expansion"
        meta["expansion_note"] = (
            "Short story -> feature film: Massive creative expansion needed. "
            "Invent scenes, deepen characters, develop subplots, "
            "expand minor characters, create visual worlds."
        )
    elif length_class == "novella":
        meta["adaptation_challenge"] = "moderate"
        meta["expansion_note"] = (
            "Novella -> feature film: Moderate adaptation needed. "
            "Expand some scenes, strengthen subplots."
        )
    elif length_class == "novel":
        meta["adaptation_challenge"] = "compression"
        meta["expansion_note"] = (
            "Novel -> feature film: Compression needed. "
            "Cut subplots, merge characters, tighten."
        )

    return state


def get_chunk_text_for_prompt(
    state: dict, chunk_index: int, min_chars: int = 100
) -> str:
    """Single source for chunk text in prompt building.

    Wraps reload_chunk_text and enforces min_chars to prevent silent
    empty-string fail in downstream prompts.
    """
    text = reload_chunk_text(state, chunk_index)
    if len(text.strip()) < min_chars:
        raise ValueError(
            f"chunk {chunk_index} text too short ({len(text.strip())} < {min_chars} chars) "
            f"- source_file or chunk metadata may be invalid"
        )
    return text


# ─── KNOWLEDGE GAP TRACKING ──────────────────────────────────────────────────

def log_knowledge_gap(topic: str, context: str = "", agent: str = ""):
    """Logs a knowledge gap — the brain was asked for something it doesn't have."""
    state = load_state()
    gaps = state.setdefault("knowledge_gaps", [])

    # Deduplicate
    for gap in gaps:
        if gap.get("topic") == topic:
            gap["occurrences"] = gap.get("occurrences", 1) + 1
            gap["last_seen"] = datetime.now().isoformat()
            save_state(state)
            return

    gaps.append({
        "topic": topic,
        "context": context,
        "agent": agent,
        "first_seen": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "occurrences": 1,
        "resolved": False,
    })
    save_state(state)


def get_knowledge_gaps(unresolved_only: bool = True) -> list:
    """Returns all knowledge gaps, optionally filtered to unresolved."""
    state = load_state()
    gaps = state.get("knowledge_gaps", [])
    if unresolved_only:
        return [g for g in gaps if not g.get("resolved")]
    return gaps


def resolve_knowledge_gap(topic: str):
    """Marks a knowledge gap as resolved (brain note was created)."""
    state = load_state()
    for gap in state.get("knowledge_gaps", []):
        if gap.get("topic") == topic:
            gap["resolved"] = True
            gap["resolved_at"] = datetime.now().isoformat()
    save_state(state)


def report_knowledge_gaps(verbose: bool = True) -> list:
    """Reports all unresolved knowledge gaps to the user."""
    gaps = get_knowledge_gaps(unresolved_only=True)
    if verbose and gaps:
        print(f"\n{'='*60}")
        print(f"KNOWLEDGE GAPS — Brain notes needed:")
        print(f"{'='*60}")
        for gap in gaps:
            occ = gap.get("occurrences", 1)
            print(f"  [{occ}×] {gap['topic']}")
            if gap.get("context"):
                print(f"       Context: {gap['context'][:80]}")
            if gap.get("agent"):
                print(f"       Needed by: {gap['agent']}")
        print(f"{'─'*60}")
        print(f"  Total gaps: {len(gaps)}")
        print(f"  Action: Create brain notes for these topics,")
        print(f"  then they'll be automatically loaded next run.")
        print(f"{'='*60}\n")
    return gaps


# ─── SCENE GRAPH ─────────────────────────────────────────────────────────────

def build_scene_graph(state: dict = None) -> dict:
    """
    Builds a queryable graph from adapted_scenes. Pure Python, no LLM call.
    Returns dict with character_scenes, location_scenes, character_pairs,
    subplot_scenes, and timeline_sequence.
    """
    if state is None:
        state = load_state()
    scenes = state.get("adapted_scenes", [])

    graph = {
        "character_scenes": {},
        "location_scenes": {},
        "character_pairs": {},
        "subplot_scenes": {},
        "timeline_sequence": [],
    }

    for scene in scenes:
        scene_id = _compat(scene, "scene_id", "szenen_id", "?")
        chars = _compat(scene, "characters", "figuren", [])
        if isinstance(chars, str):
            chars = [chars]
        elif not isinstance(chars, list):
            chars = list(chars) if hasattr(chars, '__iter__') else []
        slug = scene.get("slug", "") or "UNKNOWN"
        subplots = scene.get("subplot_threads", [])
        if isinstance(subplots, str):
            subplots = [subplots]
        elif not isinstance(subplots, list):
            subplots = []
        duration = _compat(scene, "duration_minutes", "dauer_minuten", 2.0)

        # character_scenes
        for char in chars:
            graph["character_scenes"].setdefault(char, []).append(scene_id)

        # location_scenes (normalize slug to base location)
        loc_base = slug.split("—")[0].strip() if "—" in slug else slug.split("-")[0].strip()
        graph["location_scenes"].setdefault(loc_base, []).append(scene_id)

        # character_pairs (all co-occurrences)
        for i, c1 in enumerate(chars):
            for c2 in chars[i + 1:]:
                pair_key = "|".join(sorted([c1, c2]))
                graph["character_pairs"].setdefault(pair_key, []).append(scene_id)

        # subplot_scenes
        for sp in subplots:
            graph["subplot_scenes"].setdefault(sp, []).append(scene_id)

        # timeline
        graph["timeline_sequence"].append({
            "scene_id": scene_id,
            "characters": chars,
            "location": slug,
            "duration_minutes": duration,
        })

    return graph


def save_scene_graph(state: dict = None) -> dict:
    """Builds scene graph and persists it in the state store."""
    if state is None:
        state = load_state()
    graph = build_scene_graph(state)
    state["scene_graph"] = graph
    save_state(state)
    return graph


def get_character_scenes(character_name: str) -> list:
    """Returns scene IDs where a character appears."""
    graph = build_scene_graph()
    return graph["character_scenes"].get(character_name, [])


def get_character_pair_scenes(char1: str, char2: str) -> list:
    """Returns scene IDs where two characters appear together."""
    graph = build_scene_graph()
    pair_key = "|".join(sorted([char1, char2]))
    return graph["character_pairs"].get(pair_key, [])


def get_location_scenes(location: str) -> list:
    """Returns scene IDs at a location (substring match on slug)."""
    graph = build_scene_graph()
    results = []
    location_lower = location.lower()
    for slug, scene_ids in graph["location_scenes"].items():
        if location_lower in slug.lower():
            results.extend(scene_ids)
    return results


def get_subplot_thread(subplot_id: str) -> list:
    """Returns scene IDs belonging to a subplot."""
    graph = build_scene_graph()
    return graph["subplot_scenes"].get(subplot_id, [])


# ─── PHASE E — STATE-VIEWS PRO AGENT ─────────────────────────────────────────
#
# View-Funktionen liefern das minimale State-Subset, das ein Agent für seinen
# Prompt-Bau braucht. Pure Functions: kein I/O, keine Mutation, deterministisch.
# Agents sollen in Phase E/F/G schrittweise von ``load_state()`` auf die
# entsprechende ``build_*_view(state)`` umgestellt werden.
#
# Vertrag:
# - Input: full state dict
# - Output: dict (subset; Agent ruft .get() / direkten Zugriff)
# - Idempotent + side-effect-frei
# - Reduktion ggü. Full-State im Inventar (docs/state-view-inventory.md) belegt


def _slim_style_manifest(style: dict) -> dict:
    """Returns the style fields actually consumed by Coverage / Style /
    Narrative Coherence prompts. Drops verbose nested sub-blocks not used
    in those prompts (e.g. expansion-mode internals belong only to Adaptation).
    """
    if not isinstance(style, dict):
        return {}
    keep = {}
    for key in (
        "genre", "tone", "ton",
        "reference_films", "referenzfilme",
        "language",
        "special_notes", "besonderheiten",
        "logline_seed",
    ):
        if key in style:
            keep[key] = style[key]
    return keep


def _character_summary_compact(characters: dict) -> list:
    """Coverage uses a 1-liner per character: name + role + want + need.
    Voice-Profile internals are not consumed here — drop them entirely.
    """
    rows = []
    for name, data in (characters or {}).items():
        if not isinstance(data, dict):
            continue
        role = _compat(data, "role", "rolle", "?")
        want = data.get("want", "?")
        need = data.get("need", "?")
        rows.append({"name": name, "role": role, "want": want, "need": need})
    return rows


def _scene_for_coverage_render(scene: dict) -> dict:
    """Slims an adapted_scene to only the fields used in the coverage script
    fallback render: scene_id, slug, action, dialog_draft.
    """
    return {
        "scene_id": _compat(scene, "scene_id", "szenen_id", "?"),
        "slug": scene.get("slug", ""),
        "action": _compat(scene, "action", "handlung", ""),
        "dialog_draft": scene.get("dialog_draft", scene.get("dialog_hinweise", [])),
    }


def _scene_for_recent_context(scene: dict) -> dict:
    """Slim a scene to fields used by ``adaptation_agent._get_recent_scenes``:
    scene_id, slug, action (truncated downstream), and dialog_draft first
    entry (used as preview). Drops impro_links, continuity meta, transition,
    confidence, references etc. that are not consumed in recent_scenes
    rendering.
    """
    drafts = scene.get("dialog_draft", scene.get("dialog_hinweise", []))
    return {
        "scene_id": _compat(scene, "scene_id", "szenen_id", "?"),
        "slug": scene.get("slug", ""),
        "action": _compat(scene, "action", "handlung", ""),
        "dialog_draft": (drafts[:1] if isinstance(drafts, list) else drafts) or [],
    }


def _impro_for_chunk(impro: dict, chunk_index: int) -> dict:
    """Returns ONLY the impro entry for this chunk (or {} if none).
    Mirrors the lookup logic from adaptation_agent.build_adaptation_prompt:
    exact chunk_id keys → composite-prefix → numeric-suffix fallback. Pure: no I/O.

    H'' Phase G-5 Track-H A14: composite-key prefix-match. Phase G-4
    External-Builder persisted impro under composite keys like
    `chunk_018_tension_0_85` to embed scene-tension metadata. Without
    prefix-match the strict `chunk_018` lookup misses every G-4 entry,
    causing Phase 5 prompts to fall back to "(No impro material)".
    """
    if not isinstance(impro, dict) or not impro:
        return {}
    chunk_id = f"chunk_{chunk_index + 1:03d}"
    for key in (chunk_id, f"chunk_{chunk_index + 1}", str(chunk_index)):
        if key in impro:
            return {key: impro[key]}
    composite_prefix = f"{chunk_id}_"
    for key, material in impro.items():
        if isinstance(key, str) and key.startswith(composite_prefix):
            return {key: material}
    suffix = f"_{chunk_index + 1}"
    for key, material in impro.items():
        if (
            isinstance(key, str)
            and "_tension_" not in key
            and key.endswith(suffix)
        ):
            return {key: material}
    return {}


def select_chars_for_chunk(state: dict, chunk_index: int,
                           max_chars: int = 12) -> list | None:
    """F.4 Adaptation Micro-Loop char-subset selector.

    Returns a list of character names that the adaptation prompt for
    chunk_index needs voice profiles for. Pure heuristic:
      - chars from state["chunk_character_map"][chunk_id] (set by F.1)
      - + every protagonist (always present)
      - + chars in last 2 adapted_scenes (continuity)

    Returns ``None`` when chunk_character_map carries no entry for this
    chunk_id AND no protagonists are declared — caller falls back to the
    full characters dict (legacy projects without F.1 metadata, e.g.
    Schneesturm pre-F.1 runs). Capped to ``max_chars`` deterministically.
    """
    chunks = state.get("chunks", []) or []
    if chunk_index < 0 or chunk_index >= len(chunks):
        return None
    chunk_id = chunks[chunk_index].get("id", "")
    char_map = state.get("chunk_character_map", {}) or {}
    all_chars = state.get("characters", {}) or {}
    has_chunk_entry = isinstance(char_map, dict) and chunk_id in char_map
    selected: list[str] = []

    if has_chunk_entry:
        for n in char_map.get(chunk_id, []) or []:
            if n in all_chars and n not in selected:
                selected.append(n)

    for name, data in all_chars.items():
        role = _compat(data, "role", "rolle", "")
        if role == "protagonist" and name not in selected:
            selected.append(name)

    for scene in (state.get("adapted_scenes", []) or [])[-2:]:
        for n in _compat(scene, "characters", "figuren", []) or []:
            if n in all_chars and n not in selected:
                selected.append(n)

    if not selected and not has_chunk_entry:
        return None
    return selected[:max_chars]


def build_adaptation_view(state: dict, chunk_index: int,
                          char_id_subset: list | None = None) -> dict:
    """Minimal subset for ``adaptation_agent.build_adaptation_prompt``.

    The Adaptation Agent runs once per chunk (145× per HM full-run). The
    full state is ~250-500 KB — re-loading it every chunk is wasteful.
    This view carries only what the prompt actually injects:

        - characters (subset when char_id_subset is set; full dict otherwise.
          Voice-internal slimming is Phase D's job, this view picks WHO
          rather than WHAT. F.4 caller passes a subset from
          select_chars_for_chunk so the per-chunk char-bible can shrink
          drastically — HM has 30+ named figures total but only 3-6 per
          chunk).
        - style_manifest (slim — only fields used by _build_style_brief)
        - chunk_tension_index entry for this chunk (override decision)
        - force_full_voice_next_chunk flag (override decision)
        - recent adapted scenes (last 2, slimmed to scene_id/slug/action/dialog_draft[0])
        - impro_material entry for THIS chunk only
        - reference_context.adaptation_models (legacy ref fallback)
        - meta.target_runtime_minutes, meta.scene_budget,
          meta.word_count (used by expansion_strategy)
        - chunks_remaining count (NOT the chunks themselves)
        - scenes_done count + minutes_done sum (NOT all adapted_scenes)

    Drops chunks (caller passes ``chunk_text`` arg directly), every
    adapted_scene except the last 2, every impro entry except for this
    chunk, character_extractions, world.*, casting, plot.acts/subplots/etc.
    (Adaptation does not consume them), all coverage / analysis / revision
    outputs, continuity_log, confidence_stats.

    Pure: no I/O, no state mutation, deterministic.
    """
    meta = state.get("meta", {}) or {}
    raw_scenes = state.get("adapted_scenes", []) or []
    raw_chunks = state.get("chunks", []) or []
    raw_impro = state.get("impro_material", {}) or {}
    tension_idx = state.get("chunk_tension_index", {}) or {}
    chunk_id = f"chunk_{chunk_index + 1:03d}"
    chunk_meta = (
        tension_idx.get(chunk_id, {}) if isinstance(tension_idx, dict) else {}
    ) or {}
    minutes_done = sum(
        _compat(s, "duration_minutes", "dauer_minuten", 2) for s in raw_scenes
    )
    all_chars = state.get("characters", {}) or {}
    if char_id_subset is None:
        characters_view = all_chars
    else:
        characters_view = {k: all_chars[k] for k in char_id_subset if k in all_chars}
    return {
        "characters": characters_view,
        "style_manifest": _slim_style_manifest(state.get("style_manifest", {})),
        "chunk_tension": chunk_meta,
        "force_full_voice_next_chunk": bool(
            state.get("force_full_voice_next_chunk")
        ),
        "recent_scenes": [
            _scene_for_recent_context(s) for s in raw_scenes[-2:]
        ],
        "impro_material": _impro_for_chunk(raw_impro, chunk_index),
        "reference_models": (
            (state.get("reference_context") or {}).get("adaptation_models", []) or []
        ),
        "meta": {
            "target_runtime_minutes": meta.get("target_runtime_minutes", 90),
            "scene_budget": meta.get("scene_budget", 50),
            "word_count": meta.get("word_count", "unknown"),
        },
        "scenes_done": len(raw_scenes),
        "minutes_done": minutes_done,
        "chunks_remaining": max(0, len(raw_chunks) - chunk_index - 1),
    }


def _collect_batch_character_ids(batch: list, all_chars: dict) -> list:
    """Returns character names appearing in any scene of the batch.
    Falls back to all known characters if the batch carries no explicit
    'characters' field (legacy scene shape) so voice coverage is never silently
    dropped. Mirror of agents.script_writer._collect_batch_character_ids —
    duplicated here so the view function stays import-cycle-free.
    """
    seen = []
    for scene in batch or []:
        names = _compat(scene, "characters", "figuren", []) or []
        for n in names:
            if n in all_chars and n not in seen:
                seen.append(n)
    if not seen:
        return list(all_chars.keys())
    return seen


def _characters_for_style_context(characters: dict, char_ids: list) -> dict:
    """Returns per-batch-character data needed by ``_build_style_context``:
    only ``role`` + ``rolle`` (lead detection). Voice profile internals,
    arc, want, need, extractions etc. are NOT consumed in style_ctx and are
    dropped to keep the per-batch view minimal.
    """
    out = {}
    for cid in char_ids:
        data = characters.get(cid)
        if not isinstance(data, dict):
            continue
        slim = {}
        if "role" in data:
            slim["role"] = data["role"]
        if "rolle" in data:
            slim["rolle"] = data["rolle"]
        out[cid] = slim
    return out


def build_script_writer_batch_view(
    state: dict, batch_index: int, batch_size: int
) -> dict:
    """Minimal subset for one screenplay batch in
    ``script_writer.build_screenplay_batch_prompts``.

    Returns just the slice the prompt for batch_index will inject:
        - meta.title (+ author resolution falls upstream)
        - style_manifest (slim)
        - plot.themes (only — logline + acts + subplots not used)
        - batch (raw adapted_scenes slice)
        - batch_character_ids (computed via _collect_batch_character_ids)
        - characters_for_style: slim dict (only role / rolle for leads)
        - batch_idx, total_batches, start_id, end_id (driver convenience)

    Drops chunks (no source text needed at this stage), impro_material,
    world.*, casting, character_extractions, voice_profile internals
    (rendered separately via get_voice_profiles_for_prompt), all
    coverage / analysis-layer outputs, revision_history, continuity_log,
    confidence_stats, every adapted_scene OUTSIDE the requested batch.

    Pure: no I/O, no state mutation, deterministic.
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size}")
    raw_scenes = state.get("adapted_scenes", []) or []
    total_batches = max(1, (len(raw_scenes) + batch_size - 1) // batch_size)
    start = batch_index * batch_size
    end = start + batch_size
    batch = raw_scenes[start:end]
    all_chars = state.get("characters", {}) or {}
    char_ids = _collect_batch_character_ids(batch, all_chars)
    plot = state.get("plot", {}) or {}
    meta = state.get("meta", {}) or {}
    return {
        "meta": {
            "title": meta.get("title", ""),
        },
        "style_manifest": _slim_style_manifest(state.get("style_manifest", {})),
        "plot": {"themes": plot.get("themes", []) or []},
        "batch": batch,
        "batch_character_ids": char_ids,
        "characters_for_style": _characters_for_style_context(all_chars, char_ids),
        "batch_idx": batch_index,
        "total_batches": total_batches,
        "scene_count": len(raw_scenes),
    }


def _character_arcs_compact(characters: dict) -> list:
    """Builds the compact arc rows used by Narrative Coherence:
    {name, start, change, end} — drops voice_profile + role + want/need
    + extractions etc. Skips characters with no arc declared.
    """
    rows = []
    for name, data in (characters or {}).items():
        if not isinstance(data, dict):
            continue
        arc = data.get("arc", {})
        if not isinstance(arc, dict) or not arc:
            continue
        rows.append({
            "name": name,
            "start": _compat(arc, "start_state", "ausgangszustand", "?"),
            "change": arc.get("change", "?"),
            "end": _compat(arc, "end_state", "endzustand", "?"),
        })
    return rows


def build_narrative_coherence_view(state: dict) -> dict:
    """Minimal subset for ``narrative_coherence.build_coherence_prompt``.

    Drops chunks, impro_material, world.*, casting, character_extractions,
    voice_profile internals (Narrative Coherence does NOT inject voice
    profiles), revision_history, continuity_log, all OTHER analysis-layer
    outputs (Coverage, Pacing, Subtext, etc. — Narrative Coherence reads
    none of them), confidence_stats.

    Smart script-source selection: same logic as build_coverage_view —
    only the variant actually consumed by the prompt is included.
    Plot kept slim: only themes; logline + acts + subplots not used here.
    """
    plot = state.get("plot", {}) or {}
    style = state.get("style_manifest", {}) or {}
    treatment_text = state.get("treatment_text", "") or ""
    final_script = state.get("final_script", "") or ""
    raw_scenes = state.get("adapted_scenes", []) or []

    needs_scene_fallback = not (final_script or treatment_text)
    scenes_slim = (
        [_scene_for_coverage_render(s) for s in raw_scenes]
        if needs_scene_fallback else []
    )

    return {
        "character_arcs": _character_arcs_compact(state.get("characters", {})),
        "themes": plot.get("themes", []) or [],
        "style_brief": _slim_style_manifest(style),
        "final_script": final_script,
        "treatment_text": treatment_text,
        "adapted_scenes": scenes_slim,
        "scene_count": len(raw_scenes),
    }


def build_analysis_brief(state: dict) -> dict:
    """Phase F.5 — pre-Analysis-Layer briefing.

    Produces a single compact dict the 6 Phase-9.5 analysis agents can read
    instead of (or in addition to) the full screenplay. Goal: each agent's
    prompt fetches its narrow Excerpt-Slice via excerpt_pointers and reads
    the briefing for global structure — no agent re-reads the whole script.

    Schema:
        logline, acts, themes
        scene_index: [{scene_id, slug, characters, words, emotional_core,
                       subplot_threads}]
        scene_count
        character_arcs: [{name, role, want, need, start, change, end}]
        top_risk_scenes: scenes with continuity_score < 0.75 OR confidence < 0.75
        excerpt_pointers: {scene_id: {offset, source}} (offset into final_script
                          when present; readers slice from offset to next
                          scene's offset to recover the per-scene excerpt)
        has_final_script, has_treatment

    Pure: no I/O, no state mutation, deterministic.
    """
    plot = state.get("plot", {}) or {}
    chars = state.get("characters", {}) or {}
    scenes = state.get("adapted_scenes", []) or []
    final_script = state.get("final_script", "") or ""
    treatment = state.get("treatment_text", "") or ""

    scene_index = []
    top_risk = []
    for s in scenes:
        sid = _compat(s, "scene_id", "szenen_id", "?")
        action = _compat(s, "action", "handlung", "") or ""
        dialog = s.get("dialog_draft", s.get("dialog_hinweise", [])) or []
        words = len(action.split())
        for d in dialog:
            if isinstance(d, dict):
                words += len((d.get("line") or "").split())
            elif isinstance(d, str):
                words += len(d.split())
        scene_index.append({
            "scene_id": sid,
            "slug": s.get("slug", ""),
            "characters": _compat(s, "characters", "figuren", []) or [],
            "words": words,
            "emotional_core": s.get("emotional_core", ""),
            "subplot_threads": s.get("subplot_threads", []) or [],
        })
        cresult = s.get("continuity_result", {}) or {}
        conf = _compat(s, "confidence", "konfidenz", 1.0)
        cscore = cresult.get("score", 1.0)
        if cscore < 0.75 or conf < 0.75:
            top_risk.append({
                "scene_id": sid,
                "continuity_score": cscore,
                "confidence": conf,
                "flags": (cresult.get("flags", []) or [])[:3],
            })

    char_arcs = []
    for name, data in chars.items():
        if not isinstance(data, dict):
            continue
        arc = data.get("arc") or {}
        char_arcs.append({
            "name": name,
            "role": _compat(data, "role", "rolle", "?"),
            "want": data.get("want", "?"),
            "need": data.get("need", "?"),
            "start": _compat(arc, "start_state", "ausgangszustand", "?"),
            "change": arc.get("change", "?"),
            "end": _compat(arc, "end_state", "endzustand", "?"),
        })

    excerpt_pointers: dict = {}
    if final_script:
        for s in scenes:
            sid = _compat(s, "scene_id", "szenen_id", "")
            slug = s.get("slug", "")
            if not sid or not slug:
                continue
            idx = final_script.find(slug)
            if idx >= 0:
                excerpt_pointers[sid] = {"offset": idx, "source": "final_script"}

    return {
        "logline": plot.get("logline", ""),
        "acts": plot.get("acts", []) or [],
        "themes": plot.get("themes", []) or [],
        "scene_index": scene_index,
        "scene_count": len(scenes),
        "character_arcs": char_arcs,
        "top_risk_scenes": top_risk,
        "excerpt_pointers": excerpt_pointers,
        "has_final_script": bool(final_script),
        "has_treatment": bool(treatment),
    }


def excerpt_for_scene(state: dict, scene_id: str,
                      max_chars: int = 1500) -> str:
    """F.5 helper for analysis agents: returns the slice of final_script that
    corresponds to scene_id, sized to max_chars. Slice runs from this scene's
    offset to the next scene's offset (or +max_chars cap, whichever is less).

    Falls back to "" when no analysis_brief is set, no excerpt_pointers
    entry exists, or no final_script is persisted.
    """
    brief = state.get("analysis_brief")
    if not isinstance(brief, dict):
        return ""
    pointers = brief.get("excerpt_pointers", {}) or {}
    final_script = state.get("final_script", "") or ""
    if not final_script:
        return ""
    entry = pointers.get(scene_id)
    if not isinstance(entry, dict):
        return ""
    offset = entry.get("offset", -1)
    if offset < 0 or offset >= len(final_script):
        return ""
    next_offset = len(final_script)
    for sid, e in pointers.items():
        if sid == scene_id:
            continue
        o = (e or {}).get("offset", -1)
        if isinstance(o, int) and offset < o < next_offset:
            next_offset = o
    end = min(offset + max_chars, next_offset)
    return final_script[offset:end]


def build_coverage_view(state: dict) -> dict:
    """Minimal subset for ``coverage_agent.build_coverage_prompt``.

    Drops chunks, impro_material, world.*, casting, character_extractions,
    confidence_stats, all analysis-layer outputs, revision_history,
    continuity_log, voice_profile internals (only role/want/need are used).

    Smart script-source selection: the prompt only uses ONE of
    treatment_text / final_script / adapted_scenes-fallback. The view
    therefore only includes the relevant source:
      - revision_cycle > 0 → adapted_scenes (slimmed)
      - else treatment_text if non-empty → treatment_text only
      - else final_script if non-empty → final_script only
      - else adapted_scenes (slimmed) for fallback render

    Returns a dict the caller (build_coverage_prompt) can read instead of
    the full state. Pure function: no load/save.
    """
    meta = state.get("meta", {}) or {}
    plot = state.get("plot", {}) or {}
    revision_cycle = meta.get("revision_cycle", 0) or 0
    treatment_text = state.get("treatment_text", "") or ""
    final_script = state.get("final_script", "") or ""
    raw_scenes = state.get("adapted_scenes", []) or []

    needs_scene_fallback = (
        revision_cycle > 0 or (not treatment_text and not final_script)
    )
    scenes_slim = (
        [_scene_for_coverage_render(s) for s in raw_scenes]
        if needs_scene_fallback else []
    )

    return {
        "meta": {
            "title": meta.get("title", ""),
            "target_runtime_minutes": meta.get("target_runtime_minutes"),
            "revision_cycle": revision_cycle,
        },
        "style_manifest": _slim_style_manifest(state.get("style_manifest", {})),
        "logline": plot.get("logline", ""),
        "characters_compact": _character_summary_compact(state.get("characters", {})),
        "treatment_text": "" if revision_cycle > 0 else treatment_text,
        "final_script": "" if revision_cycle > 0 else final_script,
        "adapted_scenes": scenes_slim,
        "scene_count": len(raw_scenes),
    }
