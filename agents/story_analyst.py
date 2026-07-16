"""
STORY ANALYST
=============
Reads all chunks sequentially and builds a complete
narrative structure — stored in the State Store.

Tasks:
  - Extract three-act structure
  - Identify all characters + initial character profiles
  - Map subplots & motifs
  - Emotional tension curve per scene
  - Themes & symbolism
  - Subplot priority (how cinematic is each subplot?)
  - Filmability score (how visually translatable is each chunk?)
  - Logline generation

Memory strategy:
  - Processes chunk by chunk
  - Accumulates findings in the State Store
  - Uses state summary as "memory" for the next chunk
"""

import json
import re
from state_store import (
    load_state, save_state, update_state,
    append_to_state, log_continuity_issue, log_knowledge_gap, _compat
)
from decision_log import build_criteria_instruction, log_decisions_from_block
from utils.schema_caps import apply_caps, record_findings


# ─── SYSTEM PROMPT ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Story Analyst for film projects. You analyze texts
from a novel or short story piece by piece and extract the dramaturgical
structure for a later cinematic adaptation.

You work with a persistent State Store. For each chunk you receive:
1. The current chunk text
2. The current state (what you have already analyzed)

ACCUMULATED ANALYSIS SO FAR:
<<MEMORY_SUMMARY>>

TASK PER CHUNK:
- Identify new characters, locations, plot elements
- Assign to an act (1=Introduction/Setup, 2=Confrontation, 3=Resolution)
- Rate tension intensity (0.0 = calm, 1.0 = climax)
- Identify subplots and motifs
- Detect contradictions or gaps

<<MODE_DIRECTIVE>>

OUTPUT: Always as valid JSON — no text before or after.
Format:
{
  "new_characters": [{"name": "", "initial_description": "", "role": "protagonist|antagonist|supporting"}],
  "active_characters": [""],
  "plot_elements": [{"description": "", "act": 1, "subplot_id": null}],
  "new_locations": [{"name": "", "description": ""}],
  "tension": 0.5,
  "act_estimation": 1,
  "filmability_score": 0.7,
  "theme_hints": [""],
  "symbols": [""],
  "notes": ""
}

`active_characters`: ALL named characters present or referenced in this chunk
(speaking, acting, observed, or named). Use canonical names exactly as
introduced previously (or as you introduce them in `new_characters`).
This list MUST include every previously-known character that appears in
the chunk — not just new ones. Required for downstream voice-profile
selection (per-chunk char-bible). If a character is only obliquely
referenced (mentioned in passing without dramatic weight), omit them.

Filmability score rating (0.0-1.0):
- 1.0 = Purely visual, immediately filmable (action, dialogue, physical action)
- 0.7 = Mostly visual, some inner experience to translate
- 0.4 = Lots of inner monologue, descriptions, abstract reflection
- 0.1 = Purely abstract, philosophical, barely translatable to film"""


# ─── MODE DIRECTIVES ──────────────────────────────────────────────────────────
# Injected into SYSTEM_PROMPT via <<MODE_DIRECTIVE>> based on expansion_mode.

COMPRESSION_DIRECTIVE = """ADAPTATION MODE: Novel -> Feature (Compression).
In ADDITION to the task above, for this chunk you MUST also identify:

1. FUSION CANDIDATES — named characters who share narrative function (role,
   "side", purpose, thematic echo). Real historical figures are anchors —
   do NOT fuse them into other characters; fictional figures can be fused
   around them.

2. CUTTABLE MATERIAL — subplots, authorial digressions, minor character arcs
   that are NOT load-bearing for the central protagonist's trajectory.
   Be bold: compression means cutting.

3. REFOCALIZATION — scenes where the novel shifts POV away from the central
   protagonist. Flag these so the film can either cut them, restage them
   through the protagonist's eyes, or reframe them as events the protagonist
   later learns of.

Extend the output JSON with THREE additional top-level fields:
  "fusion_candidates": [{"chars": ["X", "Y"], "reason": "both serve as ..."}],
  "cuttable": [{"element": "...", "reason": "non-load-bearing subplot"}],
  "refocalize": [{"scene": "...", "current_pov": "...", "recommended_pov": "..."}]
"""


# ─── MAIN FUNCTION ────────────────────────────────────────────────────────────

def run_story_analyst(chunk_results: list, verbose: bool = True,
                      raw_outputs: list | None = None) -> None:
    """
    Main function: Processes all chunks and builds the story state.

    Phase F.1: thin wrapper around the per-chunk micro-loop. Iterates
    ``run_story_analyst_chunk`` for each result and finalizes via
    ``finalize_story_analyst``. Source-compatible with pre-F.1 callers.

    chunk_results: List of analysis dicts (one per chunk), provided by Claude Code.
    raw_outputs:   Optional list of raw subagent-output strings (JSON + DECISIONS
                   block). When provided, each chunk's DECISIONS block is parsed
                   and written to output/adaptation_log.json. Index-aligned with
                   chunk_results. Optional so existing callers (Schneesturm,
                   older dispatchers) remain source-compatible.
    """
    state = load_state()
    chunks = state.get("chunks", [])

    if not chunks:
        raise ValueError("No chunks in state. Run main.py step 1 first.")

    total = len(chunks)
    print(f"\n{'='*60}")
    print(f"STORY ANALYST starting — {total} chunks to analyze")
    print(f"{'='*60}\n")

    reset_story_analyst_progress()

    for i, _chunk in enumerate(chunks):
        result = chunk_results[i] if i < len(chunk_results) else None
        raw = (
            raw_outputs[i]
            if raw_outputs is not None and i < len(raw_outputs)
            else None
        )
        run_story_analyst_chunk(i, result, raw_output=raw, verbose=verbose)

    finalize_story_analyst(verbose=verbose)


# ─── PHASE F.1 — MICRO-LOOP API ───────────────────────────────────────────────
# Per-chunk processing with progress persisted in state["story_analyst_progress"].
# Each step is reset-fähig: a session crash between chunks loses only the
# in-flight chunk_result (already in raw_output if persisted by caller).
#
# State shape:
#   state["story_analyst_progress"] = {
#       "chunks_done": [int, ...],          # processed chunk indices
#       "plot_elements": [...],             # accumulated, with chunk_id
#       "tension_curve": [{chunk_id, position, tension}, ...],
#       "themes": [str, ...],               # set rendered as sorted list
#       "symbols": [str, ...],
#       "fusion_candidates": [...],
#       "cuttable": [...],
#       "refocalize": [...],
#       "locations": {name: description},
#   }
# Sibling write paths (live during loop, used downstream):
#   state["characters"]                     # incremental ingest
#   state["chunk_tension_index"][chunk_id]  # F.4 Adaptation override decision
#   state["chunk_character_map"][chunk_id]  # F.4 char-subset selection


def _empty_progress() -> dict:
    return {
        "chunks_done": [],
        "plot_elements": [],
        "tension_curve": [],
        "themes": [],
        "symbols": [],
        "fusion_candidates": [],
        "cuttable": [],
        "refocalize": [],
        "locations": {},
    }


def reset_story_analyst_progress() -> dict:
    """Clears the per-chunk accumulator. Idempotent."""
    state = load_state()
    state["story_analyst_progress"] = _empty_progress()
    state.setdefault("characters", {})
    state["chunk_tension_index"] = {}
    state["chunk_character_map"] = {}
    save_state(state)
    return state


def get_story_analyst_progress() -> dict:
    """Reads current accumulator. Initializes if absent (back-compat for
    older states without the key)."""
    state = load_state()
    prog = state.get("story_analyst_progress")
    if not isinstance(prog, dict):
        prog = _empty_progress()
        state["story_analyst_progress"] = prog
        save_state(state)
    return prog


def run_story_analyst_chunk(
    chunk_index: int,
    chunk_result: dict | None,
    raw_output: str | None = None,
    verbose: bool = True,
) -> dict:
    """
    Phase F.1 micro-loop step: ingest a single chunk's analysis result.

    Side-effects (all persisted to state via save_state):
      - characters dict updated (new chars added, known chars get arc_note)
      - story_analyst_progress accumulator extended
      - chunk_tension_index[chunk_id] = {tension, is_key_scene}
      - chunk_character_map[chunk_id] = [char_names_present_or_introduced]
      - DECISIONS logged (write-only) when raw_output provided

    Returns a small status dict — useful for orchestration / progress UI.
    Reset-fähig: repeating execution for the same chunk_index is a no-op.
    """
    state = load_state()
    chunks = state.get("chunks", [])
    if chunk_index >= len(chunks):
        raise IndexError(f"chunk_index {chunk_index} out of range (have {len(chunks)})")

    chunk = chunks[chunk_index]
    progress = state.get("story_analyst_progress")
    if not isinstance(progress, dict):
        progress = _empty_progress()
        state["story_analyst_progress"] = progress

    if chunk_index in progress["chunks_done"]:
        if verbose:
            print(f"  [F.1] chunk {chunk_index+1} already processed — skip")
        return {
            "chunk_index": chunk_index,
            "status": "already_done",
            "characters_known": len(state.get("characters", {})),
        }

    if chunk_result is None:
        log_continuity_issue(f"Chunk {chunk['id']}: Analysis failed")
        progress["chunks_done"].append(chunk_index)
        save_state(state)
        if verbose:
            print(f"  [F.1] chunk {chunk_index+1}: no result — logged + skipped")
        return {
            "chunk_index": chunk_index,
            "status": "missing_result",
            "characters_known": len(state.get("characters", {})),
        }

    # Q1.5 Schema-Caps: hard-cut on input lists/strings before ingest.
    cap_findings = apply_caps(chunk_result, "story_analyst", mode="hard")
    if cap_findings:
        record_findings(state, agent="story_analyst", phase="1_analysis", findings=cap_findings)

    characters = state.setdefault("characters", {})
    chunk_id = chunk["id"]

    # Track which chars touch this chunk (for F.4 char-subset slim).
    # G.1a fix: union of new_characters AND active_characters; pre-G.1a runs
    # filled this only with new_characters, leaving the protagonist absent
    # from every chunk after his introduction (F.4 fell back to default).
    chars_in_chunk: list[str] = []

    for fig in _compat(chunk_result, "new_characters", "neue_figuren", []):
        name = fig["name"]
        if name not in characters:
            characters[name] = {
                "name": name,
                "initial_description": _compat(
                    fig, "initial_description", "erstbeschreibung", ""
                ),
                "role": _compat(fig, "role", "rolle", "supporting"),
                "first_mention_chunk": chunk_id,
                "arc_notes": [],
            }
        else:
            characters[name]["arc_notes"].append(
                f"Chunk {chunk_id}: "
                f"{_compat(fig, 'initial_description', 'erstbeschreibung', '')}"
            )
        if name not in chars_in_chunk:
            chars_in_chunk.append(name)

    for active_name in chunk_result.get(
        "active_characters", chunk_result.get("aktive_figuren", [])
    ) or []:
        if not isinstance(active_name, str):
            continue
        active_name = active_name.strip()
        if not active_name:
            continue
        if active_name not in chars_in_chunk:
            chars_in_chunk.append(active_name)
        # A7-fix: seed minimal state.characters entry if subagent referenced
        # this name only in active_characters (never in new_characters). Without
        # this, hochfrequente chars wie Shamil/Butler/Nicholas I fielen aus
        # state.characters trotz hoher chunk-Präsenz.
        if active_name not in characters:
            characters[active_name] = {
                "name": active_name,
                "initial_description": "",
                "role": "supporting",
                "first_mention_chunk": chunk_id,
                "arc_notes": [],
                "_seeded_from": "active_characters_fallback",
            }

    for element in _compat(chunk_result, "plot_elements", "handlungselemente", []):
        element["chunk_id"] = chunk_id
        element["position"] = chunk["position"]
        progress["plot_elements"].append(element)

    for loc in _compat(chunk_result, "new_locations", "neue_orte", []):
        loc_name = loc["name"]
        loc_desc = _compat(loc, "description", "beschreibung", "")
        if loc_name not in progress["locations"]:
            progress["locations"][loc_name] = loc_desc

    tension = _compat(chunk_result, "tension", "spannung", 0.5)
    progress["tension_curve"].append({
        "chunk_id": chunk_id,
        "position": chunk["position"],
        "tension": tension,
    })

    # Theme/symbol accumulation as deduped list (sorted at finalize)
    theme_set = set(progress["themes"])
    theme_set.update(
        chunk_result.get("theme_hints", chunk_result.get("themen_hinweise", []))
    )
    progress["themes"] = sorted(t for t in theme_set if t)

    sym_set = set(progress["symbols"])
    sym_set.update(chunk_result.get("symbols", chunk_result.get("symbole", [])))
    progress["symbols"] = sorted(s for s in sym_set if s)

    for fc in chunk_result.get("fusion_candidates", []):
        fc["chunk_id"] = chunk_id
        progress["fusion_candidates"].append(fc)
    for cut in chunk_result.get("cuttable", []):
        cut["chunk_id"] = chunk_id
        progress["cuttable"].append(cut)
    for rf in chunk_result.get("refocalize", []):
        rf["chunk_id"] = chunk_id
        progress["refocalize"].append(rf)

    # F.4 hand-off: tension index + character map
    is_key = bool(tension and float(tension) > 0.7)
    state.setdefault("chunk_tension_index", {})[chunk_id] = {
        "tension": float(tension),
        "is_key_scene": is_key,
    }
    state.setdefault("chunk_character_map", {})[chunk_id] = chars_in_chunk

    progress["chunks_done"].append(chunk_index)

    # Phase-K compaction at every Nth chunk
    n = len(progress["chunks_done"])
    total = len(chunks)
    if n % _COMPACT_TRIGGER_EVERY == 0 and n < total:
        before = len(progress["plot_elements"])
        progress["plot_elements"] = _compact_plot_elements(progress["plot_elements"])
        state["characters"] = _compact_arc_notes(characters)
        if verbose and len(progress["plot_elements"]) < before:
            print(
                f"     [compaction @ chunk {n}] plot_elements "
                f"{before} → {len(progress['plot_elements'])}"
            )

    save_state(state)

    if raw_output:
        logged = log_decisions_from_block(
            agent_output=raw_output,
            agent="story_analyst",
            phase="1_deep_analysis",
        )
        if verbose and logged:
            print(f"     → {logged} decision(s) logged")

    if verbose:
        bar = "█" * int(tension * 10) + "░" * (10 - int(tension * 10))
        new_chars = _compat(chunk_result, "new_characters", "neue_figuren", [])
        print(
            f"  [F.1] chunk {chunk_index+1}/{total} [{chunk['position']}]  "
            f"Tension: [{bar}] {tension:.1f}  +{len(new_chars)} chars"
        )

    return {
        "chunk_index": chunk_index,
        "status": "ok",
        "tension": float(tension),
        "is_key_scene": is_key,
        "characters_in_chunk": chars_in_chunk,
        "characters_known": len(state.get("characters", {})),
    }


def _append_dedupe_gap(state: dict, topic: str, context: str) -> None:
    """In-place knowledge_gaps append — avoids clobbering unsaved state.
    log_knowledge_gap does its own load+save which would revert in-flight
    dedupe merges held only in memory. Inline append + dedupe by topic.
    """
    from datetime import datetime as _dt
    gaps = state.setdefault("knowledge_gaps", [])
    for g in gaps:
        if g.get("topic") == topic:
            g["occurrences"] = g.get("occurrences", 1) + 1
            g["last_seen"] = _dt.now().isoformat()
            return
    now = _dt.now().isoformat()
    gaps.append({
        "topic": topic,
        "context": context,
        "agent": "story_analyst",
        "first_seen": now,
        "last_seen": now,
        "occurrences": 1,
        "resolved": False,
    })


def _canonical_char_key(name: str) -> str:
    """Lowercase, strip parens-clarifications, collapse whitespace.

    Used by G.1b dedupe to group near-duplicate names. Pure, deterministic.
    """
    s = re.sub(r"\([^)]*\)", "", name).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _dedupe_characters(state: dict, verbose: bool = True) -> tuple[dict, list]:
    """G.1b char-dedupe pass.

    Two heuristics, conservative — alias the duplicate, never silently drop:

    1. Parens-clarification rule: "Woman of the house (Sado's Wife)" gets
       folded into "Sado's Wife" when the inner-parens form exists as a
       standalone character with matching role.

    2. Canonical-key collision: two distinct names with identical
       _canonical_char_key (e.g. trailing-space variants) AND matching role
       are folded; the earlier-introduced canonical name wins (lowest
       first_mention_chunk index, lexical tiebreak).

    Role mismatches are NEVER folded — they're logged via
    log_knowledge_gap so the user can decide post-run. arc_notes from the
    duplicate are appended to the canonical entry; chunk_character_map
    entries are rewritten to point at the canonical name.
    """
    characters = state.get("characters", {}) or {}
    if len(characters) < 2:
        return state, []

    merges: list[tuple[str, str]] = []  # (alias_dropped, canonical_kept)

    # Pass 1 — parens-clarification rule
    for name in list(characters.keys()):
        if name not in characters:
            continue
        m = re.search(r"\(([^)]+)\)", name)
        if not m:
            continue
        inner = m.group(1).strip()
        target = None
        for other in characters:
            if other == name:
                continue
            if other.lower() == inner.lower() or _canonical_char_key(other) == inner.lower():
                target = other
                break
        if not target:
            continue
        alias_data = characters[name]
        canon = characters[target]
        a_role = _compat(alias_data, "role", "rolle", "")
        c_role = _compat(canon, "role", "rolle", "")
        if a_role and c_role and a_role != c_role:
            _append_dedupe_gap(state,
                f"char_dedupe_role_conflict:{name}|{target}",
                f"roles differ: {a_role} vs {c_role}")
            continue
        canon.setdefault("aliases", [])
        if name not in canon["aliases"]:
            canon["aliases"].append(name)
        canon["arc_notes"] = (
            list(canon.get("arc_notes", []))
            + list(alias_data.get("arc_notes", []))
        )
        del characters[name]
        merges.append((name, target))

    # Pass 2 — canonical-key collisions (non-parens variants)
    by_canon: dict[str, list[str]] = {}
    for name in characters:
        by_canon.setdefault(_canonical_char_key(name), []).append(name)
    for canon_key, names in by_canon.items():
        if len(names) < 2:
            continue
        # Pick canonical: lowest first_mention_chunk, then lexical
        def _sort_key(n: str):
            d = characters[n]
            fm = d.get("first_mention_chunk", "zzz")
            return (str(fm), n)
        names_sorted = sorted(names, key=_sort_key)
        canon_name = names_sorted[0]
        canon = characters[canon_name]
        for dup_name in names_sorted[1:]:
            if dup_name not in characters:
                continue
            dup = characters[dup_name]
            d_role = _compat(dup, "role", "rolle", "")
            c_role = _compat(canon, "role", "rolle", "")
            if d_role and c_role and d_role != c_role:
                _append_dedupe_gap(state,
                    f"char_dedupe_role_conflict:{dup_name}|{canon_name}",
                    f"roles differ: {d_role} vs {c_role}")
                continue
            canon.setdefault("aliases", [])
            if dup_name not in canon["aliases"]:
                canon["aliases"].append(dup_name)
            canon["arc_notes"] = (
                list(canon.get("arc_notes", []))
                + list(dup.get("arc_notes", []))
            )
            del characters[dup_name]
            merges.append((dup_name, canon_name))

    # Rewrite chunk_character_map references
    if merges:
        alias_map = {a: c for a, c in merges}
        char_map = state.get("chunk_character_map", {}) or {}
        for chunk_id, names in char_map.items():
            rewritten: list[str] = []
            for n in names or []:
                target = alias_map.get(n, n)
                if target not in rewritten:
                    rewritten.append(target)
            char_map[chunk_id] = rewritten

    if verbose and merges:
        print(f"  [G.1b] dedupe: {len(merges)} alias(es) merged")
        for a, c in merges:
            print(f"     '{a}' → '{c}'")

    state["characters"] = characters
    return state, merges


def finalize_story_analyst(verbose: bool = True) -> dict:
    """
    Phase F.1 finalize: derives acts, themes, locations, subplots from the
    accumulator and marks Phase 1 complete. Strips chunk text (C.5).
    G.1b: runs char-dedupe pass before deriving acts.
    """
    state = load_state()
    state, _dedupe_merges = _dedupe_characters(state, verbose=verbose)
    progress = state.get("story_analyst_progress") or _empty_progress()
    chunks = state.get("chunks", [])
    total = len(chunks)
    plot_elements = progress["plot_elements"]
    tension_curve = progress["tension_curve"]
    themes = progress["themes"]
    symbols = progress.get("symbols", [])
    locations = progress["locations"]
    fusion_candidates = progress["fusion_candidates"]
    cuttable_material = progress["cuttable"]
    refocalize_scenes = progress["refocalize"]

    acts = _derive_acts(plot_elements, tension_curve, total)

    state["plot"]["acts"] = acts
    state["plot"]["tension_curve"] = [t["tension"] for t in tension_curve]
    state["plot"]["themes"] = list(themes)
    state["plot"]["symbols"] = list(symbols)
    state["plot"]["subplots"] = _extract_subplots(plot_elements)
    state["world"]["locations"] = [
        {"name": k, "description": v} for k, v in locations.items()
    ]

    state["adaptation_hints"] = {
        "fusion_candidates": fusion_candidates,
        "cuttable": cuttable_material,
        "refocalize": refocalize_scenes,
    }

    state["meta"]["status"] = "analyzed"
    save_state(state)

    from state_store import strip_chunk_text
    state = strip_chunk_text(state)

    chars_count = len(state.get("characters", {}))
    if verbose:
        print(f"\n{'='*60}")
        print(f"STORY ANALYST complete:")
        print(f"  Characters:        {chars_count}")
        print(f"  Plot elements:     {len(plot_elements)}")
        print(f"  Locations:         {len(locations)}")
        print(f"  Themes:            {len(themes)}")
        print(f"  Acts:              {len(acts)}")
        if fusion_candidates or cuttable_material or refocalize_scenes:
            print(f"  Fusion candidates: {len(fusion_candidates)}")
            print(f"  Cuttable items:    {len(cuttable_material)}")
            print(f"  Refocalize scenes: {len(refocalize_scenes)}")
        print(f"{'='*60}\n")

    return {
        "characters": chars_count,
        "plot_elements": len(plot_elements),
        "locations": len(locations),
        "themes": len(themes),
        "acts": len(acts),
        "fusion_candidates": len(fusion_candidates),
        "cuttable": len(cuttable_material),
        "refocalize": len(refocalize_scenes),
    }


# ─── PUBLIC API ──────────────────────────────────────────────────────────────

def build_analysis_prompt(chunk_text: str, chunk_index: int,
                          characters: dict, plot_elements: list,
                          total_chunks: int,
                          themes=None) -> tuple:
    """
    Builds the analysis prompt with accumulated memory for a single chunk.
    Returns (system_prompt, user_message) tuple for the LLM call.

    Mode-aware: at expansion_mode == "novel_to_feature", adds the
    COMPRESSION_DIRECTIVE that requests fusion_candidates, cuttable,
    refocalize fields in the output JSON, and — when a pre-computed
    character graph exists — injects graph-derived hints (protagonists,
    historical anchors, fusion candidates, cuttable minors) so the
    agent works WITH the graph-analysis, not against it.

    Memory-Summary is hard-capped (≤ 800 Tokens, Phase K). `themes` is
    optional — pass an iterable of theme strings to include the themes
    line; legacy callers without themes-tracking remain source-compatible.
    """
    from utils.skill_loader import load_skills_for_agent
    from config.loader import load_config
    config = load_config()

    memory = _build_memory_summary(characters, plot_elements,
                                    chunk_index, total_chunks,
                                    themes=themes)
    skills = load_skills_for_agent("story_analyst")

    mode = config.get("expansion_mode")
    directive = COMPRESSION_DIRECTIVE if mode == "novel_to_feature" else ""

    system = SYSTEM_PROMPT.replace("<<MEMORY_SUMMARY>>", memory)
    system = system.replace("<<MODE_DIRECTIVE>>", directive)

    # Brain-Hook: inject graph context (characters + locations + plotlines)
    # Compression mode only — Schneesturm/expansion projects get no block.
    if mode == "novel_to_feature":
        graph_block = _build_graph_context_block()
        if graph_block:
            system += "\n\n" + graph_block
        loc_block = _build_location_context_block()
        if loc_block:
            system += "\n\n" + loc_block
        plot_block = _build_plotline_context_block()
        if plot_block:
            system += "\n\n" + plot_block

    # Criteria injection — agent cites rule IDs in the DECISIONS block.
    # Placed after graph hints (facts) so criteria (heuristics) come last.
    try:
        system += "\n\n" + build_criteria_instruction()
    except FileNotFoundError:
        pass

    if skills:
        system += f"\n\n{skills}"
    user_msg = f"CHUNK {chunk_index + 1}/{total_chunks}:\n\n{chunk_text}"
    return system, user_msg


def _build_graph_context_block(
    fusion_threshold: float = 0.8,
    max_fusion: int = 12,
    max_cuttable: int = 15,
    max_historical: int = 12,
) -> str:
    """Load the pre-computed character graph and render it as a prompt block.

    Returns "" if the graph is unavailable (e.g. Graphify hasn't run yet, or
    the project isn't using compression mode). Silent fallback — never crash
    the pipeline for a missing pre-processor output.
    """
    try:
        from utils.graph_query import load_character_graph
        g = load_character_graph()
    except (FileNotFoundError, ImportError, Exception):
        return ""

    protagonists = g.characters_by_function("protagonist")
    antagonists = g.characters_by_function("antagonist")
    historical = [n for n in g.nodes if n.get("historical")]
    fusion = g.query_fusion_candidates(fusion_threshold)
    cuttable = g.cuttable_characters(max_weight=3.0, exclude_historical=True)

    lines = [
        "=== PRE-COMPUTED ADAPTATION GRAPH ===",
        "(from T1.3 Graphify preprocessor — use as hints, confirm or override per chunk)",
        "",
        f"Graph stats: {len(g.nodes)} characters, {len(g.edges)} co-appearance edges, "
        f"{len(g.fusion_candidates)} fusion candidates total.",
        "",
    ]

    if protagonists:
        lines.append("PROTAGONIST(S) — central figure(s), do NOT cut or fuse:")
        for p in protagonists:
            lines.append(
                f"  - {p['canonical_name']} "
                f"(dramatic_weight={p.get('dramatic_weight', '?')}, "
                f"appearances={len(p.get('appearances', []))} chapters)"
            )
        lines.append("")

    if antagonists:
        lines.append("ANTAGONIST(S) — do NOT cut:")
        for a in antagonists[:5]:
            lines.append(f"  - {a['canonical_name']}")
        lines.append("")

    if historical:
        lines.append(
            f"HISTORICAL FIGURES ({len(historical)} total) — NEVER fuse, "
            f"NEVER cut (factual weight):"
        )
        for h in historical[:max_historical]:
            lines.append(f"  - {h['canonical_name']}")
        if len(historical) > max_historical:
            lines.append(f"  ... +{len(historical) - max_historical} more")
        lines.append("")

    if fusion:
        lines.append(
            f"PRE-IDENTIFIED FUSION CANDIDATES (confidence ≥ {fusion_threshold}):"
        )
        lines.append(
            "Add these to your `fusion_candidates` output when the chunk "
            "confirms them; skip if the chunk shows them as distinct."
        )
        for fc in fusion[:max_fusion]:
            chars = " + ".join(fc.get("characters", []))
            reason = (fc.get("reason", "") or "")[:120]
            conf = float(fc.get("confidence", 0))
            lines.append(f"  - [{conf:.2f}] {chars} — {reason}")
        lines.append("")

    if cuttable:
        lines.append(
            f"CUTTABLE CANDIDATES — low dramatic_weight, non-historical "
            f"(top {min(max_cuttable, len(cuttable))} of {len(cuttable)}):"
        )
        lines.append(
            "Flag these in your `cuttable` output when they appear in the chunk."
        )
        for c in cuttable[:max_cuttable]:
            lines.append(
                f"  - {c['canonical_name']} "
                f"(weight={c.get('dramatic_weight', '?')})"
            )
        lines.append("")

    lines.append("=== END GRAPH CONTEXT ===")
    return "\n".join(lines)


def _build_location_context_block(
    top_cinematic: int = 10,
    max_compressible: int = 10,
) -> str:
    """Render pre-computed location graph as prompt hints. Silent-fallback."""
    try:
        from utils.graph_query import load_location_graph
        g = load_location_graph()
    except (FileNotFoundError, ImportError, Exception):
        return ""

    stats = g.stats or {}
    by_type = stats.get("by_type", {})
    non_comp = [n for n in g.nodes if not n.get("compressible")]
    comp = g.compressible()
    top = g.top_cinematic(top_cinematic)

    lines = [
        "=== LOCATION GRAPH (T1.3 Session 2) ===",
        "",
        f"{len(g.nodes)} locations, {len(g.transitions)} transitions. "
        f"Types: {by_type}.",
        f"Compression target: {len(comp)} compressible, {len(non_comp)} anchors.",
        "",
        f"TOP {top_cinematic} CINEMATIC LOCATIONS (must survive as setpieces):",
    ]
    for n in top:
        chs = ",".join(str(c) for c in n.get("appearances", [])[:6])
        lines.append(
            f"  - {n['canonical_name']} ({n.get('type','?')}) "
            f"weight={n.get('cinematic_weight','?')} ch=[{chs}] "
            f"— {(n.get('dramatic_use') or '')[:80]}"
        )
    lines.append("")
    lines.append(
        f"LOCATION COMPRESSION CANDIDATES "
        f"(low cinematic_weight, fusable — top {max_compressible}):"
    )
    for n in sorted(comp, key=lambda x: x.get("cinematic_weight", 0))[:max_compressible]:
        lines.append(
            f"  - {n['canonical_name']} ({n.get('type','?')}) "
            f"weight={n.get('cinematic_weight','?')}"
        )
    lines.append("")
    lines.append("=== END LOCATION CONTEXT ===")
    return "\n".join(lines)


def _build_plotline_context_block(max_cuttable: int = 12) -> str:
    """Render pre-computed plotline graph as prompt hints. Silent-fallback."""
    try:
        from utils.graph_query import load_plotline_graph
        g = load_plotline_graph()
    except (FileNotFoundError, ImportError, Exception):
        return ""

    mains = g.main_threads()
    non_cut = g.non_cuttable()
    cut = g.cuttable()

    lines = [
        "=== PLOTLINE GRAPH (T1.3 Session 2) ===",
        "",
        f"{len(g.threads)} threads total — {len(mains)} main, "
        f"{len(non_cut)} must-keep, {len(cut)} cuttable. "
        f"{len(g.fusion_edges)} inter-thread fusion edges.",
        "",
    ]

    if mains:
        lines.append("MAIN THREAD(S) — the spine of the feature:")
        for t in mains:
            chs = t.get("chapters_active", [])
            span = f"ch {chs[0]}–{chs[-1]}" if chs else "?"
            lines.append(
                f"  - {t['name']} "
                f"(reach={t.get('reach','?')}, {span}, "
                f"final={t.get('final_status','?')})"
            )
        lines.append("")

    non_main_must = [t for t in non_cut if t.get("type") != "main"]
    if non_main_must:
        lines.append(
            f"MUST-KEEP SUBORDINATE THREADS ({len(non_main_must)}) "
            "— supporting arcs that structurally matter:"
        )
        for t in sorted(non_main_must, key=lambda x: -x.get("reach", 0))[:10]:
            lines.append(
                f"  - {t['name']} ({t.get('type','?')}, reach={t.get('reach','?')})"
            )
        lines.append("")

    if cut:
        lines.append(
            f"CUTTABLE THREADS (top {min(max_cuttable, len(cut))} of {len(cut)}) "
            "— compression targets for 120-min feature:"
        )
        for t in sorted(cut, key=lambda x: x.get("reach", 0))[:max_cuttable]:
            lines.append(
                f"  - {t['name']} ({t.get('type','?')}, reach={t.get('reach','?')})"
            )
        lines.append("")

    if g.fusion_edges:
        lines.append(
            f"THREAD FUSION SUGGESTIONS ({len(g.fusion_edges)}) "
            "— pairs agents flagged as mergeable:"
        )
        for e in g.fusion_edges[:10]:
            lines.append(f"  - `{e.get('a')}` + `{e.get('b')}`")
        lines.append("")

    lines.append("=== END PLOTLINE CONTEXT ===")
    return "\n".join(lines)


# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

# ─── MEMORY-SUMMARY CAPS (Phase K) ────────────────────────────────────────────
# Hard-Caps für `<<MEMORY_SUMMARY>>`-Block. Verhindert unbounded Growth bei
# langen Romanen (HM ~145 Chunks). Spec: docs/memory-summary-schema.md.

_MEMORY_TOTAL_CHAR_CAP = 3200          # ≈ 800 Tokens (4 chars/token approx)
_MEMORY_PROGRESS_CAP = 60
_MEMORY_CHARACTERS_CAP = 1500
_MEMORY_RECENT_ARC_CAP = 1500
_MEMORY_THEMES_CAP = 140
_MEMORY_MAX_CHARS_LISTED = 8
_MEMORY_MAX_PLOT_ELEMENTS = 5
_MEMORY_PLOT_ELEMENT_DESC_CAP = 80
_MEMORY_MAX_THEMES = 6

_ROLE_PRIORITY = {"protagonist": 0, "antagonist": 1, "supporting": 2}


def _truncate(text: str, cap: int, marker: str = "…") -> str:
    """Trim text to cap chars; append marker if cut. Determinism-safe."""
    if len(text) <= cap:
        return text
    if cap <= len(marker):
        return marker[:cap]
    return text[: cap - len(marker)].rstrip() + marker


def _sorted_characters(characters: dict) -> list:
    """Role-priorisierte Char-Liste, stabil nach first_mention_chunk."""
    items = list(characters.items())
    items.sort(key=lambda kv: (
        _ROLE_PRIORITY.get(kv[1].get("role", ""), 99),
        kv[1].get("first_mention_chunk", 10**9),
        kv[0],
    ))
    return items


def _build_memory_summary(characters: dict, plot_elements: list,
                           current_index: int, total: int,
                           themes=None) -> str:
    """
    Builds a compact, hard-capped summary of the current analysis state.
    Cap: ≤ _MEMORY_TOTAL_CHAR_CAP chars (≈ 800 Tokens).

    Spec: docs/memory-summary-schema.md
    """
    if not characters and not plot_elements:
        return "First analysis — no data yet."

    # Field 1 — progress
    pct = int(current_index / total * 100) if total else 0
    progress = _truncate(
        f"{current_index}/{total} chunks ({pct}%)", _MEMORY_PROGRESS_CAP
    )

    # Field 2 — characters (role-sorted, capped)
    sorted_chars = _sorted_characters(characters)
    listed = sorted_chars[:_MEMORY_MAX_CHARS_LISTED]
    overflow = len(sorted_chars) - len(listed)
    char_parts = [f"{name} ({data.get('role', 'supporting')})"
                  for name, data in listed]
    char_str = ", ".join(char_parts) if char_parts else "none yet"
    if overflow > 0:
        char_str += f" … [+{overflow} more]"
    char_str = _truncate(char_str, _MEMORY_CHARACTERS_CAP)

    # Field 3 — recent plot arc (last N, desc-capped, kausal-pfeil)
    recent = plot_elements[-_MEMORY_MAX_PLOT_ELEMENTS:] if plot_elements else []
    arc_parts = [
        _truncate(_compat(e, "description", "beschreibung", ""),
                   _MEMORY_PLOT_ELEMENT_DESC_CAP)
        for e in recent
    ]
    arc_str = " → ".join(p for p in arc_parts if p) or "none yet"
    arc_str = _truncate(arc_str, _MEMORY_RECENT_ARC_CAP)

    # Field 4 — themes (deterministic alpha-sort, capped)
    theme_str = ""
    if themes:
        theme_list = sorted(set(t.strip() for t in themes if t and t.strip()))
        top = theme_list[:_MEMORY_MAX_THEMES]
        theme_str = ", ".join(top)
        if len(theme_list) > len(top):
            theme_str += " …"
        theme_str = _truncate(theme_str, _MEMORY_THEMES_CAP)

    # Render — only emit themes line when non-empty (cleaner prompt)
    lines = [
        f"Progress: {progress}",
        f"Known characters: {char_str}",
        f"Recent plot arc: {arc_str}",
    ]
    if theme_str:
        lines.append(f"Themes (top): {theme_str}")
    rendered = "\n".join(lines)

    # Final hard-cap — wenn trotz per-field-Caps Overflow (z.B. extreme
    # Edge-Cases mit Multi-Byte-Chars in Namen): zuerst arc, dann chars trimmen.
    if len(rendered) > _MEMORY_TOTAL_CHAR_CAP:
        excess = len(rendered) - _MEMORY_TOTAL_CHAR_CAP
        # Trim recent_arc first (most volatile), then characters
        new_arc_cap = max(80, _MEMORY_RECENT_ARC_CAP - excess)
        arc_str = _truncate(arc_str, new_arc_cap)
        lines[2] = f"Recent plot arc: {arc_str}"
        rendered = "\n".join(lines)
        if len(rendered) > _MEMORY_TOTAL_CHAR_CAP:
            new_char_cap = max(80, _MEMORY_CHARACTERS_CAP -
                                (len(rendered) - _MEMORY_TOTAL_CHAR_CAP))
            char_str = _truncate(char_str, new_char_cap)
            lines[1] = f"Known characters: {char_str}"
            rendered = "\n".join(lines)
        # Last-resort hard slice — should never hit in practice
        if len(rendered) > _MEMORY_TOTAL_CHAR_CAP:
            rendered = _truncate(rendered, _MEMORY_TOTAL_CHAR_CAP)

    return rendered


# ─── COMPACTION (Phase K) ─────────────────────────────────────────────────────
# Pure-Python, deterministic. Hook: alle 10 Chunks im run_story_analyst-Loop.

_COMPACT_TRIGGER_EVERY = 10
_COMPACT_PLOT_THRESHOLD = 50
_COMPACT_PLOT_RECENT_KEEP = 20
_COMPACT_ARC_NOTES_KEEP = 5


def _compact_plot_elements(plot_elements: list) -> list:
    """
    Trim plot_elements when >50: keep act-1/3 high-tension turning points,
    keep recent 20, plus oldest+newest per subplot_id. Deterministic.
    """
    if len(plot_elements) <= _COMPACT_PLOT_THRESHOLD:
        return plot_elements

    keep_indices = set()
    n = len(plot_elements)

    # Recent N (most-recent kept fully)
    for i in range(max(0, n - _COMPACT_PLOT_RECENT_KEEP), n):
        keep_indices.add(i)

    # Turning points: act ∈ {1,3} and tension ≥ 0.7
    for i, e in enumerate(plot_elements):
        act = _compat(e, "act", "akt", 0)
        tension = e.get("tension", 0.0)
        if act in (1, 3) and tension >= 0.7:
            keep_indices.add(i)

    # Subplot anchors: oldest + newest per subplot_id
    by_subplot = {}
    for i, e in enumerate(plot_elements):
        sid = e.get("subplot_id")
        if not sid:
            continue
        by_subplot.setdefault(sid, []).append(i)
    for indices in by_subplot.values():
        if indices:
            keep_indices.add(indices[0])
            keep_indices.add(indices[-1])

    return [plot_elements[i] for i in sorted(keep_indices)]


def _compact_arc_notes(characters: dict) -> dict:
    """Trim each character's arc_notes to last N. Mutates in place + returns."""
    for data in characters.values():
        notes = data.get("arc_notes", [])
        if len(notes) > _COMPACT_ARC_NOTES_KEEP:
            data["arc_notes"] = notes[-_COMPACT_ARC_NOTES_KEEP:]
    return characters


def _derive_acts(plot_elements: list, tension_curve: list, total_chunks: int) -> list:
    """Derives three-act structure from collected elements."""
    if not plot_elements:
        return []

    act1 = [e for e in plot_elements if _compat(e, "act", "akt") == 1 or e.get("position") in ["beginning", "early"]]
    act2 = [e for e in plot_elements if _compat(e, "act", "akt") == 2 or e.get("position") == "middle"]
    act3 = [e for e in plot_elements if _compat(e, "act", "akt") == 3 or e.get("position") in ["late", "end"]]

    def summarize_act(elements, num):
        if not elements:
            return {"act": num, "elements": [], "summary": "No elements"}
        return {
            "act": num,
            "element_count": len(elements),
            "elements": [_compat(e, "description", "beschreibung", "")[:100] for e in elements[:5]],
        }

    return [
        summarize_act(act1, 1),
        summarize_act(act2, 2),
        summarize_act(act3, 3),
    ]


def _extract_subplots(plot_elements: list) -> list:
    """Extracts subplots with priority scoring from plot elements."""
    subplot_ids = set()
    for e in plot_elements:
        if e.get("subplot_id"):
            subplot_ids.add(e["subplot_id"])

    total_elements = max(len(plot_elements), 1)
    subplots = []
    for sid in subplot_ids:
        related = [e for e in plot_elements if e.get("subplot_id") == sid]
        # Priority based on frequency and act distribution
        frequency_score = min(len(related) / total_elements * 10, 5)
        # Subplots appearing in all 3 acts are more important
        acts_present = set(_compat(e, "act", "akt", 0) for e in related)
        act_spread_score = len(acts_present) * 1.5
        priority = round(min(frequency_score + act_spread_score, 10), 1)

        subplots.append({
            "id": sid,
            "description": _compat(related[0], "description", "beschreibung", "")[:100] if related else "",
            "element_count": len(related),
            "priority": priority,
            "keep": True,  # Default, orchestrator can change
            "status": "identified",
            "scenes_needed": max(1, len(related) // 2),
        })

    subplots.sort(key=lambda x: x["priority"], reverse=True)
    return subplots


# ─── LOGLINE ──────────────────────────────────────────────────────────────────

SYSTEM_LOGLINE = """Based on this analysis, formulate a logline for the film adaptation.

A logline is ONE sentence following this formula:
"When [protagonist with characterizing trait] is [inciting incident], they must [goal] before [stakes]."

Analysis data:
Characters: {characters}
Themes: {themes}
Act structure: {acts}

Reply ONLY with the logline — one sentence, no JSON."""


def build_logline_prompt() -> str:
    """Builds the logline prompt from the current state."""
    state = load_state()
    chars = ", ".join(
        f"{name} ({data.get('role', '?')})"
        for name, data in list(state["characters"].items())[:5]
    )
    themes = ", ".join(state["plot"].get("themes", [])[:5])
    acts = json.dumps(state["plot"].get("acts", []), ensure_ascii=False)[:500]

    return SYSTEM_LOGLINE.format(characters=chars, themes=themes, acts=acts)


def generate_logline() -> str:
    """
    Generates a logline prompt and returns it for Claude Code to execute.
    The logline follows the formula:
    'When [protagonist with characterizing trait] is [inciting incident],
     they must [goal] before [stakes].'

    After Claude Code generates the logline, it should be stored in
    state['plot']['logline'] via update_state('plot.logline', logline_text).

    Returns the prompt string for Claude Code to process.
    """
    state = load_state()

    if state.get("meta", {}).get("status") not in ("analyzed", "adapted", "scripted"):
        raise ValueError(
            "Story Analyst must run first before generating a logline. "
            "Current status: " + state.get("meta", {}).get("status", "unknown")
        )

    if not state.get("characters"):
        raise ValueError("No characters found in state. Run Story Analyst first.")

    prompt = build_logline_prompt()

    print(f"\n{'='*60}")
    print("LOGLINE GENERATOR")
    print(f"{'='*60}")
    print("Prompt built from state. Send this to the LLM and store the")
    print("result via: update_state('plot.logline', logline_text)")
    print(f"{'='*60}\n")

    return prompt
