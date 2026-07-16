"""H'' Phase C — Preflight Orchestrator (P0.5).

Validates pipeline run-safety before LLM dispatch. No LLM calls, no state
mutation, no source-file modification. Reads config/state, evaluates
checks, emits human report + state/preflight_report.json.

Exit codes:
    0 — PASS (no FAIL, no WARN)
    1 — WARN (one or more dokumentierte Warnungen)
    2 — FAIL (one or more blockers)

CLI:
    python -m tools.preflight --project projects/example_adaptation
    python -m tools.preflight --project <path> --state story_state.pre-Hpp-meta.backup.json
    python -m tools.preflight --project <path> --json-only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
if str(FRAMEWORK_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_ROOT))


from config.loader import load_config  # noqa: E402
from state_store import get_chunk_text_for_prompt  # noqa: E402
from utils import skill_loader as sl  # noqa: E402


SEVERITY_PASS = "PASS"
SEVERITY_WARN = "WARN"
SEVERITY_FAIL = "FAIL"

PROMPT_SIZE_WARN = 60_000
PROMPT_SIZE_FAIL = 120_000

# Phase-9.5 callsite → expected agent_skills key.
PHASE_9_5_CALLSITES: dict[str, str] = {
    "agents/pacing_analyzer.py": "pacing_analyzer",
    "agents/subtext_auditor.py": "subtext_auditor",
    "agents/dialog_thread_checker.py": "dialog_thread_checker",
    "agents/transition_mapper.py": "transition_mapper",
    "agents/narrative_coherence.py": "narrative_coherence",
    "agents/table_read.py": "table_read",
}

# Phase-9.5 outputs that MUST contain a per-scene list when adapted_scenes>0.
# Empty list while adapted_scenes>0 means the agent never ran functionally.
PHASE_9_5_LIST_FIELDS: list[tuple[str, str]] = [
    ("subtext_audit", "scenes"),
    ("table_read", "scenes"),
]


@dataclass
class CheckResult:
    name: str
    severity: str
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


def _record(results: list[CheckResult], name: str, severity: str,
            message: str, **detail: Any) -> None:
    results.append(CheckResult(name=name, severity=severity,
                               message=message, detail=detail))


# ─── Checks ──────────────────────────────────────────────────────────────


def check_state_meta_sync(state: dict, config: dict,
                          results: list[CheckResult]) -> None:
    meta = state.get("meta", {}) or {}
    drift: list[tuple[str, Any, Any]] = []

    expected_pairs = [
        ("source_file", config.get("source_file")),
        ("target_runtime_minutes", config.get("target_runtime")),
        ("expansion_mode", config.get("expansion_mode")),
    ]
    for key, expected in expected_pairs:
        if expected is None:
            continue
        actual = meta.get(key)
        if actual != expected:
            drift.append((key, actual, expected))

    if drift:
        _record(results, "state_meta_sync", SEVERITY_FAIL,
                f"State-Meta driftet: {drift}", drift=drift)
    else:
        _record(results, "state_meta_sync", SEVERITY_PASS,
                "State-Meta sync mit Config (source_file, target_runtime_minutes, expansion_mode)")

    word_count = meta.get("word_count") or 0
    length_class = meta.get("source_length_class")
    if word_count >= 40_000 and length_class != "novel":
        _record(results, "state_meta_length_class", SEVERITY_FAIL,
                f"word_count={word_count} >=40k aber source_length_class={length_class!r} (erwartet 'novel')",
                word_count=word_count, length_class=length_class)
    else:
        _record(results, "state_meta_length_class", SEVERITY_PASS,
                f"source_length_class={length_class!r} bei word_count={word_count}")

    challenge = meta.get("adaptation_challenge")
    if length_class == "novel" and challenge != "compression":
        _record(results, "state_meta_challenge", SEVERITY_WARN,
                f"length_class=novel aber adaptation_challenge={challenge!r} (erwartet 'compression')")
    else:
        _record(results, "state_meta_challenge", SEVERITY_PASS,
                f"adaptation_challenge={challenge!r}")


def check_source_file(state: dict, project_root: Path,
                      results: list[CheckResult]) -> None:
    source = (state.get("meta") or {}).get("source_file")
    if not source:
        _record(results, "source_file", SEVERITY_FAIL, "meta.source_file fehlt")
        return
    full = project_root / source
    if not full.exists():
        _record(results, "source_file", SEVERITY_FAIL,
                f"source_file {full} nicht gefunden")
        return
    try:
        size = full.stat().st_size
    except OSError as exc:
        _record(results, "source_file", SEVERITY_FAIL,
                f"source_file unlesbar: {exc}")
        return
    if size < 1_000:
        _record(results, "source_file", SEVERITY_WARN,
                f"source_file nur {size} bytes (verdächtig klein)",
                bytes=size, path=str(full))
    else:
        _record(results, "source_file", SEVERITY_PASS,
                f"{full.name} ({size:,} bytes)", bytes=size, path=str(full))


def check_chunk_text(state: dict, project_root: Path,
                     results: list[CheckResult]) -> None:
    chunks = state.get("chunks") or []
    if not chunks:
        _record(results, "chunk_text", SEVERITY_FAIL, "state.chunks ist leer")
        return

    last_idx = len(chunks) - 1
    targets = [("first", 0)]
    if last_idx > 0:
        targets.append(("last", last_idx))

    cwd_saved = Path.cwd()
    try:
        os.chdir(project_root)
        for label, idx in targets:
            try:
                text = get_chunk_text_for_prompt(state, idx, min_chars=100)
                _record(results, f"chunk_text_{label}", SEVERITY_PASS,
                        f"chunk[{idx}] OK ({len(text):,} chars)",
                        chunk_index=idx, length=len(text))
            except (ValueError, IndexError, FileNotFoundError) as exc:
                _record(results, f"chunk_text_{label}", SEVERITY_FAIL,
                        f"chunk[{idx}] reload failed: {exc}",
                        chunk_index=idx, error=str(exc))
    finally:
        os.chdir(cwd_saved)


def _eval_secondary_dirs(cwd: Path) -> list[Path]:
    candidates = (
        cwd / "obsidian-vault" / "config",
        cwd / "HM_obsidian-vault" / "config",
        FRAMEWORK_ROOT / "obsidian-vault" / "config",
    )
    return [p for p in candidates if p.exists()]


def check_skill_lengths(project_root: Path,
                        results: list[CheckResult]) -> None:
    cwd_saved = Path.cwd()
    secondary_saved = list(sl.SECONDARY_SKILLS_DIRS)
    repo_lengths: dict[str, int] = {}
    cwd_lengths: dict[str, int] = {}
    try:
        os.chdir(FRAMEWORK_ROOT)
        sl.SECONDARY_SKILLS_DIRS = _eval_secondary_dirs(FRAMEWORK_ROOT)
        for key in sl.AGENT_SKILLS:
            repo_lengths[key] = len(sl.load_skills_for_agent(key))

        os.chdir(project_root)
        sl.SECONDARY_SKILLS_DIRS = _eval_secondary_dirs(project_root)
        for key in sl.AGENT_SKILLS:
            cwd_lengths[key] = len(sl.load_skills_for_agent(key))
    finally:
        os.chdir(cwd_saved)
        sl.SECONDARY_SKILLS_DIRS = secondary_saved

    mismatches = [(k, repo_lengths[k], cwd_lengths[k])
                  for k in sl.AGENT_SKILLS
                  if repo_lengths[k] != cwd_lengths[k]]
    zeros = [k for k in sl.AGENT_SKILLS if repo_lengths[k] == 0]

    if mismatches:
        _record(results, "skill_lengths_match", SEVERITY_FAIL,
                f"Skill-Längen Repo!=CWD für {len(mismatches)} Agenten",
                mismatches=mismatches, repo=repo_lengths, cwd=cwd_lengths)
    else:
        _record(results, "skill_lengths_match", SEVERITY_PASS,
                f"Skill-Längen Repo == CWD für alle {len(sl.AGENT_SKILLS)} Agenten",
                repo=repo_lengths)

    if zeros:
        _record(results, "skill_lengths_nonzero", SEVERITY_FAIL,
                f"Skill-Length=0 für: {zeros}", zero_keys=zeros)
    else:
        _record(results, "skill_lengths_nonzero", SEVERITY_PASS,
                f"Alle {len(sl.AGENT_SKILLS)} Agenten haben Skill-Length>0",
                min_length=min(repo_lengths.values()),
                max_length=max(repo_lengths.values()))


def check_phase_9_5_callsite_keys(results: list[CheckResult]) -> None:
    pattern = re.compile(r'load_skills_for_agent\(\s*["\']([^"\']+)["\']')
    bad: list[tuple[str, str, str]] = []
    for relpath, expected in PHASE_9_5_CALLSITES.items():
        full = FRAMEWORK_ROOT / relpath
        if not full.exists():
            bad.append((relpath, "FILE_MISSING", expected))
            continue
        text = full.read_text(encoding="utf-8")
        matches = pattern.findall(text)
        if not matches:
            bad.append((relpath, "NO_LOAD_CALL", expected))
            continue
        if expected not in matches:
            actual = matches[0]
            bad.append((relpath, actual, expected))

    if bad:
        _record(results, "phase_9_5_callsite_keys", SEVERITY_FAIL,
                f"Phase-9.5 Callsite-Mismatches: {bad}", mismatches=bad)
    else:
        _record(results, "phase_9_5_callsite_keys", SEVERITY_PASS,
                "Alle 6 Phase-9.5 Callsites laden eigenen Key")


def check_phase_9_5_agent_skills_present(results: list[CheckResult]) -> None:
    missing = [k for k in PHASE_9_5_CALLSITES.values() if k not in sl.AGENT_SKILLS]
    if missing:
        _record(results, "phase_9_5_agent_skills_present", SEVERITY_FAIL,
                f"AGENT_SKILLS fehlt für: {missing}", missing=missing)
    else:
        _record(results, "phase_9_5_agent_skills_present", SEVERITY_PASS,
                "AGENT_SKILLS hat Einträge für alle 6 Phase-9.5-Agenten")


def check_phase_9_5_trash(state: dict, results: list[CheckResult]) -> None:
    """Trash-Detect: Phase-9.5-Outputs mit leeren Per-Scene-Listen trotz
    vorhandenem adapted_scenes.
    """
    adapted = state.get("adapted_scenes") or []
    findings: list[dict[str, Any]] = []
    for top, list_key in PHASE_9_5_LIST_FIELDS:
        node = state.get(top)
        if not isinstance(node, dict):
            continue
        items = node.get(list_key)
        if items is None:
            continue
        if not isinstance(items, list):
            continue
        actual = len(items)
        if adapted and actual == 0:
            findings.append({
                "key": f"{top}.{list_key}",
                "actual": actual,
                "expected_min": len(adapted),
                "verdict": "leer trotz adapted_scenes — Phase 9.5 nicht funktional gelaufen",
            })
        elif adapted and actual < max(1, int(len(adapted) * 0.5)):
            findings.append({
                "key": f"{top}.{list_key}",
                "actual": actual,
                "expected_min": len(adapted),
                "verdict": f"<50% von adapted_scenes ({actual}/{len(adapted)})",
            })

    if findings:
        _record(results, "phase_9_5_trash_detect", SEVERITY_WARN,
                f"Phase-9.5 nicht funktional: {[f['key'] for f in findings]} "
                f"(adapted_scenes={len(adapted)})",
                findings=findings, adapted_scene_count=len(adapted),
                action="Run Phase 9.5 (Plan-File §Phase E S3) "
                       "vor HM-Full-Run-Quality-Eval erforderlich")
    else:
        _record(results, "phase_9_5_trash_detect", SEVERITY_PASS,
                "Phase-9.5-Outputs plausibel oder absent",
                adapted_scene_count=len(adapted))


def check_prompt_size_estimate(state: dict, project_root: Path,
                               results: list[CheckResult]) -> None:
    chunks = state.get("chunks") or []
    if not chunks:
        _record(results, "prompt_size_estimate", SEVERITY_WARN,
                "chunks leer — Schätzung übersprungen")
        return

    meta = state.get("meta") or {}
    active = meta.get("debug_chunks_active")
    debug_n = active or len(chunks)
    debug_n = min(debug_n, len(chunks))
    mode_label = f"Debug-{debug_n}" if active else f"Full-{debug_n}"

    # Phase-G fix: invoke build_analysis_prompt() live for an accurate
    # measurement instead of the prior pseudo-formula
    # (skill+chunk+brain_budget+2000) which undercounted by ~6× because
    # it ignored SYSTEM_PROMPT template, mode directive, graph/location/
    # plotline context blocks, and criteria_instruction.
    #
    # Memory-summary growth during the run is bounded (≤800 tok / ≈3200
    # chars per Phase K) and reflected in worst_case_chars below.
    #
    # In Full-Mode (debug_n large) we sample first/mid/last to keep
    # preflight fast; Debug-Mode (≤5) measures all chunks.
    if debug_n <= 5:
        sample_indices = list(range(debug_n))
    else:
        sample_indices = sorted({0, debug_n // 2, debug_n - 1})

    characters = state.get("characters") or {}
    plot_elements = (state.get("story_analyst_progress") or {}).get(
        "plot_elements", [])
    themes = (state.get("story_analyst_progress") or {}).get("themes", [])

    cwd_saved = Path.cwd()
    secondary_saved = list(sl.SECONDARY_SKILLS_DIRS)
    sizes: list[dict[str, Any]] = []
    try:
        os.chdir(project_root)
        sl.SECONDARY_SKILLS_DIRS = _eval_secondary_dirs(project_root)
        from agents.story_analyst import build_analysis_prompt
        for idx in sample_indices:
            try:
                chunk_text = get_chunk_text_for_prompt(state, idx)
                chunk_len = len(chunk_text)
                system, user = build_analysis_prompt(
                    chunk_text=chunk_text,
                    chunk_index=idx,
                    characters=characters,
                    plot_elements=plot_elements,
                    total_chunks=len(chunks),
                    themes=themes,
                )
                prompt_len = len(system) + len(user)
            except Exception as e:
                prompt_len = 0
                chunk_len = 0
            sizes.append({"chunk": idx, "estimate_chars": prompt_len,
                          "chunk_chars": chunk_len})
    finally:
        os.chdir(cwd_saved)
        sl.SECONDARY_SKILLS_DIRS = secondary_saved

    # Memory-summary worst case: ≤800 tokens cap (Phase K) ≈ 3200 chars.
    MEMORY_GROWTH_BUDGET = 3_200
    base_max = max((s["estimate_chars"] for s in sizes), default=0)
    max_size = base_max + MEMORY_GROWTH_BUDGET

    if max_size > PROMPT_SIZE_FAIL:
        _record(results, "prompt_size_estimate", SEVERITY_FAIL,
                f"Phase-1 Prompt max {max_size:,} > {PROMPT_SIZE_FAIL:,}",
                max_chars=max_size, base_max=base_max,
                memory_growth_budget=MEMORY_GROWTH_BUDGET,
                debug_n=debug_n, sizes=sizes)
    elif max_size > PROMPT_SIZE_WARN:
        _record(results, "prompt_size_estimate", SEVERITY_WARN,
                f"Phase-1 Prompt max {max_size:,} > {PROMPT_SIZE_WARN:,}",
                max_chars=max_size, base_max=base_max,
                memory_growth_budget=MEMORY_GROWTH_BUDGET,
                debug_n=debug_n, sizes=sizes)
    else:
        _record(results, "prompt_size_estimate", SEVERITY_PASS,
                f"Phase-1 Prompt max {max_size:,} chars "
                f"({mode_label}, base {base_max:,} + memory budget "
                f"{MEMORY_GROWTH_BUDGET:,})",
                max_chars=max_size, base_max=base_max,
                memory_growth_budget=MEMORY_GROWTH_BUDGET,
                debug_n=debug_n)


def check_debug_full_mode(state: dict, results: list[CheckResult]) -> None:
    meta = state.get("meta") or {}
    chunks = state.get("chunks") or []
    active = meta.get("debug_chunks_active")
    full = meta.get("debug_chunks_full_count")
    n_chunks = len(chunks)

    if active and full and n_chunks == active and full > active:
        _record(results, "mode_clarity", SEVERITY_PASS,
                f"Debug-Mode: {active}/{full} chunks aktiv",
                mode="debug", active=active, full=full, in_state=n_chunks)
    elif (not active) and full and n_chunks == full:
        _record(results, "mode_clarity", SEVERITY_PASS,
                f"Full-Mode: {full} chunks", mode="full", in_state=n_chunks)
    elif (not active) and (not full) and n_chunks > 0:
        _record(results, "mode_clarity", SEVERITY_WARN,
                f"Mode-Felder fehlen, {n_chunks} chunks im State",
                in_state=n_chunks)
    else:
        _record(results, "mode_clarity", SEVERITY_WARN,
                f"Mode unklar: chunks={n_chunks}, active={active}, full={full}",
                in_state=n_chunks, active=active, full=full)


# ─── Driver ──────────────────────────────────────────────────────────────


def run_preflight(project_root: Path,
                  state_filename: str = "story_state.json"
                  ) -> tuple[dict, list[CheckResult], int]:
    project_root = project_root.resolve()
    results: list[CheckResult] = []

    config_path = project_root / "config" / "projekt.yaml"
    state_path = project_root / state_filename

    if not config_path.exists():
        _record(results, "config_exists", SEVERITY_FAIL,
                f"Config fehlt: {config_path}")
        return ({"project_root": project_root, "state_file": state_filename},
                results, 2)
    _record(results, "config_exists", SEVERITY_PASS,
            f"Config: {config_path.relative_to(project_root)}")

    if not state_path.exists():
        _record(results, "state_exists", SEVERITY_FAIL,
                f"State fehlt: {state_path}")
        return ({"project_root": project_root, "state_file": state_filename},
                results, 2)
    _record(results, "state_exists", SEVERITY_PASS,
            f"State: {state_path.relative_to(project_root)}")

    config = load_config(config_path)
    with open(state_path, "r", encoding="utf-8") as fh:
        state = json.load(fh)

    check_state_meta_sync(state, config, results)
    check_source_file(state, project_root, results)
    check_chunk_text(state, project_root, results)
    check_skill_lengths(project_root, results)
    check_phase_9_5_callsite_keys(results)
    check_phase_9_5_agent_skills_present(results)
    check_phase_9_5_trash(state, results)
    check_prompt_size_estimate(state, project_root, results)
    check_debug_full_mode(state, results)

    has_fail = any(r.severity == SEVERITY_FAIL for r in results)
    has_warn = any(r.severity == SEVERITY_WARN for r in results)
    exit_code = 2 if has_fail else (1 if has_warn else 0)
    report = {"project_root": project_root, "state_file": state_filename}
    return report, results, exit_code


def render_human(report: dict, results: list[CheckResult],
                 exit_code: int) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append(f"PREFLIGHT REPORT — {report['project_root']}")
    lines.append(f"  state_file: {report['state_file']}")
    lines.append("=" * 72)
    counts = {SEVERITY_PASS: 0, SEVERITY_WARN: 0, SEVERITY_FAIL: 0}
    markers = {SEVERITY_PASS: "✓", SEVERITY_WARN: "⚠", SEVERITY_FAIL: "✗"}
    for r in results:
        counts[r.severity] += 1
        lines.append(f"  [{markers[r.severity]}] {r.severity:4s}  "
                     f"{r.name:34s}  {r.message}")
    lines.append("─" * 72)
    verdict = {0: "PASS (grün)", 1: "WARN (gelb)", 2: "FAIL (rot)"}[exit_code]
    lines.append(f"  Σ  PASS={counts[SEVERITY_PASS]}  "
                 f"WARN={counts[SEVERITY_WARN]}  "
                 f"FAIL={counts[SEVERITY_FAIL]}  →  {verdict}  "
                 f"(exit {exit_code})")
    lines.append("=" * 72)
    return "\n".join(lines)


def to_json_payload(report: dict, results: list[CheckResult],
                    exit_code: int) -> dict:
    return {
        "project_root": str(report["project_root"]),
        "state_file": report["state_file"],
        "exit_code": exit_code,
        "ok": exit_code == 0,
        "counts": {
            "pass": sum(1 for r in results if r.severity == SEVERITY_PASS),
            "warn": sum(1 for r in results if r.severity == SEVERITY_WARN),
            "fail": sum(1 for r in results if r.severity == SEVERITY_FAIL),
        },
        "checks": [asdict(r) for r in results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.preflight")
    parser.add_argument("--project", required=True,
                        help="Project root (absolute or relative to framework root)")
    parser.add_argument("--state", default="story_state.json",
                        help="State filename relative to project root "
                             "(default: story_state.json)")
    parser.add_argument("--json-only", action="store_true",
                        help="Print JSON payload to stdout, suppress human output")
    parser.add_argument("--no-write-report", action="store_true",
                        help="Skip writing state/preflight_report.json")
    args = parser.parse_args(argv)

    project_root = Path(args.project)
    if not project_root.is_absolute():
        project_root = (FRAMEWORK_ROOT / args.project).resolve()
    if not project_root.exists():
        print(f"ERROR: project root not found: {project_root}",
              file=sys.stderr)
        return 2

    report, results, exit_code = run_preflight(project_root, args.state)
    payload = to_json_payload(report, results, exit_code)

    if not args.no_write_report:
        state_dir = project_root / "state"
        state_dir.mkdir(exist_ok=True)
        report_path = state_dir / "preflight_report.json"
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    if args.json_only:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_human(report, results, exit_code))
        if not args.no_write_report:
            print(f"  report: {project_root / 'state' / 'preflight_report.json'}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
