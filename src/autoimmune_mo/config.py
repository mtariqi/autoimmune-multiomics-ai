# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : src/autoimmune_mo/config.py
# Purpose     : Load the project configuration with environment variables
#               expanded and paths resolved.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Load the project configuration with environment variables expanded and paths resolved."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def load_config(path: str | Path = "config/config.yaml") -> dict:
    """Read the YAML config.

    ``${VAR}`` references are expanded from the environment. Relative entries under ``paths``
    are resolved against the repository root (the parent of the ``config/`` folder) and returned
    as ``Path`` objects. An unset variable is left as ``None`` so callers can fail clearly.
    """
    path = Path(path).resolve()
    with path.open() as fh:
        cfg = yaml.safe_load(os.path.expandvars(fh.read()))

    root = path.parent.parent
    resolved = {}
    for name, value in (cfg.get("paths") or {}).items():
        if value is None or str(value).startswith("$"):
            resolved[name] = None  # environment variable not set on this machine
        else:
            p = Path(value)
            resolved[name] = p if p.is_absolute() else root / p
    cfg["paths"] = resolved
    return cfg


def secure_path(cfg: dict, relative: str) -> Path:
    """Return a path inside the secure data area, or raise if it is not configured."""
    base = cfg["paths"].get("secure")
    if base is None:
        raise RuntimeError(
            "AMO_SECURE_DATA is not set. Participant-level analyses only run on the machine "
            "that holds the data."
        )
    return base / relative
