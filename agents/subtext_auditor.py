"""
SUBTEXT AUDITOR
===============
Measures subtext depth per dialog exchange. Flags on-the-nose lines.
Enforces the 70/30 rule: at least 70% subtext, max 30% direct.

Model: Sonnet (analytical evaluation)
Integration: After script_writer, before coverage.
"""

import json
from datetime import datetime
from state_store import load_state, save_state, _compat
from utils.schema_caps import apply_caps, record_findings


SYSTEM_SUBTEXT = """You are a dialog subtext specialist. For each dialog exchange,
measure the GAP between what the character SAYS and what they MEAN.

VOICE PROFILES (for context — what each character hides/avoids):
{voice_profiles}

SCENES WITH DIALOG:
{dialog_scenes}

───────────────────────────────────────────────

For EACH dialog line, classify:

- **DEEP SUBTEXT** (score 9-10): Character says the opposite of what they mean.
  Meaning is conveyed through action, silence, or misdirection.
  Example: "The garden looks nice" while staring at the person they love.

- **MODERATE SUBTEXT** (score 6-8): Character deflects or talks around the real issue.
  Meaning is present but indirect.
  Example: "When did you arrive?" meaning "Why didn't you come sooner?"

- **THIN SUBTEXT** (score 3-5): Character mostly says what they mean, with slight
  emotional coloring. Functional but unremarkable.
  Example: "I've been waiting" (literal truth + mild reproach).

- **ON THE NOSE** (score 0-2): Character directly states their feelings, motivation,
  or exposition. No gap between surface and meaning.
  Example: "I'm afraid you'll leave me."

THE 70/30 RULE: At least 70% of dialog lines should score 6+.
Max 30% can be score 0-5 (and those should be intentional — a moment of raw honesty
hits harder when surrounded by subtext).

OUTPUT as valid JSON:
{{
  "scenes": [
    {{
      "scene_id": "S015",
      "lines": [
        {{
          "character": "Maria",
          "text": "The weather has been unusual this year.",
          "subtext_score": 8,
          "actual_meaning": "Everything has changed since you arrived",
          "technique": "displacement — projects emotional upheaval onto weather"
        }}
      ],
      "scene_avg": 7.5,
      "on_the_nose_count": 1,
      "deepest_moment": "Maria's line about the garden — devastating misdirection"
    }}
  ],
  "overall_stats": {{
    "total_lines": 120,
    "avg_subtext_score": 7.2,
    "on_the_nose_pct": 15,
    "deep_subtext_pct": 40,
    "passes_70_30": true
  }},
  "worst_offenders": [
    {{
      "scene_id": "S020",
      "character": "Vladimir",
      "line": "I love you more than life itself",
      "score": 1,
      "fix_suggestion": "Replace with action — he touches her hand, then pulls back"
    }}
  ],
  "best_moments": [
    {{
      "scene_id": "S042",
      "character": "Maria",
      "line": "You don't need to end it.",
      "score": 10,
      "why": "Says 'you don't need to end the story' but means 'stay with me forever'"
    }}
  ]
}}"""


def build_subtext_audit_prompt() -> str:
    """Builds the subtext audit prompt from adapted scenes with dialog."""
    from agents.script_writer import get_voice_profiles_for_prompt
    from utils.skill_loader import load_skills_for_agent

    state = load_state()
    scenes = state.get("adapted_scenes", [])

    # Extract scenes with dialog
    dialog_parts = []
    for scene in scenes:
        scene_id = _compat(scene, "scene_id", "szenen_id", "?")
        slug = scene.get("slug", "")
        dialog = scene.get("dialog_draft", scene.get("dialog_hinweise", []))
        if not dialog:
            continue

        lines_text = []
        for d in dialog:
            char = d.get("character", "?")
            line = d.get("line", d.get("text", ""))
            sub = d.get("subtext", "")
            lines_text.append(f"    {char}: \"{line}\"")
            if sub:
                lines_text.append(f"      (declared subtext: {sub})")

        dialog_parts.append(
            f"--- {scene_id}: {slug} ---\n" + "\n".join(lines_text)
        )

    # Limit to ~30k chars to stay within context
    dialog_text = "\n\n".join(dialog_parts)
    if len(dialog_text) > 30000:
        dialog_text = dialog_text[:30000] + "\n\n[TRUNCATED — audit remaining scenes in next pass]"

    # Phase D: subtext auditor verifies subtext rules verbatim — needs full profiles.
    voice_profiles = get_voice_profiles_for_prompt(compact=False)

    prompt = SYSTEM_SUBTEXT.format(
        voice_profiles=voice_profiles,
        dialog_scenes=dialog_text,
    )

    skills = load_skills_for_agent("subtext_auditor")
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


# ─── Q1.3 Subtext Quality Gate ──────────────────────────────────────
# Acceptance criteria:
#   passes_70_30 == true AND avg_subtext_score >= 6.5 AND worst-offender-pct <= 10%

SUBTEXT_AVG_MIN = 6.5
SUBTEXT_OFFENDER_PCT_MAX = 10.0


def subtext_quality_gate(subtext_audit: dict) -> dict:
    """Evaluates Q1.3 gate. Returns {passes, reasons[], worst_offender_scenes[]}.

    worst_offender_scenes is a deduplicated, severity-tagged list of scene_ids
    derived from worst_offenders + low-scene_avg scenes. Used by route_revision()
    to dispatch a per-scene revision when the gate fails.
    """
    stats = subtext_audit.get("overall_stats", {}) or {}
    passes_70_30 = bool(stats.get("passes_70_30", False))
    avg = float(stats.get("avg_subtext_score", 0) or 0)
    scenes = subtext_audit.get("scenes", []) or []
    offenders = subtext_audit.get("worst_offenders", []) or []

    offender_scene_ids: list[str] = []
    seen: set[str] = set()
    for off in offenders:
        sid = off.get("scene_id")
        if isinstance(sid, str) and sid and sid not in seen:
            offender_scene_ids.append(sid)
            seen.add(sid)
    for sc in scenes:
        sid = sc.get("scene_id")
        if not isinstance(sid, str) or not sid or sid in seen:
            continue
        if (sc.get("scene_avg") or 10) < SUBTEXT_AVG_MIN:
            offender_scene_ids.append(sid)
            seen.add(sid)

    total_dialog_scenes = len(scenes) or 1
    offender_pct = (len(offender_scene_ids) / total_dialog_scenes) * 100.0

    reasons: list[str] = []
    if not passes_70_30:
        reasons.append("passes_70_30=false")
    if avg < SUBTEXT_AVG_MIN:
        reasons.append(f"avg_subtext_score={avg:.2f} < {SUBTEXT_AVG_MIN}")
    if offender_pct > SUBTEXT_OFFENDER_PCT_MAX:
        reasons.append(
            f"worst_offender_scenes_pct={offender_pct:.1f}% > {SUBTEXT_OFFENDER_PCT_MAX}%"
        )

    return {
        "passes": len(reasons) == 0,
        "reasons": reasons,
        "worst_offender_scenes": offender_scene_ids,
        "avg_subtext_score": avg,
        "passes_70_30": passes_70_30,
        "offender_pct": round(offender_pct, 1),
    }


def run_subtext_audit(result: dict, verbose: bool = True) -> dict:
    """Processes the subtext audit result."""
    stats = result.get("overall_stats", {})
    report = {
        "scenes": result.get("scenes", []),
        "overall_stats": stats,
        "worst_offenders": result.get("worst_offenders", []),
        "best_moments": result.get("best_moments", []),
        "passes_70_30": stats.get("passes_70_30", False),
        "audited_at": datetime.now().isoformat(),
    }

    state = load_state()
    state["subtext_audit"] = report
    cap_findings = apply_caps(state, "quality_gate", sub_path="subtext_audit", mode="hard")
    if cap_findings:
        record_findings(state, agent="subtext_auditor", phase="9_5_subtext", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"SUBTEXT AUDIT REPORT")
        print(f"{'='*60}")
        print(f"  Avg subtext score:  {stats.get('avg_subtext_score', '?')}/10")
        print(f"  On-the-nose:        {stats.get('on_the_nose_pct', '?')}%")
        print(f"  Deep subtext:       {stats.get('deep_subtext_pct', '?')}%")
        print(f"  70/30 rule:         {'✓ PASS' if report['passes_70_30'] else '✗ FAIL'}")
        print(f"  Worst offenders:    {len(report['worst_offenders'])}")
        if report['worst_offenders']:
            w = report['worst_offenders'][0]
            print(f"    → {w.get('scene_id')}: {w.get('character')} — \"{w.get('line', '')[:50]}\"")
        print(f"{'='*60}\n")

    return report
