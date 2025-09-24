from scripts.ifc_utils import is_external_wall
from scripts.question_helpers import (
    elements_area_by_storey,
    get_ordered_storeys,
    open_ifc,
    unique_elements,
)


def external_wall_area_by_storey(ifc_file_path):
    """Total exterior wall surface area per storey."""
    try:
        model = open_ifc(ifc_file_path)
        walls = unique_elements(
            list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        )
        external_walls = [wall for wall in walls if is_external_wall(wall)]
        if not external_walls:
            return {"No external walls": 0.0}

        storeys = get_ordered_storeys(model)
        areas = elements_area_by_storey(storeys, external_walls)
        return areas if areas else {"Unassigned": 0.0}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
