# Takes an IFC model and a script, runs the script over the model, returns the answer.


import sys
import importlib.util
import os
from pathlib import Path
import json


def run_single_question(ifc_file_path, script_path):
    """
    Run a single question script on an IFC model

    Args:
        ifc_file_path (str): Path to the IFC file
        script_path (str): Path to the Python script

    Returns:
        dict: Result containing answer and metadata
    """

    # Validate inputs
    if not os.path.exists(ifc_file_path):
        return {"error": f"IFC file not found: {ifc_file_path}"}

    if not os.path.exists(script_path):
        return {"error": f"Script file not found: {script_path}"}

    try:
        # Load the script module dynamically
        script_name = Path(script_path).stem
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the main function in the module
        # Convention: function name should match the script name or be the main function
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
                # Get all functions from module and use the first one that's not built-in
                functions = [name for name in dir(module) if callable(getattr(module, name)) and not name.startswith("_")]
                if functions:
                    main_function = getattr(module, functions[0])
                else:
                    return {"error": f"No callable function found in {script_path}"}

        # Execute the function
        result = main_function(ifc_file_path)

        return {"success": True, "ifc_file": ifc_file_path, "script": script_path, "answer": result, "answer_type": type(result).__name__}

    except Exception as e:
        return {"success": False, "error": str(e), "ifc_file": ifc_file_path, "script": script_path}


def main():
    """Command line interface for single question runner"""

    if len(sys.argv) != 3:
        print("Usage: python single_question_runner.py <ifc_file_path> <script_path>")
        print("Example: python single_question_runner.py test.ifc scripts/count_walls.py")
        sys.exit(1)

    ifc_file_path = sys.argv[1]
    script_path = sys.argv[2]

    print(f"Running script '{script_path}' on IFC file '{ifc_file_path}'...")

    result = run_single_question(ifc_file_path, script_path)

    if result.get("success", False):
        print(f"\n✅ Success!")
        print(f"Answer: {result['answer']}")
        print(f"Answer Type: {result['answer_type']}")
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
