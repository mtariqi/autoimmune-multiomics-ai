# Data

Nothing in `raw/`, `processed/` or `external/` is committed (see `.gitignore`).

| Folder | Contents | Rule |
| --- | --- | --- |
| raw/ | Original inputs exactly as received | Read-only; never edit |
| processed/ | Outputs of `workflow/` | Regenerate from code, never hand-edit |
| external/ | Public resources (GWAS summary statistics, reference atlases) | Record source URL + download date in `metadata/sources.csv` |
| metadata/ | Sample-sheet templates, data dictionaries, source logs | Synthetic or de-identified only |

Participant-level data live on the institution's secure storage and are referenced by path in
`config/config.yaml`, never copied here.
