"""
SCRIPT WRITER
=============
Takes all adapted scenes from the state and writes
the final treatment or screenplay in professional format.

Two output modes:
  - "treatment"  → Cinematic prose narrative (15-25 pages)
  - "screenplay" → Full screenplay (Fountain format)

15-Agent architecture features (Pipeline v3.2):
  - Voice profiles in prompt for screenplay mode
  - Dialog polish pass (second LLM call per batch)
  - Configurable batch sizes
  - Treatment stored separately from screenplay in state
  - Industry-standard treatment format (Craig Mazin model)
"""

import json
from state_store import load_state, save_state, _compat, log_continuity_issue


# ─── SYSTEM PROMPTS ─────────��────────────────────────────────────────────────

SYSTEM_TREATMENT = """You are a professional screenwriter crafting a film treatment.
A treatment is a cinematic prose narrative — more vivid than a synopsis,
less detailed than a full screenplay. It must READ like watching the film.

TREATMENT FORMAT (industry standard, modeled on Craig Mazin / Terry Rossio):
1. HEADER: Title, "Based on [source] by [author]", Genre, Target Runtime
2. CHARACTER PROFILES: 2-3 vivid sentences per main character — personality, role,
   what makes them compelling. Introduce with name in CAPS on first mention.
3. STORY (in three labeled acts):
   - ACT ONE / ACT TWO / ACT THREE as section headers
   - Numbered scenes with location headers (e.g., "1. THE ESTATE — WINTER EVENING")
   - Each scene: 4-8 sentences of vivid, present-tense cinematic prose
   - Selective KEY dialogue embedded in prose (only lines that are character-defining
     or thematically essential — max 2-3 quoted lines per scene, woven into narration)
   - Italicized thematic commentary between key scenes where it illuminates the
     emotional arc: *The irony deepens — she searches for the man she lost, unaware
     that fate has already delivered him.*
4. NO camera directions, NO technical jargon ("we see", "the camera reveals")
5. Write in PRESENT TENSE, always
6. Total length: 15-25 pages for a 90-minute feature

PROSE STYLE:
- Vivid, specific, compressed — not dry summary
- "She presses her palm against the frosted glass" not "She looks out the window"
- Enter late, leave early — show the dramatic heart, skip the furniture
- Make the reader FEEL the movie, not just understand the plot
- Describe what the audience sees and hears — actions, gestures, sounds, light

WHAT TO INCLUDE:
- The complete story including the ending
- Clear stakes and escalating conflict
- Emotional trajectory tracked throughout
- Every major character's arc resolved
- The tone and visual world of the film

WHAT TO NEVER INCLUDE:
- Camera angles or shot descriptions
- "We see" or "The camera reveals" or "Cut to"
- Hedging language ("perhaps", "maybe", "could")
- Every single scene — show the spine, not the connective tissue

STYLE MANIFEST:
{style_brief}

CHARACTER BIBLE:
{char_bible}

Write pure text — no JSON, no markdown except scene numbers and act labels."""

SYSTEM_SCREENPLAY = """You are a professional screenwriter writing in Fountain format.

FOUNTAIN FORMAT RULES:
- Scene heading: INT./EXT. LOCATION - TIME OF DAY (all caps, own line)
- Action lines: Normal text, present tense, active, visual — max 4 lines per paragraph
- Character cue: CHARACTER NAME (all caps, own line)
- Dialogue: Directly under character cue
- Parenthetical: (stage direction) between character cue and dialogue, use sparingly
- Transitions: CUT TO: / DISSOLVE TO: (right-aligned, use sparingly — modern style implies most cuts)
- New characters introduced in ALL CAPS on first appearance with brief visual description

QUALITY REQUIREMENTS:
- Active, visual, precise — no long descriptions
- Dialogue: Characters sound distinct and authentic
- Every scene advances the story
- Respect the style manifest
- Action lines should be lean prose — every word serves the visual
- NEVER write camera directions: no CLOSE ON, SMASH CUT, ANGLE ON, TRACKING SHOT,
  "the camera", "we see" — to emphasize a detail, isolate it in its own short paragraph
- NEVER describe internal states — only what a camera can record and an actor can perform
- NEVER explain what dialogue means in action lines — trust the dialogue to carry itself

VOICE PROFILES (every character MUST sound like this):
{voice_profiles}

Write pure Fountain/screenplay format — no JSON, no explanations."""

SYSTEM_DIALOG_POLISH = """You are a screenplay polish specialist. Revise dialogue AND action lines
in this screenplay section. Do NOT change scene structure or story content.

VOICE PROFILES:
{voice_profiles}

DIALOGUE CHECKS:
1. Does each character sound like their voice profile? (Vocabulary, sentence length, tics)
2. Is there on-the-nose dialogue? (Characters stating feelings directly → rewrite)
3. Does every exchange carry subtext? (What is NOT said is more important)
4. Could you identify the character blindly? (Without name cue → must still be clear)
5. 70/30 Rule: At least 70% subtext, max 30% direct

Test: If you remove a character name — can you still tell who's speaking?

ACTION LINE CHECKS:
6. FILMABILITY: Can an actress physically perform this line? Can a camera record it?
   DELETE: "a stillness that reads as composure but is actually hunger"
   REWRITE AS: "She sits rigid. Her eyes track the bread basket."
7. DIRECTOR INTRUSIONS: Delete ALL camera/editing language (CLOSE ON, SMASH CUT,
   "the camera pushes", "we see"). Isolate the detail in its own short paragraph instead.
8. SUBTEXT CAPTIONS: Delete any action line that EXPLAINS what dialogue means.
   DELETE: "She is constructing a wall from pleasantries."
   DELETE: "Two men who understand each other perfectly."
   KEEP action lines that describe physical movement. KILL lines that interpret meaning.

Return the COMPLETE section with all revisions applied.
Do NOT mark changed lines — just deliver the final version."""


# ─── PROMPT BUILDERS ──────────────────────────────────────────────────────────

def build_screenplay_batch_prompts() -> list:
    """
    Builds all screenplay batch prompts from current state.

    Phase E.4: per-batch construction reads
    ``state_store.build_script_writer_batch_view(state, batch_idx, batch_size)``
    instead of touching the full state per batch. View carries only the
    slice this batch's prompt injects (slim style_manifest, slim
    characters_for_style for lead detection, batch scenes, batch char ids,
    themes, title) and drops chunks, impro_material, world.*, casting,
    character_extractions, voice_profile internals, every adapted_scene
    outside the batch and all coverage / analysis / revision outputs.

    Returns:
        List of (system_prompt, user_message) tuples, one per batch.
        The caller dispatches each to the LLM and collects the text results.
    """
    from utils.skill_loader import load_skills_for_agent
    from state_store import build_script_writer_batch_view
    state = load_state()
    scenes = state.get("adapted_scenes", [])
    if not scenes:
        raise ValueError("No adapted scenes found.")

    batch_size = get_batch_size("screenplay")
    batch_count = (len(scenes) + batch_size - 1) // batch_size
    skills = load_skills_for_agent("script_writer_screenplay")

    prompts = []
    for batch_idx in range(batch_count):
        view = build_script_writer_batch_view(state, batch_idx, batch_size)
        batch = view["batch"]
        if not batch:
            continue
        start_id = _compat(batch[0], "scene_id", "szenen_id", "?")
        end_id = _compat(batch[-1], "scene_id", "szenen_id", "?")
        char_ids = view["batch_character_ids"]
        # Phase D: compact voice profiles, batch-scoped.
        voice_profiles = get_voice_profiles_for_prompt(
            character_ids=char_ids, compact=True, max_examples=1
        )
        # Phase E.4: style_ctx fed by view-slim characters (only role for
        # lead detection) — no voice profile internals propagated here.
        style_ctx = _build_style_context(
            view["style_manifest"],
            view["characters_for_style"],
            view["plot"],
            view["meta"]["title"],
        )
        system = SYSTEM_SCREENPLAY.format(voice_profiles=voice_profiles)
        if skills:
            system += f"\n\n{skills}"

        user_msg = (
            f"STYLE CONTEXT:\n{style_ctx}\n\n"
            f"Write scenes {start_id} through {end_id} "
            f"(batch {batch_idx+1}/{view['total_batches']}) "
            f"in Fountain screenplay format:\n\n"
            f"{_format_scenes_for_writer(batch)}"
        )
        prompts.append((system, user_msg))

    return prompts


def _collect_batch_character_ids(batch: list, characters: dict) -> list:
    """Returns character names appearing in any scene of the batch.

    Falls back to all known characters if the batch carries no explicit
    'characters' field (legacy scene shape) so voice coverage is never silently
    dropped.
    """
    seen = []
    for scene in batch:
        names = _compat(scene, "characters", "figuren", []) or []
        for n in names:
            if n in characters and n not in seen:
                seen.append(n)
    if not seen:
        return list(characters.keys())
    return seen


# ─── MAIN FUNCTION ─────────────────���──────────────────��───────────────────────

def run_script_writer(batch_results: list, output_mode: str = "treatment", verbose: bool = True) -> str:
    """
    Writes the final treatment or screenplay.

    Args:
        batch_results: List of script texts (one string per batch), provided by Claude Code.
        output_mode: "treatment" or "screenplay"

    Returns:
        Finished document as string (also saved in state)
    """
    state = load_state()
    scenes = state.get("adapted_scenes", [])
    style_manifest = state.get("style_manifest", {})
    characters = state.get("characters", {})
    plot = state.get("plot", {})
    title = state["meta"]["title"]

    if not scenes:
        raise ValueError("No adapted scenes found. Run adaptation agent first.")

    valid_statuses = ["adapted", "treatment_done", "covered", "revised", "scripted"]
    if state["meta"]["status"] not in valid_statuses:
        raise ValueError(f"Adaptation agent must run first. Status: {state['meta']['status']}")

    print(f"\n{'='*60}")
    print(f"SCRIPT WRITER starting — mode: {output_mode.upper()}")
    print(f"  Scenes:  {len(scenes)}")
    print(f"  Title:   {title}")
    print(f"{'='*60}\n")

    # Get batch size from config
    batch_size = get_batch_size(output_mode)

    # Build scene batches
    batches = [scenes[i:i+batch_size] for i in range(0, len(scenes), batch_size)]

    script_parts = []

    # Title page
    script_parts.append(_write_title_page(title, output_mode, state))

    for batch_idx, batch in enumerate(batches):
        if verbose:
            start = _compat(batch[0], "scene_id", "szenen_id", "?")
            end = _compat(batch[-1], "scene_id", "szenen_id", "?")
            print(f"  Writing batch {batch_idx+1}/{len(batches)} "
                  f"[{start} – {end}]...", end=" ")

        result = batch_results[batch_idx] if batch_idx < len(batch_results) else None

        if result:
            script_parts.append(result)
            if verbose:
                print(f"✓  ~{len(result.split())} words")
        else:
            if verbose:
                print("⚠ No result")
            log_continuity_issue(f"Script writer batch {batch_idx+1}: Failed")

    # Assemble
    final_script = "\n\n".join(script_parts)

    # Save to state
    state = load_state()
    if output_mode == "treatment":
        state["treatment_text"] = final_script
        state["meta"]["status"] = "treatment_done"
    else:
        state["final_script"] = final_script
        state["meta"]["status"] = "scripted"
    state["meta"]["output_mode"] = output_mode
    save_state(state)

    # Export as file
    output_filename = f"{title.lower().replace(' ', '_')}_{output_mode}.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_script)

    print(f"\n{'='*60}")
    print(f"SCRIPT WRITER complete:")
    print(f"  Words:    {len(final_script.split())}")
    print(f"  Pages:    ~{len(final_script.split()) // 200}")
    print(f"  Saved as: {output_filename}")
    print(f"{'='*60}\n")

    return final_script


# ─── DIALOG POLISH ────────────────────────────────────────────────────────────

def build_dialog_polish_prompt(batch_text: str) -> tuple:
    """
    Builds the dialog polish prompt for a single screenplay batch.
    Returns (system_prompt, user_message) tuple for the LLM call.

    Uses Opus model (routed by orchestrator via pass_type="dialog_polish").
    """
    from utils.skill_loader import load_skills_for_agent, retrieve_brain_knowledge
    voice_profiles = get_voice_profiles_for_prompt()
    skills = load_skills_for_agent("script_writer_screenplay")
    system = SYSTEM_DIALOG_POLISH.format(voice_profiles=voice_profiles)
    if skills:
        system += f"\n\n{skills}"

    # Dynamic brain retrieval: detect dialog types in the batch
    brain_ctx = {"keywords": ["action line", "filmability"]}
    batch_lower = batch_text.lower()
    for kw in ["confession", "love", "confrontation", "farewell", "silence",
                "interrogation", "humor", "power", "group", "revelation", "subtext"]:
        if kw in batch_lower:
            brain_ctx["keywords"].append(kw)
    if brain_ctx["keywords"]:
        brain_text, _ = retrieve_brain_knowledge(brain_ctx, max_chars=2000)
        if brain_text:
            system += f"\n\n{brain_text}"

    return system, batch_text


def run_dialog_polish(polish_results: list, verbose: bool = True) -> str:
    """
    Applies dialog-polished batches to the final screenplay.

    Args:
        polish_results: List of polished batch texts (one per batch).

    Returns:
        Updated final_script string.
    """
    state = load_state()
    final_script = state.get("final_script", "")
    if not final_script:
        raise ValueError("No screenplay found. Run script_writer first.")

    scenes = state.get("adapted_scenes", [])
    batch_size = get_batch_size("screenplay")
    batches = [scenes[i:i+batch_size] for i in range(0, len(scenes), batch_size)]

    # Split script into title page + body batches
    # Find title page by looking for first Fountain scene header
    import re
    scene_header_re = re.compile(r'^(?:INT\.|EXT\.|INT/EXT\.|I/E\.)', re.MULTILINE)
    match = scene_header_re.search(final_script)
    if match:
        title_page = final_script[:match.start()].rstrip()
        body_text = final_script[match.start():]
    else:
        title_page = ""
        body_text = final_script

    # Split body into batch-sized chunks (by original batch boundaries)
    # We reconstruct from the original batch_results stored during run_script_writer
    original_batches = body_text.split("\n\n\n") if body_text else []

    script_body_parts = []
    polish_results = polish_results or []

    for batch_idx in range(len(batches)):
        if batch_idx < len(polish_results) and polish_results[batch_idx]:
            script_body_parts.append(polish_results[batch_idx])
            if verbose:
                print(f"  Polish batch {batch_idx+1}/{len(batches)}: ✓ applied")
        else:
            # Fallback: keep original batch content
            if batch_idx < len(original_batches):
                script_body_parts.append(original_batches[batch_idx])
            if verbose:
                print(f"  Polish batch {batch_idx+1}/{len(batches)}: ⚠ kept original")

    polished_script = title_page + "\n\n" + "\n\n".join(script_body_parts) if title_page else "\n\n".join(script_body_parts)

    # Save
    state = load_state()
    state["final_script"] = polished_script
    state["meta"]["dialog_polished"] = True
    save_state(state)

    if verbose:
        print(f"\n  Dialog polish complete: {len(polished_script.split())} words")

    return polished_script


# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────

def _format_scenes_for_writer(scenes: list) -> str:
    """Formats scenes as structured input for the script writer."""
    parts = []
    for scene in scenes:
        scene_id = _compat(scene, "scene_id", "szenen_id", "?")
        action = _compat(scene, "action", "handlung", "")
        emotional_core = _compat(scene, "emotional_core", "emotionaler_kern", "")
        characters = _compat(scene, "characters", "figuren", [])
        visual_note = _compat(scene, "visual_note", "visuelle_note", "")

        s = (
            f"[{scene_id}] {scene.get('slug', 'LOCATION UNKNOWN')}\n"
            f"Action: {action}\n"
            f"Emotional core: {emotional_core}\n"
            f"Characters: {', '.join(characters)}\n"
            f"Visual note: {visual_note}\n"
        )
        # Dialog drafts (with subtext)
        drafts = scene.get("dialog_draft", [])
        if drafts and isinstance(drafts, list) and isinstance(drafts[0], dict):
            s += "Dialog drafts:\n"
            for d in drafts:
                s += f"  {d.get('character', '?')}: \"{d.get('line', '')}\" (Subtext: {d.get('subtext', '')})\n"
        elif scene.get("dialog_hinweise"):
            dialog = " | ".join(scene["dialog_hinweise"][:2])
            s += f"Dialog direction: {dialog}\n"

        # Emotional choreography
        beats = scene.get("emotional_beats", [])
        if beats:
            s += "Emotional beats:\n"
            for b in beats[:3]:
                s += f"  → {b.get('beat', '')}: Audience feels {b.get('audience_feels', '')}\n"

        transition = scene.get("transition", "")
        if transition:
            s += f"Transition: {transition}\n"

        parts.append(s)
    return "\n---\n".join(parts)


def get_voice_profiles_for_prompt(
    character_ids: list = None,
    compact: bool = True,
    max_examples: int = 1,
) -> str:
    """Builds voice profile string for prompt injection.

    Phase D default: compact rendering (~76% smaller than full). Pass
    compact=False to fall back to the verbose pre-D format (used only by
    Subtext Auditor, which audits the subtext rules verbatim).

    Args:
        character_ids: Optional whitelist of character names. None → all.
        compact: True (default) → §9.3 compact block. False → full schema.
        max_examples: Cap on dialog examples per profile (full mode only).
    """
    state = load_state()
    characters = state.get("characters", {})
    if not characters:
        return "(No voice profiles available)"

    if compact:
        from agents.character_agent import render_voice_profiles_compact
        return render_voice_profiles_compact(characters, character_ids=character_ids)

    items = characters.items() if character_ids is None else [
        (cid, characters[cid]) for cid in character_ids if cid in characters
    ]
    lines = []
    for name, data in items:
        vp = data.get("voice_profile", {})
        if not vp:
            continue
        lines.append(f"\n{name.upper()}:")
        voice_desc = _compat(vp, "voice_description", "stimmbeschreibung", "")
        if voice_desc:
            lines.append(f"  {voice_desc}")
        vocab = vp.get("vocabulary_level", "")
        if vocab:
            lines.append(f"  Vocabulary: {vocab}")
        sentence = _compat(vp, "sentence_pattern", "sentence_structure", "")
        if sentence:
            lines.append(f"  Sentence pattern: {sentence}")
        tics = vp.get("verbal_tics", [])
        if tics and isinstance(tics, list):
            lines.append(f"  Tics: {', '.join(str(t) for t in tics)}")
        avoidances = _compat(vp, "avoidances", "vermeidungen", [])
        if avoidances:
            lines.append(f"  Never says: {', '.join(avoidances)}")
        emo_expr = vp.get("emotional_expression", "")
        if emo_expr:
            lines.append(f"  Emotional expression: {emo_expr}")
        rhythm = vp.get("speech_rhythm", "")
        if rhythm:
            lines.append(f"  Speech rhythm: {rhythm}")
        examples = vp.get("dialog_examples", [])
        if examples:
            lines.append("  Dialog examples:")
            if isinstance(examples, dict):
                for ctx, txt in list(examples.items())[:max_examples]:
                    lines.append(f"    [{ctx}]: \"{txt}\"")
            else:
                for ex in examples[:max_examples]:
                    if isinstance(ex, dict):
                        ctx = ex.get("context", ex.get("state", "?"))
                        txt = ex.get("text", "")
                        lines.append(f"    [{ctx}]: \"{txt}\"")
                    else:
                        lines.append(f"    \"{ex}\"")
        subtext = vp.get("subtext_rules", "")
        if subtext:
            if isinstance(subtext, list):
                lines.append(f"  Subtext rules: {'; '.join(subtext)}")
            else:
                lines.append(f"  Subtext rules: {subtext}")
    return "\n".join(lines) if lines else "(No voice profiles available)"


def get_batch_size(output_mode: str) -> int:
    """Returns the optimal batch size from config."""
    from config.loader import load_config
    config = load_config()
    if output_mode == "screenplay":
        return config.get("batch_screenplay", 5)
    return config.get("batch_treatment", 8)


def _build_style_context(
    style_manifest: dict,
    characters: dict,
    plot: dict,
    title: str
) -> str:
    """Builds complete style context for the script writer."""
    lines = [f"Title: {title}"]

    if style_manifest:
        if style_manifest.get("genre"):
            lines.append(f"Genre: {style_manifest['genre']}")
        if _compat(style_manifest, "tone", "ton"):
            lines.append(f"Tone: {_compat(style_manifest, 'tone', 'ton')}")
        if _compat(style_manifest, "reference_films", "referenzfilme"):
            lines.append(f"Style like: {', '.join(_compat(style_manifest, 'reference_films', 'referenzfilme'))}")
        if _compat(style_manifest, "special_notes", "besonderheiten"):
            lines.append(f"Special: {_compat(style_manifest, 'special_notes', 'besonderheiten')}")

    if characters:
        leads = [
            f"{name}"
            for name, d in characters.items()
            if _compat(d, "role", "rolle") in ["protagonist", "antagonist"]
        ]
        if leads:
            lines.append(f"Main characters: {', '.join(leads)}")

    if plot.get("themes"):
        lines.append(f"Themes: {', '.join(list(plot['themes'])[:3])}")

    return "\n".join(lines)


def _write_title_page(title: str, output_mode: str, state: dict) -> str:
    """Generates title page.

    Author resolution order:
      1. ``state["meta"]["author"]`` (if set by an upstream step)
      2. ``config["author"]`` (parsed from projekt.autor_roman in projekt.yaml)
      3. fallback ``"(Author unknown)"`` — NEVER a hardcoded guess
    """
    from config.loader import load_config
    mode_label = "TREATMENT" if output_mode == "treatment" else "SCREENPLAY"
    author = state["meta"].get("author")
    if not author:
        author = load_config().get("author") or "(Author unknown)"
    return (
        f"{title.upper()}\n\n"
        f"{mode_label}\n\n"
        f"Based on the literary work by {author}\n"
        f"Adapted by AI Adaptation Pipeline\n"
        f"{'─' * 40}"
    )
