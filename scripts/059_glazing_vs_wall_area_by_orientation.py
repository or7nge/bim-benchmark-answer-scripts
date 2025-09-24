from collections import defaultdict

from scripts.ifc_utils import get_element_area, get_wall_direction, is_external_wall
from scripts.question_helpers import element_area, element_orientation, open_ifc, unique_elements


def glazing_vs_wall_area_by_orientation(ifc_file_path):
    """Compare window area to exterior wall area for each orientation."""
    try:
        model = open_ifc(ifc_file_path)

        walls = unique_elements(
            list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        )
        windows = list(model.by_type("IfcWindow"))

        wall_totals = defaultdict(float)
        for wall in walls:
            if not is_external_wall(wall):
                continue
            area = get_element_area(wall)
            if area <= 0:
                continue
            orientation = get_wall_direction(wall) or "Unknown"
            wall_totals[orientation] += area

        window_totals = defaultdict(float)
        for window in windows:
            area = element_area(window)
            if area is None:
                continue
            orientation = element_orientation(window) or "Unknown"
            window_totals[orientation] += area

        orientations = set(wall_totals.keys()) | set(window_totals.keys())
        if not orientations:
            return {}

        result = {}
        for orientation in orientations:
            result[orientation] = {
                "wall_area": wall_totals.get(orientation, 0.0),
                "window_area": window_totals.get(orientation, 0.0),
            }
        return result
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
