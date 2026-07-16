"""
TABLE-READ SIMULATION
=====================
Simulates how dialog would play when spoken aloud by actors.
Tests for speakability, rhythm, breath marks, and performance range.

Real screenplays are tested by actors at table reads. This agent
simulates that process — catching lines that read well on paper
but play flat when performed.

Model: Opus (needs performance intuition)
Integration: After dialog polish, before coverage.
"""

import json
from datetime import datetime
from state_store import load_state, save_state, _compat
from utils.schema_caps import apply_caps, record_findings


SYSTEM_TABLE_READ = """You are a veteran casting director and acting coach conducting
a table read of this screenplay. You read each scene aloud in your mind —
hearing how actors would deliver these lines.

VOICE PROFILES:
{voice_profiles}

SCREENPLAY DIALOG (key scenes):
{dialog_text}

───────────────────────────────────────────────

Test every line for PERFORMANCE QUALITY:

1. **SPEAKABILITY** — Can an actor say this naturally? Or is it:
   - Too long for a single breath?
   - Too literary / written-sounding? (Film dialog ≠ prose)
   - Tongue-twisting or rhythmically awkward?
   - Full of exposition that would sound like a lecture?

2. **PERFORMANCE RANGE** — Can a good actor find multiple interpretations?
   - Lines that can only be read one way = DEAD lines (no room for the actor)
   - Lines that offer 3+ interpretations = ALIVE (actors love these)
   - The best lines are ambiguous enough for the actor to discover the character

3. **RHYTHM & BREATH** — Does the dialog have musicality?
   - Do speakers alternate short/long lines? (Not all the same length)
   - Are there natural pauses (beats) where actors can react?
   - Does the rhythm accelerate toward emotional peaks?
   - Are interruptions and overlaps used effectively?

4. **SILENCES** — Are there moments where NO dialog is more powerful?
   - Mark scenes where action should replace speech
   - Flag "talking head" scenes (two people exchanging lines, nothing visual)
   - Identify moments where a look, a gesture, or leaving the room says more

5. **CHEMISTRY** — Do dialog exchanges between characters crackle?
   - Is there tension in every exchange (even friendly ones)?
   - Do characters talk AT each other, or WITH each other?
   - Is there a power dynamic in every conversation?

OUTPUT as valid JSON:
{{
  "scenes": [
    {{
      "scene_id": "S015",
      "speakability_score": 80,
      "performance_range": 85,
      "rhythm_score": 75,
      "dead_lines": [
        {{
          "character": "Maria",
          "line": "I have waited five years for someone to say those words",
          "issue": "too_literary",
          "rewrite": "Five years. [beat] Say it again."
        }}
      ],
      "alive_lines": [
        {{
          "character": "Bourmin",
          "line": "I never knew how to end it.",
          "why": "Three interpretations: the story, the war, their love"
        }}
      ],
      "silence_opportunities": [
        "After Bourmin's confession — let Maria react without words for 10 seconds"
      ]
    }}
  ],
  "overall_stats": {{
    "avg_speakability": 82,
    "avg_performance_range": 80,
    "avg_rhythm": 78,
    "dead_line_count": 8,
    "alive_line_count": 15,
    "silence_opportunities": 5
  }},
  "best_exchange": {{
    "scene_id": "S042",
    "characters": ["Maria", "Bourmin"],
    "why": "The unspoken recognition — every pause does work"
  }},
  "weakest_exchange": {{
    "scene_id": "S020",
    "characters": ["Maria", "Praskovia"],
    "issue": "Expository — mother tells Maria information she already knows"
  }}
}}"""


def build_table_read_prompt() -> str:
    """Builds the table-read simulation prompt from dialog-heavy scenes."""
    from agents.script_writer import get_voice_profiles_for_prompt
    from utils.skill_loader import load_skills_for_agent

    state = load_state()
    scenes = state.get("adapted_scenes", [])

    # Select scenes with most dialog (prioritize high-tension)
    dialog_scenes = []
    for scene in scenes:
        dialog = scene.get("dialog_draft", scene.get("dialog_hinweise", []))
        if dialog and len(dialog) >= 2:
            dialog_scenes.append((scene, len(dialog)))

    # Sort by dialog density, take top 20
    dialog_scenes.sort(key=lambda x: x[1], reverse=True)
    selected = [s for s, _ in dialog_scenes[:20]]

    # Format
    parts = []
    for scene in selected:
        sid = _compat(scene, "scene_id", "szenen_id", "?")
        slug = scene.get("slug", "")
        dialog = scene.get("dialog_draft", scene.get("dialog_hinweise", []))

        lines = [f"--- {sid}: {slug} ---"]
        lines.append(f"Emotional core: {scene.get('emotional_core', '?')}")
        for d in dialog:
            char = d.get("character", "?")
            line = d.get("line", d.get("text", ""))
            sub = d.get("subtext", "")
            lines.append(f"\n  {char.upper()}")
            lines.append(f"  {line}")
            if sub:
                lines.append(f"  (subtext: {sub})")
        parts.append("\n".join(lines))

    dialog_text = "\n\n".join(parts)
    if len(dialog_text) > 30000:
        dialog_text = dialog_text[:30000] + "\n\n[TRUNCATED]"

    # Phase D: table read needs tics + rhythm cues — compact suffices.
    voice_profiles = get_voice_profiles_for_prompt(compact=True)

    prompt = SYSTEM_TABLE_READ.format(
        voice_profiles=voice_profiles,
        dialog_text=dialog_text,
    )

    skills = load_skills_for_agent("table_read")
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


def run_table_read(result: dict, verbose: bool = True) -> dict:
    """Processes the table-read simulation result."""
    stats = result.get("overall_stats", {})
    report = {
        "scenes": result.get("scenes", []),
        "overall_stats": stats,
        "best_exchange": result.get("best_exchange", {}),
        "weakest_exchange": result.get("weakest_exchange", {}),
        "simulated_at": datetime.now().isoformat(),
    }

    state = load_state()
    state["table_read"] = report
    cap_findings = apply_caps(state, "quality_gate", sub_path="table_read", mode="hard")
    if cap_findings:
        record_findings(state, agent="table_read", phase="9_5_table_read", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"TABLE-READ SIMULATION")
        print(f"{'='*60}")
        print(f"  Speakability:       {stats.get('avg_speakability', '?')}/100")
        print(f"  Performance range:  {stats.get('avg_performance_range', '?')}/100")
        print(f"  Rhythm:             {stats.get('avg_rhythm', '?')}/100")
        print(f"  Dead lines:         {stats.get('dead_line_count', '?')}")
        print(f"  Alive lines:        {stats.get('alive_line_count', '?')}")
        print(f"  Silence opps:       {stats.get('silence_opportunities', '?')}")
        best = report.get("best_exchange", {})
        if best:
            print(f"  Best exchange:      {best.get('scene_id', '?')} — {best.get('why', '')[:60]}")
        print(f"{'='*60}\n")

    return report
