"""
CHARACTER AGENT
===============
Creates complete character bible with voice profiles,
relationship matrix, want/need arcs, and dialog improvisation.

The Character Agent is the key to dialog quality:
Voice profiles feed into the Adaptation Agent and Script Writer.

Two passes per character:
1. Extraction: Quotes, speech descriptions, social context
2. Synthesis: Voice profile, vocabulary palette, example lines

Plus: Dialog improvisation for key scenes.
"""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from state_store import load_state, save_state, append_to_state, _compat


# ─── PHASE D — VOICE PROFILE COMPACT ────────────────────────────────
# Deterministic compact derivation from full voice profiles.
# Spec: docs/voice-profile-inventory.md §9.

COMPACT_CAPS = {
    "voice_description": 200,
    "vocabulary_level": 100,
    "sentence_pattern": 100,
    "verbal_tic": 50,
    "avoidance": 50,
    "subtext_rule_short": 120,
    "example_line": 150,
}
COMPACT_TICS_MAX = 2
COMPACT_AVOIDS_MAX = 2


def _trim_on_word(text: str, limit: int) -> str:
    """Trim text to <= limit on last whitespace; fallback hard cut. Mirrors adaptation_agent._trim_on_word."""
    if not isinstance(text, str):
        return ""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    space = cut.rfind(" ")
    if space >= int(limit * 0.6):
        cut = cut[:space]
    return cut.rstrip(" ,;:—-") + "…"


def _first_sentence(text: str) -> str:
    """First sentence by '. ' split; fallback whole string."""
    if not isinstance(text, str):
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)
    return parts[0] if parts else text


def _normalize_list(value, item_cap: int, max_n: int) -> list:
    """Coerce list/string/dict into trimmed list of strings."""
    items = []
    if isinstance(value, list):
        items = [str(x) for x in value if x]
    elif isinstance(value, str) and value.strip():
        items = [s.strip() for s in value.split(",") if s.strip()]
    elif isinstance(value, dict):
        items = [str(v) for v in value.values() if v]
    items = [_trim_on_word(s, item_cap) for s in items[:max_n]]
    return items


def _pick_example_line(examples) -> str:
    """Extract first example line from various legacy shapes."""
    if not examples:
        return ""
    if isinstance(examples, list):
        first = examples[0]
        if isinstance(first, dict):
            return first.get("text") or first.get("line") or ""
        if isinstance(first, str):
            return first
        return ""
    if isinstance(examples, dict):
        for v in examples.values():
            if isinstance(v, str):
                return v
            if isinstance(v, dict):
                return v.get("text") or v.get("line") or ""
        return ""
    return ""


def _pick_subtext_short(subtext) -> str:
    """First subtext rule, trimmed."""
    if isinstance(subtext, list) and subtext:
        return str(subtext[0])
    if isinstance(subtext, str):
        return _first_sentence(subtext)
    return ""


def compact_voice_profile(vp_full: dict) -> dict:
    """Pure function. Derives the compact voice profile from full.

    Output schema (docs/voice-profile-inventory.md §9.1). Defensive against
    legacy field names via _compat. Empty fields are preserved as ""/[]
    so consumers can use a uniform shape.
    """
    if not isinstance(vp_full, dict):
        return {}

    voice_desc = _compat(vp_full, "voice_description", "stimmbeschreibung", "")
    voice_desc = _trim_on_word(_first_sentence(voice_desc) if len(voice_desc) > COMPACT_CAPS["voice_description"] else voice_desc,
                                COMPACT_CAPS["voice_description"])

    vocab = vp_full.get("vocabulary_level") or vp_full.get("vocabulary") or ""
    vocab = _trim_on_word(vocab, COMPACT_CAPS["vocabulary_level"])

    sentence = _compat(vp_full, "sentence_pattern", "sentence_structure", "")
    sentence = _trim_on_word(sentence, COMPACT_CAPS["sentence_pattern"])

    tics = _normalize_list(vp_full.get("verbal_tics"), COMPACT_CAPS["verbal_tic"], COMPACT_TICS_MAX)
    avoidances = _normalize_list(_compat(vp_full, "avoidances", "vermeidungen", []),
                                  COMPACT_CAPS["avoidance"], COMPACT_AVOIDS_MAX)

    subtext = _pick_subtext_short(vp_full.get("subtext_rules"))
    subtext = _trim_on_word(subtext, COMPACT_CAPS["subtext_rule_short"])

    examples = vp_full.get("dialog_examples") or vp_full.get("example_dialog_lines") or vp_full.get("example_lines")
    example = _pick_example_line(examples)
    example = _trim_on_word(example, COMPACT_CAPS["example_line"])

    return {
        "voice_description": voice_desc,
        "vocabulary_level": vocab,
        "sentence_pattern": sentence,
        "verbal_tics": tics,
        "avoidances": avoidances,
        "subtext_rule_short": subtext,
        "example_line": example,
    }


def voice_profile_hash(vp_full: dict) -> str:
    """Stable 16-char SHA-1 prefix over canonical JSON form."""
    if not isinstance(vp_full, dict):
        return ""
    payload = json.dumps(vp_full, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:16]


def render_voice_profiles_compact(characters: dict, character_ids: list = None) -> str:
    """Renders compact voice profiles as a prompt block.

    Lazy-builds compact + hash if missing on a character (read-only — does NOT
    mutate state). Caller is responsible for persisting via run_character_synthesis
    if persistence is desired.
    """
    if not characters:
        return "(No voice profiles available)"

    items = characters.items() if character_ids is None else [
        (cid, characters[cid]) for cid in character_ids if cid in characters
    ]

    lines = []
    for name, data in items:
        compact = data.get("voice_profile_compact")
        if not compact:
            full = data.get("voice_profile")
            if not full:
                continue
            compact = compact_voice_profile(full)
        if not any(compact.values()):
            continue

        lines.append(f"\n{name.upper()}:")
        if compact.get("voice_description"):
            lines.append(f"  Voice: {compact['voice_description']}")
        if compact.get("vocabulary_level"):
            lines.append(f"  Vocabulary: {compact['vocabulary_level']}")
        if compact.get("sentence_pattern"):
            lines.append(f"  Pattern: {compact['sentence_pattern']}")
        if compact.get("verbal_tics"):
            lines.append(f"  Tics: {', '.join(compact['verbal_tics'])}")
        if compact.get("avoidances"):
            lines.append(f"  Never: {', '.join(compact['avoidances'])}")
        if compact.get("subtext_rule_short"):
            lines.append(f"  Subtext rule: {compact['subtext_rule_short']}")
        if compact.get("example_line"):
            lines.append(f'  Example: "{compact["example_line"]}"')

    return "\n".join(lines) if lines else "(No voice profiles available)"


# ─── System Prompts ──────────────────────────────────────────────────

SYSTEM_EXTRACTION = """You are the Character Agent in extraction mode.
You analyze a text chunk and extract ALL information about characters.
You do not write creative text — only structured extraction.

Chunk text:
{chunk_text}

Known characters so far:
{known_characters}

Extract for EVERY character appearing in this chunk:

1. DIRECT QUOTES: Exact dialog lines from the character (verbatim speech)
2. SPEECH DESCRIPTORS: How the character speaks ("he said quietly", "she exclaimed")
3. ACTIONS: What the character does in this chunk
4. INNER STATES: Thoughts, feelings, motivations (if described by the narrator)
5. SOCIAL MARKERS: Class, education, era, region, speech register
6. RELATIONSHIP DYNAMICS: How does the character speak/act toward different people?
7. NEW INFORMATION: What do we learn new about the character in this chunk?

Respond as JSON:
{{
  "characters_found": [
    {{
      "name": "...",
      "direct_quotes": ["..."],
      "speech_descriptors": ["..."],
      "actions": ["..."],
      "inner_states": ["..."],
      "social_markers": ["..."],
      "relationship_dynamics": [{{"with": "...", "quality": "..."}}],
      "new_info": ["..."]
    }}
  ]
}}
"""

SYSTEM_SYNTHESIS = """You are the Character Agent in synthesis mode.
From the collected extraction data, you create a complete character profile
with a Voice Profile — the most critical element for dialog quality.

Character: {character_name}
Casting suggestion: {casting_suggestion}

Collected data from all chunks:
{extraction_data}

Style manifest:
{style_manifest}

Create a complete profile:

1. BASIC DATA
   - Role (Protagonist/Antagonist/Supporting/Minor)
   - Age, origin, social status (only from text, do not invent)
   - physical_signature: ONE recurring body-marker that makes the character visually identifiable in every scene.
     Examples: Anna Karenina's heavy eyelids, Pierre's broad build, Hadji Murat's prominent cheekbones + slight limp,
     Vorontsov's pale hands and quiet voice. Draw from the source text when possible. For casting: translates to
     a specific gesture, feature, or habit the actor must embody. REQUIRED for all Tier-1 and Tier-2 characters.

2. PSYCHOLOGY
   - WANT: What the character consciously pursues (drives the plot)
   - NEED: What the character truly needs (drives the theme)
   - FEAR: What the character fears most
   - CONTRADICTION: Where does the character contradict themselves?
   - justification: REQUIRED for role=Antagonist. ONE sentence (from the character's own perspective) that
     explains why their actions are legitimate to THEM. Tolstoi-principle: antagonists are understood from
     their own logic, not dismissed as villains. Example for Shamil: "Hadji Murad was my best warrior and
     now he runs to the enemy — he dies or returns, no third option is possible." Leave null for non-antagonists.

3. ARC
   - Starting state (Act 1)
   - Change (Act 2)
   - End state (Act 3)
   - Arc type (Transformation/Fall/Stagnation/Revelation)

4. VOICE PROFILE (CRITICAL)
   - voice_description: 3 sentences describing how the character speaks
   - Vocabulary level: formal/informal, education level, era
   - Sentence structure: Average length, complexity, question/statement/fragment tendency
   - Verbal tics: Recurring expressions, idioms
   - avoidances: What this character would NEVER say
   - emotional_expression: How does the character express feelings verbally?
   - Speech rhythm: measured/hectic/alternating
   - 5 example dialog lines for different emotional states:
     a) neutral/everyday
     b) under pressure
     c) hopeful/joyful
     d) angry/hurt
     e) vulnerable/honest
   - subtext_rules: What does the character say when they mean X?

5. RELATIONSHIPS
   - For each relevant character: Type, quality, power dynamic, speech register shift

Respond as JSON.
"""

SYSTEM_IMPRO = """You are NOW the character {character_name}.
You speak, think, and react AS this character — not about them.

Your Voice Profile:
{voice_profile}

Your current emotional state: {emotional_state}
Your goal in this scene: {scene_goal}

The situation:
{scene_situation}

The other characters in the scene:
{other_characters}

Speak as {character_name}. Stay in character.
Respond with 2-5 dialog lines that naturally react to the situation.
Remember:
- Subtext: Don't say directly what you mean
- Voice: Stay with your speech pattern
- Goal: Pursue your scene goal through dialog
- Reaction: React to what was just said/done

Format:
{{
  "character": "{character_name}",
  "lines": [
    {{"text": "...", "subtext": "...", "action_before": "..."}}
  ]
}}
"""

SYSTEM_RELATIONSHIP_MATRIX = """Create a relationship matrix for all main characters.

Characters and their profiles:
{all_characters}

For each character pair create:
1. Relationship type (Family/Friendship/Enmity/Romance/Mentor-Student/Rivalry)
2. Quality (intimate/tense/hostile/ambivalent/reverent)
3. Power dynamic (equal/dominant-submissive/alternating)
4. How they speak WITH EACH OTHER (register differences)
5. Conflict potential (0.0-1.0)

Respond as JSON array.
"""


# ─── Character Agent Functions ──────────────────────────────────────

def run_character_extraction(chunk_results: list) -> dict:
    """
    Phase 2a: Processes chunk analysis results and accumulates
    character data across all chunks.

    Args:
        chunk_results: List of extraction results per chunk
                      (each element is the JSON output of the LLM)

    Returns:
        Accumulated extraction data per character
    """
    state = load_state()
    accumulated = {}

    for result in chunk_results:
        characters_found = result.get("characters_found", [])
        for char_data in characters_found:
            name = char_data.get("name", "Unknown")

            if name not in accumulated:
                accumulated[name] = {
                    "direct_quotes": [],
                    "speech_descriptors": [],
                    "actions": [],
                    "inner_states": [],
                    "social_markers": [],
                    "relationship_dynamics": [],
                    "new_info": [],
                    "chunk_appearances": 0,
                }

            acc = accumulated[name]
            acc["direct_quotes"].extend(char_data.get("direct_quotes", []))
            acc["speech_descriptors"].extend(char_data.get("speech_descriptors", []))
            acc["actions"].extend(char_data.get("actions", []))
            acc["inner_states"].extend(char_data.get("inner_states", []))
            acc["social_markers"].extend(char_data.get("social_markers", []))
            acc["relationship_dynamics"].extend(char_data.get("relationship_dynamics", []))
            acc["new_info"].extend(char_data.get("new_info", []))
            acc["chunk_appearances"] += 1

    return accumulated


def run_character_synthesis(synthesis_results: list) -> dict:
    """
    Phase 2b: Processes voice profile synthesis results and
    writes them to the state.

    Args:
        synthesis_results: List of synthesis results per character
                          (each element is the JSON output of the LLM)

    Returns:
        Updated state
    """
    state = load_state()

    for result in synthesis_results:
        # Name may live at top level or under canonical_name (Opus-style output).
        name = result.get("name") or result.get("canonical_name") or ""
        if not name:
            continue

        # Psychology fields may arrive flat OR nested under a "psychology"
        # key (the synthesis prompt groups them under "2. PSYCHOLOGY" in the
        # template — Opus in T5.1 respected the grouping and emitted nested
        # JSON, flattening them silently dropped want/need for every single
        # character). Read both shapes; flat wins if both present.
        psych = result.get("psychology") or {}
        basic = result.get("basic_data") or {}

        def _pick(key: str, de_key: str = "", default=""):
            return (
                result.get(key)
                or (_compat(result, key, de_key) if de_key else None)
                or basic.get(key)
                or psych.get(key)
                or default
            )

        # Preserve existing data, add new
        existing = state["characters"].get(name, {})
        vp_full = result.get("voice_profile", {}) or {}
        existing.update({
            "name": name,
            "role": _compat(result, "role", "rolle", _compat(existing, "role", "rolle", "unknown")),
            "first_description": _compat(result, "first_description", "erstbeschreibung",
                                         _compat(existing, "first_description", "erstbeschreibung", "")),
            "age": _pick("age", "alter"),
            "origin": _pick("origin", "herkunft"),
            "social_status": _pick("social_status", "sozialer_status"),
            # Psychology — accept flat or nested
            "want": result.get("want") or psych.get("want") or "",
            "need": result.get("need") or psych.get("need") or "",
            "fear": result.get("fear") or psych.get("fear")
                    or _compat(result, "fear", "angst", "") or "",
            "contradiction": result.get("contradiction") or psych.get("contradiction")
                             or _compat(result, "contradiction", "widerspruch", "") or "",
            "justification": result.get("justification") or psych.get("justification"),
            # Arc
            "arc": result.get("arc", {}),
            "arc_type": _compat(result, "arc_type", "arc_typ", ""),
            # Voice Profile (the critical element)
            "voice_profile": vp_full,
            # Phase D — Compact derivative + hash for cache invalidation
            "voice_profile_compact": compact_voice_profile(vp_full),
            "voice_profile_hash": voice_profile_hash(vp_full),
            # Timestamps
            "synthesized_at": datetime.now().isoformat(),
        })

        state["characters"][name] = existing

    # Save relationships separately
    save_state(state)
    return state


def run_relationship_matrix(matrix_result: list) -> dict:
    """Saves the relationship matrix to the state."""
    state = load_state()
    state["character_relationships"] = matrix_result
    save_state(state)
    return state


def run_dialog_improvisation(impro_results: dict) -> dict:
    """
    Phase 4: Saves dialog improvisation material to the state.

    Args:
        impro_results: {scene_key: [{character, lines[], context}]}

    Returns:
        Updated state
    """
    state = load_state()
    state["impro_material"] = impro_results
    save_state(state)
    return state


# ─── Helper Functions ────────────────────────────────────────────────

def get_voice_profile(character_name: str) -> dict:
    """Loads the voice profile of a character from the state."""
    state = load_state()
    char = state["characters"].get(character_name, {})
    return char.get("voice_profile", {})


def get_all_voice_profiles() -> dict:
    """Loads compact voice profiles for prompt injection.

    Phase D: returns the canonical compact schema (docs/voice-profile-inventory.md §9.1).
    Lazy-builds compact for legacy state entries that only carry voice_profile.
    """
    state = load_state()
    profiles = {}
    for name, data in state["characters"].items():
        compact = data.get("voice_profile_compact")
        if not compact:
            full = data.get("voice_profile")
            if not full:
                continue
            compact = compact_voice_profile(full)
        if compact and any(compact.values()):
            profiles[name] = compact
    return profiles


def get_casting_context(character_name: str) -> str:
    """Returns the casting suggestion for a character.

    Handles two shapes:
      - D.3 structured entry (dict): age_range, physical_anchor,
        vocal_quality, social_presence, historical_reference
      - Legacy string (e.g. a single actor-name hint from projekt.yaml):
        returned as-is for backward compatibility.
    """
    state = load_state()
    casting = state.get("casting", {}) or {}
    entry = casting.get(character_name, "")
    if isinstance(entry, dict) and entry:
        parts = [
            f"Age range: {entry.get('age_range', '?')}",
            f"Physical: {entry.get('physical_anchor', '—')}",
            f"Vocal: {entry.get('vocal_quality', '—')}",
            f"Presence: {entry.get('social_presence', '—')}",
        ]
        if entry.get("historical_reference"):
            parts.append(f"Historical reference: {entry['historical_reference']}")
        return "Casting archetype:\n  " + "\n  ".join(parts)
    if entry and isinstance(entry, str):
        return f"Suggested casting: {entry} — orient yourself to their speech register and presence"
    return "No casting suggestion"


def build_extraction_prompt(chunk_text: str, known_characters: list) -> str:
    """Builds the extraction prompt for a chunk."""
    return SYSTEM_EXTRACTION.format(
        chunk_text=chunk_text,
        known_characters=", ".join(known_characters) if known_characters else "(none yet)"
    )


def build_synthesis_prompt(character_name: str, extraction_data: dict, style_manifest: dict) -> str:
    """Builds the synthesis prompt for a character."""
    import json
    from utils.skill_loader import load_skills_for_agent
    skills = load_skills_for_agent("character_agent")
    prompt = SYSTEM_SYNTHESIS.format(
        character_name=character_name,
        casting_suggestion=get_casting_context(character_name),
        extraction_data=json.dumps(extraction_data, ensure_ascii=False, indent=2),
        style_manifest=json.dumps(style_manifest, ensure_ascii=False, indent=2),
    )
    if skills:
        prompt += f"\n\n{skills}"
    return prompt


def build_impro_prompt(
    character_name: str,
    voice_profile: dict,
    emotional_state: str,
    scene_goal: str,
    scene_situation: str,
    other_characters: str,
) -> str:
    """Builds the dialog improvisation prompt for a character in a scene."""
    return SYSTEM_IMPRO.format(
        character_name=character_name,
        voice_profile=json.dumps(voice_profile, ensure_ascii=False, indent=2),
        emotional_state=emotional_state,
        scene_goal=scene_goal,
        scene_situation=scene_situation,
        other_characters=other_characters,
    )


# ─── Phase D.2 — Want/Need Enforcement ───────────────────────────────
#
# Coverage flagged "30+ chars with empty want/need" in T5.1: Phase 2b
# synthesis only ran for a hand-picked subset (3 chars in HM T5.1). D.2
# adds a tier-based audit that identifies Tier-1/2 chars missing the
# fields and exposes ready-to-dispatch synthesis prompts for the gaps.
# Framework-side only: actual LLM call happens via dispatcher (pattern
# from C.1/C.2).


def _normalize_name(name: str) -> str:
    """Normalize a character name for cross-source matching.

    state uses snake_case / slug-style keys (e.g. "hadji_murad",
    "boy_(host's_grandson/son)") while graphify-out uses title-case with
    spaces ("Hadji Murad"). Normalization:
      - lowercase
      - replace _ ( ) ' ’ , / with single space
      - collapse whitespace

    On HM T5.1 this matches 21/37 state chars to graph nodes (vs 0/37
    without normalization). The 12 state chars that still don't match
    are descriptive/unnamed entities Graphify didn't extract as named
    nodes ("author-narrator", "old_man_apiarist", "regimental_adjutant").
    """
    if not name:
        return ""
    s = name.lower()
    for ch in "_()'’,/":
        s = s.replace(ch, " ")
    return " ".join(s.split())


def _load_character_graph_weights() -> dict:
    """Load dramatic_weight + historical flag keyed by NORMALIZED name.

    Silent-fallback: returns empty dict if graphify-out is absent or
    malformed. D.2 is graceful about missing graph data — tier
    assignment then uses role only.
    """
    candidates = [
        Path.cwd() / "graphify-out" / "characters.json",
        Path(__file__).resolve().parents[2] / "graphify-out" / "characters.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                nodes = data.get("nodes", []) if isinstance(data, dict) else []
                weights = {}
                for n in nodes:
                    canonical = n.get("canonical_name", "")
                    if not canonical:
                        continue
                    key = _normalize_name(canonical)
                    weights[key] = {
                        "dramatic_weight": float(n.get("dramatic_weight", 0.0) or 0.0),
                        "historical": bool(n.get("historical", False)),
                        "canonical_name": canonical,
                    }
                return weights
            except (json.JSONDecodeError, OSError):
                return {}
    return {}


def assign_character_tiers(state: dict) -> dict:
    """Assign tier 1-4 per character.

    Tier 1 = protagonist/antagonist (role-based, authoritative)
    Tier 2 = supporting
    Tier 3 = minor
    Tier 4 = role missing/empty

    Graph dramatic_weight is recorded for diagnosis but NOT used for
    tier assignment (role from Phase 1 is authoritative).
    """
    graph_weights = _load_character_graph_weights()
    tiers = {}
    for name, char in (state.get("characters") or {}).items():
        role = (_compat(char, "role", "rolle", "") or "").strip().lower()
        if role in ("protagonist", "antagonist"):
            tier = 1
        elif role == "supporting":
            tier = 2
        elif role == "minor":
            tier = 3
        else:
            tier = 4
        gw = graph_weights.get(_normalize_name(name), {})
        tiers[name] = {
            "tier": tier,
            "role": role,
            "dramatic_weight": gw.get("dramatic_weight", 0.0),
            "historical": gw.get("historical", False),
            "graph_canonical_name": gw.get("canonical_name", ""),
        }
    return tiers


def run_wantneed_audit(verbose: bool = True) -> dict:
    """Scan all characters, flag Tier-1/2 with empty want or need.

    Writes state["character_coverage_gaps"] and appends one entry per
    gap to state["knowledge_gaps"]. Does NOT modify any character
    record — purely diagnostic.
    """
    state = load_state()
    tiers = assign_character_tiers(state)
    characters = state.get("characters") or {}

    gaps = []
    for name, meta in tiers.items():
        if meta["tier"] not in (1, 2):
            continue
        char = characters.get(name, {})
        want = (char.get("want") or "").strip()
        need = (char.get("need") or "").strip()
        missing = []
        if not want:
            missing.append("want")
        if not need:
            missing.append("need")
        if missing:
            gaps.append({
                "name": name,
                "tier": meta["tier"],
                "role": meta["role"],
                "dramatic_weight": meta["dramatic_weight"],
                "missing_fields": missing,
            })

    total_tier12 = sum(1 for m in tiers.values() if m["tier"] in (1, 2))
    audit = {
        "meta": {
            "version": "1",
            "tiers_checked": [1, 2],
            "total_tier12": total_tier12,
            "gap_count": len(gaps),
        },
        "character_coverage_gaps": gaps,
        "tier_map": tiers,
    }
    state["character_coverage_gaps"] = audit

    # Surface to the existing knowledge_gaps feed for dashboard visibility.
    kgaps = state.setdefault("knowledge_gaps", [])
    for g in gaps:
        msg = (
            f"Character {g['name']} ({g['role']}, tier {g['tier']}): "
            f"missing {', '.join(g['missing_fields'])}"
        )
        if msg not in kgaps:
            kgaps.append(msg)

    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print("WANT/NEED AUDIT complete")
        print(f"  Tier-1/2 characters: {total_tier12}")
        print(f"  Gaps flagged:        {len(gaps)}")
        for g in gaps:
            print(
                f"  • {g['name']} (tier {g['tier']}, {g['role']}, "
                f"weight {g['dramatic_weight']:.1f}) — missing: "
                f"{', '.join(g['missing_fields'])}"
            )
        print(f"{'='*60}\n")

    return audit


def build_wantneed_gap_prompts() -> list:
    """Return dispatch-ready synthesis prompts for Tier-1/2 want/need gaps.

    Reuses build_synthesis_prompt(); extraction_data comes from
    state["character_extractions"] (Phase 2a accumulator) if present,
    otherwise an empty dict — the LLM will then produce a best-effort
    profile from role + the chunk notes already in state.characters.
    """
    state = load_state()
    audit = state.get("character_coverage_gaps", {})
    gap_names = [g["name"] for g in audit.get("character_coverage_gaps", [])]
    extraction_cache = state.get("character_extractions", {}) or {}
    style_manifest = state.get("style_manifest", {}) or {}

    prompts = []
    for name in gap_names:
        extraction = extraction_cache.get(name, {})
        prompt = build_synthesis_prompt(name, extraction, style_manifest)
        prompts.append({"character": name, "prompt": prompt})
    return prompts


# ─── Phase D.3 — Casting-Integration ─────────────────────────────────
#
# Produces structured casting archetypes per Tier-1/2 character:
# physical_anchor, vocal_quality, age_range, social_presence, and —
# for historical figures — a source-grounded historical_reference.
# The state["casting"] dict is consumed by get_casting_context() and
# by Adaptation Agent's character-bible block. Also rendered to
# output/cast_sheet.md as a standalone deliverable.


SYSTEM_CASTING = """You are a casting director working from the source novel.
For the character {character_name}, produce a structured physical + vocal
archetype that a real casting director could act on.

HARD CONSTRAINTS:
- Describe a TYPE, not a specific modern actor. Do NOT name any living or
  historical actor or public figure.
- {historical_directive}
- Draw on the voice profile, want/need, physical_signature, and role from
  the character bible below. Do NOT invent traits that contradict the bible.
- Keep every field to 1-2 sentences. Dense, specific, castable.

CHARACTER BIBLE ENTRY:
{char_profile_json}

GRAPH METADATA:
- Role: {role}
- Historical: {historical}
- Dramatic weight: {dramatic_weight}

OUTPUT — valid JSON only, no markdown fences, no prose before or after:
{{
  "character_name": "{character_name}",
  "physical_anchor": "1-2 sentences: body type, defining feature, posture, habitual gesture.",
  "vocal_quality": "1 sentence: tone color, tempo, register.",
  "age_range": "e.g. 'early 40s', 'mid 50s', 'elder (60+)'",
  "social_presence": "1 sentence: how this character occupies a room — authority, menace, invisibility, warmth.",
  "historical_reference": {historical_reference_placeholder}
}}"""


_HIST_DIRECTIVE_YES = (
    "This is a HISTORICAL figure. The physical_anchor MUST be grounded in "
    "documented appearance from contemporary sources (portraits, memoirs, "
    "state records). The historical_reference field names the sources or "
    "describes what the record tells us — NOT a modern actor who resembles "
    "them. Do not speculate beyond the record."
)
_HIST_DIRECTIVE_NO = (
    "This is a FICTIONAL character. Build the archetype from voice_profile, "
    "physical_signature, and narrative function. Set historical_reference "
    "to null."
)


def build_casting_prompt(character_name: str, state: dict | None = None) -> str:
    """Build the casting-archetype synthesis prompt for one character.

    Pulls profile from state["characters"][name] and historical flag +
    dramatic_weight from the normalized graph lookup.
    """
    if state is None:
        state = load_state()
    char = (state.get("characters") or {}).get(character_name, {})
    tiers = assign_character_tiers(state)
    meta = tiers.get(character_name, {})
    historical = bool(meta.get("historical", False))

    # Keep the bible compact — LLM doesn't need every field.
    bible_entry = {
        "role": _compat(char, "role", "rolle", ""),
        "age": char.get("age", ""),
        "origin": char.get("origin", ""),
        "social_status": char.get("social_status", ""),
        "want": char.get("want", ""),
        "need": char.get("need", ""),
        "fear": char.get("fear", ""),
        "contradiction": char.get("contradiction", ""),
        "physical_signature": char.get("physical_signature", ""),
        "voice_profile": char.get("voice_profile", {}),
    }

    hist_directive = _HIST_DIRECTIVE_YES if historical else _HIST_DIRECTIVE_NO
    hist_placeholder = (
        '"<required: source-grounded description of appearance>"'
        if historical else "null"
    )

    return SYSTEM_CASTING.format(
        character_name=character_name,
        historical_directive=hist_directive,
        char_profile_json=json.dumps(bible_entry, ensure_ascii=False, indent=2),
        role=_compat(char, "role", "rolle", "") or "(unknown)",
        historical=historical,
        dramatic_weight=meta.get("dramatic_weight", 0.0),
        historical_reference_placeholder=hist_placeholder,
    )


def run_casting_synthesis(results: list, verbose: bool = True) -> dict:
    """Ingest a list of casting-synthesis results into state["casting"].

    Each result MUST carry "character_name" (or "name" as alias). Other
    fields are copied straight into the casting entry. Unknown extra
    fields are preserved — future schema growth is additive.
    """
    state = load_state()
    casting = state.setdefault("casting", {})
    if not isinstance(casting, dict):
        # Defensive: legacy schema had casting as dict-of-strings, still dict.
        # If it's somehow a list, reset.
        casting = {}
        state["casting"] = casting

    ingested = 0
    for result in results:
        if not isinstance(result, dict):
            continue
        name = result.get("character_name") or result.get("name") or ""
        if not name:
            continue
        entry = {
            "physical_anchor": result.get("physical_anchor", ""),
            "vocal_quality": result.get("vocal_quality", ""),
            "age_range": result.get("age_range", ""),
            "social_presence": result.get("social_presence", ""),
            "historical_reference": result.get("historical_reference"),
            "synthesized_at": datetime.now().isoformat(),
        }
        casting[name] = entry
        ingested += 1

    save_state(state)

    if verbose:
        print(f"CASTING SYNTHESIS: ingested {ingested} entries")
    return state


def run_casting_audit(verbose: bool = True) -> dict:
    """Identify Tier-1/2 characters without a casting entry.

    Writes state["casting_coverage_gaps"]. Pure diagnostic — never
    modifies casting records.
    """
    state = load_state()
    tiers = assign_character_tiers(state)
    casting = state.get("casting", {}) or {}

    gaps = []
    for name, meta in tiers.items():
        if meta["tier"] not in (1, 2):
            continue
        entry = casting.get(name)
        if not (isinstance(entry, dict) and entry.get("physical_anchor")
                and entry.get("vocal_quality")):
            gaps.append({
                "name": name,
                "tier": meta["tier"],
                "role": meta["role"],
                "dramatic_weight": meta["dramatic_weight"],
                "historical": meta["historical"],
            })

    total_tier12 = sum(1 for m in tiers.values() if m["tier"] in (1, 2))
    audit = {
        "meta": {
            "version": "1",
            "tiers_checked": [1, 2],
            "total_tier12": total_tier12,
            "gap_count": len(gaps),
        },
        "casting_coverage_gaps": gaps,
    }
    state["casting_coverage_gaps"] = audit
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print("CASTING AUDIT complete")
        print(f"  Tier-1/2 characters: {total_tier12}")
        print(f"  Casting gaps:        {len(gaps)}")
        for g in sorted(gaps, key=lambda x: -x["dramatic_weight"])[:10]:
            hist = "historical" if g["historical"] else "fictional"
            print(
                f"  • {g['name']:<25} tier={g['tier']} "
                f"weight={g['dramatic_weight']:.1f} ({hist})"
            )
        if len(gaps) > 10:
            print(f"  ... +{len(gaps)-10} more")
        print(f"{'='*60}\n")

    return audit


def build_casting_gap_prompts() -> list:
    """Return dispatch-ready casting prompts for Tier-1/2 gaps."""
    state = load_state()
    audit = state.get("casting_coverage_gaps", {})
    gap_names = [g["name"] for g in audit.get("casting_coverage_gaps", [])]

    prompts = []
    for name in gap_names:
        prompts.append({
            "character": name,
            "prompt": build_casting_prompt(name, state),
        })
    return prompts


def build_cast_sheet() -> str:
    """Render output/cast_sheet.md from state.

    Grouped by tier, sorted by dramatic_weight desc, historical flag
    surfaced in each character header. Characters without casting
    entries are listed in a trailing section with role+weight so the
    reader can see what was skipped and why.
    """
    state = load_state()
    tiers = assign_character_tiers(state)
    casting = state.get("casting", {}) or {}
    meta = state.get("meta", {})
    title = meta.get("story_title") or meta.get("title") or Path.cwd().name

    tier1 = []
    tier2 = []
    no_entry = []
    for name, tmeta in tiers.items():
        entry = casting.get(name)
        has_entry = isinstance(entry, dict) and entry.get("physical_anchor")
        row = (name, tmeta, entry if has_entry else None)
        if tmeta["tier"] == 1:
            tier1.append(row)
        elif tmeta["tier"] == 2:
            tier2.append(row)
        if (tmeta["tier"] in (1, 2)) and not has_entry:
            no_entry.append(row)

    tier1.sort(key=lambda r: -r[1]["dramatic_weight"])
    tier2.sort(key=lambda r: -r[1]["dramatic_weight"])

    filled = sum(
        1 for n, t in tiers.items()
        if t["tier"] in (1, 2)
        and isinstance(casting.get(n), dict)
        and casting[n].get("physical_anchor")
    )
    total12 = sum(1 for t in tiers.values() if t["tier"] in (1, 2))

    lines = [
        f"# Cast Sheet — {title}",
        "",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')} · "
        f"{filled}/{total12} Tier-1/2 characters with casting entries_",
        "",
    ]

    def render_group(header: str, rows: list):
        if not rows:
            return
        lines.append(f"## {header}")
        lines.append("")
        for name, tmeta, entry in rows:
            hist = "historical" if tmeta["historical"] else "fictional"
            header_line = (
                f"### {name} "
                f"({tmeta['role'] or 'unclassified'}, {hist}, "
                f"weight {tmeta['dramatic_weight']:.1f})"
            )
            lines.append(header_line)
            lines.append("")
            if entry:
                lines.append(f"**Age range:** {entry.get('age_range', '—')}")
                lines.append(f"**Physical anchor:** {entry.get('physical_anchor', '—')}")
                lines.append(f"**Vocal quality:** {entry.get('vocal_quality', '—')}")
                lines.append(f"**Social presence:** {entry.get('social_presence', '—')}")
                hr = entry.get("historical_reference")
                if hr:
                    lines.append(f"**Historical reference:** {hr}")
            else:
                lines.append("_No casting entry yet._")
            lines.append("")

    render_group("Tier 1 — Dramatic Engines", tier1)
    render_group("Tier 2 — Supporting", tier2)

    if no_entry:
        lines.append(f"## Characters without casting entries ({len(no_entry)})")
        lines.append("")
        for name, tmeta, _ in sorted(no_entry, key=lambda r: -r[1]["dramatic_weight"]):
            note = " — descriptive entity" if tmeta["dramatic_weight"] == 0.0 else ""
            lines.append(
                f"- **{name}** (tier {tmeta['tier']}, {tmeta['role']}, "
                f"weight {tmeta['dramatic_weight']:.1f}){note}"
            )
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "cast_sheet.md").write_text(content, encoding="utf-8")
    return content
