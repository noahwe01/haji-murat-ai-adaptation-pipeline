"""
REVISION AGENT
==============
Takes specific issues from coverage and style validation reports,
then rewrites targeted scenes to fix them.

Model: Opus (creative revision needs nuance)
Integration: Phase 8 via orchestrator.route_revision_clustered()
  (Phase H default — bundles issues per scene into max-5 clusters with a
  budget-guard cap of 6 dispatched calls per cycle. Falls back to flat
  route_revision() only for debug or custom dispatch.)

Key principle: Targeted revision, not full rewrite.
Only modifies scenes referenced in the issues.
Preserves continuity with surrounding scenes.
"""

import json
from datetime import datetime
from state_store import (
    load_state, save_state, _compat,
    log_continuity_issue, get_character_scenes
)
from decision_log import build_criteria_instruction, log_decisions_from_block


# ─── System Prompt ────────────────────────────────────────────────────

SYSTEM_REVISION = """You are a screenplay revision specialist. You receive specific
issues from coverage and style validation reports and must revise ONLY the
targeted scenes to fix them.

RULES:
1. Only modify scenes listed in ISSUES below — do NOT touch other scenes
2. Preserve continuity with surrounding scenes (context provided)
3. Maintain each character's voice per the profiles below
4. Every change must be traceable — log what you changed and why
5. Do NOT invent new characters, locations, or plot points
6. Maintain the declared style/tone throughout

VOICE PROFILES:
{voice_profiles}

STYLE MANIFEST:
{style_brief}

ISSUES TO FIX:
{issues_text}

SCENES TO REVISE (with surrounding context):
{scenes_text}

───────────────────────────────────────────────

For each scene, return the COMPLETE revised version.

OUTPUT as valid JSON:
{{
  "revised_scenes": [
    {{
      "scene_id": "S015",
      "slug": "INT. LOCATION — TIME",
      "action": "Full revised action text...",
      "dialog_draft": [
        {{"character": "Name", "line": "Dialogue line", "subtext": "What they really mean"}}
      ],
      "emotional_core": "What the scene is really about",
      "visual_note": "Key visual element",
      "confidence": 0.88,
      "revision_note": "What was changed and why"
    }}
  ],
  "changelog": [
    {{
      "scene_id": "S015",
      "change": "Rewrote Maria's dialogue to match guarded Act 3 voice",
      "reason": "Coverage flagged on-the-nose dialogue in confession scene",
      "category": "dialog"
    }}
  ]
}}"""


# ─── Public API ───────────────────────────────────────────────────────

def build_revision_prompt(issues: list) -> str:
    """
    Builds the revision prompt for targeted scene rewrites.

    Args:
        issues: List of issue dicts from coverage/style reports.
               Each must have 'scene_ids' or 'scene_id' and 'description'.

    Returns:
        Formatted system prompt for the LLM call.
    """
    from agents.script_writer import get_voice_profiles_for_prompt
    from agents.adaptation_agent import _build_style_brief
    from utils.skill_loader import load_skills_for_agent

    state = load_state()
    style_manifest = state.get("style_manifest", {})
    adapted_scenes = state.get("adapted_scenes", [])

    # Build scene lookup
    scene_map = {}
    for i, scene in enumerate(adapted_scenes):
        sid = _compat(scene, "scene_id", "szenen_id", "?")
        scene_map[sid] = (i, scene)

    # Collect all affected scene IDs
    affected_ids = set()
    for issue in issues:
        ids = issue.get("scene_ids", [])
        if not ids and issue.get("scene_id"):
            ids = [issue["scene_id"]]
        affected_ids.update(ids)

    # Phase D: collect characters appearing in target vs context scenes.
    # Affected chars get full voice profiles; context chars get compact.
    affected_chars = []
    context_chars = []
    seen_affected = set()
    seen_context = set()
    for sid in sorted(affected_ids):
        if sid not in scene_map:
            continue
        idx, scene = scene_map[sid]
        for n in _compat(scene, "characters", "figuren", []) or []:
            if n not in seen_affected:
                seen_affected.add(n)
                affected_chars.append(n)
        for adj_idx in (idx - 1, idx + 1):
            if 0 <= adj_idx < len(adapted_scenes):
                for n in _compat(adapted_scenes[adj_idx], "characters", "figuren", []) or []:
                    if n not in seen_affected and n not in seen_context:
                        seen_context.add(n)
                        context_chars.append(n)

    # Build scenes text with context (±1 scene)
    scenes_parts = []
    for sid in sorted(affected_ids):
        if sid not in scene_map:
            continue
        idx, scene = scene_map[sid]

        # Context: previous scene
        if idx > 0:
            prev = adapted_scenes[idx - 1]
            prev_id = _compat(prev, "scene_id", "szenen_id", "?")
            scenes_parts.append(f"[CONTEXT — Previous scene {prev_id}]")
            scenes_parts.append(f"  Slug: {prev.get('slug', '')}")
            scenes_parts.append(f"  Action (last 200 chars): ...{_compat(prev, 'action', 'handlung', '')[-200:]}")
            scenes_parts.append("")

        # Target scene (full)
        scenes_parts.append(f"[TARGET — {sid} — REVISE THIS SCENE]")
        scenes_parts.append(f"  Slug: {scene.get('slug', '')}")
        scenes_parts.append(f"  Action: {_compat(scene, 'action', 'handlung', '')}")
        scenes_parts.append(f"  Characters: {', '.join(_compat(scene, 'characters', 'figuren', []))}")
        dialog = scene.get("dialog_draft", scene.get("dialog_hinweise", []))
        if dialog:
            scenes_parts.append(f"  Dialog:")
            for d in dialog:
                char = d.get("character", "?")
                line = d.get("line", d.get("text", ""))
                sub = d.get("subtext", "")
                scenes_parts.append(f"    {char}: \"{line}\"")
                if sub:
                    scenes_parts.append(f"      (subtext: {sub})")
        scenes_parts.append(f"  Emotional core: {scene.get('emotional_core', '')}")
        scenes_parts.append(f"  Visual note: {scene.get('visual_note', '')}")
        scenes_parts.append(f"  Confidence: {scene.get('confidence', '?')}")
        scenes_parts.append("")

        # Context: next scene
        if idx + 1 < len(adapted_scenes):
            nxt = adapted_scenes[idx + 1]
            nxt_id = _compat(nxt, "scene_id", "szenen_id", "?")
            scenes_parts.append(f"[CONTEXT — Next scene {nxt_id}]")
            scenes_parts.append(f"  Slug: {nxt.get('slug', '')}")
            scenes_parts.append(f"  Action (first 200 chars): {_compat(nxt, 'action', 'handlung', '')[:200]}...")
            scenes_parts.append("")

        scenes_parts.append("─" * 40)

    # Build issues text
    issues_parts = []
    for i, issue in enumerate(issues, 1):
        ids = issue.get("scene_ids", [issue.get("scene_id", "?")])
        issues_parts.append(
            f"{i}. [{issue.get('severity', 'medium').upper()}] "
            f"Scenes: {', '.join(ids)}\n"
            f"   Category: {issue.get('category', issue.get('issue_type', '?'))}\n"
            f"   Issue: {issue.get('description', issue.get('instruction', ''))}\n"
            f"   Suggestion: {issue.get('suggestion', '')}"
        )

    # Phase D: split-render. Full for affected chars; compact for context.
    parts = []
    if affected_chars:
        full_block = get_voice_profiles_for_prompt(
            character_ids=affected_chars, compact=False, max_examples=1
        )
        parts.append("[AFFECTED — full profiles]\n" + full_block.lstrip())
    if context_chars:
        compact_block = get_voice_profiles_for_prompt(
            character_ids=context_chars, compact=True
        )
        parts.append("[CONTEXT — compact profiles]\n" + compact_block.lstrip())
    voice_profiles = "\n\n".join(parts) if parts else "(No voice profiles available)"
    style_brief = _build_style_brief(style_manifest)

    skills = load_skills_for_agent("revision_agent")
    prompt = SYSTEM_REVISION.format(
        voice_profiles=voice_profiles,
        style_brief=style_brief,
        issues_text="\n\n".join(issues_parts),
        scenes_text="\n".join(scenes_parts),
    )
    if skills:
        prompt += f"\n\n{skills}"

    # Dynamic brain retrieval based on issue types
    from utils.skill_loader import retrieve_brain_knowledge
    brain_ctx = {"keywords": []}
    for issue in issues:
        issue_type = issue.get("issue_type", "") + " " + issue.get("instruction", "")
        for kw in ["dialog", "subtext", "on-the-nose", "exposition", "pacing",
                    "tone", "confession", "confrontation", "silence", "transition"]:
            if kw in issue_type.lower():
                brain_ctx["keywords"].append(kw)
    if brain_ctx["keywords"]:
        brain_text, _ = retrieve_brain_knowledge(brain_ctx, max_chars=2000)
        if brain_text:
            prompt += f"\n\n{brain_text}"

    # Criteria injection — agent cites rule IDs in a DECISIONS block after its JSON.
    try:
        prompt += "\n\n" + build_criteria_instruction()
    except FileNotFoundError:
        pass

    return prompt


def run_revision_agent(revision_result: dict, verbose: bool = True,
                       raw_output: str | None = None) -> dict:
    """
    Applies revision results to the state.

    Args:
        revision_result: Parsed JSON from the LLM response with
                        'revised_scenes' and 'changelog'.
        raw_output:      Optional raw subagent-output string (revision JSON +
                         DECISIONS block). When provided, the DECISIONS block
                         is parsed and written to output/adaptation_log.json
                         with agent="revision_agent", phase="8_revision".
                         Optional so existing callers remain source-compatible.

    Returns:
        Updated state dict.
    """
    state = load_state()
    adapted_scenes = state.get("adapted_scenes", [])
    revised = revision_result.get("revised_scenes", [])
    changelog = revision_result.get("changelog", [])

    # Build lookup for quick replacement
    scene_map = {}
    for i, scene in enumerate(adapted_scenes):
        sid = _compat(scene, "scene_id", "szenen_id", "?")
        scene_map[sid] = i

    replaced_count = 0
    for rev_scene in revised:
        sid = rev_scene.get("scene_id", "?")
        if sid in scene_map:
            idx = scene_map[sid]
            # Preserve original fields not in revision
            original = adapted_scenes[idx]
            merged = {**original, **rev_scene}
            merged["revision_count"] = original.get("revision_count", 0) + 1
            merged["last_revised"] = datetime.now().isoformat()
            adapted_scenes[idx] = merged
            replaced_count += 1

    state["adapted_scenes"] = adapted_scenes

    # Log changelog
    for entry in changelog:
        log_continuity_issue(
            f"Revision: {entry.get('change', '')} | Reason: {entry.get('reason', '')}",
            scene_id=entry.get("scene_id"),
            resolved=True,
        )

    # Update meta
    revision_cycle = state["meta"].get("revision_cycle", 0)
    state["meta"]["last_revision"] = datetime.now().isoformat()
    state["meta"]["status"] = "revised"
    save_state(state)

    # DECISIONS logging — parse agent's raw output, append to adaptation_log.
    # Write-only contract (never re-ingested).
    logged = 0
    if raw_output:
        logged = log_decisions_from_block(
            agent_output=raw_output,
            agent="revision_agent",
            phase="8_revision",
        )

    if verbose:
        print(f"\n{'='*60}")
        print(f"REVISION AGENT complete")
        print(f"  Scenes revised:  {replaced_count}")
        print(f"  Changelog items: {len(changelog)}")
        print(f"  Revision cycle:  {revision_cycle}")
        if logged:
            print(f"  Decisions logged: {logged}")
        for entry in changelog:
            print(f"  • {entry.get('scene_id', '?')}: {entry.get('change', '')}")
        print(f"{'='*60}\n")

    return state
