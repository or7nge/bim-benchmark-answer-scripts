from scripts.ifc_utils import get_space_volume, map_elements_to_spaces
from scripts.question_helpers import open_ifc


def volume_of_lit_spaces(ifc_file_path):
    """Total volume of spaces that have at least one mapped window."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        windows = list(model.by_type("IfcWindow"))
        if not spaces or not windows:
            return 0.0

        window_map = map_elements_to_spaces(
            model,
            windows,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=1,
        )
        lit_space_ids = {space.id() for matches in window_map.values() for space in matches}
        total = 0.0
        for space in spaces:
            if space.id() not in lit_space_ids:
                continue
            volume = get_space_volume(space)
            if volume > 0:
                total += volume
        return total
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
