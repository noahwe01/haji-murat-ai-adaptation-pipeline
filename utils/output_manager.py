"""
OUTPUT MANAGER
==============
Versioned output of analysis, treatment, and screenplay.
Files are saved in output/ subdirectories with ascending
version numbers (01, 02, ...).
"""

import os
import json
from pathlib import Path
from datetime import datetime
from state_store import load_state, _compat


OUTPUT_DIR = "output"


def _next_version(folder: str, prefix: str, ext: str) -> int:
    """Determines the next version number."""
    path = Path(OUTPUT_DIR) / folder
    path.mkdir(parents=True, exist_ok=True)
    existing = sorted(path.glob(f"{prefix}_*.{ext}"))
    if not existing:
        return 1
    last = existing[-1].stem  # e.g. "Treatment_03"
    try:
        return int(last.split("_")[-1]) + 1
    except ValueError:
        return len(existing) + 1


def save_analysis() -> str:
    """
    Saves an analysis summary to output/analyse/.
    Contains: Characters, plot structure, themes, tension curve, subplots.
    """
    state = load_state()
    version = _next_version("analyse", "Analyse", "txt")
    filename = f"Analyse_{version:02d}.txt"
    filepath = Path(OUTPUT_DIR) / "analyse" / filename

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"ANALYSIS — {state['meta']['title']}")
    lines.append(f"Version {version:02d} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"{'='*60}\n")

    # Logline
    logline = state["plot"].get("logline", "")
    if logline:
        lines.append(f"LOGLINE: {logline}\n")

    # Characters
    lines.append("CHARACTERS:")
    for name, data in state.get("characters", {}).items():
        role = _compat(data, "role", "rolle", "?")
        want = data.get("want", "?")
        need = data.get("need", "?")
        lines.append(f"  {name} ({role})")
        lines.append(f"    Want: {want}")
        lines.append(f"    Need: {need}")
        vp = data.get("voice_profile", {})
        if vp:
            voice_desc = _compat(vp, "voice_description", "stimmbeschreibung", "")
            if voice_desc:
                lines.append(f"    Voice: {voice_desc[:100]}")
    lines.append("")

    # Act structure
    lines.append("THREE-ACT STRUCTURE:")
    for act in state["plot"].get("acts", []):
        act_num = _compat(act, "act", "akt", "?")
        elem_count = _compat(act, "element_count", "elemente_anzahl", 0)
        lines.append(f"  Act {act_num}: {elem_count} elements")
        elements = _compat(act, "elements", "elemente", [])
        for el in elements[:3]:
            lines.append(f"    - {el}")
    lines.append("")

    # Themes
    lines.append("THEMES:")
    for t in state["plot"].get("themes", []):
        lines.append(f"  - {t}")
    lines.append("")

    # Subplots
    lines.append("SUBPLOTS:")
    for sp in state["plot"].get("subplots", []):
        keep = "✓" if sp.get("keep", True) else "✗"
        lines.append(f"  [{keep}] {sp.get('id', '?')} (Prio {sp.get('priority', '?')}): {sp.get('description', '')[:60]}")
    lines.append("")

    # Tension curve
    tc = state["plot"].get("tension_curve", [])
    if tc:
        lines.append(f"TENSION CURVE: {' → '.join(f'{t:.1f}' for t in tc)}")

    content = "\n".join(lines)
    filepath.write_text(content, encoding="utf-8")
    print(f"Analysis saved: {filepath}")
    return str(filepath)


def save_treatment() -> str:
    """Saves the treatment to output/treatment/."""
    state = load_state()
    version = _next_version("treatment", "Treatment", "txt")
    filename = f"Treatment_{version:02d}.txt"
    filepath = Path(OUTPUT_DIR) / "treatment" / filename

    treatment = state.get("treatment_text", "")
    if not treatment:
        raise ValueError("No treatment found in state.")

    # Add header
    header = (
        f"{'='*60}\n"
        f"TREATMENT — {state['meta']['title']}\n"
        f"Version {version:02d} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"Target Runtime: {state['meta'].get('target_runtime_minutes', '?')} min.\n"
        f"Scenes: {len(state.get('adapted_scenes', []))}\n"
    )

    coverage = state.get("coverage_report")
    if coverage:
        header += f"Coverage: {coverage.get('overall_verdict', '?')} ({coverage.get('overall_score_weighted', '?')})\n"

    header += f"{'='*60}\n\n"

    filepath.write_text(header + treatment, encoding="utf-8")
    print(f"Treatment saved: {filepath}")
    return str(filepath)


def save_screenplay() -> str:
    """Saves the screenplay to output/drehbuch/."""
    state = load_state()
    version = _next_version("drehbuch", "Drehbuch", "fountain")
    filename = f"Drehbuch_{version:02d}.fountain"
    filepath = Path(OUTPUT_DIR) / "drehbuch" / filename

    script = state.get("final_script", "")
    if not script:
        raise ValueError("No screenplay found in state.")

    filepath.write_text(script, encoding="utf-8")
    print(f"Screenplay saved: {filepath}")
    return str(filepath)
