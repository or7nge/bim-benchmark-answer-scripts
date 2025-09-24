from collections import defaultdict

from scripts.question_helpers import classify_space_usage, element_area, open_ifc


def space_area_by_usage(ifc_file_path):
    """Total area grouped by inferred space usage category."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return {}

        totals = defaultdict(float)
        for space in spaces:
            area = element_area(space)
            if area is None:
                continue
            category = classify_space_usage(space)
            totals[category] += area
        return dict(totals)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
