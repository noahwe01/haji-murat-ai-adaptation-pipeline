"""
MAIN — CLI entry point for the KI-Adapter pipeline.

Usage:
    python main.py                  # Full pipeline run
    python main.py --phase 9.5      # Run only Phase 9.5 (Analysis Layer)

Phase 9.5 prints the prompt-building instructions for each analysis agent.
Actual LLM calls are performed externally (Claude Code subagent dispatch).
"""

import argparse
import json
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import Orchestrator, ANALYSIS_AGENTS
from config.loader import load_config


def run_phase_9_5(verbose: bool = True):
    """
    Phase 9.5: Analysis Layer.

    Builds prompts for all 6 analysis agents and prints them.
    In production, Claude Code dispatches each prompt as a subagent call,
    collects the JSON results, then calls orchestrator.run_analysis_layer().
    """
    from importlib import import_module

    config = load_config()
    orch = Orchestrator(config)

    print("\n" + "=" * 60)
    print("PHASE 9.5 — ANALYSIS LAYER")
    print("=" * 60)

    specs = orch.get_analysis_agent_specs()
    prompts = {}

    for spec in specs:
        name = spec["name"]
        model = spec["model"]

        # Build prompt
        module_path, func_name = spec["build_prompt"].rsplit(".", 1)
        module = import_module(module_path)
        build_fn = getattr(module, func_name)

        try:
            prompt = build_fn()
            prompts[name] = prompt
            prompt_path = os.path.join("state", f"_prompt_{name}.txt")
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(prompt)
            if verbose:
                print(f"  ✓ {name} ({model}): prompt built, "
                      f"{len(prompt)} chars → {prompt_path}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    print(f"\n  {len(prompts)}/{len(specs)} prompts ready.")
    print("  DISPATCH: Send all 6 subagent calls in ONE Claude message block (parallel).")
    print("  Agents are independent — read adapted_scenes, write to separate state keys.")
    print("  Sequential dispatch = ~6x wallclock waste at identical token cost.")
    print("  After results return: parse JSON, call orchestrator.run_analysis_layer().")
    print("=" * 60 + "\n")

    return prompts


def main():
    parser = argparse.ArgumentParser(description="KI-Adapter Pipeline")
    parser.add_argument("--phase", type=str, default=None,
                        help="Run a specific phase (e.g., '9.5' for Analysis Layer)")
    args = parser.parse_args()

    if args.phase == "9.5":
        run_phase_9_5()
    elif args.phase is None:
        print("Full pipeline run not yet implemented via CLI.")
        print("Use individual agent calls or --phase 9.5")
    else:
        print(f"Unknown phase: {args.phase}")
        print("Available: 9.5 (Analysis Layer)")
        sys.exit(1)


if __name__ == "__main__":
    main()
