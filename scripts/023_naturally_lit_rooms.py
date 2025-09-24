import ifcopenshell


def naturally_lit_rooms(ifc_file_path):
    """Counts the number of rooms that have at least one window by checking space boundaries."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
    except Exception as e:
        return f"Error opening IFC file: {e}"

    lit_rooms = set()

    # Try using IfcRelSpaceBoundary first
    space_boundaries = ifc_file.by_type("IfcRelSpaceBoundary")
    if space_boundaries:
        for boundary in space_boundaries:
            space = boundary.RelatingSpace
            element = boundary.RelatedBuildingElement

            if not space or not element or not space.is_a("IfcSpace"):
                continue
            if space.GlobalId in lit_rooms:
                continue
            if element.is_a("IfcWindow"):
                lit_rooms.add(space.GlobalId)
                continue
            if element.is_a("IfcWall") or element.is_a("IfcWallStandardCase") or element.is_a("IfcCurtainWall"):
                if not hasattr(element, "HasOpenings"):
                    continue
                for rel_voids in element.HasOpenings:
                    opening = rel_voids.RelatedOpeningElement
                    if not opening or not hasattr(opening, "HasFillings"):
                        continue
                    for rel_fills in opening.HasFillings:
                        if rel_fills.RelatedBuildingElement and rel_fills.RelatedBuildingElement.is_a("IfcWindow"):
                            lit_rooms.add(space.GlobalId)
                            break
                    if space.GlobalId in lit_rooms:
                        break
    else:
        # Fallback: For each IfcSpace, check for windows in its boundaries or nearby elements
        for space in ifc_file.by_type("IfcSpace"):
            # Check if the space is already counted
            if space.GlobalId in lit_rooms:
                continue
            # Check related elements via ContainsElements (for spatial structure)
            if hasattr(space, "BoundedBy"):
                for rel in space.BoundedBy:
                    element = getattr(rel, "RelatedBuildingElement", None)
                    if element and element.is_a("IfcWindow"):
                        lit_rooms.add(space.GlobalId)
                        break
            # Fallback: Check if any window is spatially contained in the space
            if hasattr(space, "ContainsElements"):
                for rel in space.ContainsElements:
                    for elem in getattr(rel, "RelatedElements", []):
                        if elem.is_a("IfcWindow"):
                            lit_rooms.add(space.GlobalId)
                            break
                    if space.GlobalId in lit_rooms:
                        break
            # Fallback: Check if any window is geometrically close (brute force)
            # This is a last resort and may be slow for large models
            if space.GlobalId not in lit_rooms:
                for window in ifc_file.by_type("IfcWindow"):
                    # If the window is on the same floor or spatial structure as the space
                    if hasattr(window, "ContainedInStructure") and hasattr(space, "ContainedInStructure"):
                        if window.ContainedInStructure == space.ContainedInStructure:
                            lit_rooms.add(space.GlobalId)
                            break

    return len(lit_rooms)
