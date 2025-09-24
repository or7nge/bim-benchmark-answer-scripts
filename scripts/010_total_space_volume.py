import ifcopenshell
from scripts.ifc_utils import get_space_volume


def total_space_volume(ifc_file_path):
    """Calculate total space volume from geometry"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = [s for s in ifc_file.by_type("IfcSpace") if hasattr(s, "is_a")]
        total_volume = 0.0

        for space in spaces:
            try:
                total_volume += get_space_volume(space)
            except:
                continue

        return round(total_volume, 2)

    except Exception as e:
        return f"Error: {str(e)}"
