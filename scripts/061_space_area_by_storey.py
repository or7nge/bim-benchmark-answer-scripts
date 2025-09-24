from scripts.question_helpers import elements_area_by_storey, get_ordered_storeys, open_ifc


def space_area_by_storey(ifc_file_path):
    """Sum space floor area for each storey."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return {}
        storeys = get_ordered_storeys(model)
        return elements_area_by_storey(storeys, spaces)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
