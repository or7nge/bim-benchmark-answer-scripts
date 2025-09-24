import ifcopenshell
from scripts.ifc_utils import is_external_wall


def count_corner_rooms(ifc_file_path):
    """Count rooms that are corner rooms (have walls on 2+ exterior sides)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        walls = ifc_file.by_type("IfcWall")

        if not spaces:
            return 0

        external_walls = [wall for wall in walls if is_external_wall(wall)]
        corner_rooms = 0

        for space in spaces:
            external_wall_count = 0

            # Try BoundedBy first
            if hasattr(space, "BoundedBy") and space.BoundedBy:
                for boundary in space.BoundedBy:
                    if hasattr(boundary, "RelatedBuildingElement"):
                        element = boundary.RelatedBuildingElement
                        if element in external_walls:
                            external_wall_count += 1
            else:
                # Fallback: geometric proximity (centroid to wall axis)
                if hasattr(space, "ObjectPlacement") and space.ObjectPlacement:
                    try:
                        space_loc = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
                        if space_loc:
                            for wall in external_walls:
                                if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
                                    wall_loc = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
                                    if wall_loc:
                                        dist = ((space_loc[0] - wall_loc[0]) ** 2 + (space_loc[1] - wall_loc[1]) ** 2) ** 0.5
                                        if dist < 1.5:
                                            external_wall_count += 1
                    except Exception:
                        pass

            if external_wall_count >= 2:
                corner_rooms += 1

        return corner_rooms

    except Exception as e:
        return f"Error: {str(e)}"
