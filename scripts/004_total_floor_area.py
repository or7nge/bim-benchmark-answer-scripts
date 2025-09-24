import ifcopenshell

from scripts.ifc_utils import get_element_area


def total_floor_area(ifc_file_path):
    """Return the summed floor area of all spaces in square metres."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = [space for space in ifc_file.by_type("IfcSpace")]

        if not spaces:
            return 0.0

        total_area = 0.0
        for space in spaces:
            try:
                area = get_element_area(space)
                if area and area > 0:
                    total_area += area
            except Exception:
                continue

        return round(total_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"
