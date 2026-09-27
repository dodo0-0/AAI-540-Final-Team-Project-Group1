"""Create reproducible, non-model EDA artifacts from raw EMBER2024 JSONL."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from malware_data.eda import load_eda_config, make_eda_config, stratified_unique_sample, summarize_eda, write_eda_reports
from malware_data.logging_utils import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create reproducible EDA summaries; no model training is performed.")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "eda.example.json")
    parser.add_argument("--data-root")
    parser.add_argument("--validation-summary")
    parser.add_argument("--output-dir")
    parser.add_argument("--sample-per-class", type=int)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    values = load_eda_config(args.config)
    config = make_eda_config(
        values, data_root=args.data_root, validation_summary=args.validation_summary,
        output_dir=args.output_dir, sample_per_class=args.sample_per_class,
    )
    with config.validation_summary.open(encoding="utf-8") as handle:
        validation = json.load(handle)
    rows, sampling = stratified_unique_sample(config)
    summary = summarize_eda(rows, sampling, validation)
    write_eda_reports(rows, summary, config)
    logging.getLogger(__name__).info("EDA completed with %d sampled records", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
