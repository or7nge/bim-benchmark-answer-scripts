import ifcopenshell
import ifcopenshell.util.element


def unique_ceiling_heights(ifc_file_path):
    """Count how many different ceiling heights exist in the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0

        heights = set()

        for space in spaces:
            height = _get_space_height(space)
            if height and height > 0:
                # Round to nearest 0.1 to group similar heights
                rounded_height = round(height, 1)
                heights.add(rounded_height)

        # If no heights found from spaces, check storeys
        if not heights:
            storeys = ifc_file.by_type("IfcBuildingStorey")
            if len(storeys) >= 2:
                elevations = [s.Elevation for s in storeys if s.Elevation is not None]
                if len(elevations) >= 2:
                    elevations.sort()
                    for i in range(len(elevations) - 1):
                        height = elevations[i + 1] - elevations[i]
                        heights.add(round(height, 1))

        return len(heights) if heights else 1  # Default to 1 if no data

    except Exception as e:
        return f"Error: {str(e)}"


# Helper function stub
def _get_space_height(space):
    # ...existing code...
    pass
