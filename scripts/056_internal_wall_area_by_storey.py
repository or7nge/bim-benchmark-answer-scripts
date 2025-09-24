from scripts.ifc_utils import is_external_wall
from scripts.question_helpers import (
    elements_area_by_storey,
    get_ordered_storeys,
    open_ifc,
    unique_elements,
)


def internal_wall_area_by_storey(ifc_file_path):
    """Total internal wall area per storey."""
    try:
        model = open_ifc(ifc_file_path)
        walls = unique_elements(
            list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        )
        internal_walls = [wall for wall in walls if not is_external_wall(wall)]
        if not internal_walls:
            return {"No internal walls": 0.0}

        storeys = get_ordered_storeys(model)
        areas = elements_area_by_storey(storeys, internal_walls)
        return areas if areas else {"Unassigned": 0.0}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
