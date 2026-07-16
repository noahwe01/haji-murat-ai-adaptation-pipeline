"""
Graph Query API — Pipeline-Zugriff auf den Character-Graph des Projekts.
=========================================================================

Wird von Story-Analyst, Character-Agent und Adaptation-Agent aufgerufen,
um Figuren-, Fusion- und Co-Occurrence-Informationen abzufragen, statt den
Volltext zu scannen. Erwartet eine vorverarbeitete `characters.json` unter
`<project>/graphify-out/characters.json` (siehe T1.3 Graphify-Präprozessor).

Projekt-Layout:
    <project>/
        config/projekt.yaml
        graphify-out/
            characters.json        ← diese Datei liest die API
            locations.json         (Session 2)
            plotlines.json         (Session 2)

Standard-Resolution: der Graph wird relativ zu `Path.cwd()` gesucht, analog
zum Config-Loader — das Framework liegt im Submodule, die Daten im Projekt.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


GRAPH_FILE = "characters.json"


def _resolve_graph_path(explicit: Optional[Path] = None) -> Path:
    """Finds characters.json. Project-layout (cwd/graphify-out/) takes precedence."""
    if explicit is not None:
        p = Path(explicit)
        return p if p.is_file() else p / GRAPH_FILE
    return Path.cwd() / "graphify-out" / GRAPH_FILE


@dataclass
class CharacterGraph:
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    fusion_candidates: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    _alias_index: Dict[str, str] = field(default_factory=dict)  # alias.lower() → canonical
    _node_by_canon: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # --------- construction ---------

    @classmethod
    def load(cls, graph_dir_or_file: Optional[Path] = None) -> "CharacterGraph":
        path = _resolve_graph_path(graph_dir_or_file)
        if not path.exists():
            raise FileNotFoundError(
                f"Character graph not found at {path}. "
                f"Run the Graphify preprocessor first (T1.3)."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        g = cls(
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            fusion_candidates=data.get("fusion_candidates", []),
            stats=data.get("stats", {}),
        )
        g._build_indexes()
        return g

    def _build_indexes(self) -> None:
        self._alias_index = {}
        self._node_by_canon = {}
        for n in self.nodes:
            canon = n["canonical_name"]
            self._node_by_canon[canon] = n
            self._alias_index[canon.lower()] = canon
            for alias in n.get("aliases", []):
                # Don't overwrite if alias is already tied to another canonical — first-come
                key = alias.strip().lower()
                if key and key not in self._alias_index:
                    self._alias_index[key] = canon

    # --------- lookup ---------

    def canonical_name(self, name_or_alias: str) -> Optional[str]:
        """Resolve any alias or approximate form to its canonical name."""
        if not name_or_alias:
            return None
        key = name_or_alias.strip().lower()
        return self._alias_index.get(key)

    def get_character(self, name_or_alias: str) -> Optional[Dict[str, Any]]:
        canon = self.canonical_name(name_or_alias)
        return self._node_by_canon.get(canon) if canon else None

    def characters_by_function(
        self, function: str, historical: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Return all characters with given narrative_function (and optional historical filter)."""
        out = [n for n in self.nodes if n.get("narrative_function") == function]
        if historical is not None:
            out = [n for n in out if n.get("historical") == historical]
        return out

    # --------- core queries (T1.3 API contract) ---------

    def query_characters_in_chunks(
        self, chunk_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """Characters appearing in any of the given chunks (chapter numbers).

        Sorted by dramatic_weight descending. Used by Story Analyst and
        Adaptation Agent to prune prompt context to the characters actually
        present in the scene being processed.
        """
        chunk_set = set(chunk_ids)
        out = [
            n for n in self.nodes
            if chunk_set.intersection(n.get("appearances", []))
        ]
        return sorted(out, key=lambda n: -n.get("dramatic_weight", 0))

    def query_cooccurrence(
        self, char_a: str, char_b: str
    ) -> Optional[Dict[str, Any]]:
        """Return edge-record for two characters if they share any scene.

        Accepts either canonical names or aliases.
        """
        a = self.canonical_name(char_a)
        b = self.canonical_name(char_b)
        if not a or not b:
            return None
        key = tuple(sorted([a, b]))
        for e in self.edges:
            if tuple(sorted([e["source"], e["target"]])) == key:
                return e
        return None

    def query_fusion_candidates(
        self, threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Fusion candidates at or above the confidence threshold.

        Sorted by confidence descending. Story Analyst uses this (when
        expansion.mode == 'novel_to_feature') to surface merge proposals
        during the Deep Analysis phase.
        """
        return [
            h for h in self.fusion_candidates
            if float(h.get("confidence", 0)) >= threshold
        ]

    # --------- neighborhood queries ---------

    def get_neighbors(
        self, name_or_alias: str, min_weight: int = 1
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Characters that share at least `min_weight` scenes with the given char.

        Returns list of (neighbor_node, edge_record) tuples, sorted by edge weight.
        """
        canon = self.canonical_name(name_or_alias)
        if not canon:
            return []
        out: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
        for e in self.edges:
            if e.get("weight", 0) < min_weight:
                continue
            if e["source"] == canon:
                other = self._node_by_canon.get(e["target"])
                if other:
                    out.append((other, e))
            elif e["target"] == canon:
                other = self._node_by_canon.get(e["source"])
                if other:
                    out.append((other, e))
        return sorted(out, key=lambda p: -p[1].get("weight", 0))

    # --------- adaptation helpers ---------

    def cuttable_characters(
        self, max_weight: float = 3.0, exclude_historical: bool = True
    ) -> List[Dict[str, Any]]:
        """Characters that are candidates for *cutting* in adaptation.

        Default: dramatic weight < 3.0 and not historical figures.
        Historical figures are cut-sensitive because they carry factual weight.
        """
        out = []
        for n in self.nodes:
            if n.get("dramatic_weight", 0) >= max_weight:
                continue
            if exclude_historical and n.get("historical"):
                continue
            out.append(n)
        return sorted(out, key=lambda n: n.get("dramatic_weight", 0))

    def summary(self) -> str:
        """One-line status for logs and handoffs."""
        return (
            f"CharacterGraph: {len(self.nodes)} chars "
            f"({self.stats.get('historical_figures', '?')} historical), "
            f"{len(self.edges)} co-appearance edges, "
            f"{len(self.fusion_candidates)} fusion candidates "
            f"({self.stats.get('high_confidence_fusions', '?')} ≥0.8)"
        )


# --------- convenience module-level API ---------

_CACHED: Optional[CharacterGraph] = None


def load_character_graph(path: Optional[Path] = None) -> CharacterGraph:
    """Load (and cache) the character graph from the current project.

    The cache is per-process; re-call with an explicit path to force reload.
    """
    global _CACHED
    if path is not None or _CACHED is None:
        _CACHED = CharacterGraph.load(path)
    return _CACHED


def query_characters_in_chunks(chunk_ids: List[int]) -> List[Dict[str, Any]]:
    return load_character_graph().query_characters_in_chunks(chunk_ids)


def query_cooccurrence(char_a: str, char_b: str) -> Optional[Dict[str, Any]]:
    return load_character_graph().query_cooccurrence(char_a, char_b)


def query_fusion_candidates(threshold: float = 0.7) -> List[Dict[str, Any]]:
    return load_character_graph().query_fusion_candidates(threshold)


# =============================================================================
# LocationGraph
# =============================================================================

LOCATIONS_FILE = "locations.json"


def _resolve_locations_path(explicit: Optional[Path] = None) -> Path:
    if explicit is not None:
        p = Path(explicit)
        return p if p.is_file() else p / LOCATIONS_FILE
    return Path.cwd() / "graphify-out" / LOCATIONS_FILE


@dataclass
class LocationGraph:
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "LocationGraph":
        p = _resolve_locations_path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"Locations graph not found at {p}. "
                f"Run build_location_graph.py first (T1.3 Session 2)."
            )
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(
            nodes=data.get("nodes", []),
            transitions=data.get("transitions", []),
            stats=data.get("stats", {}),
        )

    def by_type(self, t: str) -> List[Dict[str, Any]]:
        return [n for n in self.nodes if n.get("type") == t]

    def compressible(self) -> List[Dict[str, Any]]:
        return [n for n in self.nodes if n.get("compressible")]

    def top_cinematic(self, n: int = 10) -> List[Dict[str, Any]]:
        return sorted(self.nodes, key=lambda x: -x.get("cinematic_weight", 0))[:n]

    def summary(self) -> str:
        return (
            f"LocationGraph: {len(self.nodes)} locations, "
            f"{len(self.transitions)} transitions, "
            f"{self.stats.get('compressible_count', '?')} compressible"
        )


# =============================================================================
# PlotlineGraph
# =============================================================================

PLOTLINES_FILE = "plotlines.json"


def _resolve_plotlines_path(explicit: Optional[Path] = None) -> Path:
    if explicit is not None:
        p = Path(explicit)
        return p if p.is_file() else p / PLOTLINES_FILE
    return Path.cwd() / "graphify-out" / PLOTLINES_FILE


@dataclass
class PlotlineGraph:
    threads: List[Dict[str, Any]] = field(default_factory=list)
    fusion_edges: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "PlotlineGraph":
        p = _resolve_plotlines_path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"Plotlines graph not found at {p}. "
                f"Run build_plotline_graph.py first (T1.3 Session 2)."
            )
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(
            threads=data.get("threads", []),
            fusion_edges=data.get("fusion_edges", []),
            stats=data.get("stats", {}),
        )

    def by_type(self, t: str) -> List[Dict[str, Any]]:
        return [x for x in self.threads if x.get("type") == t]

    def main_threads(self) -> List[Dict[str, Any]]:
        return self.by_type("main")

    def cuttable(self) -> List[Dict[str, Any]]:
        return [x for x in self.threads if x.get("cuttable_for_feature")]

    def non_cuttable(self) -> List[Dict[str, Any]]:
        return [x for x in self.threads if not x.get("cuttable_for_feature")]

    def threads_in_chapters(self, chapters: List[int]) -> List[Dict[str, Any]]:
        s = set(chapters)
        return [x for x in self.threads if s.intersection(x.get("chapters_active", []))]

    def summary(self) -> str:
        return (
            f"PlotlineGraph: {len(self.threads)} threads, "
            f"{self.stats.get('cuttable_count', '?')} cuttable, "
            f"{len(self.fusion_edges)} fusion edges"
        )


# ---------- Module-level convenience ----------

_LOC_CACHED: Optional[LocationGraph] = None
_PLOT_CACHED: Optional[PlotlineGraph] = None


def load_location_graph(path: Optional[Path] = None) -> LocationGraph:
    global _LOC_CACHED
    if path is not None or _LOC_CACHED is None:
        _LOC_CACHED = LocationGraph.load(path)
    return _LOC_CACHED


def load_plotline_graph(path: Optional[Path] = None) -> PlotlineGraph:
    global _PLOT_CACHED
    if path is not None or _PLOT_CACHED is None:
        _PLOT_CACHED = PlotlineGraph.load(path)
    return _PLOT_CACHED


if __name__ == "__main__":
    # Smoke-test the API if invoked directly from a project directory.
    g = load_character_graph()
    print(g.summary())
    print()
    print("Protagonist(s):", [n["canonical_name"] for n in g.characters_by_function("protagonist")])
    print("Top fusion candidates (≥0.85):")
    for h in g.query_fusion_candidates(0.85):
        print(f"  [{h['confidence']:.2f}] {' + '.join(h['characters'])}: {h['reason'][:80]}")
    print()
    try:
        lg = load_location_graph()
        print(lg.summary())
    except FileNotFoundError as e:
        print(f"(locations: {e})")
    try:
        pg = load_plotline_graph()
        print(pg.summary())
    except FileNotFoundError as e:
        print(f"(plotlines: {e})")
