import ifcopenshell
from scripts.ifc_utils import get_space_height


def average_ceiling_height(ifc_file_path):
    """Calculate average ceiling height in the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        total_height = 0.0
        valid_spaces = 0

        for space in spaces:
            height = get_space_height(space)
            if height and height > 0:
                total_height += height
                valid_spaces += 1

        if valid_spaces == 0:
            # Fallback: use storey heights
            storeys = ifc_file.by_type("IfcBuildingStorey")
            if len(storeys) >= 2:
                elevations = [s.Elevation for s in storeys if s.Elevation is not None]
                if len(elevations) >= 2:
                    elevations.sort()
                    typical_height = elevations[1] - elevations[0]
                    return round(typical_height, 2)

            return 3.0  # Default assumption

        average = total_height / valid_spaces
        return round(average, 2)

    except Exception as e:
        return f"Error: {str(e)}"
