# Data standards

Every table that enters the pipeline is checked against a schema in
`src/autoimmune_mo/standards.py`. The pipeline stops with a list of problems if a check fails.

## Three kinds of table

| Table | Shape | Key | Example |
| --- | --- | --- | --- |
| Sample sheet | One row per participant visit | `sample_id` (unique), `participant_id` + `visit` | `data/metadata/sample_sheet_template.csv` |
| Feature matrix | One row per sample, one column per feature | Row index = `sample_id` | metabolite concentrations, CLR abundances |
| Feature annotation | One row per feature | `feature_id` | metabolite HMDB IDs, Ensembl gene IDs |

## Sample sheet columns

| Column | Type | Required | Allowed values |
| --- | --- | --- | --- |
| `sample_id` | text | yes | unique |
| `participant_id` | text | yes | |
| `visit` | integer | yes | ≥ 0 |
| `months_from_baseline` | number | yes | ≥ 0 |
| `group` | category | yes | `at_risk`, `ra_reference`, `healthy_control`, `qc_pool` |
| `acpa_status` | category | no | `positive`, `negative`, `unknown` |
| `sex` | category | yes | `F`, `M`, `other`, `unknown` |
| `age` | number | yes | 0 to 120 |
| `bmi` | number | no | 10 to 80 |
| `progressed` | integer | no | 0, 1 |
| `months_to_onset` | number | no | ≥ 0 |
| `batch` | text | no | assay plate or run |

## File rules

- Tab-separated `.tsv` with a header row; UTF-8; missing values left empty.
- Identifiers never contain names, dates of birth, health-card numbers or other direct identifiers.
- Units go in the feature annotation, not in column names.
- Each public dataset is logged in `data/metadata/sources.csv` with URL, version and download date.

## Checking a table yourself

```python
import pandas as pd
from autoimmune_mo.standards import SAMPLE_SHEET, validate_table

problems = validate_table(pd.read_csv("samples.tsv", sep="\t"), SAMPLE_SHEET)
print(problems or "valid")
```
