from scripts.question_helpers import get_ordered_storeys, open_ifc, storey_elevation


def storeys_below_ground(ifc_file_path):
    """Count storeys with elevation below 0."""
    try:
        model = open_ifc(ifc_file_path)
        return sum(1 for storey in get_ordered_storeys(model) if storey_elevation(storey) < 0)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
