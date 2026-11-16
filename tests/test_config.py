# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : tests/test_config.py
# Purpose     : Unit tests: config.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

from pathlib import Path

import pytest

from autoimmune_mo.config import load_config, secure_path

CFG = """
random_seed: 1
paths:
  results: results
  secure: ${AMO_SECURE_DATA}
"""


def _write(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir()
    f = tmp_path / "config" / "config.yaml"
    f.write_text(CFG)
    return f


def test_relative_paths_resolve_to_repo_root(tmp_path, monkeypatch):
    monkeypatch.delenv("AMO_SECURE_DATA", raising=False)
    cfg = load_config(_write(tmp_path))
    assert cfg["paths"]["results"] == tmp_path.resolve() / "results"


def test_secure_path_requires_env_var(tmp_path, monkeypatch):
    monkeypatch.delenv("AMO_SECURE_DATA", raising=False)
    cfg = load_config(_write(tmp_path))
    with pytest.raises(RuntimeError):
        secure_path(cfg, "metabolomics/x.csv")


def test_secure_path_uses_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("AMO_SECURE_DATA", "/secure/store")
    cfg = load_config(_write(tmp_path))
    assert secure_path(cfg, "a.csv") == Path("/secure/store/a.csv")
