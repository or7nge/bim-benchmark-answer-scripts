import ifcopenshell


def count_corner_rooms(ifc_file_path):
    """Count rooms that are corner rooms (have walls on 2+ exterior sides)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        walls = ifc_file.by_type("IfcWall")

        if not spaces:
            return 0

        external_walls = [wall for wall in walls if _is_external_wall(wall)]
        corner_rooms = 0

        for space in spaces:
            external_wall_count = 0

            # Count external walls bounding this space
            if hasattr(space, "BoundedBy"):
                for boundary in space.BoundedBy:
                    if hasattr(boundary, "RelatedBuildingElement"):
                        element = boundary.RelatedBuildingElement
                        if element in external_walls:
                            external_wall_count += 1

            # Consider corner room if bounded by 2+ external walls
            if external_wall_count >= 2:
                corner_rooms += 1

        return corner_rooms

    except Exception as e:
        return f"Error: {str(e)}"


# Helper function stub
def _is_external_wall(wall):
    # ...existing code...
    pass
