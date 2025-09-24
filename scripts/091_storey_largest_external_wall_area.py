from scripts.ifc_utils import is_external_wall
from scripts.question_helpers import elements_area_by_storey, get_ordered_storeys, open_ifc


def storey_largest_external_wall_area(ifc_file_path):
    """Identify the storey with the highest exterior wall area."""
    try:
        model = open_ifc(ifc_file_path)
        walls = list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        external_walls = [wall for wall in walls if is_external_wall(wall)]
        if not external_walls:
            return "No external walls"

        storeys = get_ordered_storeys(model)
        areas = elements_area_by_storey(storeys, external_walls)
        if not areas:
            return "No storey assignments"
        target = max(areas.items(), key=lambda item: (item[1], item[0]))
        return target[0]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
