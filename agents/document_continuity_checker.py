"""
DOCUMENT CONTINUITY CHECKER (Phase E)
=====================================
Document-level continuity guard for ASSEMBLED/TRANSFORMED final texts
(treatments, format transforms, polish rewrites).

Closes the guard gap: orchestrator.continuity_check() validates scenes
against story_state during generation (Phase 5) — but once scenes are
fused into a treatment and rewritten by later passes, the resulting
DOCUMENT is never re-validated as a whole. None of the analysis agents
checks fact continuity on the final text (dialog_thread_checker checks
conversational threads, not character status). This module audits the
final document text for INTERNAL contradictions, independent of
story_state, so it works on any text artifact the pipeline emits.

Hybrid, three stages:
  1. LLM fact extraction per segment (acts + key scene) — blind, facts
     only, no judgment. Prompts contain NO hints at known issues.
  2. Pure-Python contradiction rules over the merged fact database
     (death-then-active, count mismatch, object without establishment).
  3. LLM judge verifies candidates against the full text and scans the
     fact database for contradictions the rules missed. A parallel
     holistic full-document pass provides a second, independent lens.

Model: Sonnet (analytical, standard routing — no creative writing).
Integration: standalone dispatch (like scene_dedup_auditor), after any
assembly/transform/rewrite pass. Findings feed orchestrator.
route_revision() as an additional source ("document_continuity").

Design contract:
- Additive only: writes state["document_continuity_check"]; never
  touches treatment text or adapted_scenes.
- Deterministic rules are generic continuity logic; they encode no
  document-specific knowledge.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime

from state_store import load_state, save_state


# ─── Segmentation (pure Python) ─────────────────────────────────────

_SCENE_RE = re.compile(r"^(\d+)\.\s+(.+)$")
_ACT_RE = re.compile(r"^ACT (ONE|TWO|THREE|FOUR|FIVE)\s*$")
_HEADER_RE = re.compile(r"^##\s+(.+)$")


def segment_document(document_path: str) -> dict:
    """Split a pipeline treatment into checkable segments.

    Recognizes: '## Character Descriptions', '## Treatment' (with plain
    'ACT ONE/TWO/THREE' lines and 'N. SLUGLINE' scenes), '## Key Scene'
    (matched by prefix). Front matter (logline/summary) is not segmented
    scene-wise — it is covered by the holistic pass and the judge, which
    both receive the full text.
    """
    with open(document_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    sections = {}  # header -> (start, end) line indices, end exclusive
    current, start = None, 0
    for i, line in enumerate(lines):
        m = _HEADER_RE.match(line)
        if m:
            if current is not None:
                sections[current] = (start, i)
            current, start = m.group(1).strip(), i + 1
    if current is not None:
        sections[current] = (start, len(lines))

    def _find(prefix):
        for name, span in sections.items():
            if name.lower().startswith(prefix.lower()):
                return span
        return None

    char_span = _find("Character Descriptions")
    treat_span = _find("Treatment")
    key_span = _find("Key Scene")

    characters_section = (
        "\n".join(lines[char_span[0]:char_span[1]]).strip() if char_span else ""
    )
    key_scene = (
        "\n".join(lines[key_span[0]:key_span[1]]).strip() if key_span else ""
    )

    acts = []
    scene_count = 0
    if treat_span:
        body = lines[treat_span[0]:treat_span[1]]
        act_name, act_lines = None, []
        for line in body:
            am = _ACT_RE.match(line.strip())
            if am:
                if act_name is not None:
                    acts.append({"act": act_name, "text": "\n".join(act_lines).strip()})
                act_name, act_lines = am.group(1), []
            else:
                act_lines.append(line)
        if act_name is not None:
            acts.append({"act": act_name, "text": "\n".join(act_lines).strip()})
        scene_count = sum(
            1 for line in body if _SCENE_RE.match(line.strip())
        )

    return {
        "characters_section": characters_section,
        "acts": acts,
        "key_scene": key_scene,
        "scene_count": scene_count,
    }


# ─── LLM Prompts ────────────────────────────────────────────────────

SYSTEM_DOC_EXTRACT = """You are a script supervisor building a continuity fact database for a film treatment.
Extract FACTS ONLY — do not judge, do not interpret, do not flag problems.

CHARACTER LIST (for name normalization — use these canonical names):
{characters_section}

DOCUMENT SEGMENT: {segment_label}
──────────────────────────────────
{segment_text}
──────────────────────────────────

For EVERY scene in this segment (scenes are numbered "N. SLUGLINE"; if the segment
is a single unnumbered dialogue scene, treat it as one scene with id "KEY_SCENE"),
extract:

1. "characters_active": characters who speak or perform physical actions in the scene.
2. "characters_inert": characters only mentioned, referenced, remembered, absent,
   or present without acting.
3. "ordered_events": chronological list of significant events AS THEY OCCUR in the
   scene text. Event types: death, wound, capture, escape, arrival, departure,
   object_transfer, speech, physical_action. Include "speech" and "physical_action"
   events ONLY for characters that also have a death/wound/capture event in the
   SAME scene (for everyone else, characters_active suffices). Each event:
   {{"position": <1-based order in scene>, "who": "<canonical name or GROUP>",
     "event": "<type>", "detail": "<max 15 words>", "quote": "<exact fragment, max 12 words>"}}
4. "objects": significant props:
   {{"object": "...", "action": "introduced|used|transferred|destroyed",
     "holder": "<who has it>", "detail": "<max 12 words>"}}
5. "counts": explicit numbers of people/animals/things:
   {{"what": "...", "value": <number>, "quote": "<exact fragment>"}}
6. "time_markers": explicit time/season/day markers as strings.
7. "injuries": {{"character": "...", "injury": "...", "quote": "<exact fragment>"}}

Be exhaustive on status events (death/wound/capture) — every single one, even for
minor characters. Use exact quotes from the text.

OUTPUT as valid JSON only — no markdown fences, no commentary:
{{"segment": "{segment_label}",
  "scene_facts": [
    {{"scene": "<number or KEY_SCENE>",
      "characters_active": [], "characters_inert": [],
      "ordered_events": [], "objects": [], "counts": [],
      "time_markers": [], "injuries": []}}
  ]}}"""


SYSTEM_DOC_HOLISTIC = """You are a continuity script supervisor performing a full-document audit of a film
treatment before it goes to production.

Read the ENTIRE document below, then report every INTERNAL CONTINUITY CONTRADICTION
you find — places where the document contradicts itself. Check systematically:

1. CHARACTER STATUS: alive/dead/wounded/captured status must be consistent within
   each scene and across scenes. Note that a treatment may tell the same events
   twice (a summary scene AND a fully realized scene) — the two tellings must agree
   on what happens and in what order.
2. OBJECT PROVENANCE: props that are used, handed over, or pointedly featured must
   be consistent with how and where they were established; two similar objects must
   not blur into each other.
3. COUNTS: numbers of people, horses, objects must match across scenes unless the
   text explains the change.
4. TIMELINE: time/season/day markers must not contradict each other.
5. INJURIES / PHYSICAL STATE: wounds and physical limitations must persist until
   healed or explained.
6. IDENTITY: names, ages, and relationships must stay consistent, including between
   the character list, the logline/summary, and the scenes.

Do NOT report style, pacing, or quality judgments — ONLY factual contradictions
internal to this document. For each finding give exact evidence quotes.

Severity: "critical" = breaks story logic on screen; "high" = audience-visible
inconsistency; "medium" = detail-level; "low" = cosmetic.

DOCUMENT:
──────────────────────────────────
{document_text}
──────────────────────────────────

OUTPUT as valid JSON only — no markdown fences, no commentary:
{{"findings": [
    {{"finding_id": "H1", "type": "character_status|object|count|timeline|injury|identity",
      "severity": "critical|high|medium|low", "scenes": ["<scene numbers or KEY_SCENE>"],
      "description": "<one sentence>", "evidence_quotes": ["<exact quote>", "<exact quote>"]}}
  ],
  "scenes_checked": <int>}}"""


SYSTEM_DOC_JUDGE = """You are the verifying continuity judge for a film treatment. You receive:
(1) a merged continuity fact database extracted scene-by-scene,
(2) candidate contradictions (from deterministic rules and an independent
    holistic pass), and
(3) the full document text as ground truth.

TASKS:
A. For EACH candidate: verify it against the full document text. Verdict
   "CONFIRMED" only if the contradiction is real in the text (quote the exact
   evidence); otherwise "REJECTED" with a one-line reason. Be strict: a candidate
   that has an in-text explanation (time passage, intentional repetition,
   clarified perspective) is REJECTED.
B. Scan the fact database for contradictions the candidates MISSED (character
   status, object provenance, counts, timeline, injuries, identity — including
   consistency between summary-level scenes and fully-realized scenes describing
   the same events, and between front matter and scenes). Verify each against the
   full text before reporting.

Do NOT report style or quality issues — only factual internal contradictions.

OUTPUT BUDGET — stay compact or the response will be truncated:
- At most 2 evidence_quotes per finding, each at most 20 words.
- One-sentence descriptions. Do NOT restate the fact database or the document.
- Report every CONFIRMED contradiction, but do not pad with speculative or
  cosmetic ones. Rejected candidates: id + a short reason only.

FACT DATABASE:
{fact_database}

CANDIDATES:
{candidates}

FULL DOCUMENT:
──────────────────────────────────
{document_text}
──────────────────────────────────

OUTPUT as valid JSON only — no markdown fences, no commentary:
{{"findings": [
    {{"finding_id": "F1", "type": "character_status|object|count|timeline|injury|identity",
      "severity": "critical|high|medium|low", "scenes": ["<scene numbers or KEY_SCENE>"],
      "description": "<one sentence>",
      "evidence_quotes": ["<exact quote>", "<exact quote>"],
      "origin": "candidate|judge_scan"}}
  ],
  "rejected": [{{"candidate_id": "<id>", "why": "<short reason>"}}]}}"""


# ─── Prompt builders ────────────────────────────────────────────────

def build_document_continuity_prompts(document_path: str) -> list:
    """Builds the stage-1 prompts: one extraction prompt per act, one for
    the key scene, plus one holistic full-document prompt.

    Returns list of {"label": str, "prompt": str}. The judge prompt is
    built separately via build_judge_prompt() after stage-1 results exist.
    """
    seg = segment_document(document_path)
    with open(document_path, encoding="utf-8") as f:
        full_text = f.read()

    prompts = []
    for act in seg["acts"]:
        label = f"extract_act_{act['act'].lower()}"
        prompts.append({
            "label": label,
            "prompt": SYSTEM_DOC_EXTRACT.format(
                characters_section=seg["characters_section"],
                segment_label=f"ACT {act['act']}",
                segment_text=act["text"],
            ),
        })
    if seg["key_scene"]:
        prompts.append({
            "label": "extract_key_scene",
            "prompt": SYSTEM_DOC_EXTRACT.format(
                characters_section=seg["characters_section"],
                segment_label="KEY_SCENE",
                segment_text=seg["key_scene"],
            ),
        })
    prompts.append({
        "label": "holistic",
        "prompt": SYSTEM_DOC_HOLISTIC.format(document_text=full_text),
    })
    return prompts


def build_judge_prompt(document_path: str, extract_results: list,
                       holistic_result: dict) -> str:
    """Builds the stage-3 judge prompt from merged facts + candidates."""
    with open(document_path, encoding="utf-8") as f:
        full_text = f.read()

    merged = merge_facts(extract_results)
    candidates = contradiction_candidates(merged)
    for i, f_ in enumerate(holistic_result.get("findings", []), 1):
        candidates.append({
            "candidate_id": f_.get("finding_id", f"H{i}"),
            "rule": "holistic_pass",
            "type": f_.get("type", ""),
            "severity": f_.get("severity", "medium"),
            "scenes": f_.get("scenes", []),
            "description": f_.get("description", ""),
            "evidence_quotes": f_.get("evidence_quotes", []),
        })

    return SYSTEM_DOC_JUDGE.format(
        fact_database=json.dumps(merged, ensure_ascii=False, indent=1),
        candidates=json.dumps(candidates, ensure_ascii=False, indent=1),
        document_text=full_text,
    )


# ─── Pure Python: merge + deterministic contradiction rules ─────────

def merge_facts(extract_results: list) -> list:
    """Merge stage-1 extraction results into one scene-ordered fact list.

    Numbered scenes sort numerically; KEY_SCENE sorts last but is excluded
    from cross-scene ordering rules (it is a parallel full realization of
    treatment events, not a sequential continuation).
    """
    scenes = []
    for res in extract_results:
        if not res:
            continue
        scenes.extend(res.get("scene_facts", []))

    def _order(sf):
        sid = str(sf.get("scene", ""))
        return (1, 0) if sid == "KEY_SCENE" else (0, int(sid)) if sid.isdigit() else (2, 0)

    return sorted(scenes, key=_order)


def _norm_tokens(text: str) -> set:
    return {w for w in re.findall(r"[a-z']+", str(text).lower()) if len(w) >= 3}


def _tok_overlap(a: str, b: str) -> float:
    ta, tb = _norm_tokens(a), _norm_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def contradiction_candidates(merged: list) -> list:
    """Deterministic contradiction rules over the merged fact database.

    R1 death-then-active: a character with a death event acts/speaks later
        (same scene at a later event position, or active in a later
        numbered scene). KEY_SCENE participates intra-scene only.
    R2 count mismatch: near-identical count subjects with different values.
    R3 object without establishment: used/transferred with no earlier
        introduction (low confidence — judge filters).
    """
    candidates = []
    cid = 0

    def _add(rule, ctype, severity, scenes, description, quotes):
        nonlocal cid
        cid += 1
        candidates.append({
            "candidate_id": f"R{cid}",
            "rule": rule,
            "type": ctype,
            "severity": severity,
            "scenes": [str(s) for s in scenes],
            "description": description,
            "evidence_quotes": quotes,
        })

    # R1 — death-then-active
    deaths = []  # (scene_id, is_key, order_idx, position, who, quote)
    for idx, sf in enumerate(merged):
        sid = str(sf.get("scene", ""))
        for ev in sf.get("ordered_events", []):
            if ev.get("event") == "death":
                deaths.append((sid, sid == "KEY_SCENE", idx,
                               ev.get("position", 0), ev.get("who", ""),
                               ev.get("quote", "")))
    for sid, is_key, idx, pos, who, quote in deaths:
        if not who or who.upper() == "GROUP":
            continue
        # intra-scene: later event by same character in same scene
        sf = merged[idx]
        for ev in sf.get("ordered_events", []):
            if (ev.get("who", "").lower() == who.lower()
                    and ev.get("position", 0) > pos
                    and ev.get("event") in ("speech", "physical_action")):
                _add("death_then_active_intra", "character_status", "critical",
                     [sid],
                     f"{who} has a death event but {ev.get('event')} occurs "
                     f"later in the same scene: {ev.get('detail', '')}",
                     [quote, ev.get("quote", "")])
        # cross-scene: active in a later numbered scene (skip KEY_SCENE both ways)
        if is_key:
            continue
        for later in merged[idx + 1:]:
            lsid = str(later.get("scene", ""))
            if lsid == "KEY_SCENE":
                continue
            actives = [a.lower() for a in later.get("characters_active", [])]
            if who.lower() in actives:
                _add("death_then_active_cross", "character_status", "critical",
                     [sid, lsid],
                     f"{who} dies in scene {sid} but is active in scene {lsid}",
                     [quote])

    # R2 — count mismatches
    counts = []  # (scene_id, what, value, quote)
    for sf in merged:
        sid = str(sf.get("scene", ""))
        for c in sf.get("counts", []):
            if isinstance(c.get("value"), (int, float)):
                counts.append((sid, c.get("what", ""), c["value"],
                               c.get("quote", "")))
    for i in range(len(counts)):
        for j in range(i + 1, len(counts)):
            s1, w1, v1, q1 = counts[i]
            s2, w2, v2, q2 = counts[j]
            if v1 != v2 and _tok_overlap(w1, w2) >= 0.5:
                _add("count_mismatch", "count", "medium", [s1, s2],
                     f"'{w1}' = {v1} (scene {s1}) vs '{w2}' = {v2} (scene {s2})",
                     [q1, q2])

    # R3 — object used/transferred without establishment.
    # Restricted to RECURRING props: an object appearing in only one scene
    # cannot have a provenance contradiction, so single-appearance props
    # (a pipe lit once, a ladle rung once) are ignored. Only objects that
    # recur across >=2 scenes are candidates — those are the ones whose
    # "where did this come from / who holds it" can actually conflict.
    all_objs = []  # (scene_id, object_name)
    for sf in merged:
        sid = str(sf.get("scene", ""))
        for obj in sf.get("objects", []):
            all_objs.append((sid, obj.get("object", "")))

    def _recurring(name: str) -> bool:
        scenes = {sid for sid, n in all_objs if _tok_overlap(name, n) >= 0.5}
        return len(scenes) >= 2

    introduced = []  # (order_idx, object_name)
    for idx, sf in enumerate(merged):
        sid = str(sf.get("scene", ""))
        for obj in sf.get("objects", []):
            name = obj.get("object", "")
            action = obj.get("action", "")
            if action == "introduced":
                introduced.append((idx, name))
            elif action in ("used", "transferred") and _recurring(name):
                if not any(ii <= idx and _tok_overlap(name, n) >= 0.5
                           for ii, n in introduced):
                    _add("object_no_establishment", "object", "low", [sid],
                         f"'{name}' is {action} in scene {sid} without prior "
                         f"introduction ({obj.get('detail', '')})",
                         [])
                    introduced.append((idx, name))  # flag once per object

    return candidates


# ─── Runner ─────────────────────────────────────────────────────────

def run_document_continuity_check(judge_result: dict,
                                  extract_results: list = None,
                                  holistic_result: dict = None,
                                  document_label: str = "",
                                  verbose: bool = True) -> dict:
    """Persists the document continuity check.

    Writes state["document_continuity_check"] (consumed by
    orchestrator.route_revision as source "document_continuity") plus a
    raw dump at state/_result_document_continuity.json. Additive only.
    """
    merged = merge_facts(extract_results or [])
    py_candidates = contradiction_candidates(merged) if merged else []

    findings = [
        f for f in judge_result.get("findings", [])
        if str(f.get("verdict", "CONFIRMED")).upper() != "REJECTED"
    ]

    report = {
        "meta": {
            "version": "1",
            "document": document_label,
            "checked_at": datetime.now().isoformat(),
            "segments_extracted": len(extract_results or []),
            "scenes_in_fact_db": len(merged),
            "python_candidates": len(py_candidates),
            "holistic_findings": len((holistic_result or {}).get("findings", [])),
            "rejected_by_judge": len(judge_result.get("rejected", [])),
            "detection_mode": "document-level",
        },
        "findings": findings,
        "python_candidates": py_candidates,
        "rejected": judge_result.get("rejected", []),
    }

    state = load_state()
    state["document_continuity_check"] = report
    save_state(state)

    os.makedirs("state", exist_ok=True)
    with open(os.path.join("state", "_result_document_continuity.json"),
              "w", encoding="utf-8") as f:
        json.dump({
            "extract_results": extract_results,
            "holistic_result": holistic_result,
            "judge_result": judge_result,
        }, f, ensure_ascii=False, indent=1)

    if verbose:
        print(f"\n{'=' * 60}")
        print("DOCUMENT CONTINUITY CHECK complete")
        print(f"  Document:          {document_label}")
        print(f"  Scenes in fact DB: {len(merged)}")
        print(f"  Python candidates: {len(py_candidates)}")
        print(f"  Confirmed findings: {len(findings)}")
        for f_ in findings:
            print(f"  • [{f_.get('severity', '?'):8s}] "
                  f"{f_.get('type', '?'):16s} "
                  f"scenes {','.join(f_.get('scenes', []))}: "
                  f"{f_.get('description', '')[:80]}")
        print(f"{'=' * 60}\n")

    return report
