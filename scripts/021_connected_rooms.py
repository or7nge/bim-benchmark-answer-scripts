import ifcopenshell
import ifcopenshell.util.element


def connected_rooms(ifc_file_path):
    """Find which rooms are directly connected to each other"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        doors = ifc_file.by_type("IfcDoor")
        openings = ifc_file.by_type("IfcOpeningElement")

        if not spaces:
            return {"error": "No rooms found"}

        connections = {}
        space_dict = {space.id(): space.Name or f"Room_{space.id()}" for space in spaces}

        # Method 1: Through doors
        for door in doors:
            connected_spaces = _find_spaces_connected_by_element(door, spaces)
            if len(connected_spaces) >= 2:
                for i, space1 in enumerate(connected_spaces):
                    for space2 in connected_spaces[i + 1 :]:
                        name1 = space_dict[space1.id()]
                        name2 = space_dict[space2.id()]

                        if name1 not in connections:
                            connections[name1] = set()
                        if name2 not in connections:
                            connections[name2] = set()

                        connections[name1].add(name2)
                        connections[name2].add(name1)

        # Method 2: Through openings
        for opening in openings:
            connected_spaces = _find_spaces_connected_by_element(opening, spaces)
            if len(connected_spaces) >= 2:
                for i, space1 in enumerate(connected_spaces):
                    for space2 in connected_spaces[i + 1 :]:
                        name1 = space_dict[space1.id()]
                        name2 = space_dict[space2.id()]

                        if name1 not in connections:
                            connections[name1] = set()
                        if name2 not in connections:
                            connections[name2] = set()

                        connections[name1].add(name2)
                        connections[name2].add(name1)

        # Convert sets to lists for JSON serialization
        result = {room: list(connected) for room, connected in connections.items()}
        return result if result else {"message": "No room connections found"}

    except Exception as e:
        return f"Error: {str(e)}"


def _find_spaces_connected_by_element(element, spaces):
    """Find spaces that are connected by a door or opening"""
    connected_spaces = []

    # Check which spaces contain this element
    for space in spaces:
        if hasattr(space, "BoundedBy"):
            for boundary in space.BoundedBy:
                if hasattr(boundary, "RelatedBuildingElement"):
                    if boundary.RelatedBuildingElement == element:
                        connected_spaces.append(space)
                        break

    return connected_spaces
