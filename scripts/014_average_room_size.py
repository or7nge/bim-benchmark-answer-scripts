import ifcopenshell
from scripts.ifc_utils import get_element_area


def average_room_size(ifc_file_path):
    """Calculate average room size in the building, using geometry if properties are missing."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        total_area = 0.0
        valid_spaces = 0

        for space in spaces:
            area = get_element_area(space)
            if area > 0:
                total_area += area
                valid_spaces += 1

        if valid_spaces == 0:
            return 0.0

        average = total_area / valid_spaces
        return round(average, 2)

    except Exception as e:
        return f"Error: {str(e)}"
