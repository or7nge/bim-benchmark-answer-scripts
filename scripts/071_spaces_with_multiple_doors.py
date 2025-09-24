from scripts.ifc_utils import map_elements_to_spaces
from scripts.question_helpers import open_ifc


def spaces_with_multiple_doors(ifc_file_path):
    """Count spaces connected to two or more distinct doors."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        doors = list(model.by_type("IfcDoor"))
        if not spaces or not doors:
            return 0

        door_map = map_elements_to_spaces(
            model,
            doors,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=None,
        )
        space_counts = {}
        for door_spaces in door_map.values():
            for space in door_spaces:
                space_counts[space.id()] = space_counts.get(space.id(), 0) + 1
        return sum(1 for count in space_counts.values() if count > 1)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
