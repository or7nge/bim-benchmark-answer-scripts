from collections import defaultdict

from scripts.ifc_utils import find_storey_for_element
from scripts.question_helpers import classify_space_usage, element_area, get_ordered_storeys, open_ifc, storey_label


def storey_largest_circulation_area(ifc_file_path):
    """Identify the storey with the greatest corridor/lobby area."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return "No spaces found"

        storeys = get_ordered_storeys(model)
        totals = defaultdict(float)

        for space in spaces:
            category = classify_space_usage(space)
            if category not in {"Corridor", "Lobby"}:
                continue
            area = element_area(space)
            if area is None:
                continue
            storey = find_storey_for_element(space, storeys)
            key = storey_label(storey) if storey else "Unassigned"
            totals[key] += area

        if not totals:
            return "No circulation spaces"

        target = max(totals.items(), key=lambda item: (item[1], item[0]))
        return target[0]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
