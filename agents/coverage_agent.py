"""
COVERAGE AGENT
==============
Simulates a professional Hollywood script reader.
Evaluates treatment/screenplay against industry coverage criteria.

Output: Coverage report with scores, top issues, and revision targets.

Calibrated against real industry standards:
- ICM Partners coverage format (dual-track verdict)
- Coverage Ink Pro analysis (detailed developmental notes)
- Standard categories: Concept, Structure, Characters, Dialog, Pacing, Visual, Marketability
- Verdicts: PASS / CONSIDER / RECOMMEND (for both script AND writer separately)
"""

from datetime import datetime
from state_store import load_state, save_state, _compat


# ─── Coverage Categories and Weights ────────────────────────────────

COVERAGE_CATEGORIES = {
    "concept":            {"weight": 0.10, "label": "Concept/Premise"},
    "structure":          {"weight": 0.20, "label": "Structure"},
    "characters":         {"weight": 0.20, "label": "Characters"},
    "dialog":             {"weight": 0.20, "label": "Dialogue"},
    "pacing":             {"weight": 0.15, "label": "Pacing"},
    "visual_storytelling": {"weight": 0.10, "label": "Visual Storytelling"},
    "marketability":      {"weight": 0.05, "label": "Marketability"},
}


def _get_verdict_thresholds() -> dict:
    """Loads verdict thresholds from config."""
    from config.loader import load_config
    c = load_config()
    return {
        "recommend": c.get("verdict_recommend", 80),
        "consider": c.get("verdict_consider", 65),
        "pass": c.get("verdict_pass", 50),
    }


# ─── System Prompts ─────────────────────────────────────────────────

SYSTEM_COVERAGE = """You are a professional script reader at a major production company (ICM/CAA level).
Write a coverage report — a structured evaluation of this treatment/screenplay.

Be honest, constructive, and specific. Reference exact scene IDs when citing issues.
Compare to known successful films where relevant.
Your tone should be direct and professional — like giving honest notes to a colleague.

PROJECT INFO:
Title: {title}
Based on: {source_info}
Genre: {genre}
Tone: {tone}
Target runtime: {target_runtime} minutes
Scene count: {scene_count}

STYLE MANIFEST:
{style_manifest}

CHARACTER OVERVIEW:
{character_summary}

LOGLINE:
{logline}

FULL TREATMENT/SCREENPLAY:
{script_text}

---

Evaluate in these 7 categories (0-100 each):

1. CONCEPT/PREMISE (10%)
   - Logline strength and clarity
   - Originality of the hook
   - Central dramatic question identifiable?
   - Would you want to read the screenplay based on the concept alone?

2. STRUCTURE (20%)
   - Three-act integrity
   - Act breaks at approximately 25%/50%/75%
   - Inciting incident, midpoint, climax identifiable and properly placed?
   - Does Act II have a clear throughline with escalating obstacles?
   - Is the ending earned by the preceding story?

3. CHARACTERS (20%)
   - Arc completeness (Want/Need clear and resolved?)
   - Is the protagonist ACTIVE or passive?
   - Antagonist/opposing force present and compelling?
   - Character distinguishability (can you tell them apart?)
   - Are supporting characters dimensional or functional?

4. DIALOGUE (20%)
   - Subtext present? (Not everything stated directly?)
   - Voice differentiation (do characters sound different?)
   - On-the-nose percentage (how much dialogue is too direct?)
   - Naturalness (does it sound spoken or written?)
   - Is dialogue doing work that visual storytelling could do better?

5. PACING (15%)
   - Scene-to-runtime ratio appropriate?
   - Tension curve with variation (not flat)?
   - No dead zones (scenes that advance neither plot nor character)?
   - Rhythm changes present (short/long scene alternation)?
   - Does the film earn its runtime?

6. VISUAL STORYTELLING (10%)
   - Show-don't-tell ratio
   - Camera-ready descriptions (can you see it)?
   - Visual subtext (images carrying emotional meaning)?
   - Stage directions precise and filmable?
   - Are there powerful visual moments that only cinema can deliver?

7. MARKETABILITY (5%)
   - Genre expectations met?
   - Target audience identifiable?
   - Comparable successful films?
   - Festival or theatrical potential?
   - Castable roles?

INDUSTRY FAILURE PATTERNS TO CHECK (flag each if found):
- Passive protagonist (lead reacts rather than drives)
- On-the-nose dialogue (characters stating feelings/exposition directly)
- Weak Act II throughline (no clear escalating obstacles in the middle)
- One-dimensional supporting characters (functional, not human)
- Logic holes (characters behaving inconsistently with established traits)
- Repetitive scenes (covering the same emotional ground without advancing)
- Missing "known world" (first 10 pages fail to establish ordinary life)
- Tonal inconsistency (comedy shifting to drama without justification)
- Unearned emotional moments (catharsis without sufficient buildup)
- Exposition dumps (information delivered without dramatic justification)
- Unfilmable action lines (describing internal states or metaphors that cannot be filmed — flag with exact quotes)
- Director intrusions in screenplay (CLOSE ON, SMASH CUT, camera movements, "the camera", "we see" — list every occurrence)
- Static emotional scenes (characters walking/sitting and talking without physical tasks, environmental interruptions, or spatial changes — especially in Act III)
- Subtext captions (action lines that explain what dialogue really means instead of letting subtext carry itself — flag for deletion)

Respond as JSON:
{{
  "script_verdict": "PASS|CONSIDER|RECOMMEND",
  "writer_verdict": "PASS|CONSIDER|RECOMMEND",
  "overall_score": 0-100,
  "synopsis": "Complete plot summary, 200-400 words, present tense, spoilers included",
  "character_breakdown": [
    {{"name": "...", "role": "LEAD|CO-LEAD|FEATURED", "age": "...", "description": "2-3 sentences"}}
  ],
  "categories": {{
    "concept": {{"score": 0-100, "notes": "...", "strengths": ["..."], "weaknesses": ["..."]}},
    "structure": {{"score": 0-100, "notes": "...", "strengths": ["..."], "weaknesses": ["..."], "act_breaks": {{"act_i_end": "S...", "midpoint": "S...", "act_ii_end": "S...", "climax": "S..."}}}},
    "characters": {{"score": 0-100, "notes": "...", "strengths": ["..."], "weaknesses": ["..."], "protagonist_active": true}},
    "dialog": {{"score": 0-100, "notes": "...", "strengths": ["..."], "weaknesses": ["..."], "on_the_nose_scenes": ["S..."], "voice_issues": ["..."]}},
    "pacing": {{"score": 0-100, "notes": "...", "strengths": ["..."], "weaknesses": ["..."], "dead_zones": [{{"scene_id": "S...", "issue": "...", "severity": "..."}}]}},
    "visual_storytelling": {{"score": 0-100, "notes": "...", "strengths": ["..."], "weaknesses": ["..."], "tell_not_show_scenes": ["S..."]}},
    "marketability": {{"score": 0-100, "notes": "...", "strengths": ["..."], "weaknesses": ["..."], "target_audience": ["..."], "comparable_films": ["..."]}}
  }},
  "failure_patterns_found": ["pattern name — scene reference — brief explanation"],
  "top_issues": [
    {{
      "issue_id": 1,
      "scene_ids": ["S..."],
      "issue": "Description of the problem",
      "severity": "critical|high|medium|low",
      "impact": "What this costs the story",
      "comparable_solution": "How [film] solved a similar problem: ...",
      "revision_instruction": "Specific, actionable instruction for the revision agent"
    }}
  ],
  "strengths": ["..."],
  "comparable_films": ["Film — why relevant"],
  "overall_comments": "2-3 paragraph assessment covering craft, potential, and path to improvement"
}}"""

SYSTEM_DIALOG_DEEP_CHECK = """You are a dialogue specialist. Check these scenes for dialogue quality.

VOICE PROFILES:
{voice_profiles}

SCENES:
{scenes_text}

Check every dialogue line for:
1. ON-THE-NOSE: Does the character directly state what they feel/want? (Bad)
2. VOICE: Does the language match the voice profile? Could you identify the character blindly?
3. SUBTEXT: Is there a layer beneath what's said?
4. EXPOSITION: Is information delivered through dialogue that would be better shown visually?

Respond as JSON with specific line references and suggested corrections."""


# ─── Coverage Agent Functions ───────────────────────────────────────

def run_coverage_agent(coverage_result: dict) -> dict:
    """
    Processes coverage result and saves to state.
    Calculates dual-track verdicts (script + writer).

    Args:
        coverage_result: JSON output from coverage LLM call

    Returns:
        Updated state
    """
    state = load_state()
    thresholds = _get_verdict_thresholds()

    # Calculate weighted overall score (verify/override LLM's calculation)
    categories = coverage_result.get("categories", {})
    weighted_score = 0
    for cat_key, cat_config in COVERAGE_CATEGORIES.items():
        cat_data = categories.get(cat_key, {})
        cat_score = cat_data.get("score", 50)
        weighted_score += cat_score * cat_config["weight"]

    coverage_result["overall_score_weighted"] = round(weighted_score, 1)

    # Script verdict based on weighted overall score
    if weighted_score >= thresholds["recommend"]:
        coverage_result["script_verdict"] = "RECOMMEND"
    elif weighted_score >= thresholds["consider"]:
        coverage_result["script_verdict"] = "CONSIDER"
    elif weighted_score >= thresholds["pass"]:
        coverage_result["script_verdict"] = "PASS"
    else:
        coverage_result["script_verdict"] = "FAIL"

    # Writer verdict based on craft categories (dialog + visual + concept)
    craft_score = (
        categories.get("dialog", {}).get("score", 50) * 0.35 +
        categories.get("visual_storytelling", {}).get("score", 50) * 0.35 +
        categories.get("concept", {}).get("score", 50) * 0.30
    )
    if craft_score >= thresholds["recommend"]:
        coverage_result["writer_verdict"] = "RECOMMEND"
    elif craft_score >= thresholds["consider"]:
        coverage_result["writer_verdict"] = "CONSIDER"
    else:
        coverage_result["writer_verdict"] = "PASS"

    coverage_result["evaluated_at"] = datetime.now().isoformat()
    state["coverage_report"] = coverage_result
    save_state(state)
    return state


def _compress_for_coverage(script_text: str, max_chars: int = 50000) -> str:
    """Compresses script to fit within max_chars while preserving all scenes.

    If the text fits, returns as-is. Otherwise, compresses each scene:
    keeps header + first 3 sentences of action + all dialog cues + last sentence.
    Ensures Act III is never lost (the #1 reason truncation was catastrophic).
    """
    import re
    if len(script_text) <= max_chars:
        return script_text

    # Split at scene boundaries (various formats)
    scene_pattern = re.compile(
        r'(?=(?:---\s*S\d|INT\.|EXT\.|INT/EXT\.|I/E\.))',
        re.IGNORECASE
    )
    scenes = scene_pattern.split(script_text)
    if len(scenes) <= 1:
        # No scene boundaries found — truncate with warning
        return script_text[:max_chars] + "\n\n[TRUNCATED — no scene boundaries detected]"

    # Compress each scene
    compressed = []
    for scene in scenes:
        scene = scene.strip()
        if not scene:
            continue

        # Split into lines
        lines = scene.split('\n')
        header_lines = []
        body_lines = []
        in_header = True

        for line in lines:
            stripped = line.strip()
            if in_header and (stripped.startswith('---') or
                              stripped.startswith('INT') or
                              stripped.startswith('EXT') or
                              stripped.startswith('I/E')):
                header_lines.append(line)
                in_header = False
                continue
            if in_header and not stripped:
                continue
            in_header = False
            body_lines.append(line)

        if not header_lines:
            header_lines = [lines[0]] if lines else []
            body_lines = lines[1:] if len(lines) > 1 else []

        # Keep: header + dialog cues + first 3 action sentences + last sentence
        kept = list(header_lines)
        action_count = 0
        # Match both indented (traditional) and Fountain (non-indented ALL CAPS) character cues
        scene_header_words = {'INT', 'EXT', 'I/E', 'CUT', 'FADE', 'DISSOLVE', 'SMASH'}

        def _is_dialog_cue(ln):
            s = ln.strip()
            if not s or len(s) < 2:
                return False
            # Indented all-caps (traditional screenplay format)
            if re.match(r'^\s{10,}[A-Z][A-Z\s\-\.]+$', ln):
                return True
            # Fountain: all-caps line that's NOT a scene header or transition
            if s.isupper() and not any(s.startswith(w) for w in scene_header_words):
                # Exclude lines that are just "---" separators
                if s.replace('-', '').replace(' ', ''):
                    return True
            return False

        for i, line in enumerate(body_lines):
            stripped = line.strip()
            # Keep dialog character cues and their first line
            if _is_dialog_cue(line):
                kept.append(line)
                if i + 1 < len(body_lines):
                    kept.append(body_lines[i + 1])
            elif action_count < 3 and stripped and not stripped.startswith('('):
                kept.append(line)
                action_count += 1

        # Add last line if different
        if body_lines and body_lines[-1] not in kept:
            kept.append(body_lines[-1])

        compressed.append('\n'.join(kept))

    result = '\n\n'.join(compressed)

    # If still too long, proportionally cut middle scenes more aggressively
    if len(result) > max_chars:
        # Keep first 20% and last 30% at full compression, cut middle harder
        n = len(compressed)
        first_n = max(1, n // 5)
        last_n = max(1, int(n * 0.3))
        mid_start = first_n
        mid_end = n - last_n

        final_parts = compressed[:first_n]
        for i in range(mid_start, mid_end):
            # Middle scenes: header only
            scene_lines = compressed[i].split('\n')
            final_parts.append(scene_lines[0] + "\n  [COMPRESSED]")
        final_parts.extend(compressed[mid_end:])
        result = '\n\n'.join(final_parts)

    total_original = len(script_text)
    pct = int((1 - len(result) / total_original) * 100)
    result += f"\n\n[Coverage compression: {pct}% reduced, {len(compressed)} scenes preserved]"
    return result[:max_chars]


def build_coverage_prompt() -> str:
    """Builds the coverage prompt from a minimal coverage-view of the state.

    Phase E.2: reads ``state_store.build_coverage_view(state)`` instead of the
    full state. View drops chunks, impro_material, world.*, casting,
    character_extractions, voice_profile internals, revision_history,
    continuity_log and all analysis-layer outputs — none of which are
    referenced in this prompt.
    """
    import json
    from utils.skill_loader import load_skills_for_agent
    from state_store import build_coverage_view
    view = build_coverage_view(load_state())

    # Character summary (compact)
    char_summary = [
        f"- {row['name']} ({row['role']}): Want={row['want']}, Need={row['need']}"
        for row in view["characters_compact"]
    ]

    # Script text (treatment or screenplay)
    # After revision, treatment_text and final_script are stale — render from adapted_scenes
    if view["meta"]["revision_cycle"] > 0:
        script_text = ""
    else:
        script_text = view["treatment_text"] or view["final_script"]
    if not script_text:
        # Render from adapted_scenes (authoritative after revision)
        scenes = view["adapted_scenes"]
        script_text = "\n\n".join(
            f"--- {_compat(s, 'scene_id', 'szenen_id', '?')} ---\n"
            f"{s.get('slug', '')}\n"
            f"{_compat(s, 'action', 'handlung', '')}\n"
            f"Dialog: {json.dumps(s.get('dialog_draft', s.get('dialog_hinweise', [])), ensure_ascii=False)}"
            for s in scenes
        )

    style = view["style_manifest"]

    skills = load_skills_for_agent("coverage_agent")
    prompt = SYSTEM_COVERAGE.format(
        title=view["meta"]["title"],
        source_info=f"{view['meta']['title']} (literary adaptation)",
        genre=style.get("genre", "?"),
        tone=_compat(style, "tone", "ton", "?"),
        target_runtime=view["meta"].get("target_runtime_minutes", "?") or "?",
        scene_count=view["scene_count"],
        style_manifest=json.dumps(style, ensure_ascii=False, indent=2),
        character_summary="\n".join(char_summary),
        logline=view["logline"] or "No logline available",
        script_text=_compress_for_coverage(script_text, 50000),
    )
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


def get_revision_needs(min_severity: str = "high") -> list:
    """Extracts revision tasks from the coverage report."""
    state = load_state()
    report = state.get("coverage_report")
    if not report:
        return []

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    min_level = severity_order.get(min_severity, 1)

    issues = report.get("top_issues", report.get("top_3_issues", []))
    return [
        issue for issue in issues
        if severity_order.get(issue.get("severity", "medium"), 2) <= min_level
    ]


def get_category_scores() -> dict:
    """Returns category scores in a readable format."""
    state = load_state()
    report = state.get("coverage_report")
    if not report:
        return {}

    result = {}
    for cat_key, cat_config in COVERAGE_CATEGORIES.items():
        cat_data = report.get("categories", {}).get(cat_key, {})
        result[cat_config["label"]] = {
            "score": cat_data.get("score", "—"),
            "weight": f"{cat_config['weight'] * 100:.0f}%",
            "notes": cat_data.get("notes", ""),
        }
    return result


def needs_dialog_revision() -> bool:
    """Checks if dialog score requires revision."""
    state = load_state()
    report = state.get("coverage_report")
    if not report:
        return False
    dialog_score = report.get("categories", {}).get("dialog", {}).get("score", 100)
    return dialog_score < 70
