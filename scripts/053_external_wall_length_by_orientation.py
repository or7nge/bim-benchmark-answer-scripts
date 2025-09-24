from collections import defaultdict

from scripts.ifc_utils import get_wall_direction, get_wall_length, is_external_wall
from scripts.question_helpers import open_ifc, unique_elements


def external_wall_length_by_orientation(ifc_file_path):
    """Sum external wall lengths grouped by orientation."""
    try:
        model = open_ifc(ifc_file_path)
        walls = unique_elements(
            list(model.by_type("IfcWall")) + list(model.by_type("IfcWallStandardCase"))
        )
        if not walls:
            return {"No walls found": 0.0}

        totals = defaultdict(float)
        for wall in walls:
            if not is_external_wall(wall):
                continue
            direction = get_wall_direction(wall) or "Unknown"
            length = get_wall_length(wall)
            if length <= 0:
                continue
            totals[direction] += length

        return dict(totals) if totals else {"Unknown": 0.0}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
