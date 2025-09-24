from scripts.ifc_utils import get_element_area, is_external_wall
from scripts.question_helpers import element_area, open_ifc, unique_elements


def building_envelope_area(ifc_file_path):
    """Approximate total external envelope area (walls + roofs + windows)."""
    try:
        model = open_ifc(ifc_file_path)

        walls = unique_elements(
            list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        )
        external_walls = [wall for wall in walls if is_external_wall(wall)]
        wall_area = sum(max(get_element_area(wall), 0.0) for wall in external_walls)

        windows = list(model.by_type("IfcWindow"))
        window_area = sum(area for area in (element_area(window) for window in windows) if area is not None)

        roofs = list(model.by_type("IfcRoof"))
        roof_area = sum(max(get_element_area(roof), 0.0) for roof in roofs)

        return wall_area + window_area + roof_area
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
