# Running EMBER2024 exploratory data analysis

EDA is intentionally separate from feature engineering and model training. The reusable implementation streams raw JSONL, removes repeat `sha256` records from the EDA sample, and creates small descriptive artifacts. It never edits `data/raw`.

The reusable command-line modules require only the Python standard library. To open the visualization notebook, install the optional notebook dependencies once:

```powershell
python -m pip install -r requirements.txt
```

First complete validation:

```powershell
python scripts/run_validation.py
```

Then create a reproducible balanced EDA sample and summaries:

```powershell
python scripts/run_eda.py
```

The default 5,000 unique records per class is controlled by `configs/eda.example.json`. Override it for a faster local check:

```powershell
python scripts/run_eda.py --sample-per-class 1000
```

Outputs under `reports/eda/` are:

- `eda_sample_metrics.csv`: descriptive metrics used by the notebook, not a model-training dataset.
- `eda_summary.json`: reproducible missingness, distribution, outlier, class-comparison, and correlation results.
- `eda_summary.md`: concise EDA conclusions.

Open `notebooks/01_ember2024_eda.ipynb` after running the command. It loads those generated artifacts and contains visualizations only; reusable loading, sampling, validation, and descriptive summarization remain in `src/malware_data/`.

Temporal charts use `first_submission_date` and the supplied partition/week metadata only because validation confirmed their presence and the official train/test naming convention. `last_analysis_date` is shown only as a potential leakage field and must not be treated as an inference-time static feature.
