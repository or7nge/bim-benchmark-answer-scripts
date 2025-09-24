from scripts.question_helpers import elements_area_by_storey, get_ordered_storeys, open_ifc


def window_area_by_storey(ifc_file_path):
    """Calculate the total glazed area assigned to each storey."""
    try:
        model = open_ifc(ifc_file_path)
        windows = list(model.by_type("IfcWindow"))
        if not windows:
            return {"No windows found": 0.0}

        storeys = get_ordered_storeys(model)
        areas = elements_area_by_storey(storeys, windows)
        return areas if areas else {"Unassigned": 0.0}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
