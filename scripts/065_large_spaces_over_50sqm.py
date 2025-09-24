from scripts.question_helpers import element_area, open_ifc


def large_spaces_over_50sqm(ifc_file_path):
    """List spaces whose area exceeds 50 m²."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        result = []
        for space in spaces:
            area = element_area(space)
            if area is None or area <= 50.0:
                continue
            name = getattr(space, "Name", None) or getattr(space, "LongName", None) or getattr(space, "GlobalId", "Unknown")
            result.append({"name": str(name), "area": area})
        result.sort(key=lambda item: item["area"], reverse=True)
        return result
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
