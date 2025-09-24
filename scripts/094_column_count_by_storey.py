from scripts.question_helpers import count_elements_by_storey, get_ordered_storeys, open_ifc


def column_count_by_storey(ifc_file_path):
    """Count structural columns per storey."""
    try:
        model = open_ifc(ifc_file_path)
        columns = list(model.by_type("IfcColumn"))
        if not columns:
            return {"No columns": 0}
        storeys = get_ordered_storeys(model)
        counts = count_elements_by_storey(storeys, columns)
        return counts if counts else {"Unassigned": len(columns)}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
