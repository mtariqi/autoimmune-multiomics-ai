"""Snakemake script: validate inputs against the project data standards; stop on any problem."""

import pandas as pd

from autoimmune_mo.standards import SAMPLE_SHEET, check_matrix_matches_samples, validate_table

samples = pd.read_csv(snakemake.input.samples, sep="\t")  # noqa: F821
matrix = pd.read_csv(snakemake.input.metabolomics, sep="\t", index_col=0)  # noqa: F821

problems = validate_table(samples, SAMPLE_SHEET) + check_matrix_matches_samples(matrix, samples)
if problems:
    raise ValueError("Input validation failed:\n  - " + "\n  - ".join(problems))

with open(snakemake.output[0], "w") as fh:  # noqa: F821
    fh.write(f"sample sheet: {len(samples)} rows, valid\n")
    fh.write(f"metabolomics: {matrix.shape[0]} samples x {matrix.shape[1]} features, matched\n")
