from scripts.question_helpers import element_area, open_ifc


def largest_windows(ifc_file_path):
    """List the five windows with the greatest glazed area."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return []

        window_areas = []
        for window in windows:
            area = element_area(window)
            if area is None:
                continue
            name = getattr(window, "Name", None) or getattr(window, "GlobalId", "Unknown")
            window_areas.append({"name": str(name), "area": area})

        window_areas.sort(key=lambda item: item["area"], reverse=True)
        return window_areas[:5]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
