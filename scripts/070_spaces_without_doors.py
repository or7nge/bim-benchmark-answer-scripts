from scripts.ifc_utils import map_elements_to_spaces
from scripts.question_helpers import open_ifc


def spaces_without_doors(ifc_file_path):
    """Count spaces that do not map to any door."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        doors = list(model.by_type("IfcDoor"))
        if not spaces:
            return 0
        if not doors:
            return len(spaces)

        door_map = map_elements_to_spaces(
            model,
            doors,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=None,
        )
        spaces_with_doors = {space.id() for matches in door_map.values() for space in matches}
        return sum(1 for space in spaces if space.id() not in spaces_with_doors)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
