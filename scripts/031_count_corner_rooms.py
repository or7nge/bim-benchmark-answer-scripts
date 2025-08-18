import ifcopenshell
import ifcopenshell.util.placement


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
    # Check if wall is defined as external
    if hasattr(wall, "PredefinedType"):
        if "EXTERNAL" in str(wall.PredefinedType):
            return True
    # Check property sets for external indication (manual walk)
    try:
        for rel in getattr(wall, "IsDefinedBy", []):
            prop_set = getattr(rel, "RelatingPropertyDefinition", None)
            if prop_set and hasattr(prop_set, "HasProperties"):
                for prop in prop_set.HasProperties:
                    if prop.Name.lower() == "isexternal" and hasattr(prop, "NominalValue"):
                        if str(prop.NominalValue.wrappedValue).lower() == "true":
                            return True
    except Exception:
        pass
    # Fallback: check for 'external' in name/description
    if "external" in (getattr(wall, "Name", "") or "").lower() or "external" in (getattr(wall, "Description", "") or "").lower():
        return True
    return False
