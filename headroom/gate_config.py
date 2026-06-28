"""Load ``~/.config/headroom/env`` into ``os.environ`` for CLI convenience.

The proxy systemd service reads this file via ``EnvironmentFile=``, but the
CLI runs in the user's shell and inherits only what is already exported.
This module bridges the gap so that ``headroom usage``, ``headroom auth``,
and ``headroom audit`` work without a manual ``source`` step.
"""

from __future__ import annotations

import os
from pathlib import Path


def _env_file_path() -> Path:
    """Return the path to the gate config file (resolved at call time)."""
    return Path.home() / ".config" / "headroom" / "env"


def load_gate_config() -> None:
    """Load ``~/.config/headroom/env`` into ``os.environ``.

    Only sets variables that are **not** already present in the environment,
    so shell-exported values always take precedence.  Comments, blank lines,
    and malformed lines are silently ignored.
    """
    env_file = _env_file_path()
    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        # Strip surrounding quotes (single or double)
        val = val.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, val)
