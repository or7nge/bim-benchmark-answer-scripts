from scripts.question_helpers import count_elements_by_storey, get_ordered_storeys, open_ifc


def storey_most_columns(ifc_file_path):
    """Identify the storey hosting the largest number of columns."""
    try:
        model = open_ifc(ifc_file_path)
        columns = list(model.by_type("IfcColumn"))
        if not columns:
            return "No columns found"

        storeys = get_ordered_storeys(model)
        counts = count_elements_by_storey(storeys, columns)
        if not counts:
            return "No storey assignments"
        target = max(counts.items(), key=lambda item: (item[1], item[0]))
        return target[0]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
