"""CLI to create chronological train/validation/test/reserved-production handoff datasets."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from malware_data.logging_utils import configure_logging
from malware_data.splits import create_temporal_splits, load_temporal_split_config, make_temporal_split_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create strict temporal EMBER2024 feature splits; no model training occurs.")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "temporal_split.example.json")
    parser.add_argument("--source-processed-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--schema-path")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    values = load_temporal_split_config(args.config)
    config = make_temporal_split_config(values, source_processed_dir=args.source_processed_dir, output_dir=args.output_dir, schema_path=args.schema_path)
    manifest = create_temporal_splits(config)
    logging.getLogger(__name__).info("Temporal split complete: %s", {name: item['row_count'] for name, item in manifest['splits'].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
