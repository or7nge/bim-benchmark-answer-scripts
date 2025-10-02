"""Core execution logic for the benchmark CLI."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import multiprocessing
import time
from pathlib import Path
from queue import Empty
from typing import Iterable, Optional

import pandas as pd
from tqdm import tqdm

from . import paths


SCRIPT_TIMEOUT = 8000  # seconds


def _run_script_worker(result_queue, ifc_model_path: Path, script_path: Path) -> None:
    """Execute a benchmark script and push the outcome to the provided queue."""
    result = run_benchmark_script(ifc_model_path, script_path)
    result_queue.put(result)


def run_benchmark_script(ifc_model_path: Path, script_path: Path):
    """Run a single benchmark script on an IFC model and return the result."""
    try:
        script_path = paths.resolve_relative(script_path)
        ifc_model_path = paths.resolve_relative(ifc_model_path)

        if not script_path.exists():
            return f"Error: Script not found at {script_path}"

        if not ifc_model_path.exists():
            return f"Error: IFC file not found at {ifc_model_path}"

        spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        function_name = script_path.stem[4:]
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            try:
                return func(str(ifc_model_path))
            except TypeError:
                return func(str(ifc_model_path), str(script_path))
        return f"Error: Function '{function_name}' not found in {script_path}"

    except Exception as exc:  # pragma: no cover - defensive logging path
        return f"Error: {exc}"


def run_full_benchmark(
    ifc_model_path: str | Path,
    csv_path: str | Path | None = None,
    question_ids: Optional[Iterable[str | int]] = None,
):
    """Run every benchmark question defined in the CSV for a single IFC file."""
    paths.ensure_required_directories()

    ifc_model_path = paths.resolve_relative(ifc_model_path)
    csv_path = paths.resolve_relative(csv_path or paths.QUESTIONS_PATH)

    df = pd.read_csv(csv_path)
    results = {}

    if not question_ids:
        selection = list(range(len(df)))
    else:
        selection = []
        for requested in question_ids:
            if isinstance(requested, int):
                selection.append(requested)
                continue
            matches = df.index[df["question_id"] == requested]
            if not matches.empty:
                selection.append(int(matches[0]))

    def process_question(idx: int):
        if idx >= len(df):
            return None
        row = df.iloc[idx]
        question_id = row["question_id"]
        script_path = paths.resolve_relative(row["script_path"])

        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_run_script_worker,
            args=(result_queue, ifc_model_path, script_path),
        )

        start_time = time.time()
        process.start()
        process.join(SCRIPT_TIMEOUT)

        if process.is_alive():
            process.terminate()
            process.join()
            result = "EXECUTION TIMEOUT"
            elapsed = float(SCRIPT_TIMEOUT)
        else:
            try:
                result = result_queue.get_nowait()
            except Empty:
                result = "Error: No result returned"
            elapsed = time.time() - start_time

        result_queue.close()
        result_queue.join_thread()

        return (
            question_id,
            {
                "question": row["question_text"],
                "result": result,
                "difficulty": row["difficulty"],
                "time": round(elapsed, 3),
            },
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        future_to_idx = {executor.submit(process_question, idx): idx for idx in selection}
        results_iter = concurrent.futures.as_completed(future_to_idx)
        for future in tqdm(
            results_iter,
            total=len(future_to_idx),
            desc=f"{ifc_model_path.stem}.ifc Benchmark",
            ncols=120,
        ):
            res = future.result()
            if res is not None:
                q_id, data = res
                results[q_id] = data

    results = dict(sorted(results.items(), key=lambda item: item[0]))

    results_df = pd.DataFrame(
        [
            {
                "question_id": q_id,
                "question": data["question"],
                "result": data["result"],
                "difficulty": data["difficulty"],
                "model": str(ifc_model_path),
                "time_seconds": data["time"],
            }
            for q_id, data in results.items()
        ]
    )
    output_path = paths.RESULTS_DIR / f"{ifc_model_path.stem}_answers.csv"
    results_df.to_csv(output_path, index=False)
    return results


def run_directory(
    models_dir: str | Path,
    csv_path: str | Path | None = None,
    question_ids: Optional[Iterable[str | int]] = None,
):
    """Run the benchmark for every IFC file found in a directory."""
    models_dir = paths.resolve_relative(models_dir)

    if not models_dir.exists():
        raise FileNotFoundError(f"Models directory not found: {models_dir}")

    aggregate = {}
    for model_path in sorted(models_dir.glob("*.ifc")):
        aggregate[str(model_path)] = run_full_benchmark(model_path, csv_path, question_ids)
    return aggregate
