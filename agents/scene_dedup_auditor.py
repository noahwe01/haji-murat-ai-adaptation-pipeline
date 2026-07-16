"""
SCENE DEDUP AUDITOR (Phase D.1)
================================
Pure-Python heuristic detector for near-duplicate adapted_scenes caused
by chunk-overlap: the 200-word overlap between adjacent chunks leads
the Adaptation Agent to emit the same narrative beat from both sides.

Finds pairs of scenes whose source_chunks overlap or are adjacent AND
that share location, characters, and action-word content above a
combined threshold. Flags them — does NOT auto-merge. The flagged
pairs are picked up by orchestrator.route_revision() as a ninth source
and handed to the Revision Agent with an explicit MERGE_SCENES
instruction; the Revision Agent's DECISIONS block keeps the merge
auditable in output/adaptation_log.json.

Design contract:
- Zero LLM calls. Zero token cost. Deterministic.
- Additive only: writes state["scene_dedup_audit"]; never touches
  adapted_scenes.
- English-focused: stopwords/time-tokens target the English pipeline
  output. German fallback not relevant (pipeline language = EN).
"""

from __future__ import annotations

import re

from state_store import load_state, save_state, _compat


# ─── Config ─────────────────────────────────────────────────────────

WEIGHTS = {
    "chunk_proximity": 0.20,
    "location_match": 0.25,
    "character_overlap": 0.25,
    "action_similarity": 0.30,
}
THRESHOLD = 0.55

# Hard floor on action_similarity. Without this, scenes sharing the same
# location and character roster (which is common in chamber-piece beats
# like "5 scenes inside Sado's saklya") score above THRESHOLD purely on
# setting, even when their action content is entirely distinct. The floor
# enforces the real dedup criterion: near-duplicates must share action
# content, not just a room.
MIN_ACTION_SIMILARITY = 0.25

# Stopwords for action-text content-word extraction. Kept small and
# English-focused because the pipeline runs in English.
STOPWORDS = frozenset({
    "the", "and", "that", "this", "with", "from", "have", "has",
    "been", "were", "into", "over", "under", "about", "their", "they",
    "them", "through", "while", "where", "what", "when", "then", "than",
    "which", "there", "here", "some", "both", "each", "other", "more",
    "less", "very", "just", "only", "also", "across", "against",
    "between", "above", "below", "before", "after", "during", "again",
    "such", "those", "these", "once", "would", "could", "should",
    "still", "even", "ever", "never", "must", "shall", "might",
})

# Time/atmosphere tokens that appear in slugs but are not location-defining.
# Filtered out of slug tokens so `INT. ROOM - NIGHT` vs `INT. ROOM - DAY`
# still matches on location.
SLUG_TIME_TOKENS = frozenset({
    "day", "night", "dusk", "dawn", "evening", "morning", "afternoon",
    "midnight", "noon", "continuous", "later", "moments", "same", "time",
    "midday", "midsummer", "winter", "summer", "spring", "autumn", "fall",
})


# ─── Tokenizers ─────────────────────────────────────────────────────

_SLUG_PREFIX = re.compile(r"^(INT\.?|EXT\.?|I/E\.?|INT/EXT\.?|INT\./EXT\.?)\s+", re.IGNORECASE)
_SLUG_PAREN = re.compile(r"\s*\([^)]*\)\s*$")
_WORD = re.compile(r"[A-Za-z']+")


def _slug_tokens(slug: str) -> set[str]:
    """Tokenize a slug into location-defining tokens.

    Strips INT./EXT. prefix and any trailing parenthetical (e.g.
    "(MIDSUMMER)"). Splits on whitespace, dashes, and slashes.
    Filters time/atmosphere tokens (DAY, NIGHT, CONTINUOUS, ...).
    """
    if not slug:
        return set()
    s = _SLUG_PREFIX.sub("", slug)
    s = _SLUG_PAREN.sub("", s).lower()
    tokens = re.split(r"[\s\-/]+", s)
    return {
        t for t in tokens
        if len(t) >= 3 and t not in SLUG_TIME_TOKENS
    }


def _content_tokens(text: str, min_len: int = 4) -> set[str]:
    """Extract content-word tokens from action text for Jaccard similarity."""
    if not text:
        return set()
    words = _WORD.findall(text.lower())
    return {w for w in words if len(w) >= min_len and w not in STOPWORDS}


# ─── Sub-Scores ─────────────────────────────────────────────────────

def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _chunk_proximity(src_a: list, src_b: list) -> float:
    """1.0 if source_chunks overlap, 0.7 if adjacent (gap=1), else 0.0."""
    if not src_a or not src_b:
        return 0.0
    set_a, set_b = set(src_a), set(src_b)
    if set_a & set_b:
        return 1.0
    min_gap = min(abs(a - b) for a in set_a for b in set_b)
    if min_gap == 1:
        return 0.7
    return 0.0


def _combined(scores: dict) -> float:
    return round(sum(WEIGHTS[k] * scores[k] for k in WEIGHTS), 3)


def _build_reason(scores: dict, src_a: list, src_b: list) -> str:
    parts = []
    prox = scores["chunk_proximity"]
    if prox == 1.0:
        parts.append(f"shared chunks {src_a} vs {src_b}")
    elif prox == 0.7:
        parts.append(f"adjacent chunks {src_a} vs {src_b}")
    if scores["location_match"] >= 0.5:
        parts.append(f"location-Jaccard {scores['location_match']:.2f}")
    if scores["character_overlap"] >= 0.5:
        parts.append(f"char-overlap {scores['character_overlap']:.2f}")
    if scores["action_similarity"] >= 0.3:
        parts.append(f"action-Jaccard {scores['action_similarity']:.2f}")
    return ", ".join(parts) if parts else "threshold-triggered"


# ─── Main ───────────────────────────────────────────────────────────

def run_scene_dedup_audit(verbose: bool = True) -> dict:
    """Scan adapted_scenes for near-duplicate pairs, flag them in state.

    Writes `state["scene_dedup_audit"]`. Does NOT modify adapted_scenes.
    Returns the audit dict (also persisted).
    """
    state = load_state()
    scenes = state.get("adapted_scenes", [])

    candidates = []
    pairs_checked = 0

    for i in range(len(scenes)):
        for j in range(i + 1, len(scenes)):
            a, b = scenes[i], scenes[j]
            prox = _chunk_proximity(
                a.get("source_chunks", []),
                b.get("source_chunks", []),
            )
            if prox == 0.0:
                continue
            pairs_checked += 1

            loc = _jaccard(
                _slug_tokens(a.get("slug", "")),
                _slug_tokens(b.get("slug", "")),
            )
            chars_a = set(_compat(a, "characters", "figuren", []))
            chars_b = set(_compat(b, "characters", "figuren", []))
            chars = _jaccard(chars_a, chars_b)
            act = _jaccard(
                _content_tokens(_compat(a, "action", "handlung", "")),
                _content_tokens(_compat(b, "action", "handlung", "")),
            )

            scores = {
                "chunk_proximity": prox,
                "location_match": round(loc, 3),
                "character_overlap": round(chars, 3),
                "action_similarity": round(act, 3),
            }
            combined = _combined(scores)
            scores["combined"] = combined

            if combined >= THRESHOLD and act >= MIN_ACTION_SIMILARITY:
                sid_a = _compat(a, "scene_id", "szenen_id", f"idx_{i}")
                sid_b = _compat(b, "scene_id", "szenen_id", f"idx_{j}")
                candidates.append({
                    "scene_pair": [sid_a, sid_b],
                    "scores": scores,
                    "reason": _build_reason(
                        scores,
                        a.get("source_chunks", []),
                        b.get("source_chunks", []),
                    ),
                    "recommended_action": "MERGE",
                    "source_chunks": [
                        a.get("source_chunks", []),
                        b.get("source_chunks", []),
                    ],
                })

    audit = {
        "meta": {
            "version": "1",
            "threshold": THRESHOLD,
            "min_action_similarity": MIN_ACTION_SIMILARITY,
            "pairs_checked": pairs_checked,
            "flagged": len(candidates),
        },
        "dedup_candidates": candidates,
    }

    state["scene_dedup_audit"] = audit
    save_state(state)

    if verbose:
        print(f"\n{'='*60}")
        print("SCENE DEDUP AUDITOR complete")
        print(f"  Scenes:         {len(scenes)}")
        print(f"  Pairs checked:  {pairs_checked} (within chunk-proximity filter)")
        print(f"  Flagged:        {len(candidates)} (threshold {THRESHOLD})")
        for c in candidates:
            a, b = c["scene_pair"]
            combined = c["scores"]["combined"]
            print(f"  • {a} ↔ {b}  combined={combined:.3f}  — {c['reason']}")
        print(f"{'='*60}\n")

    return audit
