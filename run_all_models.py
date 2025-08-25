import os
import subprocess
import sys
from scripts_runner import run_full_benchmark


def main(models_folder):

    # List all model files in the specified folder
    model_files = [f for f in os.listdir(models_folder) if os.path.isfile(os.path.join(models_folder, f))]
    total_models = len(model_files)
    processed_count = 0

    for filename in model_files:
        model_path = os.path.join(models_folder, filename)
        try:
            run_full_benchmark(model_path, "questions.csv")
        except Exception as e:
            print(f"Error occurred while running scripts_runner.py for model: {model_path}")
            print(f"Error details: {e}")
        finally:
            processed_count += 1
            print(f"Finished processing model: {model_path} ({processed_count}/{total_models})")


# e.g. python run_all_models.py models
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <models_folder>")
        sys.exit(1)
    main(sys.argv[1])
