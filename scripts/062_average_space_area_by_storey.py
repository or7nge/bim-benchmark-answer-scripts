from collections import defaultdict

from scripts.ifc_utils import find_storey_for_element
from scripts.question_helpers import element_area, get_ordered_storeys, open_ifc, storey_label


def average_space_area_by_storey(ifc_file_path):
    """Compute average space area for every storey."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return {}

        storeys = get_ordered_storeys(model)
        totals = defaultdict(float)
        counts = defaultdict(int)

        for space in spaces:
            area = element_area(space)
            if area is None:
                continue
            storey = find_storey_for_element(space, storeys)
            key = storey_label(storey) if storey else "Unassigned"
            totals[key] += area
            counts[key] += 1

        return {key: totals[key] / counts[key] for key in totals if counts[key]}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
