"""H'' Phase E — S1 Prompt-Smoke (no-LLM).

Builds Phase-1 (story_analyst) and Phase-5 (adaptation_agent) prompts for
all Debug-Chunks and reports sizes (chars + est_tokens). Reports state.meta
sync, chunk_text lengths, skill-lengths repo-vs-cwd. No LLM calls, no state
mutation.

CLI:
    python -m tools.prompt_smoke --project projects/example_adaptation
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
if str(FRAMEWORK_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_ROOT))


def _est_tokens(s: str) -> int:
    return len(s) // 4


def _skill_lens(agents: list[str]) -> dict[str, int]:
    from utils import skill_loader as sl
    return {a: len(sl.load_skills_for_agent(a) or "") for a in agents}


def _skill_lens_at_cwd(project_root: Path, agents: list[str]) -> dict[str, int]:
    """Re-evaluate SECONDARY_SKILLS_DIRS at project_root, return lengths."""
    from utils import skill_loader as sl
    saved_secondary = list(sl.SECONDARY_SKILLS_DIRS)
    saved_cwd = os.getcwd()
    try:
        os.chdir(project_root)
        sl.SECONDARY_SKILLS_DIRS = [
            Path("obsidian-vault/config").resolve(),
            Path("HM_obsidian-vault/config").resolve(),
            FRAMEWORK_ROOT / "obsidian-vault/config",
        ]
        return {a: len(sl.load_skills_for_agent(a) or "") for a in agents}
    finally:
        sl.SECONDARY_SKILLS_DIRS = saved_secondary
        os.chdir(saved_cwd)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--out", default=None,
                   help="Optional Markdown-Output (default: stdout only)")
    args = p.parse_args()

    project_root = Path(args.project).resolve()
    if not project_root.exists():
        print(f"ERROR: project not found: {project_root}", file=sys.stderr)
        return 2

    saved_cwd = os.getcwd()
    os.chdir(project_root)
    try:
        from config.loader import load_config
        from state_store import load_state, get_chunk_text_for_prompt

        config = load_config()
        state = load_state()
        chunks = state.get("chunks", [])
        n_chunks = len(chunks)
        characters = state.get("characters", {})
        plot_elements = state.get("plot_elements", []) or []
        themes = state.get("themes") or None

        report: dict = {
            "project": str(project_root.name),
            "state_meta": {
                "title": state["meta"].get("title"),
                "source_file": state["meta"].get("source_file"),
                "expansion_mode": state["meta"].get("expansion_mode"),
                "source_length_class": state["meta"].get("source_length_class"),
                "target_runtime_minutes": state["meta"].get("target_runtime_minutes"),
                "word_count": state["meta"].get("word_count"),
                "scene_budget": state["meta"].get("scene_budget"),
                "debug_chunks_active": state["meta"].get("debug_chunks_active"),
            },
            # Sync-Logik analog tools/preflight.check_state_meta_sync:
            # config-feld == None → Sync-Check skip (kein Drift wenn config nichts vorgibt).
            "config_meta_match": {
                "source_file": (config.get("source_file") is None
                                or state["meta"].get("source_file") == config.get("source_file")),
                "expansion_mode": (config.get("expansion_mode") is None
                                   or state["meta"].get("expansion_mode") == config.get("expansion_mode")),
                "target_runtime_minutes": (config.get("target_runtime") is None
                                           or state["meta"].get("target_runtime_minutes") == config.get("target_runtime")),
            },
            "chunks_total": n_chunks,
            "chunk_lengths": {},
            "skill_lengths_repo": {},
            "skill_lengths_cwd": {},
            "phase1_prompts": [],
            "phase5_prompts": [],
        }

        for i in range(n_chunks):
            try:
                txt = get_chunk_text_for_prompt(state, i)
                report["chunk_lengths"][i] = len(txt)
            except Exception as e:
                report["chunk_lengths"][i] = f"ERROR: {e}"

        # Skill-Längen (Repo-Root vs Project-CWD)
        agents_to_check = [
            "story_analyst", "adaptation_agent", "revision_agent",
            "script_writer_screenplay", "pacing_analyzer", "subtext_auditor",
            "dialog_thread_checker", "transition_mapper", "narrative_coherence",
            "table_read",
        ]
        report["skill_lengths_cwd"] = _skill_lens(agents_to_check)
        # Repo-root: chdir into framework, re-eval
        os.chdir(FRAMEWORK_ROOT)
        from utils import skill_loader as sl
        saved_secondary = list(sl.SECONDARY_SKILLS_DIRS)
        try:
            sl.SECONDARY_SKILLS_DIRS = [
                Path("obsidian-vault/config").resolve(),
                FRAMEWORK_ROOT / "obsidian-vault/config",
            ]
            report["skill_lengths_repo"] = _skill_lens(agents_to_check)
        finally:
            sl.SECONDARY_SKILLS_DIRS = saved_secondary
        os.chdir(project_root)

        # Phase-1 Prompts
        from agents.story_analyst import build_analysis_prompt
        for i in range(n_chunks):
            chunk_text = get_chunk_text_for_prompt(state, i)
            sys_prompt, user_msg = build_analysis_prompt(
                chunk_text, i, characters, plot_elements, n_chunks, themes=themes
            )
            full = sys_prompt + "\n\n" + user_msg
            report["phase1_prompts"].append({
                "chunk": i,
                "sys_chars": len(sys_prompt),
                "user_chars": len(user_msg),
                "total_chars": len(full),
                "est_tokens": _est_tokens(full),
            })

        # Phase-5 Prompts (build_adaptation_prompt is side-effect-free at default)
        from agents.adaptation_agent import build_adaptation_prompt
        for i in range(n_chunks):
            chunk_text = get_chunk_text_for_prompt(state, i)
            prompt = build_adaptation_prompt(chunk_text, i)  # persist_reference_meta=False
            report["phase5_prompts"].append({
                "chunk": i,
                "total_chars": len(prompt),
                "est_tokens": _est_tokens(prompt),
            })

    finally:
        os.chdir(saved_cwd)

    # Render
    print("=" * 72)
    print(f"S1 PROMPT-SMOKE — {report['project']}")
    print("=" * 72)
    print("\n[STATE META]")
    for k, v in report["state_meta"].items():
        print(f"  {k:30s} {v}")
    print("\n[CONFIG↔STATE SYNC]")
    for k, v in report["config_meta_match"].items():
        flag = "✓" if v else "✗"
        print(f"  {flag} {k}")
    print(f"\n[CHUNKS] total={report['chunks_total']}")
    for i, ln in report["chunk_lengths"].items():
        print(f"  chunk[{i}] len={ln}")
    print("\n[SKILL LENGTHS] (repo-root vs cwd)")
    for a in report["skill_lengths_repo"]:
        r = report["skill_lengths_repo"][a]
        c = report["skill_lengths_cwd"][a]
        flag = "✓" if r == c else "✗"
        print(f"  {flag} {a:30s} repo={r:5d}  cwd={c:5d}")
    print("\n[PHASE-1 PROMPTS] (story_analyst)")
    for row in report["phase1_prompts"]:
        print(f"  chunk={row['chunk']}  sys={row['sys_chars']:6d}  "
              f"user={row['user_chars']:5d}  total={row['total_chars']:6d}  "
              f"≈{row['est_tokens']:5d} tok")
    p1_max = max(r["total_chars"] for r in report["phase1_prompts"])
    p1_max_tok = max(r["est_tokens"] for r in report["phase1_prompts"])
    print(f"  MAX={p1_max} chars / {p1_max_tok} tok")
    print("\n[PHASE-5 PROMPTS] (adaptation_agent)")
    for row in report["phase5_prompts"]:
        print(f"  chunk={row['chunk']}  total={row['total_chars']:6d}  "
              f"≈{row['est_tokens']:5d} tok")
    p5_max = max(r["total_chars"] for r in report["phase5_prompts"])
    p5_max_tok = max(r["est_tokens"] for r in report["phase5_prompts"])
    print(f"  MAX={p5_max} chars / {p5_max_tok} tok")
    print()

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"  json report: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
