"""
FILMABILITY VALIDATOR (Q1.1 — report-only)
==========================================
Heuristic per-scene check whether an adapted scene is cinematically playable
or merely paraphrases the source. NOT a Phase-8 blocking gate in Phase F:
generates a report that future calibration can promote to a hard gate.

Six criteria, each 0.0..1.0 (weighted equal):
  - visible_action     : enough action_words to support physical staging
  - dramatic_question  : emotional_core / conflict signal present
  - conflict_or_tension: tension / confidence threshold met
  - setting_clarity    : slug + visual_note non-empty
  - subtext_carrier    : dialog_draft has subtext-tagged lines OR subplot threads
  - runtime_fit        : duration_minutes inside [0.5, 6.0]

Pure-Python in Phase F. May be upgraded to Sonnet-call once false-positive
calibration is done.
"""

from datetime import datetime, timezone
from state_store import load_state, save_state
from utils.schema_caps import apply_caps, record_findings


SCENE_THRESHOLD = 0.7
OVERALL_THRESHOLD = 0.75


def _score_visible_action(scene: dict) -> float:
    action = scene.get("action") or ""
    if not isinstance(action, str):
        return 0.0
    words = len(action.split())
    if words >= 60:
        return 1.0
    if words >= 30:
        return 0.7
    if words >= 12:
        return 0.4
    return 0.1


def _score_dramatic_question(scene: dict) -> float:
    core = scene.get("emotional_core") or ""
    beats = scene.get("emotional_beats") or []
    if isinstance(core, str) and len(core) >= 12 and beats:
        return 1.0
    if isinstance(core, str) and len(core) >= 8:
        return 0.7
    if beats:
        return 0.5
    return 0.2


def _score_conflict(scene: dict) -> float:
    conf = float(scene.get("confidence", 0.5) or 0.5)
    action = (scene.get("action") or "").lower()
    cues = ("fight", "argue", "shout", "refuse", "betray", "tension",
            "hesitate", "draw", "crash", "block", "challenge")
    cue_hit = any(c in action for c in cues)
    if conf >= 0.8 or cue_hit:
        return 1.0
    if conf >= 0.6:
        return 0.7
    if conf >= 0.4:
        return 0.4
    return 0.1


def _score_setting_clarity(scene: dict) -> float:
    slug = scene.get("slug") or ""
    visual = scene.get("visual_note") or ""
    has_slug = isinstance(slug, str) and len(slug) >= 6
    has_visual = isinstance(visual, str) and len(visual) >= 12
    if has_slug and has_visual:
        return 1.0
    if has_slug or has_visual:
        return 0.5
    return 0.1


def _score_subtext_carrier(scene: dict) -> float:
    drafts = scene.get("dialog_draft") or []
    threads = scene.get("subplot_threads") or []
    deep_lines = 0
    if isinstance(drafts, list):
        for d in drafts:
            score = d.get("subtext_score") if isinstance(d, dict) else None
            if isinstance(score, (int, float)) and score >= 6:
                deep_lines += 1
    if deep_lines >= 2 and threads:
        return 1.0
    if deep_lines >= 1 or threads:
        return 0.7
    if isinstance(drafts, list) and drafts:
        return 0.4
    # Silent scene — neutral, not a fail.
    return 0.6


def _score_runtime_fit(scene: dict) -> float:
    dur = scene.get("duration_minutes")
    try:
        dur = float(dur)
    except (TypeError, ValueError):
        return 0.4
    if 1.0 <= dur <= 4.5:
        return 1.0
    if 0.5 <= dur < 1.0 or 4.5 < dur <= 6.0:
        return 0.7
    if 0.0 < dur < 0.5 or 6.0 < dur <= 10.0:
        return 0.4
    return 0.1


CRITERIA = (
    ("visible_action",      _score_visible_action),
    ("dramatic_question",   _score_dramatic_question),
    ("conflict_or_tension", _score_conflict),
    ("setting_clarity",     _score_setting_clarity),
    ("subtext_carrier",     _score_subtext_carrier),
    ("runtime_fit",         _score_runtime_fit),
)


def evaluate_scene(scene: dict) -> dict:
    scores = {name: round(fn(scene), 2) for name, fn in CRITERIA}
    overall = round(sum(scores.values()) / len(scores), 3)
    fails = [name for name, val in scores.items() if val < SCENE_THRESHOLD]
    return {
        "scene_id": scene.get("scene_id", "?"),
        **scores,
        "scene_filmability": overall,
        "fail_reasons": fails,
        "passes_scene_threshold": overall >= SCENE_THRESHOLD and not fails,
    }


def run_filmability_validator(verbose: bool = True) -> dict:
    """report-only: persists state.filmability_report. Never raises on failures."""
    state = load_state()
    scenes = state.get("adapted_scenes", []) or []

    scene_scores = [evaluate_scene(s) for s in scenes]
    failed_ids = [s["scene_id"] for s in scene_scores if not s["passes_scene_threshold"]]
    overall = (
        round(sum(s["scene_filmability"] for s in scene_scores) / len(scene_scores), 3)
        if scene_scores else 0.0
    )

    report = {
        "scene_scores": scene_scores,
        "overall_filmability": overall,
        "scene_count": len(scene_scores),
        "failed_scene_ids": failed_ids,
        "passes_overall_threshold": overall >= OVERALL_THRESHOLD,
        "thresholds": {"scene": SCENE_THRESHOLD, "overall": OVERALL_THRESHOLD},
        "mode": "report_only",
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    state["filmability_report"] = report
    cap_findings = apply_caps(state, "filmability", mode="hard")
    if cap_findings:
        record_findings(state, agent="filmability_validator", phase="q1_1", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"FILMABILITY REPORT (Q1.1 report-only)")
        print(f"{'='*60}")
        print(f"  scenes:                  {len(scene_scores)}")
        print(f"  overall_filmability:     {overall:.3f} (threshold {OVERALL_THRESHOLD})")
        print(f"  failed_scene_ids:        {failed_ids[:6]}{'…' if len(failed_ids)>6 else ''}")
        print(f"  passes_overall_threshold:{report['passes_overall_threshold']}")
        print(f"  mode:                    report_only — no revision routing")
        print(f"{'='*60}\n")

    return report
