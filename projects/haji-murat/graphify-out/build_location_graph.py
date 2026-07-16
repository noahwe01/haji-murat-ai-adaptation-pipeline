"""
Location-Graph Merger (T1.3 Session 2).
=======================================
Reads the 5 agent extractions in `custom/_locations_agent_{1..5}.json`,
dedupes by canonical-name + alias-overlap, accumulates appearances and
transitions, and writes:
  - locations.json  (nodes + transitions + stats)
  - locations.html  (vis.js network viz)
  - LOCATIONS_REPORT.md
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
CUSTOM = HERE / "custom"
AGENT_FILES = [CUSTOM / f"_locations_agent_{i}.json" for i in range(1, 6)]
OUT_JSON = HERE / "locations.json"
OUT_HTML = HERE / "locations.html"
OUT_MD = HERE / "LOCATIONS_REPORT.md"


# ─── DEDUP RULES ─────────────────────────────────────────────────────────────

GENERIC_ALIASES = {
    "the village", "the fort", "the city", "the palace", "the room",
    "the road", "the field", "the forest", "the mountain", "the ravine",
    "home", "the house",
}


def _norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


def _is_distinguishing_alias(alias: str) -> bool:
    """An alias is distinguishing if it's multi-word and NOT purely generic."""
    a = _norm(alias)
    if not a or a in GENERIC_ALIASES:
        return False
    if len(a.split()) < 2:
        return False
    # Don't trust "the X" if X alone is generic
    words = a.split()
    if words[0] in {"the", "a", "an"} and len(words) == 2 and words[1] in {
        "village", "fort", "city", "palace", "room", "road", "field",
        "forest", "mountain", "ravine", "house",
    }:
        return False
    return True


def _should_merge(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Merge iff canonical_name matches OR they share a distinguishing alias."""
    if _norm(a["canonical_name"]) == _norm(b["canonical_name"]):
        return True
    a_aliases = {_norm(x) for x in a.get("aliases", []) + [a["canonical_name"]]
                 if _is_distinguishing_alias(x)}
    b_aliases = {_norm(x) for x in b.get("aliases", []) + [b["canonical_name"]]
                 if _is_distinguishing_alias(x)}
    return bool(a_aliases & b_aliases)


def _merge_nodes(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Merge b into a, keeping canonical_name from the higher cinematic_weight."""
    if b.get("cinematic_weight", 0) > a.get("cinematic_weight", 0):
        canon = b["canonical_name"]
        desc = b.get("description_short") or a.get("description_short", "")
        dramatic = b.get("dramatic_use") or a.get("dramatic_use", "")
    else:
        canon = a["canonical_name"]
        desc = a.get("description_short") or b.get("description_short", "")
        dramatic = a.get("dramatic_use") or b.get("dramatic_use", "")

    aliases = sorted(set(
        a.get("aliases", []) + b.get("aliases", []) +
        [a["canonical_name"], b["canonical_name"]]
    ) - {canon})

    return {
        "canonical_name": canon,
        "type": a.get("type") or b.get("type", "unknown"),
        "aliases": aliases,
        "appearances": sorted(set(a.get("appearances", []) + b.get("appearances", []))),
        "description_short": desc,
        "dramatic_use": dramatic,
        "parent_location": a.get("parent_location") or b.get("parent_location"),
        "pov_holder": a.get("pov_holder") or b.get("pov_holder"),
        "cinematic_weight": max(a.get("cinematic_weight", 0), b.get("cinematic_weight", 0)),
        "compressible": a.get("compressible", True) and b.get("compressible", True),
    }


# ─── LOAD + MERGE ─────────────────────────────────────────────────────────────

def load_all() -> tuple[List[Dict], List[Dict]]:
    locs: List[Dict] = []
    transitions: List[Dict] = []
    for f in AGENT_FILES:
        if not f.exists():
            print(f"WARNING: missing {f.name}")
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        locs.extend(d.get("locations", []))
        transitions.extend(d.get("location_transitions", []))
    return locs, transitions


def dedupe(raw: List[Dict]) -> List[Dict]:
    merged: List[Dict] = []
    for node in raw:
        hit = None
        for i, existing in enumerate(merged):
            if _should_merge(existing, node):
                hit = i
                break
        if hit is not None:
            merged[hit] = _merge_nodes(merged[hit], node)
        else:
            merged.append(dict(node))
    return merged


def normalize_transitions(transitions: List[Dict], name_map: Dict[str, str]) -> List[Dict]:
    """Resolve transition endpoints to canonical names and dedupe."""
    seen = set()
    out = []
    for t in transitions:
        a = name_map.get(_norm(t.get("from", "")), t.get("from", ""))
        b = name_map.get(_norm(t.get("to", "")), t.get("to", ""))
        if not a or not b or a == b:
            continue
        key = (a, b, t.get("chapter"))
        if key in seen:
            continue
        seen.add(key)
        out.append({"from": a, "to": b, "chapter": t.get("chapter"), "mode": t.get("mode", "unknown")})
    return out


# ─── STATS + REPORT ───────────────────────────────────────────────────────────

def compute_stats(nodes: List[Dict], transitions: List[Dict]) -> Dict[str, Any]:
    by_type = defaultdict(int)
    compressible = 0
    for n in nodes:
        by_type[n.get("type", "unknown")] += 1
        if n.get("compressible"):
            compressible += 1
    weight_hist = defaultdict(int)
    for n in nodes:
        w = int(n.get("cinematic_weight", 0))
        weight_hist[w] += 1
    return {
        "total_locations": len(nodes),
        "by_type": dict(by_type),
        "compressible_count": compressible,
        "non_compressible_count": len(nodes) - compressible,
        "cinematic_weight_histogram": dict(sorted(weight_hist.items(), reverse=True)),
        "total_transitions": len(transitions),
    }


def build_html(nodes: List[Dict], transitions: List[Dict]) -> str:
    type_colors = {
        "village": "#8b4513", "fort": "#c0392b", "city": "#2c3e50",
        "interior": "#9b59b6", "battlefield": "#e74c3c",
        "wilderness": "#27ae60", "travel_route": "#7f8c8d",
        "abstract_region": "#95a5a6", "unknown": "#bdc3c7",
    }
    mode_colors = {
        "ride": "#d35400", "walk": "#16a085", "carriage": "#8e44ad",
        "ellipsis": "#7f8c8d", "flashback": "#3498db",
        "dispatch": "#e67e22", "unknown": "#95a5a6",
    }
    vis_nodes = []
    for n in nodes:
        weight = n.get("cinematic_weight", 3)
        vis_nodes.append({
            "id": n["canonical_name"],
            "label": n["canonical_name"],
            "title": f"{n['canonical_name']} ({n.get('type','?')})<br>weight={weight}<br>chapters={n.get('appearances',[])}<br>{n.get('description_short','')}",
            "color": type_colors.get(n.get("type", "unknown"), "#bdc3c7"),
            "size": 8 + weight * 2,
            "shape": "square" if n.get("type") in ("fort", "city") else ("triangle" if n.get("type") == "battlefield" else "dot"),
        })
    vis_edges = []
    for t in transitions:
        vis_edges.append({
            "from": t["from"], "to": t["to"],
            "color": mode_colors.get(t.get("mode", "unknown"), "#95a5a6"),
            "title": f"ch {t.get('chapter')} — {t.get('mode','?')}",
            "arrows": "to",
        })

    legend = "".join(
        f'<div style="margin:4px 0"><span style="display:inline-block;width:14px;height:14px;background:{c};margin-right:8px;border-radius:2px"></span>{t}</div>'
        for t, c in type_colors.items()
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Hadji Murat — Locations Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin:0; font-family: -apple-system, sans-serif; background:#1e1e1e; color:#eee }}
  #mynetwork {{ width: 100vw; height: 88vh; border: 1px solid #444; }}
  #legend {{ position: absolute; top:10px; right:10px; background:#2c2c2c; padding:12px; border-radius:6px; font-size:12px; z-index:10 }}
  h2 {{ margin: 10px 16px 4px; font-weight: 400 }}
  p {{ margin: 0 16px 8px; color:#aaa; font-size: 13px }}
</style></head><body>
<h2>Hadji Murat — Locations Graph</h2>
<p>{len(nodes)} locations · {len(transitions)} transitions · node size = cinematic_weight · colour = type</p>
<div id="mynetwork"></div>
<div id="legend"><b>Types</b>{legend}</div>
<script>
  const nodes = new vis.DataSet({json.dumps(vis_nodes)});
  const edges = new vis.DataSet({json.dumps(vis_edges)});
  const container = document.getElementById('mynetwork');
  const data = {{ nodes, edges }};
  const options = {{
    nodes: {{ font: {{ color: '#eee', size: 12 }} }},
    edges: {{ smooth: {{ type: 'continuous' }}, width: 1.5 }},
    physics: {{ solver: 'forceAtlas2Based', stabilization: {{ iterations: 120 }} }},
    interaction: {{ hover: true, tooltipDelay: 100 }},
  }};
  new vis.Network(container, data, options);
</script></body></html>"""


def build_report(nodes: List[Dict], transitions: List[Dict], stats: Dict) -> str:
    # Top cinematic weights
    top = sorted(nodes, key=lambda n: -n.get("cinematic_weight", 0))[:15]
    compressible = [n for n in nodes if n.get("compressible")]
    non_comp = [n for n in nodes if not n.get("compressible")]

    lines = [
        "# Hadji Murat — Locations Report",
        "",
        f"**Total locations:** {stats['total_locations']}  ",
        f"**Transitions:** {stats['total_transitions']}  ",
        f"**Compressible:** {stats['compressible_count']} / {stats['total_locations']}  ",
        "",
        "## By type",
        "",
        "| Type | Count |",
        "|---|---|",
    ]
    for t, c in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {c} |")
    lines.extend([
        "",
        "## Cinematic-weight distribution",
        "",
        "| Weight | Count |",
        "|---|---|",
    ])
    for w, c in stats["cinematic_weight_histogram"].items():
        lines.append(f"| {w} | {c} |")

    lines.extend(["", "## Top 15 by cinematic weight", "",
                  "| Location | Type | Weight | Chapters | Dramatic use |",
                  "|---|---|---|---|---|"])
    for n in top:
        chs = ",".join(str(c) for c in n.get("appearances", []))
        lines.append(f"| {n['canonical_name']} | {n.get('type','?')} | {n.get('cinematic_weight','?')} | {chs} | {n.get('dramatic_use','')[:70]} |")

    lines.extend(["", f"## Non-compressible anchors ({len(non_comp)})",
                  "_These MUST survive adaptation (historical cities, HQs, battlefield)._", ""])
    for n in sorted(non_comp, key=lambda x: -x.get("cinematic_weight", 0)):
        lines.append(f"- **{n['canonical_name']}** ({n.get('type','?')}) — {n.get('dramatic_use','')[:90]}")

    lines.extend(["", f"## Compression opportunities ({len(compressible)})",
                  "_Low-weight locations that can be fused, cut, or restaged._", ""])
    for n in sorted(compressible, key=lambda x: x.get("cinematic_weight", 0))[:25]:
        lines.append(f"- {n['canonical_name']} (weight={n.get('cinematic_weight','?')}, ch={n.get('appearances',[])})")

    return "\n".join(lines)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    raw_locs, raw_trans = load_all()
    print(f"Raw: {len(raw_locs)} locations, {len(raw_trans)} transitions")

    nodes = dedupe(raw_locs)
    print(f"After dedup: {len(nodes)} locations")

    # Build name map (alias → canonical) for transition normalization
    name_map: Dict[str, str] = {}
    for n in nodes:
        name_map[_norm(n["canonical_name"])] = n["canonical_name"]
        for a in n.get("aliases", []):
            na = _norm(a)
            if na and na not in name_map:
                name_map[na] = n["canonical_name"]

    transitions = normalize_transitions(raw_trans, name_map)
    print(f"After normalization + dedup: {len(transitions)} transitions")

    stats = compute_stats(nodes, transitions)

    payload = {
        "nodes": sorted(nodes, key=lambda n: -n.get("cinematic_weight", 0)),
        "transitions": transitions,
        "stats": stats,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"→ {OUT_JSON.name}")

    OUT_HTML.write_text(build_html(nodes, transitions), encoding="utf-8")
    print(f"→ {OUT_HTML.name}")

    OUT_MD.write_text(build_report(nodes, transitions, stats), encoding="utf-8")
    print(f"→ {OUT_MD.name}")

    print("\nStats:")
    print(f"  Types: {stats['by_type']}")
    print(f"  Compressible: {stats['compressible_count']}/{stats['total_locations']}")


if __name__ == "__main__":
    main()
