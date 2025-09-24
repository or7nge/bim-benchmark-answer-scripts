from scripts.ifc_utils import get_element_area, is_external_wall
from scripts.question_helpers import open_ifc


def external_to_internal_wall_area_ratio(ifc_file_path):
    """Return the ratio of external wall area to internal wall area."""
    try:
        model = open_ifc(ifc_file_path)
        walls = list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        if not walls:
            return 0.0

        external_area = 0.0
        internal_area = 0.0
        for wall in walls:
            area = get_element_area(wall)
            if area <= 0:
                continue
            if is_external_wall(wall):
                external_area += area
            else:
                internal_area += area

        if internal_area == 0:
            return float("inf") if external_area > 0 else 0.0
        return external_area / internal_area
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
