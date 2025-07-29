from count_walls import count_walls
from count_doors import count_doors
from list_storeys import list_storeys
from total_floor_area import total_floor_area
from building_height import building_height
from wall_materials import wall_materials
from doors_per_floor import doors_per_floor


def run_benchmark_question(ifc_file_path, question_id):
    """Run a specific benchmark question on an IFC file"""
    question_functions = {
        "Q001": count_walls,
        "Q002": count_doors,
        "Q003": list_storeys,
        "Q004": total_floor_area,
        "Q005": building_height,
        "Q006": wall_materials,
        "Q008": doors_per_floor,
    }
    if question_id in question_functions:
        return question_functions[question_id](ifc_file_path)
    else:
        return f"Question {question_id} not implemented"


def run_full_benchmark(ifc_file_path):
    """Run all benchmark questions on an IFC file"""
    results = {}
    question_functions = {
        "Q001": count_walls,
        "Q002": count_doors,
        "Q003": list_storeys,
        "Q004": total_floor_area,
        "Q005": building_height,
        "Q006": wall_materials,
        "Q008": doors_per_floor,
    }
    for q_id, func in question_functions.items():
        try:
            results[q_id] = func(ifc_file_path)
        except Exception as e:
            results[q_id] = f"Error: {str(e)}"
    return results
