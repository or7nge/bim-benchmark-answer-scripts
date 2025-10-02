"""Command-line interface for running BIM benchmark scripts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from . import paths, runner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run BIM benchmark scripts against IFC models.")
    parser.add_argument(
        "target",
        nargs="?",
        default=str(paths.MODELS_DIR),
        help="Path to an IFC file or a directory containing IFC files (defaults to bundled models).",
    )
    parser.add_argument(
        "--questions",
        dest="questions",
        default=str(paths.QUESTIONS_PATH),
        help="Override the path to questions.csv.",
    )
    parser.add_argument(
        "--question-id",
        dest="question_ids",
        action="append",
        help="Limit execution to specific question IDs (can be repeated).",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target = Path(args.target)
    questions = Path(args.questions)

    if target.is_dir():
        print(f"Running benchmarks for IFC files in {target}")
        runner.run_directory(target, questions, args.question_ids)
    else:
        print(f"Running benchmark for {target}")
        runner.run_full_benchmark(target, questions, args.question_ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
