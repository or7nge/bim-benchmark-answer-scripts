# For a specific model, runs through all questions, calculates answers, creates a dataset with answers for that specific model.


import sys
import json
import csv
import os
from pathlib import Path
from datetime import datetime
import importlib.util


def load_benchmark_questions(benchmark_file):
    """
    Load questions from JSON or CSV benchmark file

    Args:
        benchmark_file (str): Path to benchmark file (.json or .csv)

    Returns:
        list: List of question dictionaries
    """

    if not os.path.exists(benchmark_file):
        raise FileNotFoundError(f"Benchmark file not found: {benchmark_file}")

    file_ext = Path(benchmark_file).suffix.lower()

    if file_ext == ".json":
        with open(benchmark_file, "r") as f:
            data = json.load(f)
            return data.get("questions", [])

    elif file_ext == ".csv":
        questions = []
        with open(benchmark_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert tags string back to list
                if "tags" in row:
                    row["tags"] = [tag.strip() for tag in row["tags"].split(",")]
                questions.append(row)
        return questions

    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Use .json or .csv")


def run_script_on_model(ifc_file_path, script_path):
    """
    Run a single script on an IFC model (reused from single_question_runner)

    Args:
        ifc_file_path (str): Path to IFC file
        script_path (str): Path to Python script

    Returns:
        tuple: (success, result/error_message)
    """

    if not os.path.exists(script_path):
        return False, f"Script not found: {script_path}"

    try:
        # Load script dynamically
        script_name = Path(script_path).stem
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find main function
        function_name = script_name
        if hasattr(module, function_name):
            main_function = getattr(module, function_name)
        else:
            # Try common function names
            possible_names = ["main", "run", "execute", "process"]
            main_function = None
            for name in possible_names:
                if hasattr(module, name):
                    main_function = getattr(module, name)
                    break

            if main_function is None:
                # Get first callable function
                functions = [name for name in dir(module) if callable(getattr(module, name)) and not name.startswith("_")]
                if functions:
                    main_function = getattr(module, functions[0])
                else:
                    return False, f"No callable function found in {script_path}"

        # Execute function
        result = main_function(ifc_file_path)
        return True, result

    except Exception as e:
        return False, str(e)


def run_full_benchmark(ifc_file_path, benchmark_file, output_file=None):
    """
    Run all benchmark questions on an IFC model

    Args:
        ifc_file_path (str): Path to IFC file
        benchmark_file (str): Path to benchmark questions file
        output_file (str, optional): Path for output file

    Returns:
        dict: Complete results with answers
    """

    # Validate IFC file
    if not os.path.exists(ifc_file_path):
        raise FileNotFoundError(f"IFC file not found: {ifc_file_path}")

    # Load questions
    print(f"Loading benchmark questions from: {benchmark_file}")
    questions = load_benchmark_questions(benchmark_file)
    print(f"Found {len(questions)} questions")

    # Prepare results structure
    results = {
        "benchmark_info": {
            "ifc_file": ifc_file_path,
            "benchmark_source": benchmark_file,
            "execution_time": datetime.now().isoformat(),
            "total_questions": len(questions),
            "successful_answers": 0,
            "failed_answers": 0,
        },
        "questions_with_answers": [],
    }

    # Process each question
    print(f"\nRunning benchmark on: {ifc_file_path}")
    print("=" * 60)

    for i, question in enumerate(questions, 1):
        question_id = question.get("question_id", f"Q{i:03d}")
        question_text = question.get("question_text", question.get("question", "Unknown question"))
        script_path = question.get("script_path", "")

        print(f"\n[{i}/{len(questions)}] {question_id}: {question_text}")

        # Run the script
        success, result = run_script_on_model(ifc_file_path, script_path)

        # Prepare question result
        question_result = question.copy()  # Copy original question data

        if success:
            question_result["answer"] = result
            question_result["answer_type"] = type(result).__name__
            question_result["status"] = "success"
            results["benchmark_info"]["successful_answers"] += 1
            print(f"  ✅ Answer: {result}")
        else:
            question_result["answer"] = None
            question_result["error"] = result
            question_result["status"] = "failed"
            results["benchmark_info"]["failed_answers"] += 1
            print(f"  ❌ Error: {result}")

        results["questions_with_answers"].append(question_result)

    # Save results if output file specified
    if output_file:
        save_results(results, output_file)
        print(f"\n💾 Results saved to: {output_file}")

    return results


def save_results(results, output_file):
    """
    Save results to JSON or CSV file

    Args:
        results (dict): Results dictionary
        output_file (str): Output file path
    """

    file_ext = Path(output_file).suffix.lower()

    if file_ext == ".json":
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

    elif file_ext == ".csv":
        with open(output_file, "w", newline="") as f:
            fieldnames = [
                "question_id",
                "question_text",
                "difficulty",
                "category",
                "expected_output_type",
                "answer",
                "answer_type",
                "status",
                "error",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for q in results["questions_with_answers"]:
                row = {
                    "question_id": q.get("question_id", ""),
                    "question_text": q.get("question_text", q.get("question", "")),
                    "difficulty": q.get("difficulty", ""),
                    "category": q.get("category", ""),
                    "expected_output_type": q.get("expected_output_type", ""),
                    "answer": q.get("answer", ""),
                    "answer_type": q.get("answer_type", ""),
                    "status": q.get("status", ""),
                    "error": q.get("error", ""),
                }
                writer.writerow(row)

    else:
        # Default to JSON
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)


def print_summary(results):
    """Print summary of benchmark results"""

    info = results["benchmark_info"]

    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"IFC File: {info['ifc_file']}")
    print(f"Total Questions: {info['total_questions']}")
    print(f"✅ Successful: {info['successful_answers']}")
    print(f"❌ Failed: {info['failed_answers']}")
    print(f"📈 Success Rate: {(info['successful_answers']/info['total_questions']*100):.1f}%")
    print(f"⏰ Executed: {info['execution_time']}")


def main():
    """Command line interface for full benchmark runner"""

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python full_benchmark_runner.py <ifc_file> <benchmark_file> [output_file]")
        print("Examples:")
        print("  python full_benchmark_runner.py house.ifc benchmark_config.json")
        print("  python full_benchmark_runner.py house.ifc questions.csv house_results.json")
        print("  python full_benchmark_runner.py building.ifc benchmark_config.json results.csv")
        sys.exit(1)

    ifc_file_path = sys.argv[1]
    benchmark_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        # Run benchmark
        results = run_full_benchmark(ifc_file_path, benchmark_file, output_file)

        # Print summary
        print_summary(results)

        print(f"\n🎉 Benchmark completed successfully!")

    except Exception as e:
        print(f"\n💥 Error running benchmark: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
