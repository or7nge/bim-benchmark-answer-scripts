from scripts.question_helpers import element_area, open_ifc


def windows_larger_than_two_sq_m(ifc_file_path):
    """Count windows whose glazed area exceeds 2 m²."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return 0

        count = 0
        for window in windows:
            area = element_area(window)
            if area is not None and area > 2.0:
                count += 1
        return count
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
