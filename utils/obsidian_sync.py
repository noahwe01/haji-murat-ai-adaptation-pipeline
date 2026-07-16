"""
OBSIDIAN SYNC
=============
Synchronizes story_state.json → Obsidian Vault (Markdown files).
Direction: Always JSON → Obsidian. Never the reverse.

Called by the Orchestrator after Phase 2 and Phase 7 (batched).
Generates Wikilinks for the Obsidian graph automatically.
"""

import json
from pathlib import Path
from datetime import datetime
from state_store import load_state, _compat


def full_sync(vault_path: str) -> dict:
    """
    Full synchronization: State → Obsidian.
    Returns statistics.
    """
    state = load_state()
    vault = Path(vault_path)

    stats = {
        "characters": sync_characters(state, vault),
        "locations": sync_locations(state, vault),
        "scenes": sync_scenes(state, vault),
        "timeline": sync_timeline(state, vault),
        "themes": sync_themes(state, vault),
        "continuity": sync_continuity_log(state, vault),
        "dashboard": sync_dashboard(state, vault),
    }
    return stats


def sync_characters(state: dict, vault: Path) -> int:
    """Writes character files and REGISTER.md."""
    chars_dir = vault / "characters"
    chars_dir.mkdir(exist_ok=True)
    count = 0

    for name, data in state.get("characters", {}).items():
        safe_name = name.replace(" ", "_").replace("/", "-")
        filepath = chars_dir / f"{safe_name}.md"

        role = _compat(data, "role", "rolle", "unknown")
        want = data.get("want", "—")
        need = data.get("need", "—")
        fear = _compat(data, "fear", "angst", "—")
        arc = data.get("arc", {})
        vp = data.get("voice_profile", {})

        content = f"# {name}\n\n"
        content += f"**Role:** {role}\n"
        first_mention = _compat(data, "first_mention_chunk", "erste_erwähnung_chunk", "?")
        content += f"**First Appearance:** {first_mention}\n\n"
        content += f"## Psychology\n\n"
        content += f"| Field | Value |\n|-------|-------|\n"
        content += f"| Want | {want} |\n"
        content += f"| Need | {need} |\n"
        content += f"| Fear | {fear} |\n"
        contradiction = _compat(data, "contradiction", "widerspruch", "—")
        content += f"| Contradiction | {contradiction} |\n\n"

        if arc and isinstance(arc, dict):
            content += f"## Character Arc\n\n"
            start_state = _compat(arc, "start_state", "ausgangszustand", "—")
            change = _compat(arc, "change", "veränderung", "—")
            end_state = _compat(arc, "end_state", "endzustand", "—")
            arc_type = _compat(data, "arc_type", "arc_typ", "—")
            content += f"**Start State:** {start_state}\n"
            content += f"**Change:** {change}\n"
            content += f"**End State:** {end_state}\n"
            content += f"**Type:** {arc_type}\n\n"

        if vp:
            content += f"## Voice Profile\n\n"
            voice_desc = _compat(vp, "voice_description", "stimmbeschreibung", "")
            if voice_desc:
                content += f"{voice_desc}\n\n"
            verbal_tics = vp.get("verbal_tics", [])
            if verbal_tics:
                content += f"**Verbal Tics:** {', '.join(verbal_tics)}\n"
            avoidances = _compat(vp, "avoidances", "vermeidungen", [])
            if avoidances:
                content += f"**Never Says:** {', '.join(avoidances)}\n"
            examples = vp.get("dialog_examples", [])
            if examples:
                content += f"\n### Example Dialog\n\n"
                for ex in examples[:5]:
                    if isinstance(ex, dict):
                        content += f"- *{ex.get('context', '?')}:* \"{ex.get('text', '')}\"\n"
            content += "\n"

        filepath.write_text(content, encoding="utf-8")
        count += 1

    # REGISTER.md
    register = chars_dir / "REGISTER.md"
    reg_content = "# Character Register\n\n"
    reg_content += f"**Total:** {len(state.get('characters', {}))}\n\n"
    reg_content += "| Character | Role | Want | Need |\n|-----------|------|------|------|\n"
    for name, data in state.get("characters", {}).items():
        safe = name.replace(" ", "_").replace("/", "-")
        role = _compat(data, "role", "rolle", "?")
        reg_content += (
            f"| [[{safe}\\|{name}]] | {role} | "
            f"{data.get('want', '—')[:30]} | {data.get('need', '—')[:30]} |\n"
        )
    register.write_text(reg_content, encoding="utf-8")

    return count


def sync_locations(state: dict, vault: Path) -> int:
    """Writes location files."""
    locs_dir = vault / "locations"
    locs_dir.mkdir(exist_ok=True)
    count = 0

    for loc in state.get("world", {}).get("locations", []):
        name = loc.get("name", "Unknown")
        safe_name = name.replace(" ", "_").replace("/", "-").replace(".", "")[:50]
        filepath = locs_dir / f"{safe_name}.md"

        description = _compat(loc, "description", "beschreibung", "—")
        content = f"# {name}\n\n"
        content += f"**Description:** {description}\n\n"

        cinematic = _compat(loc, "cinematic_description", "filmische_beschreibung", "")
        if cinematic:
            content += f"## Cinematic Translation\n\n{cinematic}\n\n"

        atmosphere = _compat(loc, "atmosphere", "atmosphäre", "")
        if atmosphere:
            content += f"**Atmosphere:** {atmosphere}\n\n"

        notes = loc.get("production_notes", [])
        if notes:
            content += f"## Production Design\n\n"
            for note in notes:
                content += f"- {note}\n"

        filepath.write_text(content, encoding="utf-8")
        count += 1

    # REGISTER.md
    register = locs_dir / "REGISTER.md"
    reg_content = "# Location Register\n\n"
    reg_content += f"**Total:** {len(state.get('world', {}).get('locations', []))}\n\n"
    for loc in state.get("world", {}).get("locations", []):
        safe = loc.get("name", "?").replace(" ", "_").replace("/", "-").replace(".", "")[:50]
        reg_content += f"- [[{safe}|{loc.get('name', '?')}]]\n"
    register.write_text(reg_content, encoding="utf-8")

    return count


def sync_scenes(state: dict, vault: Path) -> int:
    """Writes scene files with Wikilinks to characters and locations."""
    scenes_dir = vault / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    count = 0

    for scene in state.get("adapted_scenes", []):
        sid = _compat(scene, "scene_id", "szenen_id", "S000")
        filepath = scenes_dir / f"{sid}.md"

        slug = scene.get("slug", "")
        confidence = _compat(scene, "confidence", "konfidenz", 0)
        status = "Finalized" if confidence >= 0.75 else "In Revision"

        content = f"# {sid} — {slug}\n\n"
        content += f"**Confidence:** {confidence:.2f} | **Status:** {status}\n"
        duration = _compat(scene, "duration_minutes", "dauer_minuten", "?")
        content += f"**Duration:** ~{duration} min.\n\n"

        # Characters with Wikilinks
        characters = _compat(scene, "characters", "figuren", [])
        if characters:
            links = [f"[[characters/{f.replace(' ', '_')}|{f}]]" for f in characters]
            content += f"**Characters:** {', '.join(links)}\n\n"

        action = _compat(scene, "action", "handlung", "—")
        content += f"## Action\n\n{action}\n\n"

        # Dialog drafts
        drafts = scene.get("dialog_draft", [])
        if drafts and isinstance(drafts, list):
            content += f"## Dialog Draft\n\n"
            for d in drafts:
                if isinstance(d, dict):
                    content += f"**{d.get('character', '?')}:** \"{d.get('line', '')}\"\n"
                    if d.get("subtext"):
                        content += f"  *(Subtext: {d['subtext']})*\n"
                    content += "\n"

        # Emotional beats
        beats = scene.get("emotional_beats", [])
        if beats:
            content += f"## Emotional Beats\n\n"
            for b in beats:
                if isinstance(b, dict):
                    content += f"- **{b.get('beat', '')}**\n"
                    content += f"  Audience: {b.get('audience_feels', '')}\n"
                    content += f"  Character: {b.get('character_feels', '')}\n"

        visual_note = _compat(scene, "visual_note", "visuelle_note", "—")
        content += f"\n## Visual Notes\n\n{visual_note}\n"

        filepath.write_text(content, encoding="utf-8")
        count += 1

    # Scene overview
    overview = scenes_dir / "SCENES.md"
    ov_content = "# Scene Overview\n\n"
    ov_content += f"**Total:** {len(state.get('adapted_scenes', []))}\n\n"
    ov_content += "| ID | Slug | Confidence | Status |\n|-----|------|------------|--------|\n"
    for s in state.get("adapted_scenes", []):
        sid = _compat(s, "scene_id", "szenen_id", "?")
        conf = _compat(s, "confidence", "konfidenz", 0)
        status = "✓" if conf >= 0.75 else "⚠"
        ov_content += f"| [[{sid}]] | {s.get('slug', '')[:40]} | {conf:.2f} | {status} |\n"
    overview.write_text(ov_content, encoding="utf-8")

    return count


def sync_timeline(state: dict, vault: Path) -> int:
    """Writes TIMELINE.md."""
    timeline_dir = vault / "timeline"
    timeline_dir.mkdir(exist_ok=True)

    events = state.get("world", {}).get("timeline", [])
    content = "# Timeline\n\n"

    if events:
        content += "| Time | Event | Location | Characters |\n|------|-------|----------|------------|\n"
        for e in events:
            chars = ", ".join(e.get("characters", [])[:3])
            content += f"| {e.get('time', '?')} | {e.get('event', '')[:50]} | {e.get('location', '')} | {chars} |\n"
    else:
        content += "*No timeline data yet.*\n"

    (timeline_dir / "TIMELINE.md").write_text(content, encoding="utf-8")
    return len(events)


def sync_themes(state: dict, vault: Path) -> int:
    """Writes THEMES.md."""
    themes_dir = vault / "themes"
    themes_dir.mkdir(exist_ok=True)

    themes = state.get("plot", {}).get("themes", [])
    content = "# Themes & Motifs\n\n"
    for t in themes:
        content += f"- {t}\n"

    (themes_dir / "THEMES.md").write_text(content, encoding="utf-8")
    return len(themes)


def sync_continuity_log(state: dict, vault: Path) -> int:
    """Writes LOG.md."""
    log_dir = vault / "continuity_log"
    log_dir.mkdir(exist_ok=True)

    log = state.get("continuity_log", [])
    content = "# Continuity Log\n\n"
    content += f"**Open:** {sum(1 for i in log if not i.get('resolved'))}\n"
    content += f"**Resolved:** {sum(1 for i in log if i.get('resolved'))}\n\n"

    if log:
        content += "| Timestamp | Scene | Issue | Status |\n|-----------|-------|-------|--------|\n"
        for entry in log[-30:]:  # Last 30
            status = "✓" if entry.get("resolved") else "⚠"
            content += (
                f"| {entry.get('timestamp', '?')[:16]} | {entry.get('scene_id', '—')} | "
                f"{entry.get('issue', '')[:50]} | {status} |\n"
            )

    (log_dir / "LOG.md").write_text(content, encoding="utf-8")
    return len(log)


def sync_dashboard(state: dict, vault: Path) -> int:
    """Updates START.md with current status."""
    meta = state.get("meta", {})
    stats = state.get("confidence_stats", {})
    coverage = state.get("coverage_report")

    content = f"# {meta.get('title', 'Project')} — Project Vault\n\n"
    content += f"> Project-specific long-term memory.\n"
    content += f"> General adaptation methodology in the **Adaptation Brain**.\n\n"

    content += "## Project Status\n\n"
    content += "| Field | Value |\n|-------|-------|\n"
    content += f"| Status | {meta.get('status', '?')} |\n"
    content += f"| Phase | {meta.get('current_phase', '—')} |\n"
    content += f"| Target Runtime | {meta.get('target_runtime_minutes', '?')} min. |\n"
    content += f"| Scenes | {len(state.get('adapted_scenes', []))} / {meta.get('scene_budget', '?')} |\n"
    content += f"| Characters | {len(state.get('characters', {}))} |\n"
    content += f"| Locations | {len(state.get('world', {}).get('locations', []))} |\n"
    content += f"| Open Flags | {sum(1 for i in state.get('continuity_log', []) if not i.get('resolved'))} |\n"

    if stats and stats.get("mean"):
        content += f"| Confidence avg | {stats['mean']:.2f} |\n"

    if coverage:
        content += f"| Coverage | {coverage.get('overall_verdict', '?')} ({coverage.get('overall_score_weighted', '?')}) |\n"

    content += "\n## Navigation\n\n"
    content += "- [[characters/REGISTER|Character Register]]\n"
    content += "- [[locations/REGISTER|Location Register]]\n"
    content += "- [[timeline/TIMELINE|Timeline]]\n"
    content += "- [[themes/THEMES|Themes & Motifs]]\n"
    content += "- [[scenes/SCENES|Scene Overview]]\n"
    content += "- [[continuity_log/LOG|Continuity Log]]\n"

    content += f"\n---\n*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"

    (vault / "START.md").write_text(content, encoding="utf-8")
    return 1
