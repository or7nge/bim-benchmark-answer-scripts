from collections import defaultdict

from scripts.question_helpers import element_area, element_orientation, open_ifc


def window_area_by_orientation(ifc_file_path):
    """Sum total window area grouped by cardinal orientation."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return {"No windows found": 0.0}

        totals = defaultdict(float)
        for window in windows:
            area = element_area(window)
            if area is None:
                continue
            orientation = element_orientation(window) or "Unknown"
            totals[orientation] += area

        return dict(totals) if totals else {"Unknown": 0.0}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
