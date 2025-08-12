import ifcopenshell


def naturally_lit_rooms(ifc_file_path):
    """Count rooms that have natural lighting (contain windows)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        windows = ifc_file.by_type("IfcWindow")

        if not spaces:
            return 0

        lit_rooms = set()

        # Method 1: Check which spaces contain windows
        for window in windows:
            containing_spaces = _find_containing_spaces(window, spaces)
            lit_rooms.update(containing_spaces)

        # Method 2: Check spaces that have external walls with openings
        walls = ifc_file.by_type("IfcWall")
        for wall in walls:
            if _is_external_wall(wall):
                # Check if wall has openings (potential windows)
                if hasattr(wall, "HasOpenings"):
                    for opening_rel in wall.HasOpenings:
                        # Find spaces bounded by this wall
                        for space in spaces:
                            if _space_bounded_by_wall(space, wall):
                                lit_rooms.add(space.id())

        return len(lit_rooms)

    except Exception as e:
        return f"Error: {str(e)}"


def _find_containing_spaces(element, spaces):
    """Find spaces that contain a given element"""
    containing_spaces = []

    for space in spaces:
        if hasattr(space, "BoundedBy"):
            for boundary in space.BoundedBy:
                if hasattr(boundary, "RelatedBuildingElement"):
                    if boundary.RelatedBuildingElement == element:
                        containing_spaces.append(space.id())
                        break

    return containing_spaces


def _is_external_wall(wall):
    """Check if a wall is external (simplified heuristic)"""
    # Check if wall is defined as external
    if hasattr(wall, "PredefinedType"):
        if "EXTERNAL" in str(wall.PredefinedType):
            return True

    # Check property sets for external indication
    psets = ifcopenshell.util.element.get_psets(wall)
    for pset_data in psets.values():
        is_external = pset_data.get("IsExternal") or pset_data.get("External")
        if is_external:
            return True

    return False


def _space_bounded_by_wall(space, wall):
    """Check if a space is bounded by a specific wall"""
    if hasattr(space, "BoundedBy"):
        for boundary in space.BoundedBy:
            if hasattr(boundary, "RelatedBuildingElement"):
                if boundary.RelatedBuildingElement == wall:
                    return True
    return False
