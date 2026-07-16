"""
STYLE VALIDATOR
===============
Checks consistency between style manifest and actual screenplay output.
5 evaluation categories with weighted scoring.

Model: Sonnet (analytical, not creative)
Integration: After coverage (phase 7), before revision (phase 8).
"""

import json
from state_store import load_state, save_state, _compat


# ─── Style Categories and Weights ────────────────────────────────────

STYLE_CATEGORIES = {
    "tone_consistency":   {"weight": 0.25, "label": "Tone & Mood Consistency"},
    "dialog_register":    {"weight": 0.20, "label": "Dialogue Voice Consistency"},
    "visual_vocabulary":  {"weight": 0.20, "label": "Visual Style Coherence"},
    "thematic_threads":   {"weight": 0.20, "label": "Thematic Reinforcement"},
    "pacing_rhythm":      {"weight": 0.15, "label": "Pacing & Rhythm Integrity"},
}


# ─── System Prompt ────────────────────────────────────────────────────

SYSTEM_STYLE_VALIDATION = """You are a style consistency checker for screenplays.
Your job is to evaluate whether the actual screenplay matches the declared
style manifest — the artistic DNA that defines what this film should feel like.

STYLE MANIFEST:
  Genre: {genre}
  Tone: {tone}
  Reference Films: {reference_films}
  Special Notes: {special_notes}
  Language: {language}

FULL STYLE MANIFEST (JSON):
{style_manifest_json}

CHARACTER VOICES (for dialog register check):
{voice_summary}

SCREENPLAY TEXT:
{script_text}

───────────────────────────────────────────────

EVALUATE in 5 categories. Score each 0-100.

1. TONE CONSISTENCY (25%)
   - Does the tone match the declared manifest THROUGHOUT?
   - Are there jarring shifts that break the aesthetic?
   - Does it FEEL like the reference films?

2. DIALOGUE REGISTER (20%)
   - Does each character maintain their voice profile?
   - Is the dialogue register appropriate for the genre/period?
   - Do characters sound distinct from each other?

3. VISUAL VOCABULARY (20%)
   - Do action lines match the declared visual style?
   - Are descriptions cinematic and specific (not novelistic)?
   - Do visual choices echo the reference films' aesthetic?

4. THEMATIC THREADS (20%)
   - Are the declared themes woven through scenes?
   - Does thematic material surface in dialogue and action?
   - Is theme shown through behavior, not stated?

5. PACING & RHYTHM (15%)
   - Does the scene rhythm match genre expectations?
   - Are quiet/loud beats alternating properly?
   - Does pacing accelerate toward the climax?

OUTPUT as valid JSON:
{{
  "scores": {{
    "tone_consistency": 85,
    "dialog_register": 80,
    "visual_vocabulary": 78,
    "thematic_threads": 82,
    "pacing_rhythm": 75
  }},
  "weighted_total": 80.5,
  "issues": [
    {{
      "category": "tone_consistency",
      "scene_id": "S015",
      "description": "Tone shifts from melancholic to comedic without justification",
      "severity": "medium",
      "suggestion": "Add transitional beat or rewrite the dialogue exchange"
    }}
  ],
  "strengths": ["Strong visual vocabulary throughout Act I", "..."],
  "overall_assessment": "One paragraph summary of style consistency"
}}"""


# ─── Public API ───────────────────────────────────────────────────────

def build_style_validation_prompt() -> str:
    """Builds the style validation prompt from current state.

    Returns the formatted system prompt with skills injected.
    The LLM call is made by Claude Code / orchestrator, not by this function.
    """
    from agents.coverage_agent import _compress_for_coverage
    from utils.skill_loader import load_skills_for_agent

    state = load_state()
    style = state.get("style_manifest", {})
    characters = state.get("characters", {})

    # Script text with compression
    script_text = state.get("treatment_text") or state.get("final_script") or ""
    if not script_text:
        scenes = state.get("adapted_scenes", [])
        script_text = "\n\n".join(
            f"--- {_compat(s, 'scene_id', 'szenen_id', '?')} ---\n"
            f"{s.get('slug', '')}\n"
            f"{_compat(s, 'action', 'handlung', '')}"
            for s in scenes
        )

    compressed_text = _compress_for_coverage(script_text, 40000)

    # Compact voice summary
    voice_lines = []
    for name, data in characters.items():
        vp = data.get("voice_profile", {})
        if vp:
            desc = _compat(vp, "voice_description", "stimmbeschreibung", "")
            voice_lines.append(f"  {name}: {desc[:150]}")

    ref_films = style.get("referenzfilme", style.get("reference_films", []))

    prompt = SYSTEM_STYLE_VALIDATION.format(
        genre=style.get("genre", "?"),
        tone=_compat(style, "tone", "ton", "?"),
        reference_films=", ".join(ref_films) if ref_films else "?",
        special_notes=style.get("besonderheiten", style.get("special_notes", "")),
        language=style.get("language", "English"),
        style_manifest_json=json.dumps(style, ensure_ascii=False, indent=2),
        voice_summary="\n".join(voice_lines) if voice_lines else "(No voice profiles)",
        script_text=compressed_text,
    )
    skills = load_skills_for_agent("style_validator")
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


def run_style_validator(validation_result: dict, verbose: bool = True) -> dict:
    """
    Processes the style validation result from the LLM.

    Args:
        validation_result: Parsed JSON from the LLM response.

    Returns:
        Style validation report (also saved in state).
    """
    scores = validation_result.get("scores", {})

    # Calculate weighted total
    weighted_total = 0.0
    for cat_key, cat_info in STYLE_CATEGORIES.items():
        score = scores.get(cat_key, 0)
        weighted_total += score * cat_info["weight"]

    report = {
        "scores": scores,
        "weighted_total": round(weighted_total, 1),
        "category_details": {
            key: {
                "label": info["label"],
                "weight": info["weight"],
                "score": scores.get(key, 0),
                "weighted_contribution": round(scores.get(key, 0) * info["weight"], 1),
            }
            for key, info in STYLE_CATEGORIES.items()
        },
        "issues": validation_result.get("issues", []),
        "strengths": validation_result.get("strengths", []),
        "overall_assessment": validation_result.get("overall_assessment", ""),
        "validated_at": __import__("datetime").datetime.now().isoformat(),
    }

    # Save to state
    state = load_state()
    state["style_validation"] = report
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"STYLE VALIDATION REPORT")
        print(f"{'='*60}")
        for key, detail in report["category_details"].items():
            print(f"  {detail['label']:30s} {detail['score']:3d}/100  "
                  f"(weight {detail['weight']:.0%})")
        print(f"{'─'*60}")
        print(f"  {'WEIGHTED TOTAL':30s} {report['weighted_total']:.1f}/100")
        print(f"  Issues found: {len(report['issues'])}")
        print(f"{'='*60}\n")

    return report


def get_style_issues(min_severity: str = "medium") -> list:
    """Extracts actionable style issues for the revision agent."""
    state = load_state()
    validation = state.get("style_validation")
    if not validation:
        return []

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    min_level = severity_order.get(min_severity, 2)

    return [
        issue for issue in validation.get("issues", [])
        if severity_order.get(issue.get("severity", "low"), 3) <= min_level
    ]
