from scripts.question_helpers import get_ordered_storeys, open_ifc, orientation_counts_by_storey


def door_orientation_by_storey(ifc_file_path):
    """Provide door orientation breakdown for each storey."""
    try:
        model = open_ifc(ifc_file_path)
        doors = list(model.by_type("IfcDoor"))
        if not doors:
            return {}
        storeys = get_ordered_storeys(model)
        breakdown = orientation_counts_by_storey(storeys, doors, axis_index=1)
        return breakdown
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
