from scripts.question_helpers import open_ifc, orientation_counts


def window_orientation_breakdown(ifc_file_path):
    """Return counts of windows facing each cardinal direction."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return {"No windows found": 0}
        counts = orientation_counts(windows, axis_index=1)
        return counts if counts else {"Unknown": len(windows)}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
