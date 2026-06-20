# -*- coding: utf-8 -*-
"""VirusAlign command-line interface module."""

import argparse
import sys
import time
from pathlib import Path
from typing import List

import pandas as pd

from core.config import DEFAULT_NAME_COLUMN
from core.data_manager import DataManager
from core.engine import AlignmentEngine
from core.exceptions import VirusAlignError
from core.logger import get_logger, configure_logger

logger = get_logger("cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VirusAlign - virus name alignment tool")
    parser.add_argument("-i", "--input", required=True, help="Input CSV file")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file")
    parser.add_argument("-c", "--name-col", default=DEFAULT_NAME_COLUMN, help="Name column")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    return parser


def process_csv(input_path: str, output_path: str, name_col: str) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        logger.error(f"File not found: {input_path}")
        sys.exit(1)
    logger.info(f"Reading: {input_path}")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        logger.error(f"CSV read error: {e}")
        sys.exit(1)
    if name_col not in df.columns:
        cols = ", ".join(df.columns)
        logger.error(f"Column {name_col} not found. Available: {cols}")
        sys.exit(1)

    dm = DataManager()
    engine = AlignmentEngine(dm)
    total = len(df)
    logger.info(f"Processing {total} rows")

    results: List[dict] = []
    start = time.time()
    for i, (_, row) in enumerate(df.iterrows()):
        raw = str(row[name_col])
        mr = engine.match_one(raw)
        merged = row.to_dict()
        merged.update(mr.to_dict())
        results.append(merged)
        if (i + 1) % 500 == 0:
            rate = (i + 1) / (time.time() - start)
            logger.info(f"Progress: {i+1}/{total} ({rate:.0f} rows/sec)")

    out_df = pd.DataFrame(results)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)
    logger.info(f"Written: {output_path}")

    stats = engine.match_stats
    matched = total - stats["unmatched"]
    pct = matched * 100 // total if total else 0
    elapsed = time.time() - start
    logger.info(f"Done: {elapsed:.1f}s, matched={matched}/{total} ({pct}%)")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        process_csv(args.input, args.output, args.name_col)
    except VirusAlignError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()