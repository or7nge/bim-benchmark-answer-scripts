import ifcopenshell
from scripts.ifc_utils import is_external_wall, get_element_area, get_wall_direction


def max_wall_direction(ifc_file_path):
    """Find which direction has the most external wall area"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = ifc_file.by_type("IfcWall")

        external_walls = [wall for wall in walls if is_external_wall(wall)]

        if not external_walls:
            return "No external walls found"

        direction_areas = {"North": 0.0, "South": 0.0, "East": 0.0, "West": 0.0}

        skipped = 0
        for wall in external_walls:
            area = get_element_area(wall)
            direction = get_wall_direction(wall)
            if direction is None:
                skipped += 1
                continue
            if area > 0 and direction in direction_areas:
                direction_areas[direction] += area

        if all(area == 0 for area in direction_areas.values()):
            return "Could not determine wall directions"

        max_direction = max(direction_areas, key=direction_areas.get)
        return max_direction

    except Exception as e:
        return f"Error: {str(e)}"
