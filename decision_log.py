"""
DECISION LOG
============
Protocol every creative decision an agent makes, against the named
rules in adaptations-brain/adaptation_criteria.md.

Design contract:
- This log is WRITE-ONLY from the pipeline's point of view. It is
  NEVER loaded into agent context. It exists as an audit artifact
  for reproducibility analysis + human review.
- Storage: <project>/output/adaptation_log.json (relative to cwd).
  Chosen so the log sits next to the deliverables (screenplay,
  treatment) that the decisions produced.
- Agents emit a DECISIONS block at the end of their normal output;
  parse_decisions_block() extracts it, log_decision() appends to
  the file.
- Regex parsing is permissive: malformed entries fall back to a
  DEVIATION entry with the raw text preserved as justification.
  Hard-fail on format drift would silently drop decisions — worse
  than a sloppy log.

Format spec (enforced in agent prompts):

    DECISIONS:
    - TYPE object_id: reason → CRITERION: RULE-ID[, RULE-ID]
    - ...

Examples:

    DECISIONS:
    - FUSE Khan Mahoma → Bata: both guides, <4 scenes each → CF-01
    - CUT_SUBPLOT author_digression_thistle: repeats frame → SS-02, NF-08
    - REFOCAL Nikolaus-Hof: seen only through HM's letter → CF-08
    - DEVIATION scene_S007: both compression rules inconclusive → kept for tension arc
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


ADAPTATION_LOG_DIR = "output"
ADAPTATION_LOG_FILE = "adaptation_log.json"
LOG_SCHEMA_VERSION = "1"
CRITERIA_VERSION = "v1_2026-04-23"


# ─── Decision-block parsing ─────────────────────────────────────────

# Matches one decision line. Permissive: allows either Criterion: or
# Kriterium: prefix, or no prefix at all; comma-separated rule IDs;
# arrow may be → or ->. Rule-ID pattern: 1-3 uppercase letters + "-"
# + digits (CF-01, SC-10, M-02, NF-9) OR the literal DEVIATION.
_RULE_ID_PAT = r"(?:[A-Z]{1,3}-\d+|DEVIATION)"

# Standard line with rule-ID: "- TYPE object: reason → RULE-ID"
_DECISION_LINE = re.compile(
    r"^\s*[-•*]?\s*"                               # optional bullet
    r"(?P<type>[A-Z][A-Z_]{1,30})"                 # TYPE
    r"\s+"
    r"(?P<object>.+?)"                             # object (non-greedy)
    r"\s*:\s*"
    r"(?P<reason>.+?)"                             # reason (non-greedy)
    r"\s*(?:→|->|—>)\s*"                           # arrow
    r"(?i:(?:Criterion|Kriterium|Criteria|Criterio)s?\s*:\s*)?"  # optional label (case-insensitive: matches CRITERION, Criterion, criterion)
    r"(?P<rule_ids>" + _RULE_ID_PAT + r"(?:\s*,\s*" + _RULE_ID_PAT + r")*)"
    r"\s*$"
)

# Deviation line: "- DEVIATION object: reason" (no arrow, no rule)
_DEVIATION_LINE = re.compile(
    r"^\s*[-•*]?\s*DEVIATION\s+(?P<object>.+?)\s*:\s*(?P<reason>.+?)\s*$"
)

_BLOCK_HEADER = re.compile(r"^\s*DECISIONS?\s*:?\s*$", re.MULTILINE | re.IGNORECASE)


def parse_decisions_block(agent_output: str) -> list[dict]:
    """Extracts structured decisions from agent raw output.

    Scans for a line matching ``DECISIONS:`` (case-insensitive) and
    parses the following lines until a blank line or a line that
    doesn't look like a decision entry.

    Malformed lines are preserved as DEVIATION entries — we never
    silently drop.
    """
    results: list[dict] = []
    if not agent_output:
        return results

    match = _BLOCK_HEADER.search(agent_output)
    if not match:
        return results

    after = agent_output[match.end():].splitlines()
    for raw in after:
        line = raw.strip()
        if not line:
            # Blank line ends the block — but some models add a blank
            # line between entries. Allow one blank, stop on second.
            if results and results[-1].get("_trailing_blank"):
                break
            if results:
                results[-1]["_trailing_blank"] = True
            continue
        # Strip trailing markers that some models like to add
        if line.lower().startswith(("decisions ", "end ", "end.", "```")):
            break

        parsed = _DECISION_LINE.match(line)
        if parsed:
            rule_ids = [r.strip() for r in parsed.group("rule_ids").split(",")]
            deviation = "DEVIATION" in rule_ids
            entry = {
                "type": parsed.group("type").strip(),
                "object": parsed.group("object").strip(),
                "reason": parsed.group("reason").strip(),
                "rule_ids": rule_ids,
                "deviation_justification": (
                    parsed.group("reason").strip() if deviation else None
                ),
            }
        elif (dev := _DEVIATION_LINE.match(line)):
            # DEVIATION shortcut: "- DEVIATION object: reason" (no arrow, no rule)
            entry = {
                "type": "DEVIATION",
                "object": dev.group("object").strip(),
                "reason": dev.group("reason").strip(),
                "rule_ids": ["DEVIATION"],
                "deviation_justification": dev.group("reason").strip(),
            }
        else:
            # Unparseable line — log as DEVIATION rather than silently drop
            entry = {
                "type": "DEVIATION",
                "object": "<unparseable>",
                "reason": line[:400],
                "rule_ids": ["DEVIATION"],
                "deviation_justification": f"parse_failed: {line[:400]}",
            }
        # Clean internal helper keys
        entry.pop("_trailing_blank", None)
        results.append(entry)

    # Final cleanup of helper flags
    for e in results:
        e.pop("_trailing_blank", None)
    return results


# ─── Logger ─────────────────────────────────────────────────────────


def _log_path() -> Path:
    return Path(ADAPTATION_LOG_DIR) / ADAPTATION_LOG_FILE


def _project_name() -> str:
    """Best-effort: name of project-root cwd."""
    return Path.cwd().name


def _initialize_log_if_missing() -> dict:
    path = _log_path()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    Path(ADAPTATION_LOG_DIR).mkdir(exist_ok=True)
    log = {
        "meta": {
            "version": LOG_SCHEMA_VERSION,
            "created_at": datetime.now().isoformat(),
            "criteria_version": CRITERIA_VERSION,
            "project": _project_name(),
        },
        "entries": [],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    return log


def log_decision(
    agent: str,
    phase: str,
    decision_type: str,
    object_id: str,
    reason: str,
    rule_ids: list[str] | str,
    deviation_justification: Optional[str] = None,
) -> None:
    """Appends one decision entry to output/adaptation_log.json.

    Idempotent-safe for the schema (each call appends one entry).
    File is created on first call.
    """
    log = _initialize_log_if_missing()

    if isinstance(rule_ids, str):
        rule_ids = [rule_ids]

    entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "agent": agent,
        "type": decision_type,
        "object": object_id,
        "reason": reason,
        "rule_ids": rule_ids,
        "deviation_justification": deviation_justification,
    }
    log["entries"].append(entry)

    path = _log_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def log_decisions_from_block(
    agent_output: str,
    agent: str,
    phase: str,
) -> int:
    """Convenience: parse + log in one call.

    Returns the number of decisions written.
    """
    decisions = parse_decisions_block(agent_output)
    for d in decisions:
        log_decision(
            agent=agent,
            phase=phase,
            decision_type=d["type"],
            object_id=d["object"],
            reason=d["reason"],
            rule_ids=d["rule_ids"],
            deviation_justification=d.get("deviation_justification"),
        )
    return len(decisions)


# ─── Criteria-document loader ───────────────────────────────────────


def _criteria_path() -> Path:
    """Locates adaptation_criteria.md.

    Resolution order:
      1. ./adaptions-brain/adaptation_criteria.md (when running from
         the super-repo root)
      2. ../../adaptions-brain/... (when running from a project
         subdirectory such as projects/example_adaptation/)
      3. environment variable KI_ADAPTER_CRITERIA_PATH (escape hatch)
    """
    env = os.environ.get("KI_ADAPTER_CRITERIA_PATH")
    if env:
        return Path(env)

    here = Path.cwd()
    candidates = [
        here / "adaptions-brain" / "adaptation_criteria.md",
        here / ".." / ".." / "adaptions-brain" / "adaptation_criteria.md",
        here / ".." / "adaptions-brain" / "adaptation_criteria.md",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return candidates[0]  # nonexistent; load_criteria will raise


def load_criteria() -> str:
    """Loads the raw criteria markdown as a string for prompt injection.

    Agent prompts embed the whole document so the agent can cite rule
    IDs accurately. ~17k chars for v1 — acceptable prompt-overhead.
    """
    path = _criteria_path()
    if not path.exists():
        raise FileNotFoundError(
            f"adaptation_criteria.md not found. Expected at {path}. "
            f"Override with env var KI_ADAPTER_CRITERIA_PATH."
        )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_criteria_index() -> dict:
    """Parses adaptation_criteria.md into {rule_id: {title, domain}}.

    Useful for validation: reject DECISIONS entries citing non-existent
    rule IDs.
    """
    text = load_criteria()
    # Match headings like: ### [CF-01] Funktionale Figurenfusion
    pat = re.compile(r"^###\s+\[(?P<id>[A-Z]{1,3}-\d+)\]\s+(?P<title>.+?)\s*$", re.MULTILINE)
    index = {}
    for m in pat.finditer(text):
        rid = m.group("id")
        index[rid] = {
            "title": m.group("title").strip(),
            "domain": rid.split("-", 1)[0],
        }
    return index


DECISIONS_INSTRUCTION_BLOCK = """
ADAPTATION CRITERIA — DECISION RULES

You MUST refer to the adaptation criteria defined in
`adaptions-brain/adaptation_criteria.md` (v1, loaded below). When you
make a creative decision in these categories — character fusion (CF),
scene compression (SC), subplot suppression (SS), narrator frame (NF)
— cite the specific rule ID (e.g., CF-01, SC-03) that drove your
choice.

If no rule applies, or two rules conflict after meta-rules M-01..M-05,
use rule_id = "DEVIATION" and make the reason field the deviation
justification (what principle you followed instead). Deviations are
allowed but must be traceable. Target: ≤15% deviations per run.

--- CRITERIA (v1) ---
{criteria_text}
--- END CRITERIA ---

OUTPUT REQUIREMENTS:
After your normal JSON/text output, append a DECISIONS block using
this exact format:

    DECISIONS:
    - TYPE object_id: reason ≤15 words → CRITERION: RULE-ID
    - TYPE object_id: reason ≤15 words → CRITERION: RULE-ID, RULE-ID

TYPE values (use the closest match):
  FUSE, CUT, CUT_SUBPLOT, COMPRESS, EXPAND, MERGE_SCENES, REFOCAL,
  KEEP_FRAME, DISSOLVE_FRAME, INVENT_BRIDGE, TRANSLATE_TO_VISUAL,
  KEEP, REWRITE, DEVIATION

Example:
    DECISIONS:
    - FUSE Khan Mahoma → Bata: both guides, <4 scenes, functional overlap → CF-01
    - CUT_SUBPLOT thistle-field-reprise: repeats opening frame → NF-08
    - REFOCAL Nikolaus-Hof: seen only through HM's letter → CF-08
    - DEVIATION scene_S007: SC-01 and M-02 conflict, kept for tension arc
""".strip()


def build_criteria_instruction() -> str:
    """Returns the full instruction block for agent prompt injection.

    The block includes (1) the expectation to cite rules, (2) the
    criteria document inline, and (3) the DECISIONS output format.
    Agents that make creative decisions should inject this via
    prompt_builder.
    """
    criteria_text = load_criteria()
    return DECISIONS_INSTRUCTION_BLOCK.format(criteria_text=criteria_text)
