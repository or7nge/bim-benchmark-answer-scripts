import ifcopenshell
import ifcopenshell.util.element


def volume_per_floor(ifc_file_path):
    """Calculate total volume of enclosed spaces per floor"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        storeys = ifc_file.by_type("IfcBuildingStorey")
        spaces = ifc_file.by_type("IfcSpace")

        if not storeys or not spaces:
            return {"error": "No floors or spaces found"}

        floor_volumes = {}

        for storey in storeys:
            storey_name = storey.Name or f"Floor_{storey.id()}"
            total_volume = 0.0

            # Find spaces in this storey
            storey_spaces = []
            for space in spaces:
                if hasattr(space, "ContainedInStructure"):
                    for rel in space.ContainedInStructure:
                        if rel.RelatingStructure == storey:
                            storey_spaces.append(space)
                            break

            # Calculate volume for each space
            for space in storey_spaces:
                volume = _get_space_volume(space)
                if volume > 0:
                    total_volume += volume

            if total_volume > 0:
                floor_volumes[storey_name] = round(total_volume, 2)

        return floor_volumes if floor_volumes else {"message": "No volumes calculated"}

    except Exception as e:
        return f"Error: {str(e)}"


# Helper function stub
def _get_space_volume(space):
    # ...existing code...
    pass
