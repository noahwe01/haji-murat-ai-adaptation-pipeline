"""
DIALOG THREAD CHECKER
=====================
Checks dialog continuity across consecutive scenes for each character.
Detects unjustified mood shifts, broken promises, and missing callbacks.

Hybrid: Pure Python (thread extraction) + LLM (continuity evaluation).

Model: Sonnet (analytical)
Integration: After script_writer, before coverage.
"""

import json
from datetime import datetime
from state_store import load_state, save_state, _compat, build_scene_graph
from utils.schema_caps import apply_caps, record_findings


# ─── Pure Python: Extract dialog threads ──────────────────────────────

def extract_dialog_threads() -> dict:
    """Extracts consecutive dialog appearances per character.

    Returns dict: {character_name: [{scene_id, lines, emotional_core}, ...]}
    Uses the scene graph for efficient lookup.
    """
    state = load_state()
    scenes = state.get("adapted_scenes", [])
    graph = build_scene_graph(state)

    threads = {}
    for char, scene_ids in graph["character_scenes"].items():
        appearances = []
        for scene in scenes:
            sid = _compat(scene, "scene_id", "szenen_id", "?")
            if sid not in scene_ids:
                continue
            dialog = scene.get("dialog_draft", scene.get("dialog_hinweise", []))
            char_lines = [
                d for d in dialog
                if d.get("character", "").lower() == char.lower()
            ]
            if char_lines:
                appearances.append({
                    "scene_id": sid,
                    "slug": scene.get("slug", ""),
                    "lines": [d.get("line", d.get("text", "")) for d in char_lines],
                    "subtext": [d.get("subtext", "") for d in char_lines],
                    "emotional_core": scene.get("emotional_core", ""),
                })
        if len(appearances) >= 2:
            threads[char] = appearances

    return threads


# ─── LLM Prompt ───────────────────────────────────────────────────────

SYSTEM_THREAD_CHECK = """You are a script continuity specialist focused on DIALOG THREADS.
You check whether characters' dialog flows logically across consecutive scenes.

CHARACTER DIALOG THREADS:
{threads_text}

VOICE PROFILES:
{voice_profiles}

───────────────────────────────────────────────

For each character thread, check:

1. **EMOTIONAL CONTINUITY**: When a character is devastated in scene A, they can't be
   cheerful in scene B without a REASON shown on screen. Flag unjustified shifts.

2. **PROMISES & CALLBACKS**: If a character says "I'll come back" in scene A, does
   another scene show whether they did? Flag unresolved promises.

3. **ESCALATION LOGIC**: Characters should escalate OR de-escalate across scenes.
   Random emotional fluctuation = bad writing. Flag scenes where the arc stutters.

4. **VOICE DRIFT**: Does the character sound like the SAME person across all scenes?
   Or do they lose their verbal tics, vocabulary level, sentence patterns?

5. **INFORMATION CONSISTENCY**: Does the character ever say something that contradicts
   what they said in a previous scene? (Unless the contradiction is intentional.)

OUTPUT as valid JSON:
{{
  "threads": [
    {{
      "character": "Maria",
      "scene_count": 15,
      "continuity_score": 85,
      "issues": [
        {{
          "from_scene": "S012",
          "to_scene": "S013",
          "issue_type": "unjustified_mood_shift",
          "description": "Maria is devastated in S012 but composed in S013 with no transition",
          "severity": "high",
          "fix_suggestion": "Add a beat showing passage of time, or show her composing herself"
        }}
      ],
      "strongest_thread": "S038→S042: Maria's gradual opening to Bourmin — perfectly escalated",
      "voice_consistency": 90
    }}
  ],
  "unresolved_promises": [
    {{
      "scene_id": "S008",
      "character": "Vladimir",
      "promise": "I will find a way",
      "resolved": false,
      "resolution_scene": null
    }}
  ],
  "overall_continuity_score": 82,
  "critical_breaks": 1
}}"""


def build_thread_check_prompt() -> str:
    """Builds the dialog thread checking prompt."""
    from agents.script_writer import get_voice_profiles_for_prompt
    from utils.skill_loader import load_skills_for_agent

    threads = extract_dialog_threads()

    # Format threads compactly
    thread_parts = []
    for char, appearances in threads.items():
        thread_parts.append(f"\n{'='*40}\nCHARACTER: {char} ({len(appearances)} scenes)")
        for app in appearances:
            thread_parts.append(f"\n  [{app['scene_id']}] {app['slug']}")
            thread_parts.append(f"  Emotional core: {app['emotional_core']}")
            for i, line in enumerate(app['lines']):
                sub = app['subtext'][i] if i < len(app['subtext']) else ""
                thread_parts.append(f"    \"{line}\"")
                if sub:
                    thread_parts.append(f"      → subtext: {sub}")

    threads_text = "\n".join(thread_parts)
    if len(threads_text) > 35000:
        threads_text = threads_text[:35000] + "\n\n[TRUNCATED]"

    # Phase D: thread checker only needs voice tics + patterns — compact suffices.
    voice_profiles = get_voice_profiles_for_prompt(compact=True)

    prompt = SYSTEM_THREAD_CHECK.format(
        threads_text=threads_text,
        voice_profiles=voice_profiles,
    )

    skills = load_skills_for_agent("dialog_thread_checker")
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


def run_thread_check(result: dict, verbose: bool = True) -> dict:
    """Processes the dialog thread check result."""
    report = {
        "threads": result.get("threads", []),
        "unresolved_promises": result.get("unresolved_promises", []),
        "overall_continuity_score": result.get("overall_continuity_score", 0),
        "critical_breaks": result.get("critical_breaks", 0),
        "checked_at": datetime.now().isoformat(),
    }

    state = load_state()
    state["dialog_thread_check"] = report
    cap_findings = apply_caps(state, "quality_gate", sub_path="dialog_thread_check", mode="hard")
    if cap_findings:
        record_findings(state, agent="dialog_thread_checker", phase="9_5_threads", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"DIALOG THREAD CHECK")
        print(f"{'='*60}")
        print(f"  Overall continuity: {report['overall_continuity_score']}/100")
        print(f"  Critical breaks:    {report['critical_breaks']}")
        print(f"  Unresolved promises: {len(report['unresolved_promises'])}")
        for t in report['threads']:
            issues = len(t.get('issues', []))
            print(f"  {t['character']:20s} {t.get('continuity_score', '?')}/100  "
                  f"({issues} issues, voice: {t.get('voice_consistency', '?')})")
        print(f"{'='*60}\n")

    return report
