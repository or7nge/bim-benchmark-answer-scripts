import ifcopenshell


def floor_most_rooms(ifc_file_path):
    """Find which floor has the most rooms"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        storeys = ifc_file.by_type("IfcBuildingStorey")

        if not spaces or not storeys:
            return "No rooms or floors found"

        storey_dict = {storey.id(): storey.Name or f"Floor_{storey.id()}" for storey in storeys}

        room_count_per_floor = {}

        for space in spaces:
            storey_id = None

            # Find containing storey
            if hasattr(space, "ContainedInStructure"):
                for rel in space.ContainedInStructure:
                    if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                        storey_id = rel.RelatingStructure.id()
                        break

            if storey_id and storey_id in storey_dict:
                storey_name = storey_dict[storey_id]
                room_count_per_floor[storey_name] = room_count_per_floor.get(storey_name, 0) + 1

        if not room_count_per_floor:
            return "No room-floor relationships found"

        # Return floor with most rooms
        max_floor = max(room_count_per_floor, key=room_count_per_floor.get)
        return max_floor

    except Exception as e:
        return f"Error: {str(e)}"
