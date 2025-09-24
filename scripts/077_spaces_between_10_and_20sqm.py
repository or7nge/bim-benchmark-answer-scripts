from scripts.question_helpers import element_area, open_ifc


def spaces_between_10_and_20sqm(ifc_file_path):
    """Count spaces whose area is between 10 and 20 m² (inclusive of lower bound)."""
    try:
        model = open_ifc(ifc_file_path)
        count = 0
        for space in model.by_type("IfcSpace"):
            area = element_area(space)
            if area is None:
                continue
            if 10.0 <= area < 20.0:
                count += 1
        return count
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
