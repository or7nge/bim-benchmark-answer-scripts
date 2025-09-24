from scripts.question_helpers import element_area, open_ifc, value_distribution_buckets


def window_area_distribution(ifc_file_path):
    """Bucket window areas into 1.0 m² intervals."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return {}

        areas = [area for area in (element_area(window) for window in windows) if area is not None]
        if not areas:
            return {}
        return value_distribution_buckets(areas, bucket_size=1.0)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
