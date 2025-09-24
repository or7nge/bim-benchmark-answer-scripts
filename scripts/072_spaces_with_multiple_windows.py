from scripts.ifc_utils import map_elements_to_spaces
from scripts.question_helpers import open_ifc


def spaces_with_multiple_windows(ifc_file_path):
    """Count spaces that have at least three mapped windows."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        windows = list(model.by_type("IfcWindow"))
        if not spaces or not windows:
            return 0

        window_map = map_elements_to_spaces(
            model,
            windows,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=None,
        )
        space_counts = {}
        for window_spaces in window_map.values():
            for space in window_spaces:
                space_counts[space.id()] = space_counts.get(space.id(), 0) + 1
        return sum(1 for count in space_counts.values() if count >= 3)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
