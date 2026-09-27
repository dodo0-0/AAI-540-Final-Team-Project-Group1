"""CLI entry point for read-only EMBER2024 raw-data validation."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from malware_data.logging_utils import configure_logging
from malware_data.validation import load_config, make_config, validate_dataset, write_reports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect and validate raw EMBER2024 JSONL files without modifying them.")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "validation.example.json")
    parser.add_argument("--data-root", help="Override configured raw-data root.")
    parser.add_argument("--output-dir", help="Override configured report directory.")
    parser.add_argument("--strict-json", action="store_true", help="Stop at the first invalid JSONL record.")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    values = load_config(args.config)
    config = make_config(values, args.data_root, args.output_dir)
    if args.strict_json:
        config = config.__class__(**{**config.__dict__, "strict_json": True})
    summary = validate_dataset(config)
    write_reports(summary, config.output_dir)
    logging.getLogger(__name__).info("Reports written successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
