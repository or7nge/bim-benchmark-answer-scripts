from collections import defaultdict

from scripts.ifc_utils import find_storey_for_element
from scripts.question_helpers import get_element_dimensions, get_ordered_storeys, open_ifc, storey_label


def door_area_by_storey(ifc_file_path):
    """Approximate door leaf area per storey using width × height."""
    try:
        model = open_ifc(ifc_file_path)
        doors = list(model.by_type("IfcDoor"))
        if not doors:
            return {"No doors found": 0.0}

        storeys = get_ordered_storeys(model)
        totals = defaultdict(float)
        for door in doors:
            width, height = get_element_dimensions(door)
            if width is None or height is None:
                continue
            storey = find_storey_for_element(door, storeys)
            key = storey_label(storey) if storey else "Unassigned"
            totals[key] += width * height

        return dict(totals) if totals else {"Unassigned": 0.0}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
