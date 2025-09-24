
import pandas as pd
from pathlib import Path
import importlib.util
import time
import multiprocessing
import concurrent.futures
from tqdm import tqdm


def run_benchmark_script(ifc_model_path, script_path):
    """Run a benchmark script on an IFC model and return the result."""
    try:
        script_path = Path(script_path)

        if not script_path.exists():
            return f"Error: Script not found at {script_path}"

        if not Path(ifc_model_path).exists():
            return f"Error: IFC file not found at {ifc_model_path}"

        # Load the script as a module
        spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Try to pass both the IFC path and script path to the function
        function_name = script_path.stem[4:]
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            # Try calling with just IFC path, fallback to both args if needed
            try:
                return func(ifc_model_path)
            except TypeError:
                return func(ifc_model_path, script_path)
        else:
            return f"Error: Function '{function_name}' not found in {script_path}"

    except Exception as e:
        return f"Error: {str(e)}"


def run_full_benchmark(ifc_model_path, csv_path, question_ids=None):
    """
    Run all benchmark questions from CSV on an IFC model.

    Args:
        ifc_model_path (str): Path to IFC file
        csv_path (str): Path to questions.csv

    Returns:
        dict: Results for all questions {question_id: result}
    """
    # Read questions CSV
    df = pd.read_csv(csv_path)

    results = {}

    if not question_ids:
        question_ids = df.index.tolist()

    def process_question(idx):
        if idx >= len(df):
            return None
        row = df.iloc[idx]
        question_id = row["question_id"]
        script_path = row["script_path"]

        start_time = time.time()
        result = run_benchmark_script(ifc_model_path, script_path)
        elapsed = time.time() - start_time

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
        future_to_idx = {executor.submit(process_question, idx): idx for idx in question_ids}
        results_iter = concurrent.futures.as_completed(future_to_idx)
        for future in tqdm(results_iter, total=len(future_to_idx), desc=f"{Path(ifc_model_path).stem}.ifc Benchmark", ncols=120):
            res = future.result()
            if res is not None:
                q_id, data = res
                results[q_id] = data

    # Sort results by question_id key
    results = dict(sorted(results.items(), key=lambda x: x[0]))

    results_df = pd.DataFrame(
        [
            {
                "question_id": q_id,
                "question": data["question"],
                "result": data["result"],
                "difficulty": data["difficulty"],
                "model": ifc_model_path,
                "time_seconds": data["time"],
            }
            for q_id, data in results.items()
        ]
    )
    results_df.to_csv(f"model_benchmarks/{Path(ifc_model_path).stem}_answers.csv", index=False)
    return results


# Usage example
if __name__ == "__main__":
    # ifc_model_path = "models/big_house.ifc"
    ifc_model_path = "models/V_21.ifc"
    csv_path = "questions.csv"
    question_ids = None
    results = run_full_benchmark(ifc_model_path, csv_path, question_ids)

    # print()
    # for q_id, data in results.items():
    #     print(f"{q_id}: {data['question']} - {data['time']}s\n{data['result']}\n")
