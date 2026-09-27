# EMBER2024 feature preparation

This stage creates a reusable static-feature dataset for the model-training teammate. It does not train, tune, evaluate, or select a model.

## Policy

`ember2024_win64_static_v1` uses 13 low-cardinality static PE metrics:

- General: `general_size`, `general_entropy`.
- Strings: `strings_numstrings`, `strings_avlength`, `strings_printables`, `strings_entropy`.
- PE structure: `section_count`, `import_library_count`, `export_count`, `richheader_count`, `pefilewarning_count`.
- Authenticode: `authenticode_num_certs`, `authenticode_self_signed`.

Count-like fields receive `log1p`; all approved fields are standardized using train-only fitted mean and standard deviation. Missing values are mean-imputed after standardization as `0.0`. The schema records every source path, transform, fit statistic, and missing-value count.

The following are excluded from model inputs: target/taxonomy labels; hashes; temporal and VirusTotal metadata; Capa enrichment; and high-dimensional/dynamic nested structures. `general.is_pe` is excluded because it is nearly constant in this Win64 data. See the generated schema's `exclusion_policy` for the complete, machine-readable rationale.

## Run

From `project/`:

```powershell
python scripts/prepare_features.py
```

The command is intentionally ordered:

1. Fit transformations only on unique valid rows from the supplied `train` partition.
2. Transform and deduplicate `train` with the saved train statistics.
3. Transform and deduplicate `test` with those same statistics; when configured, discard test hashes already seen in train to prevent duplicate-based evaluation leakage.

It preserves the supplied temporal partitions and does not create a random split or a validation split.

## Outputs

All outputs are local-only under the configured `data/processed/...` directory and are ignored by Git:

- `feature_schema.json`: final feature names/order, source fields, transforms, train-only statistics, exclusion policy, and output contract.
- `train_features.csv` and `test_features.csv`: `record_id`, `label`, `source_partition`, `source_week_start`, `source_week_end`, then the model feature columns in the exact schema order. Week fields are lineage metadata, not model inputs.
- `processing_report.json`: row, invalid, duplicate, overlap, and output counts.

For model training, use only `model_feature_columns` from `feature_schema.json`; never pass `record_id`, `label`, `source_partition`, `source_week_start`, or `source_week_end` into a model. These files can later be copied to S3 unchanged, together with the schema and processing report.
