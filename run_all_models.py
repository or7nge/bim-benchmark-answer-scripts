"""Backward-compatible entry point that forwards to the package CLI."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.bim_benchmark import paths, runner  # noqa: E402
from src.bim_benchmark.cli import main as cli_main  # noqa: E402


def run_target(target: str | Path) -> None:
    """Run benchmarks for a single IFC file or every IFC in a provided directory."""
    target_path = Path(target)
    if target_path.is_dir():
        runner.run_directory(target_path)
    else:
        runner.run_full_benchmark(target_path, paths.QUESTIONS_PATH)


def main(argv: list[str] | str | None = None) -> int:
    """Entry point compatible with the historic API and the new CLI."""
    if isinstance(argv, (str, Path)):
        run_target(argv)
        return 0

    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 1 and not str(argv[0]).startswith("-"):
        run_target(argv[0])
        return 0

    return cli_main(argv)


if __name__ == "__main__":
    sys.exit(main())
