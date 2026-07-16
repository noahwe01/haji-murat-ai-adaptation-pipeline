"""
Schema-Cap-Validator (Q1.5).
Hard-cut on maxItems / maxLength loaded from schemas/*.schema.json.
Token-Sinker für Phase 1, 5, 9.5 outputs. report-only Mode optional.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = FRAMEWORK_ROOT / "schemas"

_SCHEMA_CACHE: dict[str, dict] = {}


def load_schema(name: str) -> dict:
    """Load schemas/<name>.schema.json. Cached."""
    if name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[name]
    path = SCHEMAS_DIR / f"{name}.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"schema not found: {path}")
    schema = json.loads(path.read_text(encoding="utf-8"))
    _SCHEMA_CACHE[name] = schema
    return schema


def _trim_on_word(text: str, limit: int, marker: str = "…") -> str:
    """Trim to <= limit on the last whitespace; fall back to hard cut."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    space = cut.rfind(" ")
    if space >= int(limit * 0.6):
        cut = cut[:space]
    return cut.rstrip(" ,;:—-") + marker


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _apply_property(
    obj: dict,
    key: str,
    spec: dict,
    findings: list,
    *,
    path: str,
    mode: str,
) -> None:
    """Apply a single property's caps. Mutates obj in place when mode='hard'."""
    if key not in obj:
        return
    val = obj[key]

    max_len = spec.get("maxLength")
    max_items = spec.get("maxItems")
    item_spec = spec.get("items") or {}
    item_max_len = item_spec.get("maxLength")

    full_path = f"{path}.{key}" if path else key

    if isinstance(val, str) and max_len is not None and len(val) > max_len:
        finding = {
            "field": full_path,
            "kind": "maxLength",
            "original": len(val),
            "cap": max_len,
            "timestamp": _now_iso(),
        }
        findings.append(finding)
        if mode == "hard":
            obj[key] = _trim_on_word(val, max_len)

    if isinstance(val, list):
        if max_items is not None and len(val) > max_items:
            finding = {
                "field": full_path,
                "kind": "maxItems",
                "original": len(val),
                "cap": max_items,
                "timestamp": _now_iso(),
            }
            findings.append(finding)
            if mode == "hard":
                obj[key] = val[:max_items]
                val = obj[key]

        if item_max_len is not None:
            for i, item in enumerate(val):
                if isinstance(item, str) and len(item) > item_max_len:
                    finding = {
                        "field": f"{full_path}[{i}]",
                        "kind": "maxLength",
                        "original": len(item),
                        "cap": item_max_len,
                        "timestamp": _now_iso(),
                    }
                    findings.append(finding)
                    if mode == "hard":
                        val[i] = _trim_on_word(item, item_max_len)


def apply_caps(
    data: dict,
    schema_name: str,
    *,
    mode: str = "hard",
    sub_path: str | None = None,
) -> list[dict]:
    """
    Apply caps from schemas/<schema_name>.schema.json to `data` in-place (mode='hard')
    or report-only (mode='report'). Returns list of findings.

    sub_path lets you target a sub-tree of the schema (e.g. 'pacing_analysis' inside
    quality_gate.schema.json).
    """
    if mode not in ("hard", "report"):
        raise ValueError(f"mode must be 'hard' or 'report', got {mode!r}")
    if not isinstance(data, dict):
        return []

    schema = load_schema(schema_name)
    props = schema.get("properties") or {}

    if sub_path:
        sub_spec = props.get(sub_path) or {}
        props = sub_spec.get("properties") or {}
        path_prefix = sub_path
        data = data.get(sub_path) if isinstance(data, dict) else None
        if not isinstance(data, dict):
            return []
    else:
        path_prefix = ""

    findings: list[dict] = []
    for key, spec in props.items():
        if not isinstance(spec, dict):
            continue
        # Drill into nested object spec
        if spec.get("type") == "object" and "properties" in spec:
            nested = data.get(key)
            if isinstance(nested, dict):
                for nk, nspec in spec["properties"].items():
                    _apply_property(
                        nested, nk, nspec, findings,
                        path=f"{path_prefix}.{key}" if path_prefix else key,
                        mode=mode,
                    )
        else:
            _apply_property(data, key, spec, findings, path=path_prefix, mode=mode)

    return findings


def record_findings(state: dict, agent: str, phase: str, findings: list[dict]) -> None:
    """Append schema-cap findings to state.meta.schema_caps_findings."""
    if not findings:
        return
    meta = state.setdefault("meta", {})
    log = meta.setdefault("schema_caps_findings", [])
    for f in findings:
        log.append({**f, "agent": agent, "phase": phase})
