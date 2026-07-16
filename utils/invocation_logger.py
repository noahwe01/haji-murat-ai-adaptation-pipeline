"""
INVOCATION LOGGER
=================
Records every agent invocation during a reproducible pipeline run.

For each LLM call: prompt sent, response received, state before/after,
token usage, timing, and errors. Produces a reproducible audit trail.

Usage:
    logger = InvocationLogger(run_id="pipeline_run_v1")

    with logger.invocation(
        agent_name="story_analyst",
        agent_version="v3.2",
        model="claude-sonnet-4-5",
        phase="1",
        chunk_id="chunk_003",
        trigger="orchestrator.run_phase_1",
    ) as inv:
        prompt = build_prompt(...)
        inv.record_prompt(prompt)
        response = call_claude(prompt)
        inv.record_response(response)
        inv.record_tokens(input=12345, output=2345)
"""

import json
import os
import shutil
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class InvocationLogger:
    """Manages a single pipeline run's invocation log."""

    def __init__(self, run_id: str, base_dir: str = "runs"):
        self.run_id = run_id
        self.base_dir = Path(base_dir)
        self.run_dir = self.base_dir / run_id
        self._counter = 0

        # Resolve project root (where agents/ and config/ live)
        self._project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        self._init_run()

    def _init_run(self):
        """Sets up the run directory. Aborts if it already exists."""
        if self.run_dir.exists():
            raise FileExistsError(
                f"Run '{self.run_id}' already exists at {self.run_dir}. "
                f"Choose a different run_id or delete the existing run."
            )

        # Create directory structure
        self.run_dir.mkdir(parents=True)
        (self.run_dir / "invocations").mkdir()
        prompts_dir = self.run_dir / "prompts_snapshot"
        prompts_dir.mkdir()

        # Copy config snapshot
        config_src = self._project_root / "config" / "projekt.yaml"
        if config_src.exists():
            shutil.copy2(config_src, self.run_dir / "config_snapshot.yaml")

        # Copy all agent files to prompts_snapshot
        agents_dir = self._project_root / "agents"
        if agents_dir.exists():
            for py_file in sorted(agents_dir.glob("*.py")):
                if py_file.name == "__init__.py":
                    continue
                shutil.copy2(py_file, prompts_dir / py_file.name)

        # Create empty run log
        (self.run_dir / "run_log.jsonl").touch()

    @contextmanager
    def invocation(
        self,
        agent_name: str,
        agent_version: str = "v3.2",
        model: str = "claude-sonnet-4-5",
        phase: str = "",
        chunk_id: str = "",
        trigger: str = "",
    ):
        """Context manager for a single agent invocation."""
        self._counter += 1
        inv = _Invocation(
            logger=self,
            invocation_id=f"{self._counter:03d}",
            agent_name=agent_name,
            agent_version=agent_version,
            model=model,
            phase=phase,
            chunk_id=chunk_id,
            trigger=trigger,
        )

        inv._start()

        try:
            yield inv
            inv._finish(status="success")
        except Exception as e:
            inv._finish(status="failed", error=e)
            raise

    def _append_log_line(self, entry: dict):
        """Appends a single JSONL line to run_log.jsonl."""
        log_path = self.run_dir / "run_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class _Invocation:
    """Tracks a single agent invocation within a run."""

    def __init__(
        self,
        logger: InvocationLogger,
        invocation_id: str,
        agent_name: str,
        agent_version: str,
        model: str,
        phase: str,
        chunk_id: str,
        trigger: str,
    ):
        self._logger = logger
        self.invocation_id = invocation_id
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.model = model
        self.phase = phase
        self.chunk_id = chunk_id
        self.trigger = trigger

        self._prompt = ""
        self._response = ""
        self._tokens_in = 0
        self._tokens_out = 0
        self._started_at = None
        self._finished_at = None
        self._input_state = None
        self._inv_dir = None

    def _start(self):
        """Captures start time and input state snapshot."""
        self._started_at = datetime.now(timezone.utc)

        # Create invocation directory
        ts = self._started_at.strftime("%Y-%m-%dT%H-%M-%S")
        dir_name = f"{self.invocation_id}_{ts}_{self.agent_name}"
        self._inv_dir = self._logger.run_dir / "invocations" / dir_name
        self._inv_dir.mkdir(parents=True)

        # Snapshot input state
        self._input_state = self._load_current_state()
        with open(self._inv_dir / "input_state_snapshot.json", "w", encoding="utf-8") as f:
            json.dump(self._input_state, f, ensure_ascii=False, indent=2)

    def _finish(self, status: str, error: Exception = None):
        """Captures end time, writes all artifacts."""
        self._finished_at = datetime.now(timezone.utc)
        duration = (self._finished_at - self._started_at).total_seconds()

        # Write prompt and response
        with open(self._inv_dir / "rendered_prompt.txt", "w", encoding="utf-8") as f:
            f.write(self._prompt)

        with open(self._inv_dir / "raw_response.txt", "w", encoding="utf-8") as f:
            f.write(self._response)

        # Snapshot output state and compute diff
        output_state = self._load_current_state()
        with open(self._inv_dir / "output_state_snapshot.json", "w", encoding="utf-8") as f:
            json.dump(output_state, f, ensure_ascii=False, indent=2)

        state_diff = self._compute_state_diff(self._input_state, output_state)
        with open(self._inv_dir / "state_diff.json", "w", encoding="utf-8") as f:
            json.dump(state_diff, f, ensure_ascii=False, indent=2)

        # Build meta
        error_msg = None
        if error:
            error_msg = f"{type(error).__name__}: {error}"
            # Write full traceback
            with open(self._inv_dir / "error.txt", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())

        meta = {
            "invocation_id": self.invocation_id,
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "model": self.model,
            "started_at": self._started_at.isoformat(),
            "finished_at": self._finished_at.isoformat(),
            "duration_seconds": round(duration, 1),
            "status": status,
            "token_usage": {
                "input": self._tokens_in,
                "output": self._tokens_out,
            },
            "phase": self.phase,
            "chunk_id": self.chunk_id,
            "trigger": self.trigger,
            "error": error_msg,
        }

        with open(self._inv_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        # Append to run_log.jsonl
        self._logger._append_log_line({
            "id": self.invocation_id,
            "ts": self._started_at.isoformat(),
            "agent": self.agent_name,
            "phase": self.phase,
            "chunk": self.chunk_id,
            "status": status,
            "duration": round(duration, 1),
            "tokens_in": self._tokens_in,
            "tokens_out": self._tokens_out,
        })

    # ─── Public recording methods ────────────────────────────────

    def record_prompt(self, prompt: str):
        """Records the rendered prompt sent to the LLM."""
        self._prompt = prompt

    def record_response(self, response: str):
        """Records the raw LLM response."""
        self._response = response

    def record_tokens(self, input: int = 0, output: int = 0):
        """Records token usage from the SDK response."""
        self._tokens_in = input
        self._tokens_out = output

    # ─── Internal helpers ────────────────────────────────────────

    def _load_current_state(self) -> dict:
        """Loads the current story_state.json."""
        state_path = self._logger._project_root / "state" / "story_state.json"
        if not state_path.exists():
            return {}
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _compute_state_diff(before: dict, after: dict) -> dict:
        """Computes a shallow diff between two state dicts.

        Returns a dict of changed top-level keys with their before/after values.
        For large nested structures (adapted_scenes, chunks), only reports
        whether the count changed rather than dumping the full content.
        """
        diff = {}
        large_keys = {"adapted_scenes", "chunks", "continuity_log"}

        all_keys = set(list(before.keys()) + list(after.keys()))
        for key in sorted(all_keys):
            val_before = before.get(key)
            val_after = after.get(key)

            if val_before == val_after:
                continue

            if key in large_keys:
                # For large arrays, report count change only
                len_before = len(val_before) if isinstance(val_before, (list, dict)) else 0
                len_after = len(val_after) if isinstance(val_after, (list, dict)) else 0
                if len_before != len_after:
                    diff[key] = {
                        "type": "count_change",
                        "before": len_before,
                        "after": len_after,
                    }
                else:
                    diff[key] = {"type": "content_changed", "count": len_after}
            else:
                diff[key] = {"before": val_before, "after": val_after}

        return diff
