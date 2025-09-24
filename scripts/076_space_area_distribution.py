from scripts.question_helpers import element_area, open_ifc, value_distribution_buckets


def space_area_distribution(ifc_file_path):
    """Bucket space areas into 10 m² intervals."""
    try:
        model = open_ifc(ifc_file_path)
        areas = [area for area in (element_area(space) for space in model.by_type("IfcSpace")) if area is not None]
        if not areas:
            return {}
        return value_distribution_buckets(areas, bucket_size=10.0)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
