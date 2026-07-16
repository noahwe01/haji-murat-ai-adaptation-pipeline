"""
TRANSITION MAPPER
=================
Analyzes all scene transitions and proposes thematic connections.
Match cuts, sound bridges, contrast cuts, visual rhymes.

Professional screenplays use transitions as invisible storytelling —
they encode pacing and theme between scenes, not just within them.

Model: Sonnet (analytical with creative suggestions)
Integration: Post-pass after script_writer, before coverage.
"""

import json
from datetime import datetime
from state_store import load_state, save_state, _compat
from utils.schema_caps import apply_caps, record_findings


SYSTEM_TRANSITIONS = """You are a film editor and transition architect. You analyze
scene-to-scene connections and design transitions that do THEMATIC WORK.

Good transitions are invisible storytelling: they encode pacing, theme, and emotion
between scenes — not just within them.

SCENE PAIRS (consecutive scenes):
{scene_pairs}

DECLARED THEMES:
{themes}

STYLE / REFERENCE FILMS:
{style_brief}

───────────────────────────────────────────────

For each scene pair, evaluate the current transition and propose improvements:

TRANSITION TYPES (from strongest to simplest):
- **MATCH CUT**: Visual element connects two scenes (bone → spaceship, letter → newspaper)
- **SOUND BRIDGE**: Audio from next scene bleeds into current (church bells over departure)
- **CONTRAST CUT**: Opposite moods slam together (wedding → funeral, laughter → weeping)
- **VISUAL RHYME**: Same composition, different context (Maria at window in Act I → Act III)
- **THEMATIC CUT**: Same idea, different situation (two characters lying in parallel)
- **QUESTION CUT**: Scene ends with unresolved tension, next scene answers (or doesn't)
- **SMASH CUT**: Hard, unexpected jump for shock or comedy
- **TIME CUT**: Same location, different time (season change, aging)
- **SIMPLE CUT**: No special technique — just move forward (use sparingly)

RULES:
1. At least 30% of transitions should use a technique (not all SIMPLE CUT)
2. Act breaks deserve the strongest transitions (match cuts, contrast cuts)
3. Recurring motifs (snow, letters, the willow) should connect distant scenes
4. Transitions set pacing rhythm — fast cuts for tension, slow dissolves for reflection

OUTPUT as valid JSON:
{{
  "transitions": [
    {{
      "from_scene": "S015",
      "to_scene": "S016",
      "current_transition": "CUT TO:",
      "proposed_type": "sound_bridge",
      "proposal": "Maria's sob carries over into the howling wind of the next scene",
      "thematic_link": "Personal grief → Nature's indifference",
      "priority": "high"
    }}
  ],
  "act_break_transitions": [
    {{
      "break": "Act I → Act II",
      "from_scene": "S012",
      "to_scene": "S013",
      "proposed_type": "match_cut",
      "proposal": "Maria's hand releasing Vladimir's → same hand releasing a letter into the fire"
    }}
  ],
  "motif_connections": [
    {{
      "motif": "snow",
      "scenes_connected": ["S001", "S018", "S045"],
      "visual_rhyme": "Snow as barrier (S001) → snow as erasure (S018) → snow as peace (S045)"
    }}
  ],
  "stats": {{
    "total_transitions": 44,
    "technique_transitions": 15,
    "technique_pct": 34,
    "simple_cuts": 29
  }}
}}"""


def build_transition_prompt() -> str:
    """Builds the transition mapping prompt from consecutive scene pairs."""
    from utils.skill_loader import load_skills_for_agent

    state = load_state()
    scenes = state.get("adapted_scenes", [])
    plot = state.get("plot", {})
    style = state.get("style_manifest", {})

    # Build scene pairs (consecutive)
    pair_parts = []
    for i in range(len(scenes) - 1):
        s1 = scenes[i]
        s2 = scenes[i + 1]
        sid1 = _compat(s1, "scene_id", "szenen_id", "?")
        sid2 = _compat(s2, "scene_id", "szenen_id", "?")

        # Last line of scene 1
        action1 = _compat(s1, "action", "handlung", "")
        last_line1 = action1.split(".")[-2].strip() + "." if "." in action1 else action1[-100:]

        # First line of scene 2
        action2 = _compat(s2, "action", "handlung", "")
        first_line2 = action2.split(".")[0].strip() + "." if "." in action2 else action2[:100]

        transition = s1.get("transition", "CUT TO:")
        act1 = s1.get("act", "")
        act2 = s2.get("act", "")
        act_break = f" *** ACT BREAK: {act1} → {act2} ***" if act1 != act2 and act1 and act2 else ""

        pair_parts.append(
            f"[{sid1} → {sid2}]{act_break}\n"
            f"  End: {s1.get('slug', '')} — \"{last_line1[:120]}\"\n"
            f"  Emotional: {s1.get('emotional_core', '?')}\n"
            f"  ---({transition})---\n"
            f"  Start: {s2.get('slug', '')} — \"{first_line2[:120]}\"\n"
            f"  Emotional: {s2.get('emotional_core', '?')}"
        )

    pairs_text = "\n\n".join(pair_parts)
    if len(pairs_text) > 30000:
        pairs_text = pairs_text[:30000] + "\n\n[TRUNCATED]"

    # Themes and style
    themes = ", ".join(plot.get("themes", [])) if plot.get("themes") else "?"
    style_parts = []
    if style.get("genre"):
        style_parts.append(f"Genre: {style['genre']}")
    refs = style.get("referenzfilme", style.get("reference_films", []))
    if refs:
        style_parts.append(f"Reference films: {', '.join(refs)}")

    prompt = SYSTEM_TRANSITIONS.format(
        scene_pairs=pairs_text,
        themes=themes,
        style_brief="\n".join(style_parts) if style_parts else "?",
    )

    skills = load_skills_for_agent("transition_mapper")
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


def run_transition_mapper(result: dict, verbose: bool = True) -> dict:
    """Processes the transition mapping result."""
    stats = result.get("stats", {})
    report = {
        "transitions": result.get("transitions", []),
        "act_break_transitions": result.get("act_break_transitions", []),
        "motif_connections": result.get("motif_connections", []),
        "stats": stats,
        "mapped_at": datetime.now().isoformat(),
    }

    state = load_state()
    state["transition_map"] = report
    cap_findings = apply_caps(state, "quality_gate", sub_path="transition_map", mode="hard")
    if cap_findings:
        record_findings(state, agent="transition_mapper", phase="9_5_transitions", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"TRANSITION MAP")
        print(f"{'='*60}")
        print(f"  Total transitions:   {stats.get('total_transitions', '?')}")
        print(f"  With technique:      {stats.get('technique_transitions', '?')} "
              f"({stats.get('technique_pct', '?')}%)")
        print(f"  Act break proposals: {len(report['act_break_transitions'])}")
        print(f"  Motif connections:   {len(report['motif_connections'])}")
        high_prio = [t for t in report['transitions'] if t.get('priority') == 'high']
        print(f"  High-priority:       {len(high_prio)}")
        print(f"{'='*60}\n")

    return report
