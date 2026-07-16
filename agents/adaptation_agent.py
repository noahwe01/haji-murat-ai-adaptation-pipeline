"""
ADAPTATION AGENT
================
Translates literary texts into cinematic scenes.
The most creative and complex transformation:

  Internal monologue  → Visual behavior / Dialogue
  Description         → Camera direction / Image
  Time-lapse passages → Montage sequence
  Subtext             → Body language / Dialogue subtext

15-Agent architecture features (Pipeline v3.2):
- Dialog drafts with subtext annotations
- Emotional choreography per scene
- Impro material consumption
- Few-shot reference scenes
- Multi-dimensional confidence scoring
- Show-don't-tell tracking
- Expansion strategy for short stories
"""

import json
from datetime import datetime, timezone
from state_store import (
    load_state, save_state, _compat,
    append_to_state, log_continuity_issue
)
from decision_log import build_criteria_instruction, log_decisions_from_block


# ─── PHASE M.3 — OUTPUT-SCHEMA CAPS ─────────────────────────────────
# Hard cuts applied post-LLM. Caps mirror SYSTEM_PROMPT contract.
SCHEMA_CAPS = {
    "action": 800,           # max characters
    "dialog_draft": 6,       # max entries
    "visual_note": 200,      # max characters
}


def _trim_on_word(text: str, limit: int) -> str:
    """Trim to <= limit on the last whitespace; fall back to hard cut."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    space = cut.rfind(" ")
    if space >= int(limit * 0.6):
        cut = cut[:space]
    return cut.rstrip(" ,;:—-") + "…"


def _apply_schema_caps(scene: dict, findings: list) -> None:
    """Mutates scene in-place. Appends per-violation entries to findings.
    Each finding: {scene_id, field, original_len, trimmed_to, timestamp}."""
    sid = scene.get("scene_id", "?")
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    action = scene.get("action") or ""
    cap = SCHEMA_CAPS["action"]
    if isinstance(action, str) and len(action) > cap:
        scene["action"] = _trim_on_word(action, cap)
        findings.append({
            "scene_id": sid, "field": "action",
            "original_len": len(action), "trimmed_to": len(scene["action"]),
            "timestamp": ts,
        })

    visual = scene.get("visual_note") or ""
    cap = SCHEMA_CAPS["visual_note"]
    if isinstance(visual, str) and len(visual) > cap:
        scene["visual_note"] = _trim_on_word(visual, cap)
        findings.append({
            "scene_id": sid, "field": "visual_note",
            "original_len": len(visual), "trimmed_to": len(scene["visual_note"]),
            "timestamp": ts,
        })

    drafts = scene.get("dialog_draft")
    cap = SCHEMA_CAPS["dialog_draft"]
    if isinstance(drafts, list) and len(drafts) > cap:
        original_len = len(drafts)
        scene["dialog_draft"] = drafts[:cap]
        findings.append({
            "scene_id": sid, "field": "dialog_draft",
            "original_len": original_len, "trimmed_to": cap,
            "timestamp": ts,
        })


# ─── SYSTEM PROMPT ──────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert screenplay adapter. You translate literary texts into cinematic
scene descriptions. You think in images, sounds, and actions.

CORE PRINCIPLES:
- Show, don't tell: What the novel narrates, you must make visible
- Internal experience becomes external behavior or precise dialogue
- Every scene needs: location, time, action, emotional core
- Respect the style manifest consistently
- Check every character against the character bible and voice profiles

DIALOGUE RULES:
- 70/30 Rule: At least 70% of dialogue lines carry subtext (don't state feelings directly)
- Action before speech: Physical action/reaction BEFORE every line of dialogue
- Every character must match their voice profile
- No on-the-nose: Characters never directly name their emotions
- Silence is dialogue: Pauses, glances, and objects must be scripted — they ARE the scene
- Physical anchor rule: If a scene has 6+ lines of dialogue, characters MUST have a
  physical task (cooking, repairing, packing), face an environmental interruption
  (weather, a visitor, a noise), or change location mid-scene. Walking side-by-side
  and talking is NOT a physical anchor — it is the absence of one.

ADAPTATION RULE — SHOW RELATIONSHIPS:
When the source text summarizes a relationship development ("they saw each other often",
"he visited her regularly"), you MUST create at least ONE scene that concretely SHOWS
this development — don't just report it. Show the approach, the conflict, the change
in a playable scene with specific gestures, dialogue, and emotional beats.

ADAPTATION RULE — CREATIVE EXPANSION:
{expansion_strategy}

BUDGET:
Target runtime: {target_runtime} minutes (feature length)
Scene budget: {scene_budget} scenes total
Already adapted: {scenes_done} scenes ({minutes_done} min.)
Remaining: {chunks_remaining} chunks
→ Distribute the budget wisely. Not every chunk becomes its own scene.
→ Some chunks need MULTIPLE scenes (when expansion is required).
→ For short stories: Invent additional scenes that the source only implies.

STYLE MANIFEST:
{style_brief}

CHARACTER BIBLE WITH VOICE PROFILES:
{char_bible}

PREVIOUS SCENES (for continuity):
{recent_scenes}

IMPRO MATERIAL (if available — use the best lines):
{impro_material}

FEW-SHOT REFERENCE SCENE (quality model):
{reference_scene}

OUTPUT: Valid JSON — no text before/after.

HARD SCHEMA CAPS (Phase M.2). Stay UNDER these limits:
- `action`: max 800 characters per scene. Compress; do not pad.
- `dialog_draft`: max 6 entries per scene. Cut weakest exchanges first.
- `visual_note`: max 200 characters per scene. Lean noun phrases, no full prose.
Output that violates these caps will be trimmed automatically and logged.

Format:
{{
  "scenes": [
    {{
      "scene_id": "S001",
      "slug": "INT. LOCATION - TIME",
      "action": "Filmable action ONLY — what a camera records and an actor performs (2-5 sentences, present tense, active verbs). NEVER describe thoughts, interpretations, or metaphors. If an actress cannot physically DO it, do not write it.",
      "dialog_draft": [
        {{
          "character": "Name",
          "line": "Dialogue line",
          "subtext": "What the character really means",
          "action_before": "Physical action before speaking"
        }}
      ],
      "emotional_beats": [
        {{
          "beat": "What happens",
          "audience_feels": "What the audience feels",
          "character_feels": "What the character feels"
        }}
      ],
      "emotional_core": "Central emotion of the scene",
      "visual_note": "Key props, lighting quality, spatial blocking, color palette — NO camera directions, NO shot types",
      "characters": ["Name1", "Name2"],
      "duration_minutes": 2.0,
      "confidence": 0.85,
      "confidence_breakdown": {{
        "narrative_coherence": 0.90,
        "character_consistency": 0.85,
        "visual_filmability": 0.80,
        "dialog_quality": 0.75,
        "show_dont_tell": 0.88
      }},
      "show_dont_tell_score": 0.85,
      "inner_monologue_converted": [
        {{
          "original": "Internal state from the source",
          "converted_to": "Visual/behavioral translation"
        }}
      ],
      "on_the_nose_risk": [],
      "subplot_threads": ["subplot_id"],
      "source_chunks": [0],
      "transition": "Scene bridge description (e.g. 'sound of bells carries into next scene', 'her hand on glass rhymes with his hand on door') — NO technical edit commands"
    }}
  ],
  "skipped_elements": ["What was removed and why"]
}}"""


# ─── EXPANSION STRATEGY TEMPLATE ────────────────────────────────────

EXPANSION_TEMPLATE = """EXPANSION STRATEGY (Short Story → Feature Film):
This source text is approximately {word_count} words. The target is a {target_runtime}-minute
feature film (~90 screenplay pages). This requires radical expansion.

Composition targets:
- ~{direct_pct}% direct source material (key scenes from the original)
- ~{ellipses_pct}% dramatized ellipses (what the source summarizes in a sentence,
  you expand into full scenes: the courtship, the mourning, the war years)
- ~{subplot_pct}% invented subplots and character perspectives (give voice to
  characters the source neglects; add a B-story that mirrors the theme)
- ~{world_pct}% worldbuilding and external conflict (period detail, social context,
  historical backdrop, atmospheric scenes)

Expansion principles (from Arrival, Brokeback Mountain, Shawshank Redemption, Stand By Me):
1. Build an external conflict spine around the internal story
2. Dramatize every ellipsis — every sentence of summary is a potential scene
3. Invent characters who embody the theme (mirror figures, antagonists, confidants)
4. Find a recurring visual metaphor (the snowstorm, the sealed letter, the willow tree)
5. Restructure time for dramatic effect — the source's chronology is not sacred"""


# Phase D.4 — keyword triggers that drive both brain-retrieval and MCP
# reference-excerpt retrieval. Extracted to a module constant so both
# callsites use the same vocabulary (previously hardcoded inline).
_ADAPTATION_TRIGGER_KEYWORDS = (
    "love", "confession", "farewell", "confrontation", "silence",
    "death", "war", "recognition", "irony", "subtext", "exposition",
    "reunion", "departure", "interrogation", "power", "humor",
    "group", "party", "dinner", "longing", "desire", "guilt",
    "secret", "revelation", "epiphany",
)


COMPRESSION_TEMPLATE = """COMPRESSION STRATEGY (Novel → Feature Film):
This source text is approximately {word_count} words. The target is a {target_runtime}-minute
feature film (~{target_pages} screenplay pages). This requires radical compression — you will
use roughly {keep_pct}% of the source material; the rest must be cut, fused, or refocalized.

Composition targets:
- ~{source_pct}% direct source material (key scenes from the novel, tightly compressed)
- ~{cuttable_pct}% cuttable material (subplots, minor characters, authorial excursions,
  period detail — identify and cut cleanly; do not try to keep everything)
- ~{restructured_pct}% restructured (character fusion, act reordering, refocalized scenes)
- ~{bridges_pct}% invented bridges (transition scenes ONLY — NEVER new plotlines)

Compression principles (from War and Peace 1966, The English Patient, The Last Duel,
Anna Karenina 2012, Barry Lyndon):
1. KILL DARLINGS: Subplots and minor characters that do not serve the protagonist's arc
   must be cut, not condensed. Resist the instinct to preserve every beat.
2. FUSE CHARACTERS: When the source has many named figures, collapse functional duplicates
   into composite characters. Prefer composites over dilution. Historical figures (real
   people from the source period) are anchors — fuse fictional figures around them, not
   the other way around.
3. REFOCALIZE: Multi-POV novels lose dramatic force on screen. Choose ONE protagonist
   (even when the novel distributes perspective), and let other POVs become relationships
   TO that protagonist — seen through his eyes, or through scenes he inhabits.
4. RESTRUCTURE TIME: The novel's chronology is a starting point, not sacred. Use framing
   devices, intercutting, and non-linear structure where it serves drama.
5. TRUST THE IMAGE: What the novel describes in a paragraph, show in a shot. Massive
   passages of interiority become silent gestures, loaded objects, environmental
   storytelling — never voiceover unless structurally justified.
6. DO NOT INVENT NEW PLOTLINES: Your job is compression, not expansion. Invented material
   is strictly transitional (bridging cuts, setup payoffs, scene orientations).
7. DECLARE CUTS EXPLICITLY: When you skip substantial source material, log it in
   skipped_elements with a one-line reason. Makes the compression auditable."""


# ─── MAIN FUNCTION ──────────────────────────────────────────────────

# ─── PHASE F.4 — MICRO-LOOP API ─────────────────────────────────────────────
# Per-chunk processing with progress persisted in state["adaptation_progress"].
#
# Caller pattern:
#   start_adaptation()                       # reset accumulator
#   for i, chunk_text in chunks:
#       prompt = build_adaptation_prompt(
#           chunk_text, i, persist_reference_meta=True
#       )                                                       # F.4 char-slim + P1.1 opt-in log
#       result = <subagent dispatch>
#       run_adaptation_chunk(i, result, raw_output=...)        # validate+continuity
#   summary = finalize_adaptation()
#
# Note (H'' Phase D / P1.1): build_adaptation_prompt is side-effect-free by
# default (state-hash invariant). Pass persist_reference_meta=True to enable
# the MCP-auto-retrieved reference being appended to
# state["adaptation_references"]. Pure-prompt-build callers (preflight,
# token-estimation, S1 prompt-smoke) must keep the default to avoid
# accidental state mutation.


def _empty_adaptation_progress() -> dict:
    return {
        "chunks_done": [],
        "scene_counter": 1,
        "minutes_done": 0.0,
        "continuity_sub_threshold": 0,
        "over_cap_findings": [],
        "batch_meta": [],
    }


def reset_adaptation_progress() -> dict:
    """Clears the per-chunk adaptation accumulator. Idempotent."""
    state = load_state()
    state["adaptation_progress"] = _empty_adaptation_progress()
    state.setdefault("adapted_scenes", [])
    save_state(state)
    return state


def get_adaptation_progress() -> dict:
    """Reads current accumulator, initializing if absent."""
    state = load_state()
    prog = state.get("adaptation_progress")
    if not isinstance(prog, dict):
        prog = _empty_adaptation_progress()
        state["adaptation_progress"] = prog
        save_state(state)
    return prog


def measure_prompt_size(prompt: str) -> dict:
    """Returns chars + estimated tokens (chars / 4 heuristic). Cheap O(1)
    over len(prompt). Useful for batch-summary logging."""
    chars = len(prompt)
    return {"chars": chars, "estimated_tokens": chars // 4}


def run_adaptation_chunk(
    chunk_index: int,
    chunk_result: dict | None,
    raw_output: str | None = None,
    orchestrator=None,
    prompt_size: dict | None = None,
    verbose: bool = True,
) -> dict:
    """
    Phase F.4 micro-loop step: validates, continuity-checks, and persists
    one chunk's adaptation result. Reset-fähig — repeating execution for the
    same chunk_index is a no-op.

    prompt_size is optional metadata (from measure_prompt_size on the
    prompt the caller dispatched); persisted to batch_meta for audit.

    Side-effects:
      - state["adapted_scenes"] extended with new scenes (with continuity_result)
      - state["adaptation_progress"] updated (counters + batch_meta)
      - state["meta"]["status"] becomes "adapted" once at least one chunk done
        (consistent with run_adaptation_agent legacy behaviour)
      - DECISIONS logged when raw_output provided
      - Sub-threshold scenes flagged into continuity_log

    Returns batch summary: chunk_index, scenes_added, avg_confidence,
    continuity_flagged, prompt_chars, status.
    """
    state = load_state()
    valid_statuses = ["analyzed", "enriched", "strategy_set", "impro_done", "adapted"]
    if state["meta"]["status"] not in valid_statuses:
        raise ValueError(
            f"Previous phases must run first. Status: {state['meta']['status']}"
        )

    progress = state.get("adaptation_progress")
    if not isinstance(progress, dict):
        progress = _empty_adaptation_progress()
        state["adaptation_progress"] = progress

    if chunk_index in progress["chunks_done"]:
        if verbose:
            print(f"  [F.4] chunk {chunk_index+1} already adapted — skip")
        return {
            "chunk_index": chunk_index,
            "status": "already_done",
            "scenes_added": 0,
        }

    if orchestrator is None:
        from agents.orchestrator import Orchestrator
        from config.loader import load_config
        orchestrator = Orchestrator(load_config())

    if chunk_result is None:
        log_continuity_issue(f"Adaptation chunk {chunk_index+1}: result missing")
        progress["chunks_done"].append(chunk_index)
        save_state(state)
        if verbose:
            print(f"  [F.4] chunk {chunk_index+1}: no result — logged + skipped")
        return {
            "chunk_index": chunk_index,
            "status": "missing_result",
            "scenes_added": 0,
        }

    new_scenes = chunk_result.get("scenes", chunk_result.get("szenen", []))
    confs = []
    flagged = 0
    scene_counter = progress["scene_counter"]
    minutes_done = progress["minutes_done"]
    over_cap = progress["over_cap_findings"]

    for scene in new_scenes:
        scene["scene_id"] = f"S{scene_counter:03d}"
        scene_counter += 1

        _apply_schema_caps(scene, over_cap)

        minutes_done += _compat(scene, "duration_minutes", "dauer_minuten", 2.0)

        breakdown = _compat(scene, "confidence_breakdown", "konfidenz_breakdown", {})
        if breakdown:
            scene["confidence"] = round(
                breakdown.get("narrative_coherence", 0.7) * 0.20 +
                breakdown.get("character_consistency", 0.7) * 0.25 +
                breakdown.get("visual_filmability", 0.7) * 0.15 +
                breakdown.get("dialog_quality", 0.7) * 0.25 +
                breakdown.get("show_dont_tell", 0.7) * 0.15,
                3,
            )

        # Reload state for orchestrator continuity check (it reads characters etc.)
        save_state(state)
        cresult = orchestrator.continuity_check(scene)
        # Re-load — continuity_check may have logged via log_continuity_issue
        state = load_state()
        progress = state["adaptation_progress"]
        scene["continuity_result"] = cresult
        if cresult["score"] < 0.75:
            flagged += 1
            log_continuity_issue(
                f"Scene {scene['scene_id']}: continuity score "
                f"{cresult['score']:.2f} — flags: {cresult['flags']}",
                scene_id=scene["scene_id"],
                resolved=False,
            )
            state = load_state()
            progress = state["adaptation_progress"]

        if _compat(scene, "confidence", "konfidenz", 1.0) < 0.75:
            log_continuity_issue(
                f"Scene {scene['scene_id']}: Low confidence "
                f"({_compat(scene, 'confidence', 'konfidenz', 0):.2f})",
                scene_id=scene["scene_id"],
                resolved=False,
            )
            state = load_state()
            progress = state["adaptation_progress"]

        confs.append(_compat(scene, "confidence", "konfidenz", 0))

    state["adapted_scenes"] = (state.get("adapted_scenes") or []) + new_scenes
    state["meta"]["status"] = "adapted"
    state["meta"]["estimated_runtime_minutes"] = round(minutes_done)

    progress["scene_counter"] = scene_counter
    progress["minutes_done"] = minutes_done
    progress["continuity_sub_threshold"] += flagged
    progress["over_cap_findings"] = over_cap
    progress["chunks_done"].append(chunk_index)
    progress["batch_meta"].append({
        "chunk_index": chunk_index,
        "scenes_added": len(new_scenes),
        "prompt_chars": (prompt_size or {}).get("chars"),
        "avg_confidence": round(sum(confs) / len(confs), 3) if confs else None,
        "continuity_flagged": flagged,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })

    save_state(state)

    if raw_output:
        logged = log_decisions_from_block(
            agent_output=raw_output,
            agent="adaptation_agent",
            phase="5_adaptation",
        )
        if verbose and logged:
            print(f"     → {logged} decision(s) logged")

    summary = {
        "chunk_index": chunk_index,
        "status": "ok",
        "scenes_added": len(new_scenes),
        "avg_confidence": round(sum(confs) / len(confs), 3) if confs else None,
        "continuity_flagged": flagged,
        "prompt_chars": (prompt_size or {}).get("chars"),
        "minutes_done": round(minutes_done, 1),
    }
    if verbose:
        print(
            f"  [F.4] chunk {chunk_index+1}  +{summary['scenes_added']} scenes  "
            f"avg_conf={summary['avg_confidence']}  "
            f"flagged={flagged}  ~{minutes_done:.0f} min"
        )
    return summary


def finalize_adaptation(verbose: bool = True) -> dict:
    """Phase F.4 finalize: persists over_cap_findings into top-level state
    and returns a summary. No status change here — micro-loop persists
    'adapted' incrementally so a partial run is still picked up by
    downstream phases (Coverage etc.)."""
    state = load_state()
    progress = state.get("adaptation_progress") or _empty_adaptation_progress()
    over_cap = progress["over_cap_findings"]
    if over_cap:
        state.setdefault("over_cap_findings", []).extend(over_cap)
        progress["over_cap_findings"] = []
        save_state(state)

    adapted_scenes = state.get("adapted_scenes", [])
    summary = {
        "chunks_done": len(progress["chunks_done"]),
        "scenes_total": len(adapted_scenes),
        "minutes_estimated": round(progress["minutes_done"], 1),
        "continuity_flagged": progress["continuity_sub_threshold"],
        "over_cap_trims": len(over_cap),
        "batch_meta": progress["batch_meta"],
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"ADAPTATION (F.4) micro-loop complete:")
        print(f"  Chunks done:          {summary['chunks_done']}")
        print(f"  Scenes total:         {summary['scenes_total']}")
        print(f"  Estimated runtime:    ~{summary['minutes_estimated']:.0f} min.")
        print(f"  Continuity flagged:   {summary['continuity_flagged']}")
        print(f"  Over-cap trims:       {summary['over_cap_trims']}")
        if progress["batch_meta"]:
            avg_chars = sum(b.get("prompt_chars") or 0 for b in progress["batch_meta"])
            counted = sum(1 for b in progress["batch_meta"] if b.get("prompt_chars"))
            if counted:
                print(f"  Avg prompt chars:     {avg_chars // counted:,}")
        print(f"{'='*60}\n")
    return summary


# ─── BULK API (Phase E and earlier) ─────────────────────────────────────────


def run_adaptation_agent(chunk_results: list, verbose: bool = True,
                         orchestrator=None,
                         raw_outputs: list | None = None) -> None:
    """
    Adapts all chunks into cinematic scenes.
    chunk_results: List of adaptation dicts (one per chunk/batch).
    raw_outputs:   Optional list of raw subagent-output strings (scenes JSON +
                   DECISIONS block). When provided, each batch's DECISIONS block
                   is parsed and written to output/adaptation_log.json with
                   agent="adaptation_agent", phase="5_adaptation". Index-aligned
                   with chunk_results. Optional so existing callers remain
                   source-compatible.

    Runs the Continuity Watcher after EVERY assigned
    scene: each scene's continuity_result is persisted on the scene dict
    and sub-threshold scenes (< 0.75) are logged to continuity_log with
    resolved=False for the revision loop.

    The orchestrator instance is lazy-imported to avoid a circular import
    (orchestrator may dispatch this module). Callers can inject their own
    instance via the ``orchestrator`` kwarg (tests, custom wiring).
    """
    state = load_state()
    chunks = state.get("chunks", [])
    characters = state.get("characters", {})
    style_manifest = state.get("style_manifest", {})

    valid_statuses = ["analyzed", "enriched", "strategy_set", "impro_done", "adapted"]
    if state["meta"]["status"] not in valid_statuses:
        raise ValueError(
            f"Previous phases must run first. Status: {state['meta']['status']}"
        )

    if orchestrator is None:
        from agents.orchestrator import Orchestrator
        from config.loader import load_config
        orchestrator = Orchestrator(load_config())

    total = len(chunks)
    print(f"\n{'='*60}")
    print(f"ADAPTATION AGENT starting — {total} chunks to adapt")
    print(f"Style: {style_manifest.get('genre', '?')} / {style_manifest.get('ton', style_manifest.get('tone', '?'))}")
    print(f"Voice profiles loaded: {sum(1 for c in characters.values() if c.get('voice_profile'))}")
    print(f"{'='*60}\n")

    adapted_scenes = []
    scene_counter = 1
    total_estimated_minutes = 0.0
    continuity_sub_threshold = 0
    over_cap_findings: list = []

    for i, result in enumerate(chunk_results):
        if verbose:
            print(f"  Processing batch {i+1}/{len(chunk_results)}...", end=" ")

        if result is None:
            if verbose:
                print("⚠ No result, skipping")
            log_continuity_issue(f"Batch {i+1}: Adaptation failed")
            continue

        new_scenes = result.get("scenes", result.get("szenen", []))

        # Phase L: continuity_warning self-report removed from prompt.
        # Drift detection runs deterministically per-scene below via
        # orchestrator.deterministic_continuity_pass (pass_per_type).

        # Assign sequential scene IDs
        for scene in new_scenes:
            scene["scene_id"] = f"S{scene_counter:03d}"
            scene_counter += 1

            # Phase M.3 — hard-cut schema caps before downstream consumers
            # see the scene (continuity check, runtime calc, persistence).
            _apply_schema_caps(scene, over_cap_findings)

            total_estimated_minutes += _compat(scene, "duration_minutes", "dauer_minuten", 2.0)

            # Calculate weighted overall confidence
            breakdown = _compat(scene, "confidence_breakdown", "konfidenz_breakdown", {})
            if breakdown:
                scene["confidence"] = round(
                    breakdown.get("narrative_coherence", 0.7) * 0.20 +
                    breakdown.get("character_consistency", 0.7) * 0.25 +
                    breakdown.get("visual_filmability", 0.7) * 0.15 +
                    breakdown.get("dialog_quality", 0.7) * 0.25 +
                    breakdown.get("show_dont_tell", 0.7) * 0.15,
                    3
                )

            # Continuity watcher — mandatory per scene
            continuity_result = orchestrator.continuity_check(scene)
            scene["continuity_result"] = continuity_result
            if continuity_result["score"] < 0.75:
                continuity_sub_threshold += 1
                log_continuity_issue(
                    f"Scene {scene['scene_id']}: continuity score "
                    f"{continuity_result['score']:.2f} — flags: {continuity_result['flags']}",
                    scene_id=scene["scene_id"],
                    resolved=False,
                )

        adapted_scenes.extend(new_scenes)

        if verbose and new_scenes:
            avg_conf = sum(_compat(s, "confidence", "konfidenz", 0) for s in new_scenes) / len(new_scenes)
            print(f"✓  {len(new_scenes)} scenes  |  "
                  f"avg confidence: {avg_conf:.2f}  |  "
                  f"~{total_estimated_minutes:.0f} min total")

        # DECISIONS logging — parse agent's raw output, append to adaptation_log.
        # Write-only contract (never re-ingested).
        if raw_outputs is not None and i < len(raw_outputs) and raw_outputs[i]:
            logged = log_decisions_from_block(
                agent_output=raw_outputs[i],
                agent="adaptation_agent",
                phase="5_adaptation",
            )
            if verbose and logged:
                print(f"     → {logged} decision(s) logged")

    # Flag low-confidence scenes
    low_confidence = [s for s in adapted_scenes if _compat(s, "confidence", "konfidenz", 1.0) < 0.75]
    for scene in low_confidence:
        log_continuity_issue(
            f"Scene {scene.get('scene_id', '?')}: Low confidence ({_compat(scene, 'confidence', 'konfidenz', 0):.2f})",
            scene_id=scene.get("scene_id", ""),
            resolved=False,
        )

    # Save state
    state = load_state()
    state["adapted_scenes"] = adapted_scenes
    state["meta"]["status"] = "adapted"
    state["meta"]["estimated_runtime_minutes"] = round(total_estimated_minutes)
    if over_cap_findings:
        state.setdefault("over_cap_findings", []).extend(over_cap_findings)
    save_state(state)

    print(f"\n{'='*60}")
    print(f"ADAPTATION AGENT complete:")
    print(f"  Scenes total:         {len(adapted_scenes)}")
    print(f"  Estimated runtime:    ~{total_estimated_minutes:.0f} min.")
    print(f"  Low confidence:       {len(low_confidence)} scenes")
    print(f"  Continuity flagged:   {continuity_sub_threshold} scenes (score < 0.75)")
    print(f"  Over-cap trims:       {len(over_cap_findings)} (Phase M)")
    print(f"{'='*60}\n")


# ─── PROMPT BUILDER ─────────────────────────────────────────────────

def build_adaptation_prompt(
    chunk_text: str,
    chunk_index: int,
    reference_scene: str = "",
    char_id_subset: list | None = None,
    persist_reference_meta: bool = False,
) -> str:
    """
    Builds the complete adaptation prompt for a chunk/batch.
    Integrates voice profiles, impro material, and few-shot references.

    Phase E.5: reads ``state_store.build_adaptation_view(state, chunk_index)``
    for the slim per-chunk subset (recent 2 scenes, this-chunk impro entry,
    tension-index entry, slim style_manifest, scene/minute counters,
    chunks_remaining).

    Phase F.4: ``char_id_subset`` (list[str], optional) restricts the
    character-bible rendering to the chars actually relevant for this
    chunk. Resolves the E.5 honest-fail (HM Δ 63.3%): the per-chunk
    bible drops from full 30+ figures to a 3-8 head subset. When
    ``None`` (default), the full characters dict is used — backward
    compatible with pre-F.1 projects (Schneesturm).

    H'' Phase D / P1.1: ``persist_reference_meta`` (bool, default False)
    gates the auto-retrieval reference-log write. With the default the
    builder is fully side-effect-free (state-hash invariant). Callers that
    want the MCP-auto-retrieved reference recorded in
    ``state["adaptation_references"]`` must opt in explicitly via
    ``persist_reference_meta=True`` (typically the orchestrator subagent
    dispatcher right before/after the chunk is processed).
    """
    state = load_state()
    from state_store import build_adaptation_view, select_chars_for_chunk
    if char_id_subset is None:
        char_id_subset = select_chars_for_chunk(state, chunk_index)
    view = build_adaptation_view(state, chunk_index, char_id_subset=char_id_subset)
    characters = view["characters"]

    # Phase D: chunk-scoped character bible.
    # Compact voice profiles by default. Full triggered when the chunk hosts
    # a key scene per state["chunk_tension_index"][chunk_id] (set upstream
    # by Story Analyst / Orchestrator) or via explicit override.
    chunk_meta = view["chunk_tension"]
    use_full_voice = bool(
        chunk_meta.get("is_key_scene")
        or (chunk_meta.get("tension") or 0) > 0.7
        or view["force_full_voice_next_chunk"]
    )
    char_bible = _build_character_bible_with_voice(characters, full_voice=use_full_voice)
    style_brief = _build_style_brief(view["style_manifest"])
    # View pre-slices to last 2 scenes; _get_recent_scenes' own [-n:] is a no-op here.
    recent = _get_recent_scenes(view["recent_scenes"])

    # Impro material for this chunk (single-entry dict from the view)
    impro_text = ""
    if view["impro_material"]:
        impro_text = json.dumps(
            next(iter(view["impro_material"].values())),
            ensure_ascii=False,
            indent=2,
        )

    # Budget info
    target_runtime = view["meta"]["target_runtime_minutes"]
    scene_budget = view["meta"]["scene_budget"]
    scenes_done = view["scenes_done"]
    minutes_done = view["minutes_done"]
    chunks_remaining = view["chunks_remaining"]

    # Build expansion strategy from config
    expansion_strategy = _build_expansion_strategy(state)

    # Reference scene — 3-tier priority:
    #   1. explicit reference_scene arg (caller override)
    #   2. pre-seeded state.reference_context.adaptation_models (legacy path)
    #   3. D.4 — auto-retrieve one screenplay excerpt from MCP corpus
    ref_scene = reference_scene
    ref_models = view["reference_models"]
    if not ref_scene and ref_models:
        ref_scene = (ref_models[0].get("text", "") or "")[:1000]
    if not ref_scene:
        retrieved, ref_meta = _retrieve_reference_for_chunk(
            chunk_text, state, chunk_index
        )
        ref_scene = retrieved  # empty string if no match; prompt format
                               # below falls back to "(No reference scene)"
        if ref_meta and persist_reference_meta:
            refs_log = state.setdefault("adaptation_references", [])
            refs_log.append(ref_meta)
            save_state(state)

    # Load static skills + dynamic brain knowledge
    from utils.skill_loader import load_skills_for_agent, retrieve_brain_knowledge
    skills_text = load_skills_for_agent("adaptation_agent")

    # Dynamic brain retrieval based on chunk context
    brain_context = {
        "keywords": ["action line", "filmability"],
        "emotional_core": "",
    }
    # Extract keywords from chunk text for brain matching
    chunk_lower = chunk_text.lower()
    for keyword in _ADAPTATION_TRIGGER_KEYWORDS:
        if keyword in chunk_lower:
            brain_context["keywords"].append(keyword)
    # Also use recent scene emotional core as context (last scene, raw state)
    raw_recent = state.get("adapted_scenes", []) or []
    if raw_recent:
        last_core = raw_recent[-1].get("emotional_core", "")
        brain_context["emotional_core"] = last_core

    brain_knowledge, brain_gaps = retrieve_brain_knowledge(brain_context, max_chars=3000)

    prompt = SYSTEM_PROMPT.format(
        style_brief=style_brief,
        char_bible=char_bible,
        recent_scenes=recent or "(First scene — no context yet)",
        impro_material=impro_text or "(No impro material for this chunk)",
        reference_scene=ref_scene or "(No reference scene)",
        expansion_strategy=expansion_strategy,
        target_runtime=target_runtime,
        scene_budget=scene_budget,
        scenes_done=scenes_done,
        minutes_done=f"{minutes_done:.0f}",
        chunks_remaining=chunks_remaining,
    )

    if skills_text:
        prompt += f"\n\n{skills_text}"
    if brain_knowledge:
        prompt += f"\n\n{brain_knowledge}"

    # Criteria injection — agent cites rule IDs in a DECISIONS block after its JSON.
    try:
        prompt += "\n\n" + build_criteria_instruction()
    except FileNotFoundError:
        pass

    return prompt + f"\n\nSOURCE TEXT CHUNK:\n{chunk_text}"


# ─── HELPER FUNCTIONS ───────────────────────────────────────────────

def _build_expansion_strategy(state: dict) -> str:
    """Builds the expansion/compression strategy block from config and state.

    Branches on config['expansion_mode']:
      - "short_story_to_feature" -> EXPANSION_TEMPLATE (20/30/25/25)
      - "novel_to_feature"       -> COMPRESSION_TEMPLATE (25/60/10/5)
      - None                     -> standard adaptation string
    """
    from config.loader import load_config
    config = load_config()

    expansion_mode = config.get("expansion_mode")
    if not expansion_mode:
        return "Standard adaptation — maintain source proportions."

    targets = config.get("composition_targets", {})
    word_count = state["meta"].get("word_count", "unknown")
    target_runtime = state["meta"].get("target_runtime_minutes", 90)

    if expansion_mode == "novel_to_feature":
        source_pct = targets.get("source_compression_pct", 25)
        cuttable_pct = targets.get("cuttable_material_pct", 60)
        restructured_pct = targets.get("restructured_pct", 10)
        bridges_pct = targets.get("invented_bridges_pct", 5)
        return COMPRESSION_TEMPLATE.format(
            word_count=word_count,
            target_runtime=target_runtime,
            target_pages=int(target_runtime * 1.0),
            keep_pct=source_pct + restructured_pct + bridges_pct,
            source_pct=source_pct,
            cuttable_pct=cuttable_pct,
            restructured_pct=restructured_pct,
            bridges_pct=bridges_pct,
        )

    # Default: expansion (short_story_to_feature)
    return EXPANSION_TEMPLATE.format(
        word_count=word_count,
        target_runtime=target_runtime,
        direct_pct=targets.get("direct_source_pct", 20),
        ellipses_pct=targets.get("dramatized_ellipses_pct", 30),
        subplot_pct=targets.get("invented_subplots_pct", 25),
        world_pct=targets.get("worldbuilding_external_pct", 25),
    )


# Phase D.4 — MCP reference retrieval

def _retrieve_reference_for_chunk(
    chunk_text: str,
    state: dict,
    chunk_index: int,
) -> tuple:
    """Pull one screenplay excerpt from the MCP corpus matching this chunk.

    Builds a keyword-query from chunk content + the last adapted scene's
    emotional_core, calls skill_loader.retrieve_reference_excerpts with
    categories=["screenplay"] and top_n=1. Silent-fallback on empty
    match or missing index.

    Returns (excerpt_text, ref_metadata):
      - excerpt_text: formatted excerpt block (empty string if no match)
      - ref_metadata: dict with chunk_index, query, match (or None if no match)
    """
    from utils.skill_loader import retrieve_reference_excerpts

    query_terms = []
    chunk_lower = chunk_text.lower()
    for kw in _ADAPTATION_TRIGGER_KEYWORDS:
        if kw in chunk_lower:
            query_terms.append(kw)

    adapted = state.get("adapted_scenes", [])
    if adapted:
        last_core = (adapted[-1].get("emotional_core") or "").lower()
        if last_core:
            # Filter stopwords / short tokens so the query stays specific
            # (emotional_core can be a full sentence like "the moment of war").
            _STOP = {"the", "and", "for", "with", "from", "into", "this",
                     "that", "has", "have", "was", "were", "being", "been"}
            query_terms.extend([
                t for t in last_core.split()
                if len(t) >= 4 and t not in _STOP
            ][:3])

    if not query_terms:
        query_terms = ["scene", "dialog", "beat"]

    query = " ".join(query_terms[:8])
    excerpt, metadata = retrieve_reference_excerpts(
        query=query,
        max_chars=1200,
        categories=["screenplay"],
        top_n=1,
    )
    if not metadata:
        return "", {"chunk_index": chunk_index, "query": query, "match": None}

    return excerpt, {
        "chunk_index": chunk_index,
        "query": query,
        "match": metadata[0],  # {title, category, chunk, score}
    }


def _build_character_bible_with_voice(characters: dict, full_voice: bool = False) -> str:
    """Builds character bible WITH voice profiles for the prompt.

    Phase D: compact voice rendering by default (~76% smaller). Pass
    full_voice=True to revert to the verbose pre-D format — used only for
    chunks hosting key scenes (tension > 0.7 or is_key_scene).

    If state["casting"] contains a D.3 structured entry for a character,
    a one-line casting hint is appended right after the role/want/need
    line. Legacy casting (string) or missing casting is skipped silently.
    """
    if not characters:
        return "No character data available."

    casting = (load_state().get("casting") or {})

    # Phase D: lazy-import compact helper to avoid circular dependency on
    # character_agent at module load time.
    from agents.character_agent import compact_voice_profile

    lines = []
    for name, data in list(characters.items())[:8]:
        rolle = _compat(data, "role", "rolle", "supporting")
        want = data.get("want", "?")
        need = data.get("need", "?")
        lines.append(f"• {name} ({rolle}) — Want: {want} | Need: {need}")

        cast_entry = casting.get(name)
        if isinstance(cast_entry, dict) and cast_entry.get("physical_anchor"):
            age = cast_entry.get("age_range", "?")
            phys = (cast_entry.get("physical_anchor", "") or "")[:120]
            vocal = (cast_entry.get("vocal_quality", "") or "")[:80]
            lines.append(f"  Casting: {age} · {phys}")
            if vocal:
                lines.append(f"    Voice-type: {vocal}")

        vp = data.get("voice_profile", {})
        if vp:
            if full_voice:
                _render_voice_full(vp, lines)
            else:
                compact = data.get("voice_profile_compact") or compact_voice_profile(vp)
                _render_voice_compact(compact, lines)

        arc = data.get("arc", {})
        if isinstance(arc, dict) and arc:
            start = _compat(arc, "start_state", "ausgangszustand", "?")
            end = _compat(arc, "end_state", "endzustand", "?")
            lines.append(f"  Arc: {start} → {end}")

    return "\n".join(lines)


def _render_voice_full(vp: dict, lines: list) -> None:
    """Pre-D verbose render. Used only when full_voice=True."""
    voice_desc = _compat(vp, "voice_description", "stimmbeschreibung", "")
    if voice_desc:
        lines.append(f"  Voice: {voice_desc}")
    vocab = vp.get("vocabulary_level", "")
    if vocab:
        lines.append(f"  Vocabulary: {vocab}")
    sentence = _compat(vp, "sentence_pattern", "sentence_structure", "")
    if sentence:
        lines.append(f"  Sentence pattern: {sentence}")
    tics = vp.get("verbal_tics", [])
    if tics:
        lines.append(f"  Tics: {', '.join(tics)}")
    avoidances = _compat(vp, "avoidances", "vermeidungen", [])
    if avoidances:
        lines.append(f"  Never says: {', '.join(avoidances)}")
    emo_expr = vp.get("emotional_expression", "")
    if emo_expr:
        lines.append(f"  Emotional expression: {emo_expr}")
    rhythm = vp.get("speech_rhythm", "")
    if rhythm:
        lines.append(f"  Speech rhythm: {rhythm}")
    examples = vp.get("dialog_examples", [])
    if examples:
        lines.append("  Dialog examples:")
        if isinstance(examples, dict):
            for ctx, txt in list(examples.items())[:5]:
                lines.append(f"    [{ctx}]: \"{txt}\"")
        else:
            for ex in examples[:5]:
                if isinstance(ex, dict):
                    ctx = ex.get("context", ex.get("state", "?"))
                    txt = ex.get("text", "")
                    lines.append(f"    [{ctx}]: \"{txt}\"")
                else:
                    lines.append(f"    \"{ex}\"")
    subtext = vp.get("subtext_rules", "")
    if subtext:
        if isinstance(subtext, list):
            lines.append(f"  Subtext rules: {'; '.join(subtext)}")
        else:
            lines.append(f"  Subtext rules: {subtext}")


def _render_voice_compact(compact: dict, lines: list) -> None:
    """Phase D compact render. Mirrors character_agent.render_voice_profiles_compact body."""
    if not compact:
        return
    if compact.get("voice_description"):
        lines.append(f"  Voice: {compact['voice_description']}")
    if compact.get("vocabulary_level"):
        lines.append(f"  Vocabulary: {compact['vocabulary_level']}")
    if compact.get("sentence_pattern"):
        lines.append(f"  Pattern: {compact['sentence_pattern']}")
    if compact.get("verbal_tics"):
        lines.append(f"  Tics: {', '.join(compact['verbal_tics'])}")
    if compact.get("avoidances"):
        lines.append(f"  Never: {', '.join(compact['avoidances'])}")
    if compact.get("subtext_rule_short"):
        lines.append(f"  Subtext rule: {compact['subtext_rule_short']}")
    if compact.get("example_line"):
        lines.append(f'  Example: "{compact["example_line"]}"')


def _build_style_brief(style_manifest: dict) -> str:
    """Translates style manifest into precise instructions."""
    if not style_manifest:
        return "No style manifest defined — standard drama style."

    lines = []
    if style_manifest.get("genre"):
        lines.append(f"Genre: {style_manifest['genre']}")
    if _compat(style_manifest, "tone", "ton"):
        lines.append(f"Tone: {_compat(style_manifest, 'tone', 'ton')}")
    if _compat(style_manifest, "reference_films", "referenzfilme"):
        refs = ", ".join(_compat(style_manifest, "reference_films", "referenzfilme"))
        lines.append(f"Reference films: {refs}")
    if style_manifest.get("pov"):
        lines.append(f"POV: {style_manifest['pov']}")
    if _compat(style_manifest, "special_notes", "besonderheiten"):
        lines.append(f"Special notes: {_compat(style_manifest, 'special_notes', 'besonderheiten')}")

    return "\n".join(lines) if lines else "Standard drama style"


def _get_recent_scenes(scenes: list, n: int = 2) -> str:
    """Returns the last n scenes as context string."""
    if not scenes:
        return ""

    recent = scenes[-n:]
    parts = []
    for s in recent:
        dialog_preview = ""
        drafts = s.get("dialog_draft", s.get("dialog_hinweise", []))
        if drafts and isinstance(drafts, list):
            if isinstance(drafts[0], dict):
                dialog_preview = f" | Dialog: {drafts[0].get('character', '?')}: \"{drafts[0].get('line', '')[:50]}...\""
            elif isinstance(drafts[0], str):
                dialog_preview = f" | Dialog: {drafts[0][:60]}..."

        scene_id = _compat(s, "scene_id", "szenen_id", "?")
        action = _compat(s, "action", "handlung", "")
        parts.append(
            f"[{scene_id}] {s.get('slug', '')}\n"
            f"{action[:200]}{dialog_preview}"
        )
    return "\n\n".join(parts)
