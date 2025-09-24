import ifcopenshell

from scripts.ifc_utils import get_wall_length


def total_wall_length(ifc_file_path):
    """Calculate total length of all walls - simplified approach"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = list(ifc_file.by_type("IfcWall"))

        if not walls:
            return 0.0

        total_length = 0.0
        for wall in walls:
            try:
                length = get_wall_length(wall)
            except Exception:
                continue
            if length and length > 0:
                total_length += length

        return round(total_length, 2)

    except Exception as e:
        return f"Error: {str(e)}"
