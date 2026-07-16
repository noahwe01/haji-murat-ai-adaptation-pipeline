"""
PACING ANALYZER
===============
Granular rhythm analysis beyond simple tension scores.
Measures dialog weight, scene length variation, momentum curve,
dead zones, and act-level pacing integrity.

Hybrid: Pure Python (metrics) + LLM (interpretation).

Model: Sonnet (analytical)
Integration: After script_writer, feeds into coverage and revision.
"""

import json
import re
from datetime import datetime
from state_store import load_state, save_state, _compat
from utils.schema_caps import apply_caps, record_findings


# ─── Pure Python Metrics ──────────────────────────────────────────────

def compute_pacing_metrics() -> dict:
    """Computes pacing metrics from adapted scenes. No LLM call."""
    state = load_state()
    scenes = state.get("adapted_scenes", [])

    if not scenes:
        return {"error": "No adapted scenes found"}

    metrics = {
        "scene_count": len(scenes),
        "per_scene": [],
        "per_act": {},
        "momentum_curve": [],
        "dead_zones": [],
        "variation_score": 0.0,
    }

    # Per-scene metrics
    act_scenes = {}
    for i, scene in enumerate(scenes):
        sid = _compat(scene, "scene_id", "szenen_id", f"S{i:03d}")
        action = _compat(scene, "action", "handlung", "")
        dialog = scene.get("dialog_draft", scene.get("dialog_hinweise", []))
        act = scene.get("act", "?")

        action_words = len(action.split()) if action else 0

        # Count dialog from structured dialog_draft
        draft_lines = len(dialog) if isinstance(dialog, list) else 0
        draft_words = sum(
            len(d.get("line", d.get("text", "")).split())
            for d in dialog
        ) if isinstance(dialog, list) else 0

        # Also detect dialog embedded in action text (quotes, speech verbs)
        embedded_dialog_words = 0
        if action:
            # Count words inside quotation marks (direct speech in action)
            quotes = re.findall(r'["\u201c\u201e](.+?)["\u201d\u201c]', action)
            embedded_dialog_words = sum(len(q.split()) for q in quotes)
            # Count Fountain-style character cues (ALL CAPS line)
            for line in action.split('\n'):
                stripped = line.strip()
                if (stripped.isupper() and len(stripped) > 2
                        and not stripped.startswith(('INT', 'EXT', 'CUT', 'FADE'))):
                    draft_lines += 1

        dialog_words = draft_words + embedded_dialog_words
        dialog_lines = max(draft_lines, len(re.findall(r'["\u201c]', action)) if action else 0)
        total_words = action_words + draft_words  # don't double-count embedded
        dialog_pct = round(dialog_words / max(total_words, 1) * 100)
        tension = scene.get("confidence", 0.5)

        scene_metrics = {
            "scene_id": sid,
            "act": act,
            "action_words": action_words,
            "dialog_lines": dialog_lines,
            "dialog_words": dialog_words,
            "total_words": total_words,
            "dialog_pct": dialog_pct,
            "estimated_minutes": round(total_words / 100, 1),  # ~100 words/min on screen
            "tension": tension,
            "is_silent": dialog_lines == 0 and embedded_dialog_words == 0,
        }
        metrics["per_scene"].append(scene_metrics)

        # Group by act
        act_scenes.setdefault(act, []).append(scene_metrics)

        # Momentum (rolling average of tension × dialog density)
        momentum = tension * (1 + dialog_pct / 100)
        metrics["momentum_curve"].append({
            "scene_id": sid,
            "momentum": round(momentum, 2),
        })

    # Per-act aggregates
    for act, act_data in act_scenes.items():
        total_words = sum(s["total_words"] for s in act_data)
        avg_dialog_pct = round(
            sum(s["dialog_pct"] for s in act_data) / max(len(act_data), 1)
        )
        silent_count = sum(1 for s in act_data if s["is_silent"])
        est_minutes = round(sum(s["estimated_minutes"] for s in act_data), 1)

        metrics["per_act"][act] = {
            "scene_count": len(act_data),
            "total_words": total_words,
            "avg_dialog_pct": avg_dialog_pct,
            "silent_scenes": silent_count,
            "estimated_minutes": est_minutes,
        }

    # Dead zones (Q1.4): 3+ consecutive low-tension + low-dialog scenes,
    # OR any window whose summed estimated_minutes > 5 with the same low signal.
    # Duration is the gate-relevant metric; scene_count is supportive context.
    per_scene = metrics["per_scene"]
    for i in range(len(per_scene) - 2):
        window = per_scene[i:i + 3]
        if not all(s["tension"] < 0.5 and s["dialog_pct"] < 20 for s in window):
            continue
        # Greedy extension while the low-signal pattern continues.
        end = i + 2
        while end + 1 < len(per_scene):
            nxt = per_scene[end + 1]
            if nxt["tension"] < 0.5 and nxt["dialog_pct"] < 20:
                end += 1
            else:
                break
        zone_window = per_scene[i:end + 1]
        duration = round(sum(s["estimated_minutes"] for s in zone_window), 1)
        # Skip already-emitted overlapping zone (last zone covers this start)
        if metrics["dead_zones"] and metrics["dead_zones"][-1]["end"] == zone_window[-1]["scene_id"]:
            continue
        metrics["dead_zones"].append({
            "start": zone_window[0]["scene_id"],
            "end": zone_window[-1]["scene_id"],
            "scene_count": len(zone_window),
            "duration_minutes": duration,
            "exceeds_5min": duration > 5.0,
            "reason": (
                f"{len(zone_window)} consecutive low-tension, low-dialog scenes "
                f"({duration} min)"
            ),
        })

    # Scene length variation (higher = more dynamic pacing)
    word_counts = [s["total_words"] for s in metrics["per_scene"]]
    if word_counts:
        mean = sum(word_counts) / len(word_counts)
        variance = sum((w - mean) ** 2 for w in word_counts) / len(word_counts)
        std_dev = variance ** 0.5
        metrics["variation_score"] = round(std_dev / max(mean, 1) * 100, 1)

    return metrics


# ─── LLM Evaluation ──────────────────────────────────────────────────

SYSTEM_PACING = """You are a film editor analyzing the PACING of a screenplay.
You have the quantitative metrics below. Your job is to INTERPRET them
and identify pacing problems a human reader would feel.

PACING METRICS:
{metrics_json}

SCENE LIST (for context):
{scene_list}

───────────────────────────────────────────────

Analyze:

1. **ACT BALANCE**: Are the three acts proportioned correctly?
   - Standard: 25% / 50% / 25% (give or take 5%)
   - Is any act too long or too short?

2. **DIALOG DENSITY CURVE**: Does dialog increase toward emotional peaks?
   - Silent scenes in Act I (world-building) = fine
   - Silent scenes in Act III (climax) = problem unless intentional

3. **DEAD ZONES**: The metrics flagged potential dead zones. Are they:
   - Deliberate pacing choices (calm before storm)?
   - Or momentum killers that should be cut/compressed?

4. **ACCELERATION**: Do scenes get shorter toward the climax?
   - Act III scenes should average shorter than Act I
   - The last 10 scenes should be the fastest

5. **SCENE LENGTH VARIATION**: Is there enough contrast?
   - All same-length scenes = monotonous
   - Variation score > 40 = good dynamic range

OUTPUT as valid JSON:
{{
  "pacing_score": 82,
  "act_balance": {{
    "balanced": true,
    "act_1_pct": 28,
    "act_2_pct": 48,
    "act_3_pct": 24,
    "issues": []
  }},
  "dialog_density_issues": [
    "Act III has 4 silent scenes — consider adding dialog to at least 2"
  ],
  "dead_zone_verdict": [
    {{
      "zone": "S012-S014",
      "verdict": "deliberate — mourning sequence, but could lose one scene"
    }}
  ],
  "acceleration_check": {{
    "act3_faster_than_act1": true,
    "last_10_avg_words": 180,
    "act1_avg_words": 250
  }},
  "variation_verdict": "Good — variation score 45 indicates dynamic scene rhythm",
  "cut_suggestions": [
    "S014 repeats S013's emotional territory — merge or cut"
  ]
}}"""


def build_pacing_prompt() -> str:
    """Builds the pacing analysis prompt with computed metrics.

    Three retrieval layers:
    1. load_skills_for_agent — mandatory methodology skills
    2. retrieve_brain_knowledge — destilled pacing-rhythmus + slow-cinema-pacing notes
    3. retrieve_reference_excerpts — raw theory from Save the Cat, Field, Stoehr etc.
       (deep-dive when destilled brain isn't enough)
    """
    from utils.skill_loader import (
        load_skills_for_agent,
        retrieve_brain_knowledge,
        retrieve_reference_excerpts,
        get_retrieval_budget,
    )

    metrics = compute_pacing_metrics()
    state = load_state()
    scenes = state.get("adapted_scenes", [])

    # Compact scene list
    scene_list = []
    for s in metrics.get("per_scene", []):
        scene_list.append(
            f"{s['scene_id']} [{s['act']}] {s['total_words']}w "
            f"(dialog {s['dialog_pct']}%, tension {s['tension']:.1f})"
            f"{' [SILENT]' if s['is_silent'] else ''}"
        )

    prompt = SYSTEM_PACING.format(
        metrics_json=json.dumps({
            "per_act": metrics.get("per_act", {}),
            "dead_zones": metrics.get("dead_zones", []),
            "variation_score": metrics.get("variation_score", 0),
            "scene_count": metrics.get("scene_count", 0),
            "momentum_curve_summary": {
                "start": metrics["momentum_curve"][:3] if metrics.get("momentum_curve") else [],
                "peak": max(metrics.get("momentum_curve", [{"momentum": 0}]),
                           key=lambda x: x["momentum"]),
                "end": metrics["momentum_curve"][-3:] if metrics.get("momentum_curve") else [],
            },
        }, indent=2),
        scene_list="\n".join(scene_list),
    )

    skills = load_skills_for_agent("pacing_analyzer")
    if skills:
        prompt += f"\n\n{skills}"

    brain_keywords = ["momentum", "acceleration", "variation", "dialog density", "dead zone"]
    refs = (state.get("style_manifest", {}).get("referenzfilme", [])
            + state.get("style_manifest", {}).get("reference_films", []))
    if any(str(r).lower() in ("ida", "cold war", "loveless", "leviathan") for r in refs):
        brain_keywords.append("slow cinema")

    # H'' Phase D / P1.2 — central retrieval budgets enforced
    brain_budget = get_retrieval_budget("pacing_analyzer", "brain")
    mcp_budget = get_retrieval_budget("pacing_analyzer", "mcp")

    if brain_budget > 0:
        brain_text, _ = retrieve_brain_knowledge(
            {"keywords": brain_keywords, "agent": "pacing_analyzer"},
            max_chars=brain_budget,
        )
        if brain_text:
            prompt += f"\n\n{brain_text}"

    # Third layer: MCP reference excerpts (Save the Cat, Syd Field Paradigm,
    # Stoehr 8 Sequences, McKee on pacing). Only loaded when the central
    # budget table allocates an MCP quota for this agent.
    if mcp_budget > 0:
        ref_text, _ = retrieve_reference_excerpts(
            "pacing rhythm acceleration variation dead zone beat sheet act balance momentum",
            max_chars=mcp_budget,
            categories=["theory"],
            top_n=3,
        )
        if ref_text:
            prompt += f"\n\n{ref_text}"

    return prompt


# ─── Q1.4 Pacing Quality Gate ───────────────────────────────────────
# Acceptance criteria:
#   pacing_score >= 70 AND no dead_zone > 5min AND act-tags present.

PACING_SCORE_MIN = 70
DEAD_ZONE_MAX_MINUTES = 5.0


def pacing_quality_gate(state: dict) -> dict:
    """Evaluates Q1.4 gate. Reads state.pacing_analysis + state.adapted_scenes.

    Returns {passes, reasons[], long_dead_zones[], missing_act_tags(bool)}.
    long_dead_zones is the list of dead_zone records that exceed 5 minutes —
    each becomes a per-zone revision task in route_revision().
    """
    pacing = state.get("pacing_analysis", {}) or {}
    score = float(pacing.get("pacing_score", 0) or 0)
    metrics = pacing.get("metrics", {}) or {}
    dead_zones = metrics.get("dead_zones", []) or []
    if not dead_zones:
        # Fallback: pacing_analysis output may carry a top-level dead_zone list
        # under a different key (e.g. dead_zone_verdict). Use whichever exists.
        dead_zones = pacing.get("dead_zones", []) or []

    long_dead_zones = [
        z for z in dead_zones
        if isinstance(z, dict) and (
            z.get("exceeds_5min") is True
            or float(z.get("duration_minutes", 0) or 0) > DEAD_ZONE_MAX_MINUTES
        )
    ]

    scenes = state.get("adapted_scenes", []) or []
    untagged = [
        s.get("scene_id", "?")
        for s in scenes
        if not s.get("act") and s.get("act") != 0
    ]
    missing_act_tags = bool(untagged)

    reasons: list[str] = []
    if score < PACING_SCORE_MIN:
        reasons.append(f"pacing_score={score:g} < {PACING_SCORE_MIN}")
    if long_dead_zones:
        zone_descs = ", ".join(
            f"{z.get('start','?')}-{z.get('end','?')} ({z.get('duration_minutes','?')}min)"
            for z in long_dead_zones
        )
        reasons.append(f"dead_zone>5min: {zone_descs}")
    # missing_act_tags is a WARN, not a gate-breaker — kept in result but does
    # not block passes by itself; it remains a fragment/debug marker.

    return {
        "passes": len(reasons) == 0,
        "reasons": reasons,
        "long_dead_zones": long_dead_zones,
        "missing_act_tags": missing_act_tags,
        "untagged_scene_ids": untagged,
        "pacing_score": score,
    }


def run_pacing_analysis(result: dict, verbose: bool = True) -> dict:
    """Processes the pacing analysis result."""
    metrics = compute_pacing_metrics()
    report = {
        "metrics": metrics,
        "pacing_score": result.get("pacing_score", 0),
        "act_balance": result.get("act_balance", {}),
        "dialog_density_issues": result.get("dialog_density_issues", []),
        "dead_zone_verdict": result.get("dead_zone_verdict", []),
        "acceleration_check": result.get("acceleration_check", {}),
        "variation_verdict": result.get("variation_verdict", ""),
        "cut_suggestions": result.get("cut_suggestions", []),
        "analyzed_at": datetime.now().isoformat(),
    }

    state = load_state()
    state["pacing_analysis"] = report
    cap_findings = apply_caps(state, "quality_gate", sub_path="pacing_analysis", mode="hard")
    if cap_findings:
        record_findings(state, agent="pacing_analyzer", phase="9_5_pacing", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"PACING ANALYSIS")
        print(f"{'='*60}")
        print(f"  Pacing score:     {report['pacing_score']}/100")
        ab = report.get("act_balance", {})
        if ab:
            print(f"  Act balance:      I={ab.get('act_1_pct', '?')}% "
                  f"II={ab.get('act_2_pct', '?')}% "
                  f"III={ab.get('act_3_pct', '?')}%")
        print(f"  Variation score:  {metrics.get('variation_score', '?')}")
        print(f"  Dead zones:       {len(metrics.get('dead_zones', []))}")
        print(f"  Cut suggestions:  {len(report.get('cut_suggestions', []))}")
        for act, data in metrics.get("per_act", {}).items():
            print(f"  {act}: {data['scene_count']} scenes, "
                  f"~{data['estimated_minutes']} min, "
                  f"dialog {data['avg_dialog_pct']}%, "
                  f"silent {data['silent_scenes']}")
        print(f"{'='*60}\n")

    return report
