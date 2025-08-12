import ifcopenshell


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

        # Get spaces that contain windows
        spaces_with_windows = set()

        for window in windows:
            # Check if window is contained in any space
            if hasattr(window, "ContainedInStructure"):
                for rel in window.ContainedInStructure:
                    if rel.RelatingStructure.is_a("IfcSpace"):
                        spaces_with_windows.add(rel.RelatingStructure.id())

        # Check if any space doesn't have windows
        for space in spaces:
            if space.id() not in spaces_with_windows:
                return True

        return False

    except Exception as e:
        return f"Error: {str(e)}"
