import os
import subprocess
import sys
from scripts_runner import run_full_benchmark


def main(models_folder):
    if os.path.isfile(models_folder) and models_folder.lower().endswith(".ifc"):
        # Single IFC file provided
        print(f"Single IFC file provided: {models_folder}")
        try:
            run_full_benchmark(models_folder, "questions.csv")
        except Exception as e:
            print(f"Error occurred while running scripts_runner.py for model: {models_folder}")
            print(f"Error details: {e}")
        print()
        print("Done with single model!")
    else:
        # List all .ifc model files in the specified folder
        model_files = [f for f in os.listdir(models_folder) if os.path.isfile(os.path.join(models_folder, f)) and f.lower().endswith(".ifc")]
        print(f"Found {len(model_files)} IFC models: {model_files}\n")

        for model_id in range(len(model_files)):
            model_path = os.path.join(models_folder, model_files[model_id])
            try:
                run_full_benchmark(model_path, "questions.csv")
            except Exception as e:
                print(f"Error occurred while running scripts_runner.py for model: {model_path}")
                print(f"Error details: {e}")
            print()
        print("Done with all models!")


# e.g. python run_all_models.py models
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <models_folder>")
        sys.exit(1)
    main(sys.argv[1])
