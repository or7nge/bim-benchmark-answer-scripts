from scripts.question_helpers import count_elements_by_storey, get_ordered_storeys, open_ifc


def storey_most_windows(ifc_file_path):
    """Identify the storey with the highest window count."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return "No windows found"
        storeys = get_ordered_storeys(model)
        counts = count_elements_by_storey(storeys, windows)
        if not counts:
            return "No storey assignments"
        target = max(counts.items(), key=lambda item: (item[1], item[0]))
        return target[0]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
