"""
NARRATIVE COHERENCE AGENT
=========================
Reads the ENTIRE screenplay as a single narrative experience.
Evaluates whether the whole is greater than the sum of its parts.

This is NOT scene-by-scene analysis (coverage does that).
This is: "Does this screenplay work as a FILM?"

Model: Opus (needs deep literary understanding)
Integration: After coverage + style validation, before revision.
"""

import json
from datetime import datetime
from state_store import load_state, save_state, _compat
from utils.schema_caps import apply_caps, record_findings


SYSTEM_COHERENCE = """You are a master screenplay analyst — think Robert McKee crossed
with a Sundance programmer. You have just read an entire screenplay in one sitting.
Your job is NOT to score individual scenes (that's been done). Your job is to assess
the screenplay as a SINGLE NARRATIVE ORGANISM.

SCREENPLAY:
{script_text}

CHARACTER ARCS:
{character_arcs}

DECLARED THEMES:
{themes}

STYLE MANIFEST:
{style_brief}

───────────────────────────────────────────────

Evaluate the screenplay as ONE EXPERIENCE. Answer these questions honestly:

1. NARRATIVE MOMENTUM
   - Does the story pull you forward? Or do you check the page count?
   - Where does momentum stall? Where does it surge?
   - Is the pacing of revelation (information, emotion, surprise) well-distributed?

2. EMOTIONAL ARCHITECTURE
   - What is the single most powerful moment? Is it properly set up and landed?
   - Do quiet moments make loud moments louder (and vice versa)?
   - Does the ending feel EARNED — not just thematically apt but emotionally necessary?
   - What would a viewer FEEL walking out of this film?

3. THEMATIC COHERENCE
   - Do the declared themes surface through ACTION and BEHAVIOR, not just dialog?
   - Does the formal structure (scene order, transitions, visual motifs) ECHO the theme?
   - Is there a single image or moment that crystallizes the entire film's meaning?

4. CHARACTER ECOSYSTEM
   - Does every character NEED to exist? (Or could two be merged?)
   - Do character arcs interlock? (One character's growth forces another's change?)
   - Is the protagonist's transformation visible in their BEHAVIOR, not just stated?

5. DANGLING THREADS & MISSED OPPORTUNITIES
   - Are there setups without payoffs? Promises without delivery?
   - Are there scenes that repeat emotional territory without deepening it?
   - What's the single biggest missed opportunity in this screenplay?

6. THE "WHY THIS FILM?" TEST
   - What makes this screenplay worth producing over 10,000 other scripts?
   - What would a viewer remember one week after watching?
   - Does it say something that hasn't been said this way before?

OUTPUT as valid JSON:
{{
  "coherence_score": 85,
  "momentum": {{
    "score": 80,
    "stall_points": ["S012-S015: mourning sequence repeats without deepening"],
    "surge_points": ["S038-S042: recognition sequence builds perfectly"]
  }},
  "emotional_architecture": {{
    "score": 88,
    "peak_moment": "S042: Bourmin's confession at the pond",
    "earned_ending": true,
    "audience_feeling": "Bittersweet wonder — fate is cruel and kind simultaneously"
  }},
  "thematic_coherence": {{
    "score": 85,
    "themes_shown_not_told": true,
    "crystallizing_moment": "The snowstorm itself — chaos that creates unexpected order",
    "formal_echoes": ["Snow imagery bookends the film", "Letters as proxy for direct speech"]
  }},
  "character_ecosystem": {{
    "score": 82,
    "redundant_characters": [],
    "interlocking_arcs": true,
    "transformation_visible": "Maria's shift from questions to statements in Act 3 dialog"
  }},
  "dangling_threads": [
    "Setup without payoff: the maid's secret knowledge — introduced but never leveraged"
  ],
  "missed_opportunities": [
    "Vladimir's death could be intercut with Maria's wedding night for devastating irony"
  ],
  "why_this_film": "A meditation on how chance shapes love — told with Pushkin's irony and visual restraint",
  "overall_assessment": "One paragraph: honest, specific, no flattery"
}}"""


# ─── Public API ───────────────────────────────────────────────────────


def _assemble_brief_script_text(
    state: dict, brief: dict, max_total_chars: int = 45000
) -> str:
    """G.2 helper — build the script-context block from the analysis_brief
    plus per-scene excerpts (excerpt_for_scene). Risk-flagged scenes are
    fully excerpted (top-priority for coherence review); remaining scenes
    get short slug + emotional_core summaries from brief.scene_index until
    the budget is exhausted. Returns "" when no excerpts are available
    (no final_script yet) — caller then falls back to the legacy view.
    """
    from state_store import excerpt_for_scene

    pointers = (brief or {}).get("excerpt_pointers", {}) or {}
    if not pointers:
        return ""

    scene_index = brief.get("scene_index", []) or []
    risk_ids = {
        r.get("scene_id")
        for r in brief.get("top_risk_scenes", []) or []
        if r.get("scene_id")
    }

    parts: list[str] = []
    remaining = max_total_chars

    # Pass 1: full excerpts for risk-flagged scenes (priority)
    risk_per_scene_cap = 2500
    for si in scene_index:
        sid = si.get("scene_id")
        if not sid or sid not in risk_ids:
            continue
        excerpt = excerpt_for_scene(state, sid, max_chars=risk_per_scene_cap)
        if not excerpt:
            continue
        block = (
            f"=== {sid} [RISK] {si.get('slug','')} ===\n"
            f"emotional: {si.get('emotional_core','')}\n"
            f"chars: {', '.join(si.get('characters',[]) or [])[:120]}\n"
            f"{excerpt.strip()}"
        )
        if len(block) > remaining:
            break
        parts.append(block)
        remaining -= len(block) + 2

    # Pass 2: short summaries for remaining scenes (in scene_index order)
    summary_cap = 220
    for si in scene_index:
        sid = si.get("scene_id")
        if not sid or sid in risk_ids:
            continue
        summary = (
            f"--- {sid} {si.get('slug','')} "
            f"({si.get('words',0)}w, {si.get('emotional_core','')[:80]}) ---"
        )
        if len(summary) > summary_cap:
            summary = summary[:summary_cap] + "…"
        if len(summary) + 2 > remaining:
            break
        parts.append(summary)
        remaining -= len(summary) + 2

    if not parts:
        return ""
    return "\n\n".join(parts)


def build_coherence_prompt() -> str:
    """Builds the narrative coherence evaluation prompt.

    Phase G.2: reads ``state["analysis_brief"]`` (F.5) for character_arcs,
    themes, scene_index and top_risk_scenes; assembles the script context
    from per-scene excerpts via ``excerpt_for_scene``. Drops the legacy
    full-script-compressed-to-45k path — the brief + per-scene excerpts
    deliver ~93% reduction vs full state and let the agent focus on the
    risk-flagged scenes instead of skimming a token-bloated full script.

    Falls back to the E.3 narrative_coherence_view path when no brief is
    set (legacy states, pre-F.5 runs).

    Brain-Budget reduced 16k → 5k chars: the destilled adaptions-brain
    notes are concept-level, the raw theory deep-dive is served by
    retrieve_reference_excerpts.

    Three retrieval layers:
    1. load_skills_for_agent — mandatory methodology skills
    2. retrieve_brain_knowledge — destilled adaptions-brain notes (5k)
    3. retrieve_reference_excerpts — raw theory excerpts from the MCP corpus
    """
    from agents.coverage_agent import _compress_for_coverage
    from utils.skill_loader import (
        load_skills_for_agent,
        retrieve_brain_knowledge,
        retrieve_reference_excerpts,
    )
    from state_store import (
        build_narrative_coherence_view,
        build_analysis_brief,
        excerpt_for_scene,
    )

    state = load_state()
    brief = state.get("analysis_brief")
    if not isinstance(brief, dict):
        brief = build_analysis_brief(state)

    # G.2: assemble script context from brief + per-scene excerpts
    script_text = _assemble_brief_script_text(state, brief, max_total_chars=45000)
    used_brief = bool(script_text)

    if used_brief:
        compressed = script_text  # already budgeted
        arc_lines = [
            f"  {row['name']} ({row.get('role','?')}): "
            f"{row['start']} → {row['change']} → {row['end']}"
            for row in brief.get("character_arcs", [])
        ]
        themes = brief.get("themes", []) or []
        sm = state.get("style_manifest", {}) or {}
        style = {
            "genre": sm.get("genre", ""),
            "tone": _compat(sm, "tone", "ton", ""),
            "reference_films": sm.get(
                "reference_films", sm.get("referenzfilme", [])
            ),
        }
    else:
        # Legacy fallback (no final_script yet; pre-F.5 state)
        view = build_narrative_coherence_view(state)
        legacy_script = view["final_script"] or view["treatment_text"]
        if not legacy_script:
            scenes = view["adapted_scenes"]
            legacy_script = "\n\n".join(
                f"--- {_compat(s, 'scene_id', 'szenen_id', '?')} ---\n"
                f"{s.get('slug', '')}\n"
                f"{_compat(s, 'action', 'handlung', '')}\n"
                f"Dialog: {json.dumps(s.get('dialog_draft', []), ensure_ascii=False)}"
                for s in scenes
            )
        compressed = _compress_for_coverage(legacy_script, 45000)
        arc_lines = [
            f"  {row['name']}: {row['start']} → {row['change']} → {row['end']}"
            for row in view["character_arcs"]
        ]
        themes = view["themes"]
        style = view["style_brief"]

    style_parts = []
    if style.get("genre"):
        style_parts.append(f"Genre: {style['genre']}")
    tone = _compat(style, "tone", "ton", "")
    if tone:
        style_parts.append(f"Tone: {tone}")
    refs = style.get("reference_films", style.get("referenzfilme", []))
    if refs:
        style_parts.append(f"Reference films: {', '.join(refs)}")

    prompt = SYSTEM_COHERENCE.format(
        script_text=compressed,
        character_arcs="\n".join(arc_lines) if arc_lines else "(No arcs defined)",
        themes=", ".join(themes) if themes else "(No themes declared)",
        style_brief="\n".join(style_parts) if style_parts else "(No style manifest)",
    )

    skills = load_skills_for_agent("narrative_coherence")
    if skills:
        prompt += f"\n\n{skills}"

    brain_keywords = [
        "coherence", "dangling", "through-line", "earned ending",
        "story value", "value shift", "ecosystem", "payoff",
        "missed opportunity", "mckee",
    ]
    brain_keywords.extend(str(t).lower() for t in themes if t)

    brain_text, _ = retrieve_brain_knowledge(
        {"keywords": brain_keywords, "agent": "narrative_coherence"},
        max_chars=5000,  # Phase E.3 — reduced from 16000 (Plan V4 §G.3)
    )
    if brain_text:
        prompt += f"\n\n{brain_text}"

    # Third layer: MCP reference excerpts (raw theory from source books)
    # Deep-dive into McKee, Howard, Seger etc. when the destilled brain isn't enough.
    reference_query = (
        "story values scene change earned ending through-line dangling threads "
        "character ecosystem dramatic unity thematic coherence"
    )
    ref_text, _ = retrieve_reference_excerpts(
        reference_query,
        max_chars=5000,
        categories=["theory"],
        top_n=4,
    )
    if ref_text:
        prompt += f"\n\n{ref_text}"

    return prompt


def run_narrative_coherence(result: dict, verbose: bool = True) -> dict:
    """Processes the narrative coherence evaluation result."""
    report = {
        "coherence_score": result.get("coherence_score", 0),
        "momentum": result.get("momentum", {}),
        "emotional_architecture": result.get("emotional_architecture", {}),
        "thematic_coherence": result.get("thematic_coherence", {}),
        "character_ecosystem": result.get("character_ecosystem", {}),
        "dangling_threads": result.get("dangling_threads", []),
        "missed_opportunities": result.get("missed_opportunities", []),
        "why_this_film": result.get("why_this_film", ""),
        "overall_assessment": result.get("overall_assessment", ""),
        "evaluated_at": datetime.now().isoformat(),
    }

    state = load_state()
    state["narrative_coherence"] = report
    cap_findings = apply_caps(state, "quality_gate", sub_path="narrative_coherence", mode="hard")
    if cap_findings:
        record_findings(state, agent="narrative_coherence", phase="9_5_coherence", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"NARRATIVE COHERENCE REPORT")
        print(f"{'='*60}")
        print(f"  Overall:    {report['coherence_score']}/100")
        m = report.get("momentum", {})
        e = report.get("emotional_architecture", {})
        t = report.get("thematic_coherence", {})
        c = report.get("character_ecosystem", {})
        print(f"  Momentum:   {m.get('score', '?')}/100")
        print(f"  Emotional:  {e.get('score', '?')}/100")
        print(f"  Thematic:   {t.get('score', '?')}/100")
        print(f"  Characters: {c.get('score', '?')}/100")
        print(f"{'─'*60}")
        print(f"  Peak moment: {e.get('peak_moment', '?')}")
        print(f"  Ending earned: {e.get('earned_ending', '?')}")
        print(f"  Dangling threads: {len(report['dangling_threads'])}")
        print(f"  Missed opportunities: {len(report['missed_opportunities'])}")
        print(f"{'='*60}\n")

    return report
