"""
Plotline-Graph Merger (T1.3 Session 2).
=======================================
Reads the 5 agent extractions in `custom/_plotlines_agent_{1..5}.json`
and stitches plotline threads across chapter ranges. Unlike locations,
the same thread (e.g. "hm_defection", "butler_arc") appears in multiple
agents' outputs — we must merge them into one arc with a full timeline.

Outputs:
  - plotlines.json     (threads + stats + fusion suggestions)
  - plotlines.html     (Gantt-style timeline viz)
  - PLOTLINES_REPORT.md
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

HERE = Path(__file__).resolve().parent
CUSTOM = HERE / "custom"
AGENT_FILES = [CUSTOM / f"_plotlines_agent_{i}.json" for i in range(1, 6)]
OUT_JSON = HERE / "plotlines.json"
OUT_HTML = HERE / "plotlines.html"
OUT_MD = HERE / "PLOTLINES_REPORT.md"


# ─── MATCHING HELPERS ─────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (s or "").strip().lower()).strip("_")


def _tokens(s: str) -> Set[str]:
    """Short content tokens from a thread name (skip stopwords)."""
    STOP = {
        "the", "a", "an", "of", "and", "or", "in", "on", "to", "with",
        "for", "is", "as", "at", "by", "s", "his", "her", "its",
        "story", "arc", "plotline", "thread", "narrative",
    }
    return {w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in STOP}


TYPE_ALIASES = {
    "main_plot": "main", "main_plot_driver": "main",
    "political_military": "political_framing",
    "political_institutional": "political_framing",
    "political_institutional_arc": "political_framing",
    "political_arc": "political_framing",
    "antagonist_arc": "character_arc",
    "antagonist_arc_minor": "character_arc",
    "character_arc_minor": "character_arc",
    "character_arc_micro": "character_arc",
    "character_ensemble_arc": "character_arc",
    "psychological_arc": "character_arc",
    "thematic_microarc": "theme_micro_arc",
    "thematic_arc": "theme_micro_arc",
    "thematic_motif": "theme_micro_arc",
    "social_subplot": "subplot",
    "plot_device": "subplot",
}


def normalize_type(raw: str) -> str:
    if not raw:
        return "subplot"
    return TYPE_ALIASES.get(raw, raw)


def _primary_char(node: Dict) -> str:
    chars = [c.strip().lower() for c in node.get("characters_involved", []) if c.strip()]
    return chars[0] if chars else ""


def _similarity(a: Dict, b: Dict) -> float:
    """Symmetric similarity of two thread dicts, 0..1."""
    # exact slug match → 1.0
    if _norm(a["thread_id_suggestion"]) == _norm(b["thread_id_suggestion"]):
        return 1.0

    type_a = normalize_type(a.get("type", "subplot"))
    type_b = normalize_type(b.get("type", "subplot"))

    # Main threads sharing a primary character → force merge
    if type_a == "main" and type_b == "main":
        if _primary_char(a) == _primary_char(b) and _primary_char(a):
            return 0.95

    # name token overlap
    name_a, name_b = _tokens(a.get("name", "")), _tokens(b.get("name", ""))
    name_sim = len(name_a & name_b) / max(1, len(name_a | name_b))

    # character overlap
    chars_a = {c.strip().lower() for c in a.get("characters_involved", [])}
    chars_b = {c.strip().lower() for c in b.get("characters_involved", [])}
    if chars_a and chars_b:
        char_sim = len(chars_a & chars_b) / max(1, len(chars_a | chars_b))
    else:
        char_sim = 0.0

    # Character_arc with same primary character + high name overlap → merge
    if type_a == "character_arc" and type_b == "character_arc":
        if _primary_char(a) == _primary_char(b) and _primary_char(a) and name_sim >= 0.25:
            return 0.85

    # thistle / thematic anchors: same type + name tokens overlap → merge
    if type_a == "theme_micro_arc" and type_b == "theme_micro_arc" and name_sim >= 0.3:
        return 0.8

    # type agreement bonus
    type_match = 0.1 if type_a == type_b else 0.0

    return 0.55 * name_sim + 0.35 * char_sim + type_match


MATCH_THRESHOLD = 0.50


# ─── MERGE ─────────────────────────────────────────────────────────────────────

STATUS_ORDER = {
    "introduced": 1, "developed": 2, "paused": 2,
    "climaxed": 3, "resolved": 4, "closed_in_range": 4,
}


def _merge_threads(threads: List[Dict]) -> Dict:
    """Combine N agent-observations of the same thread into one arc."""
    threads = sorted(threads, key=lambda t: min(t.get("chapters_active", [0]) or [0]))

    thread_id = threads[0]["thread_id_suggestion"]
    # Prefer the shortest canonical thread_id
    for t in threads:
        if len(_norm(t["thread_id_suggestion"])) < len(_norm(thread_id)):
            thread_id = t["thread_id_suggestion"]

    name = max((t.get("name", "") for t in threads), key=len)

    all_chapters = sorted({c for t in threads for c in t.get("chapters_active", [])})
    all_characters = sorted({c for t in threads for c in t.get("characters_involved", [])})

    # Timeline of per-range observations
    timeline = []
    for t in threads:
        if not t.get("chapters_active"):
            continue
        timeline.append({
            "chapters": sorted(t["chapters_active"]),
            "status": t.get("status_in_range", "developed"),
            "description": t.get("description", ""),
            "dramatic_function": t.get("dramatic_function", ""),
            "source_range": t.get("chapter_span", []),
        })

    # Final status: highest in STATUS_ORDER across timeline
    final_status = max(
        (obs["status"] for obs in timeline),
        key=lambda s: STATUS_ORDER.get(s, 0),
        default="introduced",
    )

    # type: take most frequent, normalized
    type_counts = defaultdict(int)
    for t in threads:
        type_counts[normalize_type(t.get("type", "subplot"))] += 1
    thread_type = max(type_counts.items(), key=lambda x: x[1])[0]

    # Fusion candidates: union of all
    fusion = set()
    for t in threads:
        for f in (t.get("fusion_candidate_with") or []):
            if f:
                fusion.add(f)

    # cuttable: only if ALL sub-observations agree it's cuttable
    cuttable_votes = [t.get("cuttable_for_feature", False) for t in threads]
    cuttable = all(cuttable_votes) if cuttable_votes else False

    return {
        "thread_id": _norm(thread_id),
        "name": name,
        "type": thread_type,
        "characters_involved": all_characters,
        "chapters_active": all_chapters,
        "span": [all_chapters[0], all_chapters[-1]] if all_chapters else [],
        "reach": len(all_chapters),
        "final_status": final_status,
        "timeline": timeline,
        "cuttable_for_feature": cuttable,
        "fusion_candidate_with": sorted(fusion),
        "description_concat": " | ".join(obs["description"] for obs in timeline),
    }


def stitch(raw: List[Dict]) -> List[Dict]:
    groups: List[List[Dict]] = []
    for node in raw:
        hit = None
        for i, grp in enumerate(groups):
            if any(_similarity(node, g) >= MATCH_THRESHOLD for g in grp):
                hit = i
                break
        if hit is not None:
            groups[hit].append(node)
        else:
            groups.append([node])
    return [_merge_threads(g) for g in groups]


# ─── FUSION EDGES ─────────────────────────────────────────────────────────────

def resolve_fusion_edges(threads: List[Dict]) -> List[Dict]:
    """Expand raw fusion_candidate_with strings into resolved thread_id pairs."""
    by_id = {t["thread_id"]: t for t in threads}
    by_name_token = defaultdict(list)
    for t in threads:
        for tok in _tokens(t.get("name", "")):
            by_name_token[tok].append(t["thread_id"])

    edges = []
    seen = set()
    for t in threads:
        for raw in t.get("fusion_candidate_with", []) or []:
            rnorm = _norm(raw)
            # direct slug match
            target = by_id.get(rnorm)
            if not target:
                # token-based fallback
                raw_tokens = _tokens(raw.replace("_", " "))
                matches = defaultdict(int)
                for tok in raw_tokens:
                    for tid in by_name_token.get(tok, []):
                        matches[tid] += 1
                if matches:
                    best = max(matches.items(), key=lambda x: x[1])[0]
                    target = by_id.get(best)
            if not target or target["thread_id"] == t["thread_id"]:
                continue
            pair = tuple(sorted([t["thread_id"], target["thread_id"]]))
            if pair in seen:
                continue
            seen.add(pair)
            edges.append({"a": pair[0], "b": pair[1]})
    return edges


# ─── STATS + REPORT ───────────────────────────────────────────────────────────

def compute_stats(threads: List[Dict], edges: List[Dict]) -> Dict:
    by_type = defaultdict(int)
    cuttable = 0
    main_reach = []
    for t in threads:
        by_type[t.get("type", "unknown")] += 1
        if t.get("cuttable_for_feature"):
            cuttable += 1
        if t.get("type") == "main":
            main_reach.append(t["reach"])
    return {
        "total_threads": len(threads),
        "by_type": dict(by_type),
        "cuttable_count": cuttable,
        "non_cuttable_count": len(threads) - cuttable,
        "fusion_edge_count": len(edges),
        "main_thread_reach": main_reach,
    }


def build_html(threads: List[Dict]) -> str:
    type_colors = {
        "main": "#c0392b", "subplot": "#2980b9", "character_arc": "#27ae60",
        "theme_micro_arc": "#8e44ad", "authorial_digression": "#7f8c8d",
        "political_framing": "#d35400", "flashback": "#16a085",
        "epistolary": "#e67e22",
    }
    threads_sorted = sorted(
        threads,
        key=lambda t: (
            {"main": 0, "subplot": 1, "character_arc": 2, "political_framing": 3}.get(t.get("type"), 9),
            -t["reach"],
        ),
    )
    rows = []
    for idx, t in enumerate(threads_sorted):
        color = type_colors.get(t.get("type", "subplot"), "#95a5a6")
        chapters = t["chapters_active"]
        bars = []
        for ch in range(1, 26):
            active = ch in chapters
            bars.append(
                f'<td style="background:{color if active else "#2c2c2c"};'
                f'border:1px solid #1a1a1a;width:20px;height:14px;"></td>'
            )
        cuttable_marker = "✂️" if t.get("cuttable_for_feature") else ""
        rows.append(
            f"<tr><td style='padding:4px 10px;'>{t['name'][:55]} {cuttable_marker}</td>"
            f"<td style='font-size:11px;color:#999;padding:4px 10px'>{t.get('type','?')}</td>"
            f"<td style='font-size:11px;color:#999;padding:4px 10px'>{t.get('final_status','?')}</td>"
            + "".join(bars) + "</tr>"
        )
    header_cells = "".join(
        f'<th style="font-size:10px;color:#888;width:20px;padding:2px">{i}</th>'
        for i in range(1, 26)
    )
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Hadji Murat — Plotline Timeline</title>
<style>
  body {{ font-family: -apple-system, sans-serif; background:#1e1e1e; color:#eee; margin:0; padding:20px }}
  table {{ border-collapse: collapse; width: 100%; font-size: 12px }}
  th {{ border-bottom: 1px solid #444 }}
  tr:hover {{ background: #2a2a2a }}
  h2 {{ font-weight: 400 }}
  .legend {{ margin: 20px 0; font-size: 12px }}
  .legend span {{ display: inline-block; padding: 4px 10px; margin-right: 8px; border-radius: 3px }}
</style></head><body>
<h2>Hadji Murat — Plotline Timeline ({len(threads)} threads)</h2>
<div class="legend">
  <span style="background:#c0392b">main</span>
  <span style="background:#2980b9">subplot</span>
  <span style="background:#27ae60">character_arc</span>
  <span style="background:#8e44ad">theme_micro_arc</span>
  <span style="background:#7f8c8d">authorial_digression</span>
  <span style="background:#d35400">political_framing</span>
  <span style="background:#16a085">flashback</span>
  <span style="background:#e67e22">epistolary</span>
  ✂️ = cuttable
</div>
<table>
<thead><tr><th style='text-align:left;padding:4px 10px'>Thread</th>
<th style='text-align:left;padding:4px 10px'>Type</th>
<th style='text-align:left;padding:4px 10px'>Final</th>
{header_cells}</tr></thead>
<tbody>{''.join(rows)}</tbody>
</table></body></html>"""


def build_report(threads: List[Dict], edges: List[Dict], stats: Dict) -> str:
    main_threads = [t for t in threads if t.get("type") == "main"]
    cuttable = [t for t in threads if t.get("cuttable_for_feature")]
    non_cut = [t for t in threads if not t.get("cuttable_for_feature")]

    lines = [
        "# Hadji Murat — Plotlines Report",
        "",
        f"**Total threads:** {stats['total_threads']}  ",
        f"**Cuttable:** {stats['cuttable_count']} / {stats['total_threads']}  ",
        f"**Fusion edges:** {stats['fusion_edge_count']}  ",
        "",
        "## By type",
        "",
        "| Type | Count |",
        "|---|---|",
    ]
    for t, c in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {c} |")

    lines.extend(["", "## Main threads", ""])
    for t in sorted(main_threads, key=lambda x: -x["reach"]):
        lines.append(f"### {t['name']}  _(reach: {t['reach']} ch, span {t['span']}, status: {t['final_status']})_")
        lines.append(f"Characters: {', '.join(t['characters_involved'][:8])}")
        lines.append(f"\n{t['description_concat'][:400]}...")
        lines.append("")

    lines.extend(["", f"## Non-cuttable threads ({len(non_cut)})",
                  "_These must survive adaptation._", ""])
    for t in sorted(non_cut, key=lambda x: (x.get("type", ""), -x["reach"])):
        lines.append(f"- **{t['name']}** ({t.get('type','?')}, reach={t['reach']}) — {t['description_concat'][:110]}...")

    lines.extend(["", f"## Cuttable threads ({len(cuttable)})",
                  "_Compression candidates for 120-min feature._", ""])
    for t in sorted(cuttable, key=lambda x: x["reach"]):
        lines.append(f"- {t['name']} ({t.get('type','?')}, reach={t['reach']}, ch={t['chapters_active']})")

    if edges:
        lines.extend(["", f"## Fusion candidates ({len(edges)} edges)",
                      "_Thread-pairs that agents flagged as mergeable._", ""])
        for e in edges:
            lines.append(f"- `{e['a']}` + `{e['b']}`")

    return "\n".join(lines)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    raw: List[Dict] = []
    for f in AGENT_FILES:
        if not f.exists():
            print(f"WARNING: missing {f.name}")
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        for t in d.get("plotlines", []):
            t["_source_span"] = d.get("chapter_span", [])
            raw.append(t)

    print(f"Raw: {len(raw)} thread observations across 5 agents")
    threads = stitch(raw)
    print(f"After stitching: {len(threads)} unique threads")

    edges = resolve_fusion_edges(threads)
    print(f"Fusion edges: {len(edges)}")

    stats = compute_stats(threads, edges)

    payload = {
        "threads": sorted(threads, key=lambda t: (
            {"main": 0, "subplot": 1, "character_arc": 2, "political_framing": 3,
             "authorial_digression": 4, "theme_micro_arc": 5, "epistolary": 6,
             "flashback": 7}.get(t.get("type"), 9),
            -t["reach"],
        )),
        "fusion_edges": edges,
        "stats": stats,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"→ {OUT_JSON.name}")

    OUT_HTML.write_text(build_html(threads), encoding="utf-8")
    print(f"→ {OUT_HTML.name}")

    OUT_MD.write_text(build_report(threads, edges, stats), encoding="utf-8")
    print(f"→ {OUT_MD.name}")

    print("\nStats:")
    print(f"  Types: {stats['by_type']}")
    print(f"  Cuttable: {stats['cuttable_count']}/{stats['total_threads']}")


if __name__ == "__main__":
    main()
