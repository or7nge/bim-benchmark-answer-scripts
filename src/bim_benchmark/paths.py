"""Centralised filesystem locations used throughout the project."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
MODELS_DIR = DATA_DIR / "reference_models"
RESULTS_DIR = DATA_DIR / "benchmark_results"
QUESTIONS_PATH = DATA_DIR / "questions.csv"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def ensure_required_directories() -> None:
    """Make sure directories that receive generated artefacts exist."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def resolve_relative(path_fragment: str | Path) -> Path:
    """Resolve a project-relative path fragment to an absolute path."""
    candidate = Path(path_fragment)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate
