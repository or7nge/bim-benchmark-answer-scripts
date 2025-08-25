import ifcopenshell
from scripts.ifc_utils import is_external_wall


def rooms_on_exterior(ifc_file_path):
    """Find which rooms share walls with the building exterior"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        walls = ifc_file.by_type("IfcWall")

        if not spaces:
            return []

        # Get external walls
        external_walls = []
        for wall in walls:
            if is_external_wall(wall):
                external_walls.append(wall)

        if not external_walls:
            return ["No external walls identified"]

        exterior_rooms = []

        for space in spaces:
            room_name = space.Name or f"Room_{space.id()}"
            has_exterior_wall = False

            # Method 1: Check BoundedBy relationships
            if hasattr(space, "BoundedBy"):
                for boundary in space.BoundedBy:
                    if hasattr(boundary, "RelatedBuildingElement"):
                        element = boundary.RelatedBuildingElement
                        if element in external_walls:
                            has_exterior_wall = True
                            break

            # Method 2: Check spatial relationships for walls
            if not has_exterior_wall:
                has_exterior_wall = _check_space_wall_proximity(space, external_walls)

            if has_exterior_wall:
                exterior_rooms.append(room_name)

        return sorted(exterior_rooms) if exterior_rooms else ["No exterior rooms found"]

    except Exception as e:
        return f"Error: {str(e)}"


def _check_space_wall_proximity(space, external_walls):
    """Check if space is near external walls (fallback method)"""
    try:
        # This is a simplified spatial proximity check
        # In real implementation, you'd use geometric analysis
        if hasattr(space, "ObjectPlacement") and space.ObjectPlacement:
            space_matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
            space_pos = (space_matrix[3][0], space_matrix[3][1])

            for wall in external_walls:
                if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
                    wall_matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
                    wall_pos = (wall_matrix[3][0], wall_matrix[3][1])

                    # Simple distance check (simplified)
                    distance = ((space_pos[0] - wall_pos[0]) ** 2 + (space_pos[1] - wall_pos[1]) ** 2) ** 0.5
                    if distance < 10.0:  # Within 10 units (adjust as needed)
                        return True
    except Exception:
        pass

    return False
