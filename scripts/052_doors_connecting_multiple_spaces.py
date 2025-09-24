from scripts.ifc_utils import map_elements_to_spaces
from scripts.question_helpers import open_ifc


def doors_connecting_multiple_spaces(ifc_file_path):
    """Count how many doors are mapped to more than one adjacent space."""
    try:
        model = open_ifc(ifc_file_path)
        doors = list(model.by_type("IfcDoor"))
        spaces = list(model.by_type("IfcSpace"))
        if not doors or not spaces:
            return 0

        door_map = map_elements_to_spaces(
            model,
            doors,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=2,
        )
        return sum(1 for matches in door_map.values() if len(matches) > 1)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
