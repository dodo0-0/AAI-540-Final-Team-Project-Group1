# Running raw EMBER2024 validation

The validation command is read-only with respect to `data/raw`. It streams JSONL files one line at a time, so it is suitable for the full dataset without loading it into memory. It does not perform EDA, feature engineering, splitting, model training, or AWS/SageMaker actions.

From the `project` directory, run:

```powershell
python scripts/run_validation.py
```

The default configuration is `configs/validation.example.json`. It uses relative paths and therefore does not contain a machine-specific path. To point at another local copy or report location:

```powershell
python scripts/run_validation.py --data-root D:\datasets\ember2024 --output-dir reports\validation_run_01
```

Use `--strict-json` to stop rather than report an invalid JSONL line, and `--verbose` for debug-level logs.

Outputs are written to the configured output directory:

- `validation_summary.json`: complete machine-readable inventory, schema/type counts, missingness, labels, duplicates, and temporal summary.
- `validation_per_file.csv`: reproducible per-shard file, row, class, parse-error, and duplicate counts.
- `validation_summary.md`: concise readable report.

Duplicate detection uses `sha256` by default. The report counts every later occurrence of a hash as a duplicate; it does not delete or deduplicate raw data. The current Kaggle copy should be fully validated before downstream use because the existing inventory identified a possible row-doubling issue.

The report flags hashes, VirusTotal-derived fields, post-submission analysis dates, and taxonomy labels for leakage/inference-availability review. These flags are not final feature-engineering decisions.
