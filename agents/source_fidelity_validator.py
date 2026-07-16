"""
SOURCE FIDELITY VALIDATOR (Q1.2 — report-only)
==============================================
Heuristic per-scene check whether an adapted scene corresponds to its source
chunks (no invented characters, plot points anchored in source). NOT a Phase-8
blocking gate in Phase F.

Three checks per scene:
  - characters_in_state    : every speaking character exists in state.characters
  - source_anchored        : scene.source_chunks present OR invented_bridge=true
  - inventions_flagged     : if no source_chunks, scene must carry an explicit
                             invented_bridge flag (compression/expansion is fine,
                             silent invention is not)

Scene-level fidelity_score is the share of passing checks. Overall is the mean.
"""

from datetime import datetime, timezone
from state_store import load_state, save_state
from utils.schema_caps import apply_caps, record_findings


SCENE_THRESHOLD = 0.85
OVERALL_THRESHOLD = 0.85


def _check_characters(scene: dict, known_names: set[str]) -> tuple[float, list[str]]:
    drafts = scene.get("dialog_draft") or []
    chars_in_scene = scene.get("characters") or []
    issues: list[str] = []
    speakers: set[str] = set()
    if isinstance(drafts, list):
        for d in drafts:
            if not isinstance(d, dict):
                continue
            name = d.get("character") or d.get("speaker") or ""
            if isinstance(name, str) and name.strip():
                speakers.add(name.strip())
    if isinstance(chars_in_scene, list):
        for n in chars_in_scene:
            if isinstance(n, str) and n.strip():
                speakers.add(n.strip())
    if not speakers:
        # Silent scene — neutral pass.
        return 1.0, issues
    unknown = [s for s in speakers if s not in known_names]
    if not unknown:
        return 1.0, issues
    issues.append(f"unknown characters: {unknown[:5]}")
    ratio_known = (len(speakers) - len(unknown)) / len(speakers)
    return round(ratio_known, 2), issues


def _check_source_anchor(scene: dict) -> tuple[float, list[str]]:
    issues: list[str] = []
    src_chunks = scene.get("source_chunks") or []
    invented = bool(scene.get("invented_bridge"))
    if isinstance(src_chunks, list) and src_chunks:
        return 1.0, issues
    if invented:
        return 1.0, issues
    issues.append("no source_chunks AND no invented_bridge flag")
    return 0.0, issues


def _check_invention_flagged(scene: dict) -> tuple[float, list[str]]:
    issues: list[str] = []
    src_chunks = scene.get("source_chunks") or []
    invented = bool(scene.get("invented_bridge"))
    if not src_chunks and not invented:
        issues.append("scene appears invented but lacks invented_bridge=true")
        return 0.0, issues
    return 1.0, issues


def evaluate_scene(scene: dict, known_names: set[str]) -> dict:
    char_score, char_issues = _check_characters(scene, known_names)
    src_score, src_issues = _check_source_anchor(scene)
    inv_score, inv_issues = _check_invention_flagged(scene)
    overall = round((char_score + src_score + inv_score) / 3, 3)
    issues = char_issues + src_issues + inv_issues
    return {
        "scene_id": scene.get("scene_id", "?"),
        "characters_in_state": char_score,
        "source_anchored": src_score,
        "inventions_flagged": inv_score,
        "fidelity_score": overall,
        "issues": issues,
        "passes_scene_threshold": overall >= SCENE_THRESHOLD,
    }


def run_source_fidelity_validator(verbose: bool = True) -> dict:
    """report-only: persists state.source_fidelity_report. Never raises."""
    state = load_state()
    scenes = state.get("adapted_scenes", []) or []
    known_names = set((state.get("characters") or {}).keys())

    scene_scores = [evaluate_scene(s, known_names) for s in scenes]
    failed_ids = [s["scene_id"] for s in scene_scores if not s["passes_scene_threshold"]]
    overall = (
        round(sum(s["fidelity_score"] for s in scene_scores) / len(scene_scores), 3)
        if scene_scores else 0.0
    )

    report = {
        "scene_scores": scene_scores,
        "overall_fidelity": overall,
        "scene_count": len(scene_scores),
        "failed_scene_ids": failed_ids,
        "passes_overall_threshold": overall >= OVERALL_THRESHOLD,
        "thresholds": {"scene": SCENE_THRESHOLD, "overall": OVERALL_THRESHOLD},
        "mode": "report_only",
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    state["source_fidelity_report"] = report
    cap_findings = apply_caps(state, "source_fidelity", mode="hard")
    if cap_findings:
        record_findings(state, agent="source_fidelity_validator", phase="q1_2", findings=cap_findings)
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"SOURCE FIDELITY REPORT (Q1.2 report-only)")
        print(f"{'='*60}")
        print(f"  scenes:                  {len(scene_scores)}")
        print(f"  overall_fidelity:        {overall:.3f} (threshold {OVERALL_THRESHOLD})")
        print(f"  failed_scene_ids:        {failed_ids[:6]}{'…' if len(failed_ids)>6 else ''}")
        print(f"  passes_overall_threshold:{report['passes_overall_threshold']}")
        print(f"  mode:                    report_only — no revision routing")
        print(f"{'='*60}\n")

    return report
