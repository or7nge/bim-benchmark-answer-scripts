from scripts.question_helpers import element_area, open_ifc


def top10_largest_spaces(ifc_file_path):
    """Return the ten largest spaces by area."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return []

        items = []
        for space in spaces:
            area = element_area(space)
            if area is None or area <= 0:
                continue
            name = getattr(space, "Name", None) or getattr(space, "LongName", None) or getattr(space, "GlobalId", "Unknown")
            items.append({"name": str(name), "area": area})

        items.sort(key=lambda item: item["area"], reverse=True)
        return items[:10]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
