"""
Build Character Graph for Hadji Murat
======================================
Merges 5 agent JSON outputs (_agent_1..5.json) into:
- characters.json       — full merged character graph (nodes + edges + metrics)
- characters.html       — interactive vis.js visualization
- CHARACTERS_REPORT.md  — human-readable report with fusion candidates ranked

Run: python3 build_character_graph.py
"""
import json
from pathlib import Path
from collections import defaultdict
from math import sqrt

ROOT = Path(__file__).resolve().parent
CUSTOM = ROOT / "custom"
AGENT_FILES = sorted(CUSTOM.glob("_agent_*.json"))

FUNCTION_RANK = {
    "protagonist": 5, "antagonist": 4, "foil": 3,
    "supporting": 2, "cameo": 1, "unnamed": 0,
}
DIALOGUE_RANK = {"high": 4, "medium": 3, "low": 2, "none": 1}


def load_agents():
    return [json.loads(p.read_text(encoding="utf-8")) for p in AGENT_FILES]


def normalize_name(s):
    return s.strip().replace("Hadji Murat", "Hadji Murad")


def build_alias_index(agents):
    """Build a reverse index: alias_string → canonical_name.
    Also detect cross-agent canonical name conflicts (e.g. Agent A says "Major Petrov",
    Agent B says "Ivan Matveich Petrov") via alias overlap.
    """
    alias_to_canon = {}
    canon_to_aliases = defaultdict(set)
    for a in agents:
        for c in a["characters"]:
            canon = normalize_name(c["canonical_name"])
            canon_to_aliases[canon].add(canon)
            for alias in c.get("aliases", []):
                canon_to_aliases[canon].add(alias.strip())

    # Reverse index
    for canon, aliases in canon_to_aliases.items():
        for a in aliases:
            alias_to_canon[a.lower()] = canon

    # Cross-agent fusion: merge ONLY when distinguishing overlap exists.
    # Prior bug: generic single-token aliases like "Marya", "Masha", "the princess"
    # collapsed three distinct Maryas (Vasilevna/Dmitrievna/Elizabeth Ksaverevna).
    # Rule: overlap must include at least one canonical-name match OR a ≥2-word alias
    # that is not a pure title-phrase.
    def _is_distinguishing(token: str, canon_a: str, canon_b: str) -> bool:
        t = token.strip()
        if not t:
            return False
        # Exact canonical match is always distinguishing
        if t.lower() == canon_a.lower() or t.lower() == canon_b.lower():
            return True
        # Multi-word alias that isn't a pure "the XYZ" title
        words = t.split()
        if len(words) < 2:
            return False
        if words[0].lower() in {"the", "a", "an", "his", "her"}:
            return False
        return True

    canon_keys = sorted(canon_to_aliases.keys(), key=lambda k: -len(canon_to_aliases[k]))
    merge_map = {c: c for c in canon_keys}
    for i, a in enumerate(canon_keys):
        for b in canon_keys[i + 1:]:
            if merge_map[b] != b:
                continue
            aliases_a = canon_to_aliases[a]
            aliases_b = canon_to_aliases[b]
            aliases_a_lower = {x.lower() for x in aliases_a}
            aliases_b_lower = {x.lower() for x in aliases_b}
            overlap_lower = aliases_a_lower & aliases_b_lower
            # Map overlap back to original tokens (use longest original form seen)
            def _original(token_lower, pool):
                matches = [x for x in pool if x.lower() == token_lower]
                return max(matches, key=len) if matches else token_lower
            distinguishing = [
                _original(t, aliases_a | aliases_b)
                for t in overlap_lower
                if _is_distinguishing(_original(t, aliases_a | aliases_b), a, b)
            ]
            if distinguishing:
                merge_map[b] = a
                canon_to_aliases[a] |= canon_to_aliases[b]

    final_canon_to_aliases = defaultdict(set)
    for c, target in merge_map.items():
        final_canon_to_aliases[target] |= canon_to_aliases[c]
    return merge_map, final_canon_to_aliases


def merge_characters(agents, merge_map):
    """Produce unified character records keyed by canonical_name."""
    chars = {}
    for a in agents:
        for c in a["characters"]:
            canon = normalize_name(c["canonical_name"])
            canon = merge_map.get(canon, canon)
            if canon not in chars:
                chars[canon] = {
                    "canonical_name": canon,
                    "aliases": set(c.get("aliases", [])),
                    "narrative_function": c.get("narrative_function", "cameo"),
                    "historical": bool(c.get("historical", False)),
                    "appearances": set(c.get("appearances", [])),
                    "dialogue_volume": c.get("dialogue_volume", "none"),
                    "descriptions": [c.get("description", "")],
                    "_source_agents": {a["agent_number"]},
                }
            else:
                rec = chars[canon]
                rec["aliases"] |= set(c.get("aliases", []))
                # Function: take highest rank
                cur_rank = FUNCTION_RANK.get(rec["narrative_function"], 0)
                new_rank = FUNCTION_RANK.get(c.get("narrative_function", "cameo"), 0)
                if new_rank > cur_rank:
                    rec["narrative_function"] = c["narrative_function"]
                rec["historical"] = rec["historical"] or bool(c.get("historical", False))
                rec["appearances"] |= set(c.get("appearances", []))
                # Dialogue: take highest
                cur_d = DIALOGUE_RANK.get(rec["dialogue_volume"], 0)
                new_d = DIALOGUE_RANK.get(c.get("dialogue_volume", "none"), 0)
                if new_d > cur_d:
                    rec["dialogue_volume"] = c["dialogue_volume"]
                rec["descriptions"].append(c.get("description", ""))
                rec["_source_agents"].add(a["agent_number"])
    # Freeze sets → lists
    for rec in chars.values():
        rec["aliases"] = sorted(rec["aliases"])
        rec["appearances"] = sorted(rec["appearances"])
        rec["_source_agents"] = sorted(rec["_source_agents"])
        # De-dup descriptions, join unique
        seen = set()
        uniq = []
        for d in rec["descriptions"]:
            if d and d not in seen:
                uniq.append(d)
                seen.add(d)
        rec["description"] = " | ".join(uniq)
        del rec["descriptions"]
    return chars


def merge_co_appearances(agents, merge_map):
    """Merge co-appearance edges. Key by sorted pair of canonical names."""
    edges = {}
    for a in agents:
        for co in a["co_appearances"]:
            chars_raw = co.get("chars", [])
            if len(chars_raw) != 2:
                continue
            c1 = normalize_name(chars_raw[0])
            c2 = normalize_name(chars_raw[1])
            c1 = merge_map.get(c1, c1)
            c2 = merge_map.get(c2, c2)
            if c1 == c2:
                continue
            key = tuple(sorted([c1, c2]))
            if key not in edges:
                edges[key] = {
                    "source": key[0],
                    "target": key[1],
                    "chapters": set(co.get("chapters", [])),
                    "interaction_types": {co.get("interaction_type", "incidental")},
                    "weight": len(co.get("chapters", [])),
                }
            else:
                edges[key]["chapters"] |= set(co.get("chapters", []))
                edges[key]["interaction_types"].add(
                    co.get("interaction_type", "incidental")
                )
                edges[key]["weight"] = len(edges[key]["chapters"])
    out = []
    for e in edges.values():
        e["chapters"] = sorted(e["chapters"])
        e["interaction_types"] = sorted(e["interaction_types"])
        e["weight"] = len(e["chapters"])
        out.append(e)
    return out


def merge_fusion_hints(agents, merge_map):
    """Collect all fusion hints. Dedup by sorted pair, keep max confidence."""
    hints = {}
    for a in agents:
        for h in a["fusion_hints"]:
            chars = h.get("characters", [])
            if len(chars) != 2:
                continue
            c1 = normalize_name(chars[0])
            c2 = normalize_name(chars[1])
            c1 = merge_map.get(c1, c1)
            c2 = merge_map.get(c2, c2)
            if c1 == c2:
                continue
            key = tuple(sorted([c1, c2]))
            conf = float(h.get("confidence", 0.0))
            reason = h.get("reason", "")
            if key not in hints or hints[key]["confidence"] < conf:
                hints[key] = {
                    "characters": list(key),
                    "confidence": conf,
                    "reason": reason,
                    "source_agent": a["agent_number"],
                }
    return sorted(hints.values(), key=lambda x: -x["confidence"])


def compute_metrics(chars, edges):
    """Augment chars with centrality, co_appearance_count, dramatic_weight."""
    degree = defaultdict(int)
    weighted_degree = defaultdict(float)
    for e in edges:
        degree[e["source"]] += 1
        degree[e["target"]] += 1
        weighted_degree[e["source"]] += e["weight"]
        weighted_degree[e["target"]] += e["weight"]

    for canon, rec in chars.items():
        rec["degree_centrality"] = degree[canon]
        rec["weighted_centrality"] = weighted_degree[canon]
        rec["appearance_count"] = len(rec["appearances"])
        # Dramatic weight: function * dialogue * sqrt(appearances)
        fr = FUNCTION_RANK.get(rec["narrative_function"], 1)
        dr = DIALOGUE_RANK.get(rec["dialogue_volume"], 1)
        rec["dramatic_weight"] = round(fr * dr * sqrt(max(1, rec["appearance_count"])), 2)


def build_output(chars, edges, hints):
    nodes = []
    for canon, rec in chars.items():
        nodes.append({
            "id": canon,
            "label": canon,
            "canonical_name": canon,
            "aliases": rec["aliases"],
            "narrative_function": rec["narrative_function"],
            "historical": rec["historical"],
            "appearances": rec["appearances"],
            "appearance_count": rec["appearance_count"],
            "dialogue_volume": rec["dialogue_volume"],
            "description": rec["description"],
            "degree_centrality": rec["degree_centrality"],
            "weighted_centrality": rec["weighted_centrality"],
            "dramatic_weight": rec["dramatic_weight"],
            "source_agents": rec["_source_agents"],
        })
    nodes.sort(key=lambda n: (-n["dramatic_weight"], n["canonical_name"]))
    return {
        "schema_version": "1.0",
        "source_text": "sources/hadji_murat.txt (Maude translation, Public Domain)",
        "chapters_total": 25,
        "extraction": {
            "method": "5-agent parallel dispatch, Claude-driven NER + relation extraction",
            "agents": len(AGENT_FILES),
            "date": "2026-04-23",
        },
        "nodes": nodes,
        "edges": edges,
        "fusion_candidates": hints,
        "stats": {
            "total_characters": len(nodes),
            "historical_figures": sum(1 for n in nodes if n["historical"]),
            "protagonist_antagonist_foil": sum(
                1 for n in nodes
                if n["narrative_function"] in ("protagonist", "antagonist", "foil")
            ),
            "cameo_characters": sum(1 for n in nodes if n["narrative_function"] == "cameo"),
            "fusion_candidate_pairs": len(hints),
            "high_confidence_fusions": sum(1 for h in hints if h["confidence"] >= 0.8),
        },
    }


def render_html(graph):
    """Self-contained HTML with vis.js network viz."""
    nodes_js = json.dumps([
        {
            "id": n["canonical_name"],
            "label": n["canonical_name"],
            "group": n["narrative_function"],
            "value": max(5, n["dramatic_weight"]),
            "title": (
                f"<b>{n['canonical_name']}</b><br>"
                f"Function: {n['narrative_function']}<br>"
                f"Appearances: {n['appearance_count']} chapters<br>"
                f"Dialogue: {n['dialogue_volume']}<br>"
                f"Dramatic weight: {n['dramatic_weight']}<br>"
                f"Historical: {n['historical']}<br>"
                f"{n['description'][:200]}"
            ),
            "shape": "dot" if not n["historical"] else "diamond",
        }
        for n in graph["nodes"]
    ])
    edges_js = json.dumps([
        {
            "from": e["source"],
            "to": e["target"],
            "value": e["weight"],
            "title": f"Chapters: {e['chapters']} · {', '.join(e['interaction_types'])}",
        }
        for e in graph["edges"]
    ])
    html = """<!doctype html>
<html><head>
<meta charset="utf-8">
<title>Hadji Murat — Character Graph</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
  body { margin: 0; font-family: -apple-system, system-ui, sans-serif; background: #111; color: #eee; }
  #net { width: 100vw; height: 100vh; }
  #legend { position: fixed; top: 12px; left: 12px; background: rgba(20,20,20,0.9);
            padding: 10px 14px; border-radius: 6px; font-size: 13px; border: 1px solid #333; }
  .sw { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; vertical-align:middle; }
  h3 { margin: 0 0 6px 0; font-size: 13px; font-weight: 600; }
</style>
</head>
<body>
<div id="legend">
  <h3>Character Graph — Hadji Murat (25 chapters)</h3>
  <div><span class="sw" style="background:#e57373"></span>protagonist</div>
  <div><span class="sw" style="background:#64b5f6"></span>antagonist</div>
  <div><span class="sw" style="background:#ffb74d"></span>foil</div>
  <div><span class="sw" style="background:#81c784"></span>supporting</div>
  <div><span class="sw" style="background:#9e9e9e"></span>cameo</div>
  <div style="margin-top:6px; font-size:11px; color:#aaa;">Node size = dramatic weight · Edge width = co-appearance count · Diamond = historical figure</div>
</div>
<div id="net"></div>
<script>
const nodes = new vis.DataSet(__NODES__);
const edges = new vis.DataSet(__EDGES__);
const opts = {
  nodes: { font: { color: '#eee', size: 14 }, borderWidth: 1 },
  edges: { color: { color: '#555', highlight: '#fff' }, smooth: { type: 'continuous' } },
  groups: {
    protagonist: { color: { background: '#e57373', border: '#c62828' } },
    antagonist:  { color: { background: '#64b5f6', border: '#1976d2' } },
    foil:        { color: { background: '#ffb74d', border: '#e65100' } },
    supporting:  { color: { background: '#81c784', border: '#388e3c' } },
    cameo:       { color: { background: '#9e9e9e', border: '#616161' } },
  },
  physics: { barnesHut: { gravitationalConstant: -8000, springLength: 150 }, stabilization: { iterations: 250 } },
  interaction: { hover: true, tooltipDelay: 180 },
};
new vis.Network(document.getElementById('net'), { nodes, edges }, opts);
</script>
</body></html>
"""
    return html.replace("__NODES__", nodes_js).replace("__EDGES__", edges_js)


def render_report(graph):
    lines = ["# Hadji Murat — Character Graph Report", ""]
    lines.append(f"*Source:* Tolstoy, \"Hadji Murat\" (Maude translation, 25 chapters, 46,290 words)")
    lines.append(f"*Method:* 5-agent parallel character extraction (chapters 1-5, 6-10, 11-15, 16-20, 21-25)")
    lines.append(f"*Date:* 2026-04-23")
    lines.append("")
    s = graph["stats"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total characters (deduplicated): **{s['total_characters']}**")
    lines.append(f"- Historical figures: {s['historical_figures']}")
    lines.append(f"- Principal roles (prot/ant/foil): {s['protagonist_antagonist_foil']}")
    lines.append(f"- Cameo roles: {s['cameo_characters']}")
    lines.append(f"- Co-appearance edges: {len(graph['edges'])}")
    lines.append(f"- Fusion candidate pairs identified: {s['fusion_candidate_pairs']}")
    lines.append(f"- High-confidence (≥0.8) fusion pairs: {s['high_confidence_fusions']}")
    lines.append("")

    lines.append("## Fusion Candidates (ranked by confidence)")
    lines.append("")
    lines.append("| # | Characters | Confidence | Reason |")
    lines.append("|---|---|---|---|")
    for i, h in enumerate(graph["fusion_candidates"], 1):
        chars = " + ".join(h["characters"])
        lines.append(f"| {i} | {chars} | {h['confidence']:.2f} | {h['reason']} |")
    lines.append("")

    lines.append("## Top-20 Characters by Dramatic Weight")
    lines.append("")
    lines.append("| # | Character | Function | Chapters | Dialog | Weight | Historical |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, n in enumerate(graph["nodes"][:20], 1):
        lines.append(
            f"| {i} | {n['canonical_name']} | {n['narrative_function']} | "
            f"{n['appearance_count']} | {n['dialogue_volume']} | "
            f"{n['dramatic_weight']} | {'✓' if n['historical'] else ''} |"
        )
    lines.append("")

    lines.append("## Low-Weight Candidates for Cut (weight < 3.0, non-historical)")
    lines.append("")
    low = [n for n in graph["nodes"]
           if n["dramatic_weight"] < 3.0 and not n["historical"]]
    for n in low[:25]:
        lines.append(
            f"- **{n['canonical_name']}** "
            f"({n['narrative_function']}, {n['appearance_count']} ch, "
            f"weight {n['dramatic_weight']}) — {n['description'][:120]}"
        )
    lines.append("")

    lines.append("## Centrality Leaders (most connected)")
    lines.append("")
    sorted_by_cent = sorted(graph["nodes"], key=lambda n: -n["weighted_centrality"])
    for n in sorted_by_cent[:10]:
        lines.append(
            f"- **{n['canonical_name']}**: degree={n['degree_centrality']}, "
            f"weighted={n['weighted_centrality']:.0f}"
        )
    lines.append("")

    lines.append("## Files Generated")
    lines.append("- `characters.json` — full graph data (nodes + edges + fusion candidates + stats)")
    lines.append("- `characters.html` — interactive vis.js visualization")
    lines.append("- `CHARACTERS_REPORT.md` — this file")
    lines.append("")
    return "\n".join(lines)


def main():
    agents = load_agents()
    merge_map, canon_to_aliases = build_alias_index(agents)
    chars = merge_characters(agents, merge_map)
    edges = merge_co_appearances(agents, merge_map)
    hints = merge_fusion_hints(agents, merge_map)
    compute_metrics(chars, edges)
    graph = build_output(chars, edges, hints)

    # Outputs
    (ROOT / "characters.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (ROOT / "characters.html").write_text(render_html(graph), encoding="utf-8")
    (ROOT / "CHARACTERS_REPORT.md").write_text(render_report(graph), encoding="utf-8")

    print(f"Merged: {len(graph['nodes'])} characters, "
          f"{len(graph['edges'])} edges, "
          f"{len(graph['fusion_candidates'])} fusion candidates")
    print(f"  characters.json        {(ROOT / 'characters.json').stat().st_size:,} bytes")
    print(f"  characters.html        {(ROOT / 'characters.html').stat().st_size:,} bytes")
    print(f"  CHARACTERS_REPORT.md   {(ROOT / 'CHARACTERS_REPORT.md').stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
