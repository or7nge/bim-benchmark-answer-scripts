from scripts.question_helpers import count_elements_by_storey, get_ordered_storeys, open_ifc


def windows_per_storey(ifc_file_path):
    """Count windows assigned to each building storey."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return {"No windows found": 0}

        storeys = get_ordered_storeys(model)
        counts = count_elements_by_storey(storeys, windows)
        return counts if counts else {"Unassigned": len(windows)}
    except Exception as exc:  # pragma: no cover - defensive
        return f"Error: {exc}"
