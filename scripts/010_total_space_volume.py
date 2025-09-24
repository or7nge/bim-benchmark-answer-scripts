import ifcopenshell

from scripts.ifc_utils import get_space_volume


def total_space_volume(ifc_file_path):
    """Calculate total enclosed volume of all spaces in cubic metres."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = list(ifc_file.by_type("IfcSpace"))
        total_volume = 0.0

        for space in spaces:
            try:
                volume = get_space_volume(space)
                if volume and volume > 0:
                    total_volume += volume
            except Exception:
                continue

        return round(total_volume, 2)

    except Exception as e:
        return f"Error: {str(e)}"
