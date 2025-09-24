import ifcopenshell

from scripts.ifc_utils import map_elements_to_spaces


def rooms_without_windows(ifc_file_path):
    """Check if there are any rooms without windows"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        windows = ifc_file.by_type("IfcWindow")

        if not spaces:
            return False  # No rooms to check

        if not windows:
            return True  # No windows means all rooms are without windows

        element_map = map_elements_to_spaces(
            ifc_file,
            windows,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=1,
        )

        spaces_with_windows = {space.id() for matches in element_map.values() for space in matches}

        # If heuristic mapping failed completely, assume windows exist but could not be matched
        if not spaces_with_windows and windows:
            return True

        for space in spaces:
            if space.id() not in spaces_with_windows:
                return True

        return False

    except Exception as e:
        return f"Error: {str(e)}"
