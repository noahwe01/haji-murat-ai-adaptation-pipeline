"""
WORLD AGENT
===========
Translates literary space and time descriptions into cinematic
location sheets, timelines, and production design notes.

Lightest of the new agents — structured extraction,
less creative work. Runs with Sonnet.
"""

import re
from state_store import load_state, save_state, _compat


# ─── System Prompts ──────────────────────────────────────────────────

SYSTEM_WORLD_EXTRACTION = """You are the World Agent. You translate literary space and
time descriptions into concrete, cinematically usable data.

Chunk text:
{chunk_text}

Existing location data:
{current_locations}

Style manifest:
{style_manifest}

Extract for each identified location:

1. LOCATION NAME: Unique identifier (e.g. "INT. CHILDHOOD APARTMENT - DAY")
2. LITERARY DESCRIPTION: Exact text passages as basis
3. CINEMATIC TRANSLATION: How does it look on film? (Camera, light, space)
4. ATMOSPHERE: Emotional quality
5. RECURRING: Yes/No
6. TIMEFRAME: Act, time of day/season
7. PRODUCTION DESIGN NOTES: Props, colors, textures for characterization

Also extract timeline events:
- What happens WHEN at WHICH location with WHICH characters?

Respond as JSON:
{{
  "locations_new": [
    {{
      "name": "INT./EXT. LOCATION - TIME",
      "literary_description": "...",
      "cinematic_description": "...",
      "atmosphere": "...",
      "recurring": true/false,
      "timeframe": "...",
      "production_notes": ["..."]
    }}
  ],
  "locations_updated": [
    {{"name": "...", "update": "..."}}
  ],
  "timeline_events": [
    {{
      "event": "...",
      "time": "...",
      "location": "...",
      "characters": ["..."],
      "chunk_id": "..."
    }}
  ]
}}
"""

SYSTEM_WORLD_SYNTHESIS = """Create a complete location bible and timeline
from the collected extraction data.

All extracted locations:
{all_locations}

All timeline events:
{all_events}

Style manifest:
{style_manifest}

Create:
1. LOCATION BIBLE: Each location with cinematic description, atmosphere, and production notes
2. CHRONOLOGICAL TIMELINE: All events in chronological order
3. RECURRING LOCATIONS: Which places appear multiple times? (important for set planning)
4. ATMOSPHERE MAP: How does the visual mood change throughout the film?

Respond as JSON.
"""


# ─── Location Name Normalization ─────────────────────────────────────

_ARTICLE_PATTERN = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)


def _normalize_location_name(name: str) -> str:
    """Removes leading English articles (the, a, an) from location names."""
    return _ARTICLE_PATTERN.sub("", name).strip()


# ─── World Agent Functions ──────────────────────────────────────────

def run_world_extraction(chunk_results: list) -> dict:
    """
    Processes chunk extractions and accumulates location and timeline data.

    Args:
        chunk_results: List of extraction results per chunk

    Returns:
        Accumulated world data
    """
    all_locations = {}
    all_events = []

    for result in chunk_results:
        # New locations
        for loc in result.get("locations_new", []):
            name = loc.get("name", "")
            name = _normalize_location_name(name)
            if not name:
                continue
            loc["name"] = name
            if name not in all_locations:
                all_locations[name] = loc
            else:
                # Supplement existing location
                existing = all_locations[name]
                existing["production_notes"] = list(set(
                    existing.get("production_notes", []) + loc.get("production_notes", [])
                ))

        # Location updates
        for update in result.get("locations_updated", []):
            name = _normalize_location_name(update.get("name", ""))
            if name in all_locations:
                all_locations[name]["update_notes"] = update.get("update", "")

        # Timeline events
        all_events.extend(result.get("timeline_events", []))

    return {
        "locations": list(all_locations.values()),
        "timeline_events": all_events,
    }


def run_world_synthesis(synthesis_result: dict) -> dict:
    """
    Saves the synthesized world data to the state.

    Args:
        synthesis_result: Synthesis output of the LLM

    Returns:
        Updated state
    """
    state = load_state()

    state["world"]["locations"] = synthesis_result.get("locations", [])
    state["world"]["timeline"] = synthesis_result.get("timeline", [])
    state["world"]["atmosphere"] = _compat(
        synthesis_result, "atmosphere_map", "atmosphären_map", ""
    )
    state["world"]["production_notes"] = synthesis_result.get("production_notes", [])
    state["world"]["recurring_locations"] = _compat(
        synthesis_result, "recurring_locations", "wiederkehrende_locations", []
    )

    save_state(state)
    return state


def build_extraction_prompt(chunk_text: str, style_manifest: dict) -> str:
    """Builds the world extraction prompt."""
    import json
    from utils.skill_loader import load_skills_for_agent
    state = load_state()
    current_locations = [loc.get("name", "") for loc in state["world"]["locations"]]
    skills = load_skills_for_agent("world_agent")

    prompt = SYSTEM_WORLD_EXTRACTION.format(
        chunk_text=chunk_text,
        current_locations=", ".join(current_locations) if current_locations else "(none yet)",
        style_manifest=json.dumps(style_manifest, ensure_ascii=False, indent=2),
    )
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


def get_location_for_scene(scene_slug: str) -> dict:
    """Finds the matching location data for a scene slug."""
    state = load_state()
    slug_lower = scene_slug.lower()
    for loc in state["world"]["locations"]:
        if loc.get("name", "").lower() in slug_lower:
            return loc
    return {}


def get_timeline_context(chunk_index: int) -> list:
    """Returns timeline events up to a given chunk."""
    state = load_state()
    events = state["world"].get("timeline", [])
    return [e for e in events if int(e.get("chunk_id", "chunk_999").split("_")[-1]) <= chunk_index + 1]
