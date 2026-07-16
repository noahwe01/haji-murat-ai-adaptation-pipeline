"""
ORCHESTRATOR
============
Central conductor of the 7-agent system.
Coordinates all sub-agents, manages the story state,
runs continuity checks, and controls revision loops.

The Orchestrator produces NO creative output.
It dispatches work, validates results, and routes revisions.
"""

import os
from datetime import datetime
from typing import Optional
from config.loader import load_config
from state_store import (
    load_state, save_state, version_state, update_state,
    append_to_state, update_confidence_stats, log_continuity_issue,
    detect_source_length_class, strip_chunk_text, _compat,
    get_chunk_text_for_prompt,
)


# ─── Load project configuration ─────────────────────────────────────

_config = load_config()


# ─── Phase definitions ───────────────────────────────────────────────

PHASES = [
    "phase_0_intake",
    "phase_1_deep_analysis",
    "phase_2_synthesis",
    "phase_3_strategy",
    "phase_4_dialog_impro",
    "phase_5_adaptation",
    "phase_6_treatment",
    "phase_7_coverage",
    "phase_9_screenplay",
    "phase_9_5_analysis",
    "phase_8_revision",
]

STATUS_FLOW = {
    "phase_0_intake": "initialized",
    "phase_1_deep_analysis": "analyzed",
    "phase_2_synthesis": "enriched",
    "phase_3_strategy": "strategy_set",
    "phase_4_dialog_impro": "impro_done",
    "phase_5_adaptation": "adapted",
    "phase_6_treatment": "treatment_done",
    "phase_7_coverage": "covered",
    "phase_9_screenplay": "scripted",
    "phase_9_5_analysis": "analyzed_post",
    "phase_8_revision": "revised",
}

# ─── Analysis Layer sequence ────────────────────────────────────────
# Phase 9.5: Sequential execution order for the 6 Analysis Agents.
# Each agent writes its result to state and to state/_result_*.json.

ANALYSIS_AGENTS = [
    {
        "name": "pacing_analyzer",
        "build_prompt": "agents.pacing_analyzer.build_pacing_prompt",
        "run": "agents.pacing_analyzer.run_pacing_analysis",
        "result_file": "_result_pacing.json",
        "model": "sonnet",
    },
    {
        "name": "subtext_auditor",
        "build_prompt": "agents.subtext_auditor.build_subtext_audit_prompt",
        "run": "agents.subtext_auditor.run_subtext_audit",
        "result_file": "_result_subtext.json",
        "model": "sonnet",
    },
    {
        "name": "dialog_thread_checker",
        "build_prompt": "agents.dialog_thread_checker.build_thread_check_prompt",
        "run": "agents.dialog_thread_checker.run_thread_check",
        "result_file": "_result_thread.json",
        "model": "sonnet",
    },
    {
        "name": "transition_mapper",
        "build_prompt": "agents.transition_mapper.build_transition_prompt",
        "run": "agents.transition_mapper.run_transition_mapper",
        "result_file": "_result_transitions.json",
        "model": "sonnet",
    },
    {
        "name": "narrative_coherence",
        "build_prompt": "agents.narrative_coherence.build_coherence_prompt",
        "run": "agents.narrative_coherence.run_narrative_coherence",
        "result_file": "_result_coherence.json",
        "model": "sonnet",
    },
    {
        "name": "table_read",
        "build_prompt": "agents.table_read.build_table_read_prompt",
        "run": "agents.table_read.run_table_read",
        "result_file": "_result_table_read.json",
        "model": "sonnet",
    },
]

# ─── Confidence thresholds ───────────────────────────────────────────

CONFIDENCE_THRESHOLDS = {
    "approved": 0.90,
    "review": 0.75,
    "revise": 0.60,
}

MAX_REVISION_CYCLES = _config.get("max_revision_cycles", 2)
MAX_SCENE_RETRIES = 2


# ─── System prompts ─────────────────────────────────────────────────

SYSTEM_ORCHESTRATOR = """You are the Orchestrator agent in the AI adaptation system.
You coordinate the workflow, check consistency, and control quality gates.
You NEVER write creative text — only analysis, evaluation, and control.

Current story state (meta):
{state_meta}

Current phase: {current_phase}
Task: {task_description}
"""

SYSTEM_CONTINUITY_CHECK = """Check this scene for consistency against the current state.

SCENE:
{scene_json}

CHARACTER STATES (currently known):
{character_states}

KNOWN LOCATIONS:
{known_locations}

TIMELINE POSITION:
{timeline_context}

Check points:
1. Do all mentioned characters match the character register? (Name, status, knowledge)
2. Does the location exist in the location register?
3. Are there timeline contradictions with previous scenes?
4. Are new characters or locations introduced that are not yet registered?
5. Is the emotional intensity plausible within the tension arc?

Respond as JSON:
{{
  "consistent": true/false,
  "score": 0.0-1.0,
  "flags": ["..."],
  "new_entities": {{"characters": [], "locations": []}},
  "auto_fixable": ["..."]
}}
"""


# ─── Orchestrator class ─────────────────────────────────────────────

class Orchestrator:
    """Central control of the adaptation workflow."""

    def __init__(self, config: dict, vault_path: Optional[str] = None):
        self.config = config
        self.vault_path = vault_path

    # ─── Phase management ────────────────────────────────────────

    def start_phase(self, phase_id: str) -> dict:
        """Backs up state and prepares a phase."""
        if phase_id not in STATUS_FLOW:
            raise ValueError(f"Unknown phase: {phase_id}")

        version_state(phase_id)
        state = load_state()
        state["meta"]["current_phase"] = phase_id
        state["meta"]["phase_started_at"] = datetime.now().isoformat()
        save_state(state)
        return state

    def complete_phase(self, phase_id: str) -> dict:
        """Marks a phase as completed and updates the status."""
        state = load_state()
        state["meta"]["status"] = STATUS_FLOW[phase_id]
        state["meta"]["phase_completed_at"] = datetime.now().isoformat()

        if state.get("adapted_scenes"):
            state = update_confidence_stats(state)

        save_state(state)

        # C.5: Chunks strippen wenn Phase 1 oder 2 abgeschlossen sind.
        # Nach Deep Analysis + Synthesis braucht niemand mehr den Roh-Text;
        # spart MB-State bei langen Romanen (HM 119 chunks).
        if phase_id in ("phase_1_deep_analysis", "phase_2_synthesis"):
            state = strip_chunk_text(state)

        return state

    # ─── Phase 0: Intake ─────────────────────────────────────────

    def run_intake(self, chunks: list, word_count: int) -> dict:
        """Phase 0: Loads chunks and configures project parameters.

        Honors `debug_chunks` from config: if set to an int N > 0, only the
        first N chunks are persisted. word_count + length_class still reflect
        the full source so downstream classification (novel vs. novella vs.
        short_story) stays correct — we're testing on a slice of a novel,
        not a redefined project.
        """
        state = self.start_phase("phase_0_intake")

        # C.2: Config-Override hat Vorrang vor Wortzahl-Heuristik. Adaptions-
        # Direktive aus projekt.yaml (expansion.mode) trumpft Auto-Klassifikation,
        # weil Multi-POV-Romane unter 50k Wörter (z.B. Hadji Murat 46.290)
        # sonst als novella laufen würden.
        _expansion_mode = _config.get("expansion_mode")
        _mode_to_class = {
            "short_story_to_feature": "short_story",
            "novella_to_feature": "novella",
            "novel_to_feature": "novel",
        }
        if _expansion_mode in _mode_to_class:
            length_class = _mode_to_class[_expansion_mode]
        else:
            length_class = detect_source_length_class(word_count)

        # G-Phase-G fix: Phase 0 = clean slate. Wipe downstream phase outputs
        # so repeated execution over stale state (e.g. after smoke runs) doesn't leave
        # zombie data that triggers preflight WARNs (phase_9_5_trash_detect)
        # or downstream agent confusion. Meta-config + source-related fields
        # are repopulated below.
        _DOWNSTREAM_RESET = {
            "characters": {},
            "plot": {},
            "world": {},
            "voice_profiles": {},
            "relationships": {},
            "adapted_scenes": [],
            "treatment_text": None,
            "final_script": None,
            "coverage_report": None,
            "style_validation": None,
            "narrative_coherence": None,
            "subtext_audit": None,
            "pacing_analysis": None,
            "dialog_thread_check": None,
            "table_read": None,
            "transition_map": None,
            "filmability_report": None,
            "source_fidelity_report": None,
            "continuity_log": [],
            "knowledge_gaps": [],
        }
        for _k, _default in _DOWNSTREAM_RESET.items():
            state[_k] = _default
        state["meta"]["revision_cycle"] = 0

        full_count = len(chunks)
        debug_chunks = _config.get("debug_chunks")
        if isinstance(debug_chunks, int) and debug_chunks > 0 and debug_chunks < full_count:
            chunks = chunks[:debug_chunks]
            for c in chunks:
                c["total_chunks"] = debug_chunks
            state["meta"]["debug_chunks_active"] = debug_chunks
            print(
                f"\n[DEBUG MODE] debug_chunks={debug_chunks} active — "
                f"processing {debug_chunks}/{full_count} chunks. "
                f"word_count + length_class still reflect full source.\n",
                flush=True,
            )
        else:
            # Full-Mode: explicit None to overwrite any stale debug marker
            # from a previous smoke run, so preflight mode_clarity gets a
            # clean Full-Mode signal instead of a WARN.
            state["meta"]["debug_chunks_active"] = None
        # Always record full chunk count so mode_clarity check has the
        # signal it needs (Debug-Mode: N/full or Full-Mode: full).
        state["meta"]["debug_chunks_full_count"] = full_count

        state["chunks"] = chunks
        state["meta"]["word_count"] = word_count
        state["meta"]["source_length_class"] = length_class
        # C.5: Quellpfad in State persistieren — strip_chunk_text braucht ihn
        # später für Reconstruction, _config kann zwischen Runs driften.
        state["meta"]["source_file"] = _config.get("source_file")

        # C.3: target_runtime aus Config (projekt.yaml ziel_laufzeit), Default 90.
        # HM braucht 120 (epic, 30+ Figuren), Schneesturm 90.
        state["meta"]["target_runtime_minutes"] = _config.get("target_runtime", 90)
        state["meta"]["scene_budget"] = _config.get("scene_budget", 50)

        # Creative challenge based on source text length
        if length_class == "short_story":
            state["meta"]["adaptation_challenge"] = "expansion"
            state["meta"]["expansion_note"] = (
                "Short story -> feature film: Massive creative expansion needed. "
                "Invent scenes, deepen characters, develop subplots, "
                "expand minor characters, create visual worlds."
            )
        elif length_class == "novella":
            state["meta"]["adaptation_challenge"] = "moderate"
            state["meta"]["expansion_note"] = (
                "Novella -> feature film: Moderate adaptation needed. "
                "Expand some scenes, strengthen subplots."
            )
        else:
            state["meta"]["adaptation_challenge"] = "compression"
            state["meta"]["expansion_note"] = (
                "Novel -> feature film: Compression needed. "
                "Cut subplots, merge characters, tighten."
            )

        save_state(state)
        return self.complete_phase("phase_0_intake")

    # ─── Phase 1: Story Analyst Micro-Loop (F.1) ────────────────

    def start_story_analyst(self) -> dict:
        """Phase 1 prep: backs up state, resets accumulator, marks phase active.

        Caller pattern (per-chunk dispatch):
          1. orchestrator.start_story_analyst()
          2. for each chunk_index:
               result = <subagent dispatch with build_analysis_prompt(...)>
               orchestrator.story_analyst_step(chunk_index, result, raw)
          3. orchestrator.finalize_story_analyst()
        """
        from agents.story_analyst import reset_story_analyst_progress
        self.start_phase("phase_1_deep_analysis")
        return reset_story_analyst_progress()

    def story_analyst_step(self, chunk_index: int, chunk_result: dict | None,
                           raw_output: str | None = None,
                           verbose: bool = True) -> dict:
        """Phase 1 micro-loop step — one chunk per call."""
        from agents.story_analyst import run_story_analyst_chunk
        return run_story_analyst_chunk(
            chunk_index, chunk_result,
            raw_output=raw_output, verbose=verbose,
        )

    def finalize_story_analyst(self, verbose: bool = True) -> dict:
        """Phase 1 finalize: derives acts/themes/etc., marks phase complete."""
        from agents.story_analyst import finalize_story_analyst as _finalize
        result = _finalize(verbose=verbose)
        self.complete_phase("phase_1_deep_analysis")
        return result

    # ─── Phase 3: Strategy ───────────────────────────────────────

    def build_strategy_summary(self) -> dict:
        """Prepares the strategy decision for the user."""
        state = load_state()

        subplots = state["plot"].get("subplots", [])
        subplot_summary = []
        for sp in subplots:
            subplot_summary.append({
                "id": sp.get("id"),
                "description": sp.get("description", ""),
                "priority": sp.get("priority", 0),
                "scenes_needed": sp.get("scenes_needed", 0),
                "recommendation": "keep" if sp.get("priority", 0) >= 7 else "cut",
            })

        return {
            "source_length_class": state["meta"]["source_length_class"],
            "word_count": state["meta"]["word_count"],
            "target_runtime": state["meta"]["target_runtime_minutes"],
            "scene_budget": state["meta"]["scene_budget"],
            "character_count": len(state["characters"]),
            "subplot_count": len(subplots),
            "subplots": subplot_summary,
            "themes": state["plot"].get("themes", []),
        }

    def apply_strategy(self, subplot_decisions: dict, target_runtime: Optional[int] = None,
                       scene_budget: Optional[int] = None) -> dict:
        """Applies user decisions regarding the strategy.

        scene_budget is authoritative from config (set once in run_intake,
        line 235). It is NOT auto-derived from target_runtime anymore — the
        former `target_runtime / 2` heuristic silently overwrote projekt.yaml
        values (HM used 60 per config, got clobbered to 45). Pass an explicit
        scene_budget kwarg here if a caller needs to override the config.
        """
        state = self.start_phase("phase_3_strategy")

        if target_runtime:
            state["meta"]["target_runtime_minutes"] = target_runtime
        if scene_budget is not None:
            state["meta"]["scene_budget"] = scene_budget

        for sp in state["plot"].get("subplots", []):
            sp_id = sp.get("id")
            if sp_id in subplot_decisions:
                sp["keep"] = subplot_decisions[sp_id]

        save_state(state)
        return self.complete_phase("phase_3_strategy")

    # ─── Phase 5: Adaptation Micro-Loop (F.4) ────────────────────

    def start_adaptation(self) -> dict:
        """Phase 5 prep: backs up state, resets accumulator.

        Caller pattern:
          1. orchestrator.start_adaptation()
          2. for each chunk:
               size = adaptation_agent.measure_prompt_size(prompt)
               result = <subagent dispatch>
               orchestrator.adaptation_step(chunk_index, result, raw, size)
          3. orchestrator.finalize_adaptation()
        """
        from agents.adaptation_agent import reset_adaptation_progress
        self.start_phase("phase_5_adaptation")
        return reset_adaptation_progress()

    def adaptation_step(self, chunk_index: int, chunk_result: dict | None,
                        raw_output: str | None = None,
                        prompt_size: dict | None = None,
                        verbose: bool = True) -> dict:
        """Phase 5 micro-loop step — one chunk per call (incl. continuity)."""
        from agents.adaptation_agent import run_adaptation_chunk
        return run_adaptation_chunk(
            chunk_index, chunk_result,
            raw_output=raw_output,
            orchestrator=self,
            prompt_size=prompt_size,
            verbose=verbose,
        )

    def finalize_adaptation(self, verbose: bool = True) -> dict:
        """Phase 5 finalize: persists over_cap_findings, completes phase."""
        from agents.adaptation_agent import finalize_adaptation as _finalize
        result = _finalize(verbose=verbose)
        self.complete_phase("phase_5_adaptation")
        return result

    # ─── Continuity watcher ──────────────────────────────────────

    # Drift-Pass constants (Phase L)
    _DAYTIME_TOKENS = (
        "DAY", "NIGHT", "DAWN", "DUSK",
        "MORNING", "EVENING", "AFTERNOON",
    )
    _SOFT_TIME_BRIDGES = (
        "CONTINUOUS", "LATER", "MOMENTS LATER", "SAME DAY",
    )

    def deterministic_continuity_pass(self, scene: dict) -> dict:
        """
        Pure-python continuity validation across 7 drift types (Phase L).
        Called after EVERY scene in phase 5.

        Replaces the LLM-self-reported `continuity_warning` field
        (Phase-L plan §L.3): a structured pre-pass produces the same
        signal deterministically and at zero token cost.

        Drift types covered:
          1. char_drift         — scene char missing from register
          2. location_drift     — slug location missing from register
          3. subplot_drift      — scene threads a subplot marked keep=False
          4. timeline_drift     — scene_id non-monotonic vs. previous scene
          5. day_time_drift     — slug DAY/NIGHT change without bridge
          6. cast_mention_drift — dialog speaker not in scene.characters
          7. chunk_range_drift  — source_chunks index out of range

        Returns:
            dict {
              consistent: bool,         # all 7 types passed
              score: float (0..1),      # legacy aggregate (penalty-based)
              flags: list[str],         # flat list, legacy callers
              new_entities: dict,       # auto-register candidates
              auto_fixable: list[str],  # subset of flags
              pass_per_type: dict       # per-type {passed, drifts}
            }
        """
        state = load_state()
        new_entities = {"characters": [], "locations": []}
        score = 1.0
        pass_per_type = {
            "char_drift":         {"passed": True, "drifts": []},
            "location_drift":     {"passed": True, "drifts": []},
            "subplot_drift":      {"passed": True, "drifts": []},
            "timeline_drift":     {"passed": True, "drifts": []},
            "day_time_drift":     {"passed": True, "drifts": []},
            "cast_mention_drift": {"passed": True, "drifts": []},
            "chunk_range_drift":  {"passed": True, "drifts": []},
        }

        def _flag(drift_type: str, msg: str, penalty: float):
            pass_per_type[drift_type]["drifts"].append(msg)
            pass_per_type[drift_type]["passed"] = False
            return penalty

        scene_chars_raw = _compat(scene, "characters", "figuren", []) or []
        scene_chars = [c for c in scene_chars_raw if isinstance(c, str)]
        scene_location = scene.get("slug", "") or ""
        scene_id = _compat(scene, "scene_id", "szenen_id", "?")

        # 1. Char-Drift — case-insensitive register lookup
        known_chars_lc = {
            k.lower(): k for k in state.get("characters", {}).keys()
        }
        for char in scene_chars:
            if char.lower() not in known_chars_lc:
                new_entities["characters"].append(char)
                score -= _flag(
                    "char_drift",
                    f"Unknown character: '{char}' not in register",
                    0.10,
                )

        # 2. Location-Drift — substring match against location register
        known_locations = [
            (loc.get("name", "") or "").lower()
            for loc in state.get("world", {}).get("locations", [])
        ]
        location_found = any(
            loc_name and loc_name in scene_location.lower()
            for loc_name in known_locations
        )
        if known_locations and not location_found:
            score -= _flag(
                "location_drift",
                f"Location '{scene_location}' not in register",
                0.05,
            )

        # 3. Subplot-Drift — scene threads a cut subplot
        scene_subplots = scene.get("subplot_threads", []) or []
        all_subplots = state.get("plot", {}).get("subplots", []) or []
        kept_subplots = [
            sp["id"] for sp in all_subplots if sp.get("keep", True)
        ]
        for sp in scene_subplots:
            if sp not in kept_subplots and kept_subplots:
                score -= _flag(
                    "subplot_drift",
                    f"Subplot '{sp}' was marked as 'cut' but appears in scene",
                    0.05,
                )

        # 4. Timeline-Drift — scene_id monotonicity
        adapted_scenes = state.get("adapted_scenes", []) or []
        if adapted_scenes:
            prev_id = _compat(
                adapted_scenes[-1], "scene_id", "szenen_id", "S000"
            )
            try:
                prev_n = int(str(prev_id).lstrip("Ss") or "0")
                curr_n = int(str(scene_id).lstrip("Ss") or "0")
                if curr_n <= prev_n:
                    score -= _flag(
                        "timeline_drift",
                        f"scene_id non-monotonic: {prev_id} → {scene_id}",
                        0.05,
                    )
            except (ValueError, TypeError):
                # Non-numeric IDs — silently skip (legacy projects)
                pass

        # 5. Day-Time-Drift — slug TIME jump without soft bridge
        if adapted_scenes:
            prev_slug = adapted_scenes[-1].get("slug", "") or ""
            prev_time = self._extract_time_token(prev_slug)
            curr_time = self._extract_time_token(scene_location)
            slug_upper = scene_location.upper()
            has_bridge = any(b in slug_upper for b in self._SOFT_TIME_BRIDGES)
            if prev_time and curr_time and prev_time != curr_time and not has_bridge:
                score -= _flag(
                    "day_time_drift",
                    f"day-time jump without bridge: {prev_time} → {curr_time}",
                    0.03,
                )

        # 6. Cast-Mention-Drift — dialog speaker not in scene cast
        dialog = _compat(scene, "dialog_draft", "dialog_entwurf", []) or []
        cast_set_lc = {c.lower() for c in scene_chars}
        seen_unknown_lc: set[str] = set()
        for line in dialog:
            if not isinstance(line, dict):
                continue
            speaker = (line.get("character") or "").strip()
            if not speaker:
                continue
            sp_lc = speaker.lower()
            if sp_lc in cast_set_lc or sp_lc in seen_unknown_lc:
                continue
            seen_unknown_lc.add(sp_lc)
            score -= _flag(
                "cast_mention_drift",
                f"Dialog speaker '{speaker}' not in scene cast",
                0.05,
            )

        # 7. Chunk-Range-Drift — source_chunks index out of bounds
        source_chunks = scene.get("source_chunks", []) or []
        chunk_count = len(state.get("chunks", []))
        if chunk_count > 0:
            for idx in source_chunks:
                try:
                    i = int(idx)
                    if i < 0 or i >= chunk_count:
                        score -= _flag(
                            "chunk_range_drift",
                            f"source_chunks index {i} out of range "
                            f"(0..{chunk_count-1})",
                            0.10,
                        )
                except (ValueError, TypeError):
                    score -= _flag(
                        "chunk_range_drift",
                        f"source_chunks contains non-int: {idx!r}",
                        0.10,
                    )

        # Aggregate
        flags: list[str] = []
        for type_data in pass_per_type.values():
            flags.extend(type_data["drifts"])

        score = max(0.0, min(1.0, score))

        for issue in flags:
            log_continuity_issue(issue, scene_id=scene_id)

        return {
            "consistent": all(t["passed"] for t in pass_per_type.values()),
            "score": round(score, 2),
            "flags": flags,
            "new_entities": new_entities,
            "auto_fixable": [f for f in flags if "not in register" in f],
            "pass_per_type": pass_per_type,
        }

    @classmethod
    def _extract_time_token(cls, slug: str) -> Optional[str]:
        """Extracts DAY/NIGHT/etc. token from a slugline. None if absent."""
        slug_upper = (slug or "").upper()
        for tok in cls._DAYTIME_TOKENS:
            if tok in slug_upper:
                return tok
        return None

    def continuity_check(self, scene: dict) -> dict:
        """Backward-compat wrapper for deterministic_continuity_pass.

        Pre-Phase-L this method ran 4 checks (char, location,
        timeline-stub, subplot) and returned a flat result. Phase L
        extended the pass to 7 drift types and added `pass_per_type`.
        Result shape is additive — legacy callers keep working without
        change.
        """
        return self.deterministic_continuity_pass(scene)

    def register_new_entities(self, new_entities: dict) -> None:
        """Registers automatically detected new characters/locations."""
        state = load_state()

        for char in new_entities.get("characters", []):
            if char not in state["characters"]:
                state["characters"][char] = {
                    "name": char,
                    "rolle": "unknown",
                    "erstbeschreibung": "Automatically detected by Continuity Watcher",
                    "erste_erwähnung_chunk": "auto_detected",
                    "arc_notizen": [],
                    "voice_profile": None,
                }

        for loc in new_entities.get("locations", []):
            state["world"]["locations"].append({
                "name": loc,
                "beschreibung": "Automatically detected by Continuity Watcher",
                "filmische_beschreibung": "",
                "atmosphäre": "",
                "production_notes": [],
            })

        save_state(state)

    # ─── Post-analysis cleanup ───────────────────────────────────

    def post_analysis_cleanup(self) -> dict:
        """
        Called after phase 1. Cleans up:
        1. Character duplicates (fuzzy matching)
        2. Location duplicates
        3. Themes capped at max 10
        4. Subplots capped at max 5
        5. Tension normalization (relative)
        """
        state = load_state()

        # 1. Deduplicate characters (case-insensitive)
        chars = state.get("characters", {})
        normalized = {}
        name_mapping = {}  # old_name -> canonical_name

        for name, data in chars.items():
            canonical = name.strip()
            # Check if similar name exists
            found = False
            for existing in normalized:
                if self._names_similar(canonical, existing):
                    # Merge into existing
                    normalized[existing]["arc_notizen"].extend(data.get("arc_notizen", []))
                    name_mapping[name] = existing
                    found = True
                    break
            if not found:
                normalized[canonical] = data
                normalized[canonical]["name"] = canonical
                name_mapping[name] = canonical

        state["characters"] = normalized

        # 2. Deduplicate locations
        locs = state.get("world", {}).get("locations", [])
        seen_locs = {}
        for loc in locs:
            key = loc.get("name", "").lower().strip()
            key = key.replace("dorf ", "").replace("die ", "").replace("das ", "")
            if key not in seen_locs:
                seen_locs[key] = loc
        state["world"]["locations"] = list(seen_locs.values())

        # 3. Cap themes at max 12 (by frequency/relevance)
        themes = state["plot"].get("themes", [])
        if len(themes) > 12:
            state["plot"]["themes"] = themes[:12]

        # 4. Cap subplots at max 5
        subplots = state["plot"].get("subplots", [])
        if len(subplots) > 5:
            subplots.sort(key=lambda x: x.get("priority", 0), reverse=True)
            state["plot"]["subplots"] = subplots[:5]

        # 5. Tension normalization (relative 0-1)
        tc = state["plot"].get("tension_curve", [])
        if tc:
            state["plot"]["tension_curve"] = self._normalize_tension(tc)

        save_state(state)
        return state

    @staticmethod
    def _names_similar(a: str, b: str) -> bool:
        """Checks whether two names likely refer to the same person."""
        a_lower = a.lower().strip()
        b_lower = b.lower().strip()
        if a_lower == b_lower:
            return True
        # One is a substring of the other
        if a_lower in b_lower or b_lower in a_lower:
            return True
        # Simple Levenshtein approximation (character difference)
        if abs(len(a) - len(b)) <= 2:
            matches = sum(1 for ca, cb in zip(a_lower, b_lower) if ca == cb)
            if matches >= min(len(a), len(b)) - 2:
                return True
        return False

    @staticmethod
    def _normalize_tension(tension_curve: list) -> list:
        """Normalizes tension scores to a relative range (0.0 to 1.0)."""
        if not tension_curve:
            return []
        min_t = min(tension_curve)
        max_t = max(tension_curve)
        if max_t == min_t:
            return [0.5] * len(tension_curve)
        return [round((t - min_t) / (max_t - min_t), 2) for t in tension_curve]

    # ─── Model routing ───────────────────────────────────────────

    @staticmethod
    def select_model(agent: str, context: Optional[dict] = None) -> str:
        """
        Selects the optimal model based on agent and context.
        Opus only for creative peaks, Sonnet for analysis/structure.
        """
        context = context or {}

        if agent == "deep_analysis":
            return "sonnet"

        if agent == "character_synthesis":
            return "opus"  # Voice profiles need nuance

        if agent == "dialog_impro":
            return "opus"  # Most creative part

        if agent == "world_synthesis":
            return "sonnet"

        if agent == "story_synthesis":
            return "sonnet"

        if agent == "adaptation":
            tension = context.get("tension_score", 0.5)
            is_key_scene = context.get("is_key_scene", False)
            if tension > 0.7 or is_key_scene:
                return "opus"
            return "sonnet"

        if agent == "script_writer":
            if context.get("pass_type") == "dialog_polish":
                return "opus"
            return "sonnet"

        if agent == "coverage":
            return "sonnet"  # Evaluation against defined criteria

        if agent == "style_validation":
            return "sonnet"  # Analytical consistency check

        if agent == "revision":
            return "opus"  # Creative revision needs nuance

        return "sonnet"  # Default

    # ─── Identify key scenes ─────────────────────────────────────

    def identify_key_scenes(self, tension_threshold: float = None) -> list:
        """
        Identifies emotionally important scenes for dialog impro.
        Uses tension threshold (default 0.6) — all chunks at or above get impro.
        Falls back to top-N if old config key `impro_key_scenes` is set.
        """
        from config.loader import load_config
        config = load_config()

        state = load_state()
        tension_curve = state["plot"].get("tension_curve", [])

        if not tension_curve:
            return []

        # Determine threshold: explicit arg > config threshold > fallback from count
        if tension_threshold is None:
            tension_threshold = config.get("impro_tension_threshold")
            if tension_threshold is None:
                # Backward compat: convert old count to threshold via percentile
                count = config.get("impro_key_scenes", 5)
                sorted_tensions = sorted(tension_curve, reverse=True)
                if count < len(sorted_tensions):
                    tension_threshold = sorted_tensions[count]
                else:
                    tension_threshold = 0.0

        key_chunks = []
        for idx, tension in enumerate(tension_curve):
            if tension >= tension_threshold:
                chunk_id = f"chunk_{idx + 1:03d}"
                chars_in_chunk = []
                for name, data in state["characters"].items():
                    first = data.get("erste_erwähnung_chunk", data.get("first_mention_chunk", ""))
                    first_digits = ''.join(c for c in first.replace("chunk_", "") if c.isdigit())
                    first_num = int(first_digits) if first_digits else 0
                    if first_num <= idx + 1:
                        chars_in_chunk.append(name)

                key_chunks.append({
                    "chunk_index": idx,
                    "chunk_id": chunk_id,
                    "tension_score": tension,
                    "characters_present": chars_in_chunk[:5],
                })

        key_chunks.sort(key=lambda x: x["tension_score"], reverse=True)
        return key_chunks

    # ─── Phase 4: Dialog Improvisation ────────────────────────────

    def prepare_dialog_impro(self, tension_threshold: float = None) -> list:
        """Phase 4 prep: identifies key scenes and returns dispatch bundles.

        Returns a list of scene bundles. Each bundle contains one dispatch
        task per character with a populated voice_profile in the scene.
        Characters without voice_profile are exposed under
        ``characters_without_voice_profile`` so the caller can reference
        them in the scene situation without dispatching on them.

        The caller is responsible for:
          1. For each task, calling
             ``character_agent.build_impro_prompt(...)`` with
             emotional_state / scene_goal / scene_situation derived from
             scene_context and the Phase-1 analysis.
          2. Dispatching LLM subagents (Opus recommended for impro).
          3. Aggregating results as ``{scene_key: [{character, lines, ...}]}``
             and calling ``run_dialog_impro(agent_results)`` to persist.
        """
        self.start_phase("phase_4_dialog_impro")
        state = load_state()

        key_scenes = self.identify_key_scenes(tension_threshold=tension_threshold)
        if not key_scenes:
            return []

        chunks = state.get("chunks", [])
        characters = state.get("characters", {})

        bundles = []
        for scene in key_scenes:
            idx = scene["chunk_index"]
            chunk_id = scene["chunk_id"]
            tension = scene["tension_score"]

            chunk_data = chunks[idx] if idx < len(chunks) else {}
            if idx < len(chunks):
                chunk_text = get_chunk_text_for_prompt(state, idx)
            else:
                chunk_text = ""

            chars_with_voice = []
            chars_without_voice = []
            for char_name in scene["characters_present"]:
                char_data = characters.get(char_name, {})
                if char_data.get("voice_profile"):
                    chars_with_voice.append(char_name)
                else:
                    chars_without_voice.append(char_name)

            tasks = []
            for char_name in chars_with_voice:
                others_in_scene = [c for c in chars_with_voice if c != char_name] + chars_without_voice
                tasks.append({
                    "character": char_name,
                    "voice_profile": characters[char_name]["voice_profile"],
                    "other_characters": ", ".join(others_in_scene) if others_in_scene else "(alone)",
                })

            scene_key = f"{chunk_id}_tension_{str(tension).replace('.', '_')}"

            bundles.append({
                "scene_key": scene_key,
                "chunk_id": chunk_id,
                "chunk_index": idx,
                "tension_score": tension,
                "tasks": tasks,
                "scene_context": {
                    "chunk_text": chunk_text,
                    "char_start": chunk_data.get("char_start"),
                    "char_end": chunk_data.get("char_end"),
                },
                "characters_without_voice_profile": chars_without_voice,
            })

        return bundles

    def run_dialog_impro(self, agent_results: dict) -> dict:
        """Phase 4 persist: saves dialog impro results to state.

        Mirrors the ``run_analysis_layer`` pattern: the caller dispatches
        LLM subagents externally and passes parsed results in. This method
        writes them to ``state["impro_material"]`` via the existing
        ``character_agent.run_dialog_improvisation`` and marks Phase 4 done.

        Args:
            agent_results: ``{scene_key: [{character, lines[], context}]}``

        Returns:
            Updated state with ``meta.status = "impro_done"``.
        """
        from agents.character_agent import run_dialog_improvisation
        run_dialog_improvisation(agent_results)
        return self.complete_phase("phase_4_dialog_impro")

    # ─── Revision routing ────────────────────────────────────────

    def route_revision(self, coverage_report: dict) -> list:
        """
        Analyzes coverage + style validation reports and creates revision tasks.
        Merges issues from 10 sources (8 analysis sources + scene_dedup_audit
        + document_continuity), prioritized by severity.

        Phase H: prefer ``route_revision_clustered`` as the Phase 8 default.
        It bundles issues per scene into max-5-issue clusters and applies a
        budget guard (default 6 dispatched clusters per cycle), reducing
        Phase-8 token spend ~5×. Use ``route_revision`` directly only when
        a flat per-issue list is needed (debug, custom dispatch).
        """
        state = load_state()
        revision_cycle = state["meta"].get("revision_cycle", 0)

        if revision_cycle >= MAX_REVISION_CYCLES:
            return [{
                "action": "escalate_to_user",
                "reason": f"Max revision cycles ({MAX_REVISION_CYCLES}) reached",
                "remaining_issues": coverage_report.get("top_3_issues", []),
            }]

        tasks = []

        # Coverage issues
        for issue in coverage_report.get("top_3_issues", []):
            severity = issue.get("severity", "medium")
            if severity in ("high", "critical"):
                scene_ids = issue.get("scene_ids", [])
                tasks.append({
                    "target_scenes": scene_ids,
                    "scene_ids": scene_ids,
                    "issue_type": issue.get("issue", ""),
                    "agent": "revision_agent",
                    "instruction": issue.get("instruction", ""),
                    "severity": severity,
                    "source": "coverage",
                })

        # Style validation issues
        style_validation = state.get("style_validation", {})
        for issue in style_validation.get("issues", []):
            severity = issue.get("severity", "medium")
            if severity in ("high", "critical", "medium"):
                scene_ids = [issue["scene_id"]] if issue.get("scene_id") else []
                tasks.append({
                    "target_scenes": scene_ids,
                    "scene_ids": scene_ids,
                    "issue_type": issue.get("category", "style"),
                    "agent": "revision_agent",
                    "instruction": issue.get("description", ""),
                    "severity": severity,
                    "source": "style_validation",
                })

        # Narrative coherence issues
        coherence = state.get("narrative_coherence", {})
        for thread in coherence.get("dangling_threads", []):
            tasks.append({
                "target_scenes": [],
                "scene_ids": [],
                "issue_type": "dangling_thread",
                "agent": "revision_agent",
                "instruction": thread if isinstance(thread, str) else str(thread),
                "severity": "medium",
                "source": "narrative_coherence",
            })
        for opp in coherence.get("missed_opportunities", []):
            tasks.append({
                "target_scenes": [],
                "scene_ids": [],
                "issue_type": "missed_opportunity",
                "agent": "revision_agent",
                "instruction": opp if isinstance(opp, str) else str(opp),
                "severity": "medium",
                "source": "narrative_coherence",
            })

        # Subtext audit issues — Q1.3: gated by subtext_quality_gate.
        # Only route when 70/30 fails, avg_subtext_score < 6.5, or worst-offender
        # scenes > 10% of dialog scenes. One revision task per worst-offender SCENE.
        subtext = state.get("subtext_audit", {})
        if subtext:
            from agents.subtext_auditor import subtext_quality_gate
            gate = subtext_quality_gate(subtext)
            if not gate["passes"]:
                offenders_by_scene: dict[str, list] = {}
                for off in subtext.get("worst_offenders", []):
                    sid = off.get("scene_id")
                    if not sid:
                        continue
                    offenders_by_scene.setdefault(sid, []).append(off)

                gate_reason = "; ".join(gate["reasons"])
                for sid in gate["worst_offender_scenes"]:
                    lines = offenders_by_scene.get(sid, [])
                    if lines:
                        line_summary = " | ".join(
                            f'{o.get("character","?")}: "{(o.get("line") or "")[:60]}" → {o.get("fix_suggestion","")}'
                            for o in lines[:3]
                        )
                    else:
                        line_summary = "scene_avg below 6.5 — rewrite dialog with subtext"
                    tasks.append({
                        "target_scenes": [sid],
                        "scene_ids": [sid],
                        "issue_type": "subtext_gate_fail",
                        "agent": "revision_agent",
                        "instruction": (
                            f"Subtext gate fail ({gate_reason}). "
                            f"Rewrite dialog of {sid}: {line_summary}"
                        ),
                        "severity": "high",
                        "source": "subtext_audit",
                    })

        # Dialog thread issues
        thread_check = state.get("dialog_thread_check", {})
        for thread in thread_check.get("threads", []):
            for issue in thread.get("issues", []):
                if issue.get("severity") in ("high", "critical"):
                    scene_ids = [issue.get("from_scene", ""), issue.get("to_scene", "")]
                    tasks.append({
                        "target_scenes": scene_ids,
                        "scene_ids": scene_ids,
                        "issue_type": issue.get("issue_type", "dialog_continuity"),
                        "agent": "revision_agent",
                        "instruction": issue.get("description", ""),
                        "severity": issue.get("severity", "medium"),
                        "source": "dialog_thread_check",
                    })

        # Table-read dead lines
        table_read = state.get("table_read", {})
        for scene_data in table_read.get("scenes", []):
            for dead in scene_data.get("dead_lines", []):
                scene_ids = [scene_data.get("scene_id", "")]
                tasks.append({
                    "target_scenes": scene_ids,
                    "scene_ids": scene_ids,
                    "issue_type": "dead_line",
                    "agent": "revision_agent",
                    "instruction": f"{dead.get('character', '?')}: \"{dead.get('line', '')[:60]}\" — {dead.get('issue', '')}. Rewrite: {dead.get('rewrite', '')}",
                    "severity": "medium",
                    "source": "table_read",
                })

        # Transition mapper high-priority proposals
        transitions = state.get("transition_map", {})
        for t in transitions.get("transitions", []):
            if t.get("priority") == "high":
                scene_ids = [t.get("from_scene", ""), t.get("to_scene", "")]
                tasks.append({
                    "target_scenes": scene_ids,
                    "scene_ids": scene_ids,
                    "issue_type": "transition_improvement",
                    "agent": "revision_agent",
                    "instruction": f"{t.get('proposed_type', '?')}: {t.get('proposal', '')}",
                    "severity": "medium",
                    "source": "transition_mapper",
                })

        # Pacing cut suggestions — Q1.4: gated by pacing_quality_gate.
        # Routes only when pacing_score < 70 OR a dead zone exceeds 5min.
        # Each dead zone >5min becomes a dedicated per-zone revision task;
        # cut_suggestions are then routed as supporting tasks. Missing act
        # tags emit a continuity_log warning but do not block revision.
        pacing = state.get("pacing_analysis", {})
        if pacing:
            from agents.pacing_analyzer import pacing_quality_gate
            p_gate = pacing_quality_gate(state)
            if p_gate["missing_act_tags"]:
                log_continuity_issue(
                    "Pacing Q1.4 WARN: scenes without act tag — "
                    f"{p_gate['untagged_scene_ids'][:8]}"
                )
            if not p_gate["passes"]:
                gate_reason = "; ".join(p_gate["reasons"])
                for zone in p_gate["long_dead_zones"]:
                    sid_start = zone.get("start", "")
                    sid_end = zone.get("end", "")
                    scene_ids = [s for s in (sid_start, sid_end) if s]
                    tasks.append({
                        "target_scenes": scene_ids,
                        "scene_ids": scene_ids,
                        "issue_type": "pacing_dead_zone",
                        "agent": "revision_agent",
                        "instruction": (
                            f"Dead zone {sid_start}–{sid_end} runs "
                            f"{zone.get('duration_minutes','?')} min ("
                            f"{zone.get('scene_count','?')} scenes). "
                            "Compress or cut to restore momentum."
                        ),
                        "severity": "high",
                        "source": "pacing_analyzer",
                    })
                for cut in pacing.get("cut_suggestions", []):
                    tasks.append({
                        "target_scenes": [],
                        "scene_ids": [],
                        "issue_type": "pacing_cut",
                        "agent": "revision_agent",
                        "instruction": (
                            f"Pacing-gate fail ({gate_reason}). "
                            f"{cut if isinstance(cut, str) else str(cut)}"
                        ),
                        "severity": "medium",
                        "source": "pacing_analyzer",
                    })

        # Scene-dedup audit (Phase D.1) — near-duplicate pairs flagged by
        # the heuristic detector; each becomes a MERGE_SCENES revision task.
        dedup = state.get("scene_dedup_audit", {})
        for cand in dedup.get("dedup_candidates", []):
            scene_ids = cand.get("scene_pair", [])
            tasks.append({
                "target_scenes": scene_ids,
                "scene_ids": scene_ids,
                "issue_type": "scene_duplicate",
                "agent": "revision_agent",
                "instruction": (
                    f"MERGE_SCENES candidates {scene_ids}: {cand.get('reason','')}. "
                    "Collapse into one beat; preserve strongest dialog + distinct "
                    "action from both; drop the weaker scene_id from adapted_scenes."
                ),
                "severity": "high",
                "source": "scene_dedup_audit",
            })

        # Document-level continuity check (Phase E) — contradictions found
        # by document_continuity_checker on the assembled/transformed final
        # text; each confirmed finding becomes a targeted revision task.
        doc_check = state.get("document_continuity_check", {})
        for finding in doc_check.get("findings", []):
            scene_ids = [str(s) for s in finding.get("scenes", [])]
            tasks.append({
                "target_scenes": scene_ids,
                "scene_ids": scene_ids,
                "issue_type": finding.get("type", "document_continuity"),
                "agent": "revision_agent",
                "instruction": (
                    f"{finding.get('description', '')} "
                    f"Evidence: {' | '.join(finding.get('evidence_quotes', []))}"
                ).strip(),
                "severity": finding.get("severity", "medium"),
                "source": "document_continuity",
            })

        # Increment revision cycle
        state["meta"]["revision_cycle"] = revision_cycle + 1
        save_state(state)

        return tasks

    # ─── Phase 8 Revision Clustering (F.6) ───────────────────────

    _SEVERITY_RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0}

    @classmethod
    def cluster_revision_tasks(cls, tasks: list,
                               max_per_cluster: int = 5) -> list:
        """Phase F.6 — collapse per-issue revision tasks into per-scene clusters.

        Input: ``route_revision()`` flat task list — one entry per issue.
        Output: clustered task list — one entry per scene-key, up to
        ``max_per_cluster`` issues each. A scene-key with > max_per_cluster
        issues splits into multiple clusters (severity-sorted: critical/high
        before medium/low so the first cluster carries the most-impactful
        bundle).

        Cluster shape:
            {
                target_scenes / scene_ids: list[str],
                agent: "revision_agent",
                issues: [{issue_type, instruction, severity, source}, ...],
                severity: <max severity in this cluster>,
                instruction: <numbered, source-tagged merge>,
                sources: sorted list of source agents,
                cluster_part: 1-based index when scene-key splits, else None,
            }

        Escalation tasks (``action == "escalate_to_user"``) pass through unchanged.
        Empty input returns empty list. Pure function.

        Token impact (HM target): each Opus revision call is 25-40 KB prompt;
        clustering 30 issues into 6 clusters reduces from ~30 calls to ~6 —
        a 5× reduction on the revision hot-path.
        """
        if not tasks:
            return []

        groups: dict = {}
        passthrough: list = []
        rank = cls._SEVERITY_RANK

        for t in tasks:
            if t.get("action") == "escalate_to_user":
                passthrough.append(t)
                continue
            sids = tuple(sorted(s for s in (t.get("scene_ids") or []) if s))
            groups.setdefault(sids, []).append(t)

        clusters: list = []
        for sids, items in groups.items():
            items_sorted = sorted(
                items,
                key=lambda x: -rank.get((x.get("severity") or "medium"), 1),
            )
            n_parts = (len(items_sorted) + max_per_cluster - 1) // max_per_cluster
            for part_idx in range(0, len(items_sorted), max_per_cluster):
                chunk = items_sorted[part_idx:part_idx + max_per_cluster]
                instr_lines = []
                for n, t in enumerate(chunk, 1):
                    instr_lines.append(
                        f"{n}. [{t.get('source','?')}/{t.get('issue_type','?')}] "
                        f"{t.get('instruction','')}"
                    )
                max_sev = max(
                    (t.get("severity") or "medium" for t in chunk),
                    key=lambda x: rank.get(x, 1),
                )
                clusters.append({
                    "target_scenes": list(sids),
                    "scene_ids": list(sids),
                    "agent": "revision_agent",
                    "issues": [
                        {
                            "issue_type": t.get("issue_type"),
                            "instruction": t.get("instruction"),
                            "severity": t.get("severity"),
                            "source": t.get("source"),
                        }
                        for t in chunk
                    ],
                    "severity": max_sev,
                    "instruction": "\n".join(instr_lines),
                    "sources": sorted({t.get("source") or "?" for t in chunk}),
                    "cluster_part": (part_idx // max_per_cluster) + 1
                    if n_parts > 1 else None,
                })

        # Sort cluster output deterministically: by severity desc, then scene_ids
        clusters.sort(
            key=lambda c: (
                -rank.get(c["severity"] or "medium", 1),
                tuple(c["scene_ids"]),
                c.get("cluster_part") or 0,
            )
        )
        return clusters + passthrough

    # Phase H budget-guard defaults (Phase H.2)
    _DEFAULT_MAX_REVISION_CALLS = 6
    _DEFAULT_MAX_TOKENS_PER_CLUSTER = 30_000

    @classmethod
    def _estimate_cluster_tokens(cls, cluster: dict) -> int:
        """H'' Phase D / P1.3 — estimate Opus revision-prompt tokens for one cluster.

        Reuses ``revision_agent.build_revision_prompt`` to produce the
        actual prompt that Phase 8 would dispatch, then divides chars by 4
        (conservative chars/token ratio used elsewhere in the pipeline).

        Cluster["issues"] entries lack scene_ids — those live at cluster
        top-level. We rehydrate before calling the builder so the prompt
        renders the same scene-context block as a real dispatch.
        """
        from agents.revision_agent import build_revision_prompt
        sids = cluster.get("scene_ids") or cluster.get("target_scenes") or []
        rehydrated = []
        for issue in cluster.get("issues") or []:
            rehydrated.append({
                **issue,
                "scene_ids": list(sids),
                "description": issue.get("instruction", ""),
                "category": issue.get("category") or issue.get("issue_type"),
            })
        if not rehydrated:
            # Empty cluster — render a synthetic single-issue placeholder so
            # the builder still produces meaningful scene-context overhead.
            rehydrated = [{
                "scene_ids": list(sids),
                "description": cluster.get("instruction", ""),
                "severity": cluster.get("severity", "medium"),
            }]
        prompt = build_revision_prompt(rehydrated)
        return len(prompt) // 4

    @classmethod
    def _enforce_cluster_token_budget(
        cls,
        clustered: list,
        max_per_cluster: int,
        max_tokens: int,
    ) -> list:
        """H'' Phase D / P1.3 — split oversize clusters or escalate.

        For each cluster whose estimated tokens exceed ``max_tokens``:
          1. Rehydrate its issues into route-shape tasks.
          2. Re-cluster with progressively smaller ``max_per_cluster``
             (down to 1) until every sub-cluster fits.
          3. If even single-issue clusters exceed the budget, replace the
             whole cluster with an ``action="escalate_to_user"`` task —
             the prompt itself is structurally too large (e.g. extreme
             scene-context) and needs human triage.

        Passthrough tasks (escalations from upstream) flow through
        unchanged. Pure function — no state mutation.
        """
        out: list = []
        for cluster in clustered:
            if cluster.get("agent") != "revision_agent":
                out.append(cluster)
                continue
            est = cls._estimate_cluster_tokens(cluster)
            if est <= max_tokens:
                out.append(cluster)
                continue
            sids = cluster.get("scene_ids") or []
            rehydrated_tasks = []
            for issue in cluster.get("issues") or []:
                rehydrated_tasks.append({
                    "scene_ids": list(sids),
                    "target_scenes": list(sids),
                    "agent": "revision_agent",
                    **issue,
                })
            split_done = False
            new_per_cluster = max(1, max_per_cluster - 1)
            while new_per_cluster >= 1:
                sub_clusters = cls.cluster_revision_tasks(
                    rehydrated_tasks, max_per_cluster=new_per_cluster
                )
                sub_est = [cls._estimate_cluster_tokens(sc) for sc in sub_clusters]
                if sub_est and all(e <= max_tokens for e in sub_est):
                    out.extend(sub_clusters)
                    split_done = True
                    break
                new_per_cluster -= 1
            if not split_done:
                out.append({
                    "action": "escalate_to_user",
                    "scene_ids": list(sids),
                    "target_scenes": list(sids),
                    "agent": "user",
                    "severity": cluster.get("severity"),
                    "reason": (
                        f"Revision cluster exceeds {max_tokens}-token budget "
                        f"(est {est} tokens, {len(cluster.get('issues') or [])} "
                        f"issues, scenes={list(sids)}). Even single-issue "
                        f"split overflows — requires manual triage."
                    ),
                    "sources": cluster.get("sources", []),
                    "issues": cluster.get("issues", []),
                })
        return out

    def route_revision_clustered(self, coverage_report: dict,
                                 max_per_cluster: int = 5,
                                 max_calls: int | None = None,
                                 enforce_token_limit: bool = True,
                                 max_tokens_per_cluster: int | None = None) -> list:
        """Phase F.6 + H.2 + H'' P1.3 — DEFAULT entry point for Phase 8 dispatch.

        Runs ``route_revision`` to collect issues from all 10 sources, then
        clusters by scene-key (max_per_cluster issues per cluster). When the
        cluster count exceeds ``max_calls``, drops the lowest-severity
        clusters and logs them in ``state["revision_budget_log"]`` so the
        reduction is auditable post-run.

        H'' P1.3: when ``enforce_token_limit`` is True (default), each
        cluster's prompt size is estimated via ``build_revision_prompt``;
        oversize clusters are split into smaller bundles or replaced with
        an ``escalate_to_user`` task. Capsule docs/context-capsules/H.md
        previously documented the limit as "NICHT enforced" — now enforced.

        Escalation tasks (action == "escalate_to_user") always pass through.

        Args:
            coverage_report: dict with top_3_issues etc.
            max_per_cluster: max issues bundled into one Opus revision call
                (default 5).
            max_calls: hard cap on dispatched cluster count (default
                ``_DEFAULT_MAX_REVISION_CALLS`` = 6). Set None to keep
                F.6 unbounded behaviour.
            enforce_token_limit: when True, split/escalate oversize
                clusters via ``_enforce_cluster_token_budget``. Default
                True. Set False to revert to pre-P1.3 behaviour.
            max_tokens_per_cluster: token budget per cluster (default
                ``_DEFAULT_MAX_TOKENS_PER_CLUSTER`` = 30_000).

        Returns:
            list of cluster-tasks + passthrough escalations, deterministic
            order. Total cluster count <= max_calls (when set).

        Use this in Phase 8 dispatchers. Raw per-issue ``route_revision`` is
        still available for callers that prefer flat task lists.
        """
        flat = self.route_revision(coverage_report)
        clustered = self.cluster_revision_tasks(
            flat, max_per_cluster=max_per_cluster
        )

        if enforce_token_limit:
            if max_tokens_per_cluster is None:
                max_tokens_per_cluster = self._DEFAULT_MAX_TOKENS_PER_CLUSTER
            clustered = self._enforce_cluster_token_budget(
                clustered, max_per_cluster, max_tokens_per_cluster
            )

        if max_calls is None:
            max_calls = self._DEFAULT_MAX_REVISION_CALLS

        # Split passthrough (escalations) from clusterable tasks
        cluster_tasks = [c for c in clustered if c.get("agent") == "revision_agent"]
        passthrough = [c for c in clustered if c.get("agent") != "revision_agent"]

        if max_calls > 0 and len(cluster_tasks) > max_calls:
            # cluster_revision_tasks returns severity-sorted desc already.
            kept = cluster_tasks[:max_calls]
            dropped = cluster_tasks[max_calls:]

            state = load_state()
            log = state.setdefault("revision_budget_log", [])
            log.append({
                "timestamp": datetime.now().isoformat(),
                "revision_cycle": state["meta"].get("revision_cycle", 0),
                "max_calls": max_calls,
                "total_clusters": len(cluster_tasks),
                "dropped_count": len(dropped),
                "dropped_clusters": [
                    {
                        "scene_ids": d.get("scene_ids", []),
                        "severity": d.get("severity"),
                        "issue_count": len(d.get("issues", [])),
                        "sources": d.get("sources", []),
                    }
                    for d in dropped
                ],
            })
            save_state(state)

            return kept + passthrough

        return clustered

    # ─── Chunk batching (cost optimization) ──────────────────────

    def create_adaptation_batches(self) -> list:
        """
        Creates optimized batches for the adaptation phase.
        High-tension chunks processed individually, low-tension in batches of 2-3.
        """
        state = load_state()
        chunks = state.get("chunks", [])
        tension_curve = state["plot"].get("tension_curve", [])

        # If no tension data, process all individually
        if not tension_curve or len(tension_curve) != len(chunks):
            return [[c] for c in chunks]

        batches = []
        low_tension_buffer = []

        for i, chunk in enumerate(chunks):
            tension = tension_curve[i] if i < len(tension_curve) else 0.5

            if tension > 0.7:
                # High tension: flush buffer first, then process individually
                if low_tension_buffer:
                    batches.append(low_tension_buffer)
                    low_tension_buffer = []
                batches.append([chunk])
            else:
                low_tension_buffer.append(chunk)
                if len(low_tension_buffer) >= 3:
                    batches.append(low_tension_buffer)
                    low_tension_buffer = []

        if low_tension_buffer:
            batches.append(low_tension_buffer)

        return batches

    # ─── Phase 9.5: Analysis Layer ─────────────────────────────────

    def get_analysis_agent_specs(self) -> list:
        """Returns the ANALYSIS_AGENTS spec list for external dispatch.

        Each entry has: name, build_prompt (dotted path), run (dotted path),
        result_file, model. The caller (Claude Code subagent or main.py)
        is responsible for:
          1. Calling build_prompt() to get the prompt string
          2. Sending it to the LLM (model specified in spec)
          3. Parsing the JSON response
          4. Calling run(result_dict) to persist into state
          5. Saving the raw result to state/<result_file>
        """
        return list(ANALYSIS_AGENTS)

    def prepare_analysis_brief(self, save: bool = True) -> dict:
        """Phase F.5 — generate analysis_brief.json before parallel dispatch.

        Builds a compact briefing (logline, acts, scene_index,
        character_arcs, top_risk_scenes, excerpt_pointers) from current
        state and persists to ``state["analysis_brief"]`` so the 6 Phase-9.5
        agents can read structure from the brief and only fetch
        per-scene excerpts via ``excerpt_for_scene`` rather than re-reading
        the full screenplay.

        Returns the brief dict. Pure read when save=False.
        """
        from state_store import build_analysis_brief
        state = load_state()
        brief = build_analysis_brief(state)
        if save:
            state["analysis_brief"] = brief
            save_state(state)
        return brief

    def run_analysis_layer(self, agent_results: dict, verbose: bool = True) -> dict:
        """
        Runs Phase 9.5: applies pre-computed analysis results to state.

        This method does NOT call the LLM. It expects the caller to have
        already obtained results (via subagent dispatch or SDK calls) and
        passes them in as a dict keyed by agent name.

        Phase F.5: ensures ``state["analysis_brief"]`` is populated before
        dispatch (idempotent — re-builds whenever called). Agents that
        consume the brief look it up via ``state_store.excerpt_for_scene``.

        Args:
            agent_results: Dict mapping agent name to parsed LLM result dict.
                Example: {"pacing_analyzer": {...}, "subtext_auditor": {...}, ...}

        Returns:
            Updated state dict.
        """
        import json
        from importlib import import_module

        # F.5: brief is always fresh at dispatch time
        self.prepare_analysis_brief(save=True)

        state = self.start_phase("phase_9_5_analysis")

        for spec in ANALYSIS_AGENTS:
            name = spec["name"]
            result = agent_results.get(name)
            if result is None:
                if verbose:
                    print(f"  ⚠ {name}: no result provided, skipping")
                continue

            # Resolve and call the run function
            module_path, func_name = spec["run"].rsplit(".", 1)
            module = import_module(module_path)
            run_fn = getattr(module, func_name)
            run_fn(result, verbose=verbose)

            # Save raw result to state/<result_file>
            result_path = os.path.join("state", spec["result_file"])
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            if verbose:
                print(f"  ✓ {name}: result applied + saved to {result_path}")

        return self.complete_phase("phase_9_5_analysis")

    # ─── Status summary ──────────────────────────────────────────

    def get_status_summary(self) -> dict:
        """Compact status overview for the user."""
        state = load_state()
        return {
            "title": state["meta"]["title"],
            "status": state["meta"]["status"],
            "current_phase": state["meta"].get("current_phase", "—"),
            "word_count": state["meta"].get("word_count"),
            "source_class": state["meta"].get("source_length_class"),
            "target_runtime": state["meta"].get("target_runtime_minutes"),
            "scene_budget": state["meta"].get("scene_budget"),
            "scenes_done": len(state.get("adapted_scenes", [])),
            "characters": len(state.get("characters", {})),
            "locations": len(state["world"].get("locations", [])),
            "open_flags": sum(1 for i in state.get("continuity_log", []) if not i.get("resolved")),
            "confidence_stats": state.get("confidence_stats", {}),
            "revision_cycle": state["meta"].get("revision_cycle", 0),
            "coverage_verdict": (state.get("coverage_report") or {}).get("overall_verdict"),
        }
