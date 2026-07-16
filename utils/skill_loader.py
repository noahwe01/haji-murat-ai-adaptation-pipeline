"""
SKILL LOADER
=============
Loads relevant skill sections as a compact context block
for agent prompts. Three retrieval layers in order of specificity:

1. skills/ — project-local skill definitions
2. obsidian-vault/config/ — project-specific overrides
3. Adaptions-Brain — shared screenwriting knowledge vault (destilled notes)
4. MCP Reference Server index — optional, locally licensed reference corpus

The MCP layer is lazy-loaded (index.json is 17MB) and cached at module level.
Use retrieve_reference_excerpts() for deep theory lookups when the brain is too shallow.
"""

import json
import re
from pathlib import Path


FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = FRAMEWORK_ROOT / "skills"
# Project-Vault overrides live next to project CWD; fall back to framework root.
_SECONDARY_CANDIDATES = (
    Path.cwd() / "obsidian-vault" / "config",
    Path.cwd() / "HM_obsidian-vault" / "config",
    FRAMEWORK_ROOT / "obsidian-vault" / "config",
)
SECONDARY_SKILLS_DIRS = [p for p in _SECONDARY_CANDIDATES if p.exists()]
SECONDARY_SKILLS_DIR = SECONDARY_SKILLS_DIRS[0] if SECONDARY_SKILLS_DIRS else _SECONDARY_CANDIDATES[0]


# ─── Phase G.3 — Central Retrieval Budgets ────────────────────────────
# Single source of truth for per-agent retrieval-token budgets across the
# three layers (skills / brain / MCP). Replaces ad-hoc `max_chars=...`
# scattered throughout agent prompts. Callers MAY still override by passing
# an explicit max_chars; defaults pulled here keep the prompt size sane on
# long-form runs before retrieval caps are applied.
#
# Budgets are CHARS, not tokens. Conservative ratio ~4 chars/token.

RETRIEVAL_BUDGETS: dict[str, dict[str, int]] = {
    # Phase 1
    "story_analyst":         {"skills": 3000, "brain":    0, "mcp":    0},
    # Phase 2
    "character_agent":       {"skills": 3000, "brain": 2000, "mcp":    0},
    "world_agent":           {"skills": 2000, "brain":    0, "mcp":    0},
    # Phase 5
    "adaptation_agent":      {"skills": 3000, "brain": 2000, "mcp": 2000},
    # Phase 6 / 9
    "script_writer_treatment": {"skills": 2000, "brain": 1500, "mcp":    0},
    "script_writer_screenplay": {"skills": 3000, "brain": 2000, "mcp":    0},
    # Phase 7
    "coverage_agent":        {"skills": 2000, "brain": 2000, "mcp":    0},
    "style_validator":       {"skills": 2000, "brain":    0, "mcp":    0},
    # Phase 8
    "revision_agent":        {"skills": 3000, "brain": 2000, "mcp": 2000},
    # Phase 9.5 (analysis layer)
    "narrative_coherence":   {"skills": 2000, "brain": 5000, "mcp": 5000},
    "pacing_analyzer":       {"skills": 1500, "brain": 2000, "mcp":    0},
    "transition_mapper":     {"skills": 1500, "brain": 2000, "mcp":    0},
    "dialog_thread_checker": {"skills": 1500, "brain": 2000, "mcp":    0},
    "subtext_auditor":       {"skills": 1500, "brain": 2000, "mcp":    0},
    "table_read":            {"skills": 1500, "brain": 2000, "mcp":    0},
}

# Conservative defaults for any caller not in the table.
_DEFAULT_BUDGET = {"skills": 2000, "brain": 2000, "mcp": 0}


def get_retrieval_budget(agent: str, layer: str) -> int:
    """Returns char-budget for (agent, layer). layer ∈ {skills,brain,mcp}."""
    cfg = RETRIEVAL_BUDGETS.get(agent, _DEFAULT_BUDGET)
    return int(cfg.get(layer, _DEFAULT_BUDGET.get(layer, 0)))
BRAIN_ROOT = FRAMEWORK_ROOT / "adaptions-brain"
BRAIN_DIRS = [
    BRAIN_ROOT / "techniken",
    BRAIN_ROOT / "konzepte",
    BRAIN_ROOT / "patterns",
    BRAIN_ROOT / "dialog-bibliothek",
    BRAIN_ROOT / "beispiele",
    BRAIN_ROOT / "autoren",
    BRAIN_ROOT / "theorie",
    BRAIN_ROOT / "qualitaet",
]

# Which skills each agent requires
AGENT_SKILLS = {
    "story_analyst": [
        "source-material-analysis",
        "story-to-3act-structure",
        "logline-creation",
    ],
    "character_agent": [
        "character-want-need",
        "cultural-authenticity",
        "dialogue-adaptation",
        "figurenstimme-differenzieren",  # Brain: voice consistency
    ],
    "world_agent": [
        "prose-to-visual-scenes",
    ],
    "adaptation_agent": [
        "adaptation-conflict-design",
        "scene-card-breakdown",
        "subplot-weaving",
        "prose-to-visual-scenes",
        "plot-point-mapping",
        "style-guide-period-romantic-tragedy",
        "voice-profile-injection",        # Brain: full 9-dimension injection
    ],
    "script_writer_treatment": [
        "film-treatment-creation",
    ],
    "script_writer_screenplay": [
        "dialogue-adaptation",
        "screenplay-formatting",
        "theme-to-screen",
        "dialog-polish-pass",             # Brain: two-pass dialog strategy
    ],
    "coverage_agent": [
        "adaptation-workflow",
        "coverage-volltext-evaluation",   # Brain: compression strategy
    ],
    "style_validator": [
        "style-validation-methodik",      # Brain: 5-category methodology
    ],
    "revision_agent": [
        "revision-agent-workflow",        # Brain: targeted revision strategy
        "dialogue-adaptation",
    ],
    # Phase 9.5 Analysis Layer
    "narrative_coherence": [
        "narrative-audit-checkliste",     # Brain konzepte: dangling/earned-ending audit
        "story-values-rhythmus",          # Brain konzepte: McKee value oscillation
        "story-values",                   # Brain konzepte: value at stake
        "adaptation-workflow",            # skills/: orchestration baseline
    ],
    "pacing_analyzer": [
        "pacing-rhythmus",                # Brain konzepte: dead zones, momentum
        "slow-cinema-pacing",             # Brain konzepte: art-house pacing reference
        "rhythmus-pacing",                # Brain techniken: scene-duration discipline
    ],
    "transition_mapper": [
        "szenenuebergang-typen",          # Brain techniken: match-cut/sound-bridge taxonomy
        "scene-card-breakdown",           # skills/: scene-pair structure
        "theme-to-screen",                # skills/: thematic transition mapping
    ],
    "dialog_thread_checker": [
        "dialog-polish-pass",             # Brain techniken: voice-consistency checks
        "figurenstimme-differenzieren",   # Brain konzepte: voice differentiation
    ],
    "subtext_auditor": [
        "subtext",                        # Brain konzepte: 70/30 rule canonical source
        "dialog-polish-pass",             # Brain techniken: subtext layering
        "visueller-subtext",              # Brain techniken: visual subtext carriers
        "subtext-masterclass",            # Brain dialog-bibliothek: advanced examples
    ],
    "table_read": [
        "screenplay-formatting",          # skills/: speakability format rules
        "dialogue-adaptation",            # skills/: dialog phrasing
        "dialog-polish-pass",             # Brain techniken: rhythm + dead-line detection
    ],
}


# ─── Scene-type → Dialog-Bibliothek Mapping ──────────────────────────

SCENE_TYPE_KEYWORDS = {
    "konfrontation-szenen": ["confrontation", "argument", "fight", "conflict", "clash", "accusation", "quarrel", "confront"],
    "liebes-szenen": ["love", "romance", "kiss", "passion", "desire", "intimacy", "attraction", "longing", "courtship"],
    "gestaendnis-szenen": ["confession", "reveal", "secret", "truth", "admit", "recognition", "disclosure"],
    "abschied-szenen": ["farewell", "departure", "goodbye", "leaving", "parting", "separation", "loss"],
    "verhoer-szenen": ["interrogation", "questioning", "investigation", "cross-examine", "probe", "interview"],
    "exposition-szenen": ["exposition", "introduction", "setup", "establish", "world-building", "context"],
    "selbsterkenntnis-szenen": ["self-discovery", "realization", "epiphany", "recognition", "awakening", "insight"],
    "macht-szenen": ["power", "authority", "dominance", "submission", "control", "hierarchy", "manipulation"],
    "humor-szenen": ["comedy", "humor", "wit", "irony", "satire", "comic", "funny", "absurd"],
    "gruppen-szenen": ["group", "ensemble", "gathering", "party", "meeting", "assembly", "crowd", "dinner"],
    "subtext-masterclass": ["subtext master", "advanced subtext", "subtext technique", "layered dialog"],
}

# ─── Concept relevance mapping ────────────────────────────────────────

CONCEPT_TRIGGERS = {
    # Concept file → keywords that trigger loading
    "subtext": ["dialog", "subtext", "on-the-nose", "meaning", "indirect"],
    "on-the-nose": ["dialog", "direct", "exposition", "telling", "stating"],
    "show-dont-tell": ["visual", "action", "showing", "cinematic", "describing"],
    "dramatic-question": ["question", "tension", "suspense", "stakes", "will they"],
    "setup-payoff": ["setup", "payoff", "chekhov", "plant", "foreshadow"],
    "character-arc": ["arc", "transformation", "change", "growth", "flaw"],
    "klimax": ["climax", "peak", "culmination", "final", "showdown"],
    "gap-prinzip": ["gap", "expectation", "surprise", "reversal", "twist"],
    "exposition-timing": ["exposition", "information", "backstory", "reveal"],
    "dramatische-ironie": ["irony", "dramatic irony", "audience knows", "unaware"],
    "spannungskurve": ["tension", "pacing", "build", "release", "rhythm"],
    # NOTE: stille-als-dialog and innerer-monolog-visuell live in techniken/, not konzepte/
    # They are registered in TECHNIQUE_TRIGGERS below
    "filmisches-erzaehlen": ["visual storytelling", "cinematic", "camera", "mise en scene"],
    "thematische-integration": ["theme", "motif", "symbol", "meaning", "allegory"],
    "pacing-rhythmus": ["dead zone", "variation", "acceleration", "dialog density", "momentum", "pacing"],
    "slow-cinema-pacing": ["slow cinema", "pawlikowski", "zvyagintsev", "art-house", "slowness", "contemplative"],
    "story-values-rhythmus": ["story value", "value shift", "mckee", "oscillation", "coherence"],
    "narrative-audit-checkliste": ["dangling", "earned ending", "through-line", "missed opportunity", "ecosystem", "payoff"],
    "action-line-discipline": ["action line", "novelistic", "camera direction", "unfilmable", "static scene", "filmability", "walking and talking", "subtext annotation"],
    # ─── Previously unregistered konzepte (18) ───
    "acht-sequenzen": ["eight sequences", "sequence", "stoehr", "8 sequences"],
    "antagonismus": ["antagonist", "opponent", "opposing force", "villain", "obstacle"],
    "backstory": ["backstory", "background", "past", "history", "before the story"],
    "beat-sheet": ["beat sheet", "beat", "snyder", "save the cat", "15 beats"],
    "character-want-need": ["want", "need", "desire", "internal need", "external want"],
    "drei-akt-struktur": ["three act", "act structure", "act one", "act two", "act three", "3 act"],
    "figurenstimme-differenzieren": ["voice differentiation", "distinct voice", "character voice", "speech pattern"],
    "genre-konventionen": ["genre", "convention", "genre expectations", "genre rules"],
    "inciting-incident": ["inciting incident", "catalyst", "call to adventure", "trigger event"],
    "konflikttypen": ["conflict type", "man vs", "internal conflict", "external conflict"],
    "krise-entscheidung": ["crisis", "decision", "dilemma", "impossible choice", "forced choice"],
    "midpoint-wendung": ["midpoint", "midpoint reversal", "turning point", "act two midpoint"],
    "opening-image": ["opening image", "first image", "opening shot", "establish"],
    "plot-points": ["plot point", "turning point", "act break", "structural beat"],
    "praemisse": ["premise", "controlling idea", "thesis", "what the story is about"],
    "publikums-emotion": ["audience emotion", "audience feels", "empathy", "identification", "catharsis"],
    "story-values": ["story value", "value at stake", "life death", "love hate", "freedom slavery"],
    "szenenanalyse": ["scene analysis", "scene breakdown", "scene function", "scene purpose"],
    "ticking-clock": ["ticking clock", "deadline", "time pressure", "countdown", "urgency"],
    "unity-of-opposites": ["unity of opposites", "protagonist antagonist bond", "locked together", "need each other"],
    # ─── T2.2 Lernagenda (Tolstoi als Quellautor) ───
    "tolstoi-erzaehlstil": ["tolstoi", "tolstoy", "polyphone", "multi-pov", "erzaehlstil",
                            "physical signature", "tableau", "russian realism", "free indirect discourse",
                            "auktorialer erzaehler", "moralische distanz", "epic breadth"],
    # ─── T2.4 Lernagenda (Kaukasus-Kontext) ───
    "kaukasus-krieg-1851": ["caucasus", "kaukasus", "chechen", "dagestan", "imamate", "imamat",
                            "shamil", "murid", "naib", "kunak", "aoul", "cherkesska", "burka",
                            "yermolov", "caucasian war", "1851", "1852", "vorontsov caucasus",
                            "tiflis", "nukha", "vedeno", "slow advance", "deforestation"],
    "vier-figurenfunktionen": ["character function", "figurenfunktion", "storytelling function",
                               "helping function", "thematic function", "color function",
                               "catalyst character", "confidante", "narrator-observer", "narrator-actor",
                               "sympathetic character", "three five seven", "cut characters",
                               "seger characters"],
}


# ─── Technique relevance mapping ─────────────────────────────────────

TECHNIQUE_TRIGGERS = {
    "adaptation-expansion": ["expansion", "short story", "feature length", "extend", "invent scenes"],
    "cliffhanger-technik": ["cliffhanger", "suspense", "hook", "end of act"],
    "cold-open": ["cold open", "pre-credits", "opening", "hook", "teaser"],
    "dialog-durch-handlung": ["action replaces dialog", "physical dialog", "behavior", "gesture"],
    "dialog-kompression": ["dialog compression", "trim", "cut dialog", "tighten", "economize"],
    "dialog-polish-pass": ["dialog polish", "second pass", "voice consistency", "rewrite dialog"],
    "emotionale-vorbereitung": ["emotional preparation", "audience setup", "anticipation", "dread"],
    "exposition-verstecken": ["hide exposition", "buried exposition", "natural information", "disguise"],
    "figureneinfuehrung": ["character introduction", "first appearance", "introduce", "entrance"],
    "flashback-technik": ["flashback", "memory", "past", "time shift", "nonlinear"],
    "innerer-monolog-visuell": ["inner monologue", "internal", "thought", "voiceover", "externalize"],
    "montage-sequenz": ["montage", "passage of time", "compression", "sequence", "time lapse"],
    "parallelmontage": ["parallel montage", "cross-cutting", "intercut", "simultaneous"],
    "period-drama-adaption": ["period", "historical", "costume", "19th century", "era", "epoch"],
    "revision-agent-workflow": ["revision", "rewrite", "fix", "targeted revision"],
    "rhythmus-pacing": ["rhythm", "pacing", "tempo", "beat length", "scene duration"],
    "stille-als-dialog": ["silence", "pause", "wordless", "unspoken", "quiet moment"],
    "szenenuebergang-typen": ["transition", "scene bridge", "match cut", "sound bridge", "visual rhyme"],
    "treatment-konventionen": ["treatment", "craig mazin", "prose narrative", "treatment format"],
    "unreliable-narrator": ["unreliable", "narrator", "perspective", "deception", "subjective"],
    # ─── T2.6 Lernagenda (Strukturmethoden) ───
    "framing-device": ["framing device", "rahmenerzaehlung", "frame narrative type", "motiv-klammer",
                       "typ-3 rahmen", "distel-rahmen", "bildmotiv klammer"],
    "intercutting-parallelhandlung": ["intercutting", "parallelhandlung", "parallel worlds",
                                      "diptychon", "structural parallelism", "two courts",
                                      "nikolaus shamil parallel"],
    "visueller-subtext": ["visual subtext", "symbolic image", "visual metaphor", "object meaning"],
    "voice-over-regeln": ["voice over", "narration", "off-screen", "narrator voice"],
    "voice-profile-injection": ["voice profile", "character voice", "speech pattern", "verbal tic"],
    "coverage-volltext-evaluation": ["coverage", "evaluation", "full text", "compression strategy"],
    "adaptions-brain-aktiv-nutzen": ["brain usage", "knowledge retrieval", "brain lookup"],
}


# ─── Pattern relevance mapping ───────────────────────────────────────

PATTERN_TRIGGERS = {
    "dialog-zu-handlung": ["dialog to action", "replace dialog", "show instead", "behavior replaces words"],
    "erzaehler-eliminieren": ["eliminate narrator", "remove narration", "dramatize", "no narrator"],
    "expansion-kurzgeschichte": ["short story expansion", "feature from short", "expand", "invent"],
    "innerer-monolog-zu-bild": ["inner monologue to image", "thought to visual", "externalize thought"],
    "klimax-konstruktion": ["climax construction", "build climax", "final confrontation", "peak"],
    "kompression-roman": ["novel compression", "cut subplots", "merge characters", "tighten novel",
                         "killing darlings", "scale reduction", "compression cuts", "scene verdichtung"],
    "nebenfigur-aufwerten": ["elevate minor character", "secondary character", "give voice", "expand role"],
    "perspektivwechsel": ["perspective shift", "point of view", "whose story", "viewpoint change"],
    "pipeline-anti-patterns": ["anti-pattern", "common mistake", "pipeline error", "avoid"],
    "streichungen-entscheidungen": ["cut decision", "what to cut", "omit", "leave out", "sacrifice"],
    "ton-translation": ["tone translation", "literary tone", "adapt tone", "mood translation"],
    "zeitebenen-verschachteln": ["time layers", "nonlinear", "temporal", "nested timeline", "time structure"],
    # ─── T2.6 Lernagenda (Strukturmethoden Pattern-Teil) ───
    "non-linear-storytelling": ["non-linear", "rashomon pattern", "pulp fiction structure", "memento",
                                "reverse chronology", "mosaic structure", "fragmented narrative",
                                "nicht-linear"],
    "antiheroische-fokalisierung": ["antihero", "antihelden", "pov reduction", "fokalisierung",
                                    "ambivalenter protagonist", "sympathy gap", "walter white pattern",
                                    "michael corleone arc"],
    # ─── T2.1 Lernagenda (Adaptionstheorie Deep-Dive) ───
    "figurenfusion": ["character merge", "character consolidation", "fusion", "composite character",
                      "merge characters", "figurenfusion", "komposit", "nebenfigur fusion"],
    "plot-umstrukturierung": ["plot restructure", "act reorder", "in medias res", "frame narrative",
                              "timeline restructure", "rahmenerzaehlung", "strukturumbau", "plot reorder",
                              "dual timeline", "framing device"],
}


# ─── Beispiele relevance mapping ─────────────────────────────────────
# beispiele/ notes are case studies (film analyses). Retrieved when pipeline needs
# specific adaptation precedents for novel-to-feature, multi-pov, tolstoi, etc.

BEISPIELE_TRIGGERS = {
    "war-and-peace-1966-kompression": ["war and peace", "bondarchuk", "tolstoi adaptation",
                                        "close adaptation extreme", "epos-adaption", "sowjet-film",
                                        "7 stunden", "seven hour adaptation"],
    "english-patient-adaptation": ["english patient", "minghella", "ondaatje", "dual timeline case",
                                    "invented scenes", "walter murch", "temporal transitions",
                                    "multi-pov refocalization", "cave of swimmers"],
    "last-duel-rashomon-kompression": ["last duel", "ridley scott", "rashomon structure",
                                        "multi-pov preserved", "three povs", "holofcener", "jager",
                                        "medieval rashomon"],
    "anna-karenina-wright-2012": ["anna karenina", "joe wright", "stoppard", "theater adaptation",
                                   "transposition extreme", "stage concept", "tolstoi transposition"],
    "barry-lyndon-thackeray": ["barry lyndon", "kubrick", "thackeray", "unreliable narrator",
                               "voice over discipline", "candlelight cinematography",
                               "historical epic film"],
    "doctor-zhivago-analyse": ["doctor zhivago", "pasternak", "robert bolt", "david lean",
                                "frame narrator yevgraf"],
}


# ─── Theorie relevance mapping ───────────────────────────────────────
# theorie/ notes hold foundational adaptation theory that spans patterns + techniques.

THEORIE_TRIGGERS = {
    "adaptionstheorie-foundations": ["adaptation theory", "faithful", "free adaptation", "transposition",
                                     "literalism", "second original", "werkgeist", "adaptation stance",
                                     "reinvention", "dudley andrew", "close adaptation", "loose adaptation"],
    "grundlagen": ["theory", "foundations", "grundlagen", "overview"],
}


def retrieve_brain_knowledge(context: dict, max_chars: int = 4000) -> tuple:
    """
    Dynamically retrieves brain notes based on context.
    Like a real brain: "Do I know something about this? If yes, use it."

    Args:
        context: Dict with keys like:
            - scene_type: "confession", "confrontation", etc.
            - emotional_core: "guilt and revelation"
            - technique_needed: "subtext", "exposition"
            - phase: "adaptation", "coverage", "revision"
            - keywords: ["love", "farewell", "irony"]

    Returns:
        Tuple of (knowledge_text, knowledge_gaps):
        - knowledge_text: Loaded brain content as string
        - knowledge_gaps: List of topics where no brain note was found
    """
    keywords = set()

    # Collect keywords from context
    for key in ["scene_type", "emotional_core", "technique_needed"]:
        val = context.get(key, "")
        if val:
            keywords.update(val.lower().split())

    if context.get("keywords"):
        keywords.update(w.lower() for w in context["keywords"])

    if not keywords:
        return "", []

    # 1. Match scene type → dialog-bibliothek
    matched_files = []
    for biblio_file, triggers in SCENE_TYPE_KEYWORDS.items():
        if any(kw in keywords for kw in triggers):
            matched_files.append(("dialog-bibliothek", biblio_file))

    # 2. Match concepts
    for concept_file, triggers in CONCEPT_TRIGGERS.items():
        if any(kw in keywords for kw in triggers):
            matched_files.append(("konzepte", concept_file))

    # 3. Match techniques
    for tech_file, triggers in TECHNIQUE_TRIGGERS.items():
        if any(kw in keywords for kw in triggers):
            matched_files.append(("techniken", tech_file))

    # 4. Match patterns
    for pattern_file, triggers in PATTERN_TRIGGERS.items():
        if any(kw in keywords for kw in triggers):
            matched_files.append(("patterns", pattern_file))

    # 5. Match theorie (foundational adaptation theory)
    for theorie_file, triggers in THEORIE_TRIGGERS.items():
        if any(kw in keywords for kw in triggers):
            matched_files.append(("theorie", theorie_file))

    # 6. Match beispiele (case study film analyses)
    for beispiel_file, triggers in BEISPIELE_TRIGGERS.items():
        if any(kw in keywords for kw in triggers):
            matched_files.append(("beispiele", beispiel_file))

    # 7. Load matched files
    brain_root = BRAIN_ROOT
    parts = []
    remaining = max_chars
    loaded = set()
    gaps = []

    for subdir, filename in matched_files:
        if filename in loaded:
            continue
        filepath = brain_root / subdir / f"{filename}.md"
        if not filepath.exists():
            gaps.append(f"{subdir}/{filename}")
            # Auto-log the gap in state
            try:
                from state_store import log_knowledge_gap
                log_knowledge_gap(
                    topic=f"{subdir}/{filename}",
                    context=f"Keywords: {', '.join(keywords)}",
                    agent=context.get("agent", "unknown"),
                )
            except Exception:
                pass  # Don't crash if state_store unavailable
            continue

        content = filepath.read_text(encoding="utf-8")

        # Strip YAML frontmatter
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3:].strip()

        if len(content) > remaining:
            content = content[:remaining] + "..."

        parts.append(f"### [{subdir}] {filename}\n{content}")
        remaining -= len(content)
        loaded.add(filename)

        if remaining <= 0:
            break

    knowledge_text = ""
    if parts:
        knowledge_text = "BRAIN KNOWLEDGE (retrieved for this context):\n\n" + "\n\n".join(parts)

    return knowledge_text, gaps


def load_skills_for_agent(agent_name: str, max_chars: int | None = None) -> str:
    """
    Loads the mandatory skills for an agent as compact text.
    Extracts only the core sections (no YAML frontmatter).

    Search order: skills/ → obsidian-vault/config/ → Adaptions-Brain dirs.

    Args:
        agent_name: Key from AGENT_SKILLS
        max_chars: Maximum character count (context budget). When None,
            resolves from G.3 RETRIEVAL_BUDGETS[agent_name]['skills']
            (default 2000 if unknown). Pass an int to override.

    Returns:
        Compact skill text for the prompt
    """
    skill_names = AGENT_SKILLS.get(agent_name, [])
    if not skill_names:
        return ""

    if max_chars is None:
        max_chars = get_retrieval_budget(agent_name, "skills")

    parts = []
    remaining = max_chars

    for skill_name in skill_names:
        # Try primary directory first, then secondary dirs, then brain dirs
        filepath = SKILLS_DIR / f"{skill_name}.md"
        if not filepath.exists():
            for sec_dir in SECONDARY_SKILLS_DIRS:
                candidate = sec_dir / f"{skill_name}.md"
                if candidate.exists():
                    filepath = candidate
                    break
        if not filepath.exists():
            for brain_dir in BRAIN_DIRS:
                candidate = brain_dir / f"{skill_name}.md"
                if candidate.exists():
                    filepath = candidate
                    break
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8")

        # Strip YAML frontmatter
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3:].strip()

        # Trim to budget
        if len(content) > remaining:
            content = content[:remaining] + "..."

        parts.append(f"### {skill_name}\n{content}")
        remaining -= len(content)

        if remaining <= 0:
            break

    if not parts:
        return ""

    return "METHODOLOGY SKILLS (mandatory application):\n\n" + "\n\n".join(parts)


# ═══════════════════════════════════════════════════════════════════
#  MCP REFERENCE LAYER — raw theory & screenplay excerpts
# ═══════════════════════════════════════════════════════════════════

MCP_INDEX_PATH = FRAMEWORK_ROOT / "mcp-server" / "index.json"

# Lazy-loaded module-level cache (17 MB is too big to load on import)
_MCP_INDEX_CACHE = None
_MCP_TOKENIZED_CACHE = None  # pre-tokenized chunks for faster search


def _load_mcp_index() -> dict:
    """Lazy-loads the MCP server index.json and caches it module-level."""
    global _MCP_INDEX_CACHE, _MCP_TOKENIZED_CACHE
    if _MCP_INDEX_CACHE is not None:
        return _MCP_INDEX_CACHE

    if not MCP_INDEX_PATH.exists():
        _MCP_INDEX_CACHE = {"meta": {}, "documents": [], "chunks": []}
        _MCP_TOKENIZED_CACHE = []
        return _MCP_INDEX_CACHE

    with open(MCP_INDEX_PATH, "r", encoding="utf-8") as f:
        _MCP_INDEX_CACHE = json.load(f)

    # Pre-tokenize chunks into lowercased word sets for fast keyword matching
    _MCP_TOKENIZED_CACHE = []
    for chunk in _MCP_INDEX_CACHE.get("chunks", []):
        text = chunk.get("text", "")
        tokens = set(re.findall(r"\b\w+\b", text.lower()))
        _MCP_TOKENIZED_CACHE.append(tokens)

    return _MCP_INDEX_CACHE


def retrieve_reference_excerpts(
    query: str,
    max_chars: int = 4000,
    categories: list = None,
    top_n: int = 5,
) -> tuple:
    """
    Searches an optional, locally built MCP reference corpus
    for keyword matches and returns the highest-scoring excerpts.

    Args:
        query: Free-text query (e.g. "story values shift", "dead zone pacing")
        max_chars: Total character budget for returned excerpts
        categories: Filter to subset of ["theory", "screenplay", "treatment"]. None = all.
        top_n: Maximum number of excerpts to return

    Returns:
        Tuple of (excerpt_text, metadata):
        - excerpt_text: formatted text block with source attribution
        - metadata: list of dicts with document_title, category, score
    """
    index = _load_mcp_index()
    docs = index.get("documents", [])
    chunks = index.get("chunks", [])
    if not chunks or _MCP_TOKENIZED_CACHE is None:
        return "", []

    # Build doc lookup (id → metadata)
    doc_map = {d["id"]: d for d in docs}

    # Tokenize query
    query_tokens = set(re.findall(r"\b\w+\b", query.lower()))
    # Drop stopwords + single-char tokens
    stopwords = {"the", "a", "an", "of", "to", "in", "on", "at", "for", "is", "it",
                 "and", "or", "but", "with", "from", "as", "be", "by", "this", "that",
                 "how", "when", "what", "why", "where", "can", "will", "do", "does"}
    query_tokens = {t for t in query_tokens if len(t) > 2 and t not in stopwords}
    if not query_tokens:
        return "", []

    # Score each chunk by unique token overlap
    scored = []
    for i, chunk in enumerate(chunks):
        doc_id = chunk.get("doc_id")
        doc = doc_map.get(doc_id, {})
        if categories and doc.get("category") not in categories:
            continue
        chunk_tokens = _MCP_TOKENIZED_CACHE[i]
        overlap = len(query_tokens & chunk_tokens)
        if overlap >= 2:  # require at least 2 matching tokens
            scored.append((overlap, i, chunk, doc))

    if not scored:
        return "", []

    # Sort by score desc, take top_n
    scored.sort(key=lambda x: (-x[0], x[1]))
    scored = scored[:top_n]

    # Build the excerpt block
    parts = []
    metadata = []
    remaining = max_chars
    for score, _, chunk, doc in scored:
        title = doc.get("title", "Unknown")
        category = doc.get("category", "?")
        chunk_idx = chunk.get("chunk_index", "?")
        total = chunk.get("total_chunks", "?")
        text = chunk.get("text", "").strip()

        header = f"### [{category}] {title} — chunk {chunk_idx}/{total}  (score={score})"
        block = f"{header}\n{text}"

        if len(block) > remaining:
            block = block[:remaining] + "..."
        parts.append(block)
        metadata.append({
            "title": title,
            "category": category,
            "chunk": f"{chunk_idx}/{total}",
            "score": score,
        })
        remaining -= len(block)
        if remaining <= 0:
            break

    excerpt_text = ("REFERENCE EXCERPTS (retrieved from MCP corpus):\n\n"
                    + "\n\n".join(parts))
    return excerpt_text, metadata
