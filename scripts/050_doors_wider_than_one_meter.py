from scripts.question_helpers import get_element_dimensions, open_ifc


def doors_wider_than_one_meter(ifc_file_path):
    """Count doors with clear width greater than 1.0 m."""
    try:
        model = open_ifc(ifc_file_path)
        doors = list(model.by_type("IfcDoor"))
        if not doors:
            return 0

        count = 0
        for door in doors:
            width, _ = get_element_dimensions(door)
            if width is not None and width > 1.0:
                count += 1
        return count
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
