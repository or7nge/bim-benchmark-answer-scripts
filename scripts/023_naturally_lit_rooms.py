import ifcopenshell

from scripts.ifc_utils import map_elements_to_spaces


def naturally_lit_rooms(ifc_file_path):
    """Counts the number of rooms that have at least one mapped window."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
    except Exception as e:
        return f"Error opening IFC file: {e}"

    spaces = list(ifc_file.by_type("IfcSpace"))
    windows = list(ifc_file.by_type("IfcWindow"))

    if not spaces or not windows:
        return 0

    window_map = map_elements_to_spaces(
        ifc_file,
        windows,
        tolerance_horizontal=0.75,
        tolerance_vertical=1.5,
        max_matches=1,
    )

    lit_space_ids = {space.id() for matches in window_map.values() for space in matches}
    return len(lit_space_ids)
