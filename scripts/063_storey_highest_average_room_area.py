from collections import defaultdict

from scripts.ifc_utils import find_storey_for_element
from scripts.question_helpers import element_area, get_ordered_storeys, open_ifc, storey_label


def storey_highest_average_room_area(ifc_file_path):
    """Find the storey whose rooms have the largest average area."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return "No spaces found"

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

        averages = {key: totals[key] / counts[key] for key in totals if counts[key]}
        if not averages:
            return "No areas available"

        target = max(averages.items(), key=lambda item: (item[1], item[0]))
        return target[0]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
