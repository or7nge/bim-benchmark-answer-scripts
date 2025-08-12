import ifcopenshell
import ifcopenshell.util.element


def doors_per_floor(ifc_file_path):
    """Count doors on each floor"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        doors = ifc_file.by_type("IfcDoor")
        storeys = ifc_file.by_type("IfcBuildingStorey")

        # Create mapping of storey names
        storey_dict = {storey.id(): storey.Name or f"Storey_{storey.id()}" for storey in storeys}

        door_count_per_floor = {}

        for door in doors:
            # Find which storey contains this door
            storey_id = None

            # Check through spatial containment relationships
            if hasattr(door, "ContainedInStructure"):
                for rel in door.ContainedInStructure:
                    if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                        storey_id = rel.RelatingStructure.id()
                        break

            if storey_id and storey_id in storey_dict:
                storey_name = storey_dict[storey_id]
                door_count_per_floor[storey_name] = door_count_per_floor.get(storey_name, 0) + 1

        return door_count_per_floor if door_count_per_floor else {"No doors found": 0}
    except Exception as e:
        return f"Error: {str(e)}"
