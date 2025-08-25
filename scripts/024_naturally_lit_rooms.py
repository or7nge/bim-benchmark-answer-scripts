import ifcopenshell


def naturally_lit_rooms(ifc_file_path):
    """Counts the number of rooms that have at least one window by checking space boundaries."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
    except Exception as e:
        return f"Error opening IFC file: {e}"

    lit_rooms = set()

    # IfcRelSpaceBoundary connects a space to its bounding elements.
    # This is a more reliable way to find connections than inverse attributes.
    space_boundaries = ifc_file.by_type("IfcRelSpaceBoundary")

    for boundary in space_boundaries:
        space = boundary.RelatingSpace
        element = boundary.RelatedBuildingElement

        # Ensure we have a valid space and element to check
        if not space or not element or not space.is_a("IfcSpace"):
            continue

        # If the space is already identified as lit, skip to the next boundary
        if space.GlobalId in lit_rooms:
            continue

        # Case 1: The boundary is a window itself.
        if element.is_a("IfcWindow"):
            lit_rooms.add(space.GlobalId)
            continue

        # Case 2: The boundary is a wall/curtain wall that might contain a window.
        if element.is_a("IfcWall") or element.is_a("IfcWallStandardCase") or element.is_a("IfcCurtainWall"):
            # Check if the wall has openings.
            if not hasattr(element, "HasOpenings"):
                continue

            for rel_voids in element.HasOpenings:
                opening = rel_voids.RelatedOpeningElement
                if not opening or not hasattr(opening, "HasFillings"):
                    continue

                # Check if any filling in the opening is a window.
                for rel_fills in opening.HasFillings:
                    if rel_fills.RelatedBuildingElement and rel_fills.RelatedBuildingElement.is_a("IfcWindow"):
                        lit_rooms.add(space.GlobalId)
                        # Break loops once a window is found for this space boundary
                        break
                if space.GlobalId in lit_rooms:
                    break

    return len(lit_rooms)
