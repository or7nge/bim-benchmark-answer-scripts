import ifcopenshell
import ifcopenshell.util.element


def rooms_with_outdoor_access(ifc_file_path):
    """Find which room types have direct access to outdoor spaces"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        doors = ifc_file.by_type("IfcDoor")

        if not spaces:
            return []

        outdoor_access_rooms = set()

        # Method 1: Find doors that lead outside
        external_doors = []
        for door in doors:
            if _is_external_door(door):
                external_doors.append(door)

        # Find spaces connected to external doors
        for door in external_doors:
            connected_spaces = _find_spaces_connected_by_element(door, spaces)
            for space in connected_spaces:
                room_type = _get_room_type(space)
                if room_type:
                    outdoor_access_rooms.add(room_type)

        # Method 2: Find spaces with direct external wall access
        for space in spaces:
            if _has_external_wall_access(space):
                room_type = _get_room_type(space)
                if room_type:
                    outdoor_access_rooms.add(room_type)

        return sorted(list(outdoor_access_rooms)) if outdoor_access_rooms else ["No outdoor access found"]

    except Exception as e:
        return f"Error: {str(e)}"


# Helper functions (stubs for workspace consistency)
def _is_external_door(door):
    # ...existing code...
    pass


def _find_spaces_connected_by_element(door, spaces):
    # ...existing code...
    return []


def _get_room_type(space):
    # ...existing code...
    pass


def _has_external_wall_access(space):
    # ...existing code...
    pass
