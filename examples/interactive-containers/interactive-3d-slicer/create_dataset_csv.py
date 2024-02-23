#!/usr/bin/env python
import argparse
import logging
import sys

from pathlib import Path

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read files from an output directory and write them to a dataset csv as a single filename column"
    )

    parser.add_argument("--output_csv", type=str, help="output csv file path", default="/output/dataset.csv")
    parser.add_argument("--output_column_name", type=str, help="filename column in output csv", default="Filename")
    parser.add_argument("--file_dir", type=str, help="directory with files to add to dataset csv",
                        default="/output/file_data")

    args = parser.parse_args()

    logger.info(f"Processing files in directory '{args.file_dir}'")
    try:
        file_paths = [str(p.relative_to(args.file_dir)) for p in Path(args.file_dir).rglob("*") if not p.is_dir()]
        with open(args.output_csv, "w") as f:
            f.write(f"{args.output_column_name}\n")
            f.write("\n".join(file_paths) + "\n")
    except Exception:
        logger.exception(f"Error processing files in directory {args.file_dir}")
        sys.exit(1)

    logger.info(f"Finished processing files - output dataset csv written to '{args.output_csv}'")
    sys.exit(0)
