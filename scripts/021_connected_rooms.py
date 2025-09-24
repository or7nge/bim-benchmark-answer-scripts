import itertools

import ifcopenshell

from scripts.ifc_utils import map_elements_to_spaces


def connected_rooms(ifc_file_path):
    """Find which rooms are directly connected to each other"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = list(ifc_file.by_type("IfcSpace"))
        doors = list(ifc_file.by_type("IfcDoor"))
        openings = list(ifc_file.by_type("IfcOpeningElement"))

        if not spaces:
            return {"error": "No rooms found"}

        connections = {}
        space_dict = {space.id(): space.Name or f"Room_{space.id()}" for space in spaces}

        def _record_connections(space_pairs):
            for space1, space2 in space_pairs:
                name1 = space_dict.get(space1.id())
                name2 = space_dict.get(space2.id())
                if not name1 or not name2 or name1 == name2:
                    continue
                connections.setdefault(name1, set()).add(name2)
                connections.setdefault(name2, set()).add(name1)

        door_map = map_elements_to_spaces(
            ifc_file,
            doors,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=2,
        )

        for matched_spaces in door_map.values():
            if len(matched_spaces) >= 2:
                _record_connections(itertools.combinations(matched_spaces, 2))

        if openings:
            opening_map = map_elements_to_spaces(
                ifc_file,
                openings,
                tolerance_horizontal=0.75,
                tolerance_vertical=1.5,
                max_matches=2,
            )
            for matched_spaces in opening_map.values():
                if len(matched_spaces) >= 2:
                    _record_connections(itertools.combinations(matched_spaces, 2))

        # Convert sets to lists for JSON serialization
        result = {room: list(connected) for room, connected in connections.items()}
        return result if result else {"message": "No room connections found"}

    except Exception as e:
        return f"Error: {str(e)}"
