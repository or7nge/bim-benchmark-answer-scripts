import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.element


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


# Helper function stub
def _is_external_wall(wall):
    """Check if a wall is external (simplified heuristic)"""
    # Same external wall detection logic
    psets = ifcopenshell.util.element.get_psets(wall)
    is_external = False

    # Check IsExternal property
    for pset_data in psets.values():
        if "IsExternal" in pset_data and pset_data["IsExternal"]:
            is_external = True
            break

    # Check name for external keywords
    if not is_external and hasattr(wall, "Name") and wall.Name:
        external_keywords = ["наружн", "внешн", "external", "exterior", "фасад", "outer"]
        is_external = any(keyword in wall.Name.lower() for keyword in external_keywords)

    # Check wall type
    if not is_external and hasattr(wall, "IsDefinedBy"):
        for definition in wall.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByType"):
                wall_type = definition.RelatingType
                if wall_type and hasattr(wall_type, "Name") and wall_type.Name:
                    external_keywords = ["наружн", "внешн", "external", "exterior", "фасад"]
                    is_external = any(keyword in wall_type.Name.lower() for keyword in external_keywords)
                    break

    return is_external
