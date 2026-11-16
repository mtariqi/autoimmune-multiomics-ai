"""Data standards: table schemas and a validator.

Conventions used throughout the project:

* **Feature matrices** are wide: one row per sample, one column per feature,
  indexed by ``sample_id``.
* **Sample sheets** are long: one row per participant visit, keyed by ``sample_id``.
* **Feature annotations** describe each column of a feature matrix (one row per feature).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class Column:
    name: str
    kind: str  # "str", "int", "float", "category"
    required: bool = True
    allowed: tuple = ()
    min: float | None = None
    max: float | None = None
    unique: bool = False


@dataclass(frozen=True)
class Schema:
    name: str
    columns: tuple[Column, ...]
    key: tuple[str, ...] = field(default_factory=tuple)


SAMPLE_SHEET = Schema(
    "sample_sheet",
    (
        Column("sample_id", "str", unique=True),
        Column("participant_id", "str"),
        Column("visit", "int", min=0),
        Column("months_from_baseline", "float", min=0),
        Column("group", "category",
               allowed=("at_risk", "ra_reference", "healthy_control", "qc_pool")),
        Column("acpa_status", "category", required=False,
               allowed=("positive", "negative", "unknown")),
        Column("sex", "category", allowed=("F", "M", "other", "unknown")),
        Column("age", "float", min=0, max=120),
        Column("bmi", "float", required=False, min=10, max=80),
        Column("progressed", "int", required=False, allowed=(0, 1)),
        Column("months_to_onset", "float", required=False, min=0),
        Column("batch", "str", required=False),
    ),
    key=("participant_id", "visit"),
)

FEATURE_ANNOTATION = Schema(
    "feature_annotation",
    (
        Column("feature_id", "str", unique=True),
        Column("layer", "category", allowed=(
            "metabolomics", "genomics", "transcriptomics", "scrnaseq", "proteomics", "microbiome")),
        Column("name", "str"),
        Column("unit", "str", required=False),
        Column("class", "str", required=False),
        Column("identifier", "str", required=False),  # e.g. HMDB, Ensembl, UniProt, NCBI taxon
    ),
)

SCHEMAS = {s.name: s for s in (SAMPLE_SHEET, FEATURE_ANNOTATION)}


def validate_table(df: pd.DataFrame, schema: Schema) -> list[str]:
    """Return a list of human-readable problems; an empty list means the table is valid."""
    problems: list[str] = []
    for col in schema.columns:
        if col.name not in df.columns:
            if col.required:
                problems.append(f"missing required column '{col.name}'")
            continue
        s = df[col.name]
        if col.required and s.isna().any():
            problems.append(f"'{col.name}': {int(s.isna().sum())} missing values")
        v = s.dropna()
        if col.kind in ("int", "float"):
            num = pd.to_numeric(v, errors="coerce")
            bad = num.isna().sum()
            if bad:
                problems.append(f"'{col.name}': {int(bad)} non-numeric values")
            if col.kind == "int" and (num.dropna() % 1 != 0).any():
                problems.append(f"'{col.name}': non-integer values")
            if col.min is not None and (num < col.min).any():
                problems.append(f"'{col.name}': values below {col.min}")
            if col.max is not None and (num > col.max).any():
                problems.append(f"'{col.name}': values above {col.max}")
            v = num.dropna()
        if col.allowed:
            bad_vals = sorted({x for x in v if x not in col.allowed}, key=str)
            if bad_vals:
                problems.append(f"'{col.name}': values not allowed {bad_vals[:5]}")
        if col.unique and s.duplicated().any():
            problems.append(f"'{col.name}': {int(s.duplicated().sum())} duplicated values")
    if schema.key and all(k in df.columns for k in schema.key):
        dup = df.duplicated(list(schema.key)).sum()
        if dup:
            problems.append(f"{int(dup)} duplicated rows for key {schema.key}")
    return problems


def assert_valid(df: pd.DataFrame, schema: Schema) -> None:
    problems = validate_table(df, schema)
    if problems:
        raise ValueError(f"{schema.name} failed validation:\n  - " + "\n  - ".join(problems))


def check_matrix_matches_samples(matrix: pd.DataFrame, samples: pd.DataFrame) -> list[str]:
    """Every row of a feature matrix must have a sample-sheet entry, and vice versa."""
    m, s = set(matrix.index), set(samples["sample_id"])
    out = []
    if m - s:
        out.append(f"{len(m - s)} matrix samples missing from sample sheet")
    if s - m:
        out.append(f"{len(s - m)} sample-sheet samples missing from matrix")
    return out
