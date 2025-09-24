from scripts.ifc_utils import is_external_wall
from scripts.question_helpers import (
    count_elements_by_storey,
    get_ordered_storeys,
    open_ifc,
    unique_elements,
)


def external_walls_per_storey(ifc_file_path):
    """Count external walls assigned to each storey."""
    try:
        model = open_ifc(ifc_file_path)
        walls = unique_elements(
            list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        )
        external_walls = [wall for wall in walls if is_external_wall(wall)]
        if not external_walls:
            return {"No external walls": 0}

        storeys = get_ordered_storeys(model)
        counts = count_elements_by_storey(storeys, external_walls)
        return counts if counts else {"Unassigned": len(external_walls)}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
