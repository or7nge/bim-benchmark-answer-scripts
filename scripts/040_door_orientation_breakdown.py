from scripts.question_helpers import open_ifc, orientation_counts


def door_orientation_breakdown(ifc_file_path):
    """Return counts of doors facing each cardinal direction."""
    try:
        model = open_ifc(ifc_file_path)
        doors = list(model.by_type("IfcDoor"))
        if not doors:
            return {"No doors found": 0}
        counts = orientation_counts(doors, axis_index=1)
        return counts if counts else {"Unknown": len(doors)}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
