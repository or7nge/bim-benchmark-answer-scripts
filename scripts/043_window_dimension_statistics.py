from scripts.question_helpers import get_element_dimensions, open_ifc


def window_dimension_statistics(ifc_file_path):
    """Return summary statistics for window width and height."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return {"count": 0, "average_width": 0.0, "average_height": 0.0}

        widths = []
        heights = []
        for window in windows:
            width, height = get_element_dimensions(window)
            if width is not None:
                widths.append(width)
            if height is not None:
                heights.append(height)

        def stats(values):
            if not values:
                return {"min": 0.0, "max": 0.0, "average": 0.0}
            total = sum(values)
            return {
                "min": min(values),
                "max": max(values),
                "average": total / len(values),
            }

        width_stats = stats(widths)
        height_stats = stats(heights)

        return {
            "count": len(windows),
            "width_min": width_stats["min"],
            "width_max": width_stats["max"],
            "width_avg": width_stats["average"],
            "height_min": height_stats["min"],
            "height_max": height_stats["max"],
            "height_avg": height_stats["average"],
        }
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
